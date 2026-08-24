from pathlib import Path
from pydantic import BaseModel
from typing import Optional

from app.raw_storage import list_raw_documents
from app.repository_intelligence import (
    build_repository_modules,
    repository_summary,
)


class LearningPathRequest(BaseModel):
    project_id: str
    repo_metadata: Optional[dict] = None


def build_learning_path(source_files: list):
    """
    Document-based fallback.

    Used when repository metadata is unavailable.
    """

    modules = []

    PRIORITY = [
        (
            ["team_foundations"],
            "Team Foundations",
            "Understand collaboration workflow and engineering standards.",
        ),
        (
            ["readme"],
            "Project Overview",
            "Understand the project purpose, architecture, and key components.",
        ),
        (
            ["architecture"],
            "Architecture",
            "Understand the system architecture and major components.",
        ),
        (
            ["setup", "developing_locally"],
            "Local Setup",
            "Set up the development environment and run the project locally.",
        ),
        (
            ["api"],
            "API Integration",
            "Explore APIs, contracts and integration points.",
        ),
        (
            ["refund"],
            "Refund Flow",
            "Learn the refund lifecycle and related business logic.",
        ),
        (
            ["bug"],
            "Debugging & KT",
            "Review common issues and troubleshooting guidance.",
        ),
    ]

    used = set()
    step = 1

    for keywords, title, description in PRIORITY:

        matched = [
            f
            for f in source_files
            if any(
                keyword in f.lower()
                for keyword in keywords
            )
            and f not in used
        ]

        if matched:

            modules.append({
                "step": step,
                "title": title,
                "description": description,
                "sources": matched,
            })

            used.update(matched)
            step += 1

    for f in source_files:

        if f in used:
            continue

        name = (
            f.rsplit(".", 1)[0]
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        modules.append({
            "step": step,
            "title": name,
            "description":
                "Learn the concepts and implementation details "
                "covered in this document.",
            "sources": [f],
        })

        step += 1

    return modules


def generate_learning_path(
    project_id: str,
    repo_metadata: Optional[dict] = None,
):
    print("🔥 GENERATE_LEARNING_PATH FUNCTION WAS CALLED 🔥")
    docs = list_raw_documents(
        project_id=project_id
    )

    docs = list_raw_documents(
        project_id=project_id
    )

    source_files = [
        d["source_file"]
        for d in docs
    ]

    # --------------------------------------------------
    # FALLBACK: documentation-only project
    # --------------------------------------------------

    if not repo_metadata:

        return {
            "project_id": project_id,
            "learning_path":
                build_learning_path(
                    source_files
                ),
            "repository_summary": None,
            "mode": "documentation_only",
        }

    # --------------------------------------------------
    # REPOSITORY-AWARE MODE
    # --------------------------------------------------

    modules = []
    step = 1
    used_files = set()

    # --------------------------------------------------
    # FOUNDATION LAYER
    # --------------------------------------------------

    for keywords, title, description in [

        (
            ["team_foundations"],
            "Team Foundations",
            "Understand collaboration workflow and engineering standards.",
        ),

        (
            ["readme"],
            "Project Overview",
            "Understand the project's purpose, architecture, and key components.",
        ),
    ]:

        matched = [
            f
            for f in source_files
            if any(
                keyword in f.lower()
                for keyword in keywords
            )
        ]

        if matched:

            modules.append({
                "step": step,
                "title": title,
                "description": description,
                "purpose": description,
                "sources": matched,
                "confidence": "high",
                "evidence": [
                    "Provided directly by project/team documentation."
                ],
            })

            used_files.update(matched)
            step += 1

    # --------------------------------------------------
    # REPOSITORY INTELLIGENCE
    # --------------------------------------------------

    repo_modules = build_repository_modules(
        repo_metadata,
        max_modules=6,
        start_step=step,
    )

    print("\n========== REPOSITORY MODULES DEBUG ==========")
    print("repo_modules count:", len(repo_modules))
    for module in repo_modules:
        print(
            f"Step {module.get('step')}: "
            f"{module.get('title')} | "
            f"score={module.get('importance_score')} | "
            f"confidence={module.get('confidence')} | "
            f"prerequisites={module.get('prerequisites')}"
        )
    print("==============================================\n")

    modules.extend(repo_modules)

    step += len(repo_modules)

    # --------------------------------------------------
    # REMAINING PROJECT DOCUMENTATION
    # --------------------------------------------------

    remaining_files = [
        f
        for f in source_files
        if f not in used_files
    ]

    for f in remaining_files:

        name = (
            f.rsplit(".", 1)[0]
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        modules.append({
            "step": step,
            "title": name,
            "description":
                "Learn the concepts and implementation details "
                "covered in this document.",
            "purpose":
                "Provide additional project-specific knowledge.",
            "sources": [f],
            "confidence": "medium",
            "evidence": [
                "Provided by project documentation."
            ],
        })

        step += 1

    return {
        "project_id": project_id,
        "learning_path": modules,
        "repository_summary":
            repository_summary(
                repo_metadata
            ),
        "mode": "repository_aware",
    }


if __name__ == "__main__":

    import json

    result = generate_learning_path(
        "refund-service"
    )

    data_dir = (
        Path(__file__).parent.parent
        / "data"
    )

    output_path = (
        data_dir
        / "learning_path.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
        )

    print(
        "Generated learning path\n"
    )

    for item in result[
        "learning_path"
    ]:

        print(
            f"Step {item['step']}: "
            f"{item['title']}"
        )

        print(
            f"Purpose: "
            f"{item.get('purpose', '')}"
        )

        print(
            f"Confidence: "
            f"{item.get('confidence', '')}"
        )

        print(
            f"Estimated time: "
            f"{item.get('estimated_minutes', 'N/A')} min"
        )

        print(
            f"Prerequisites: "
            f"{item.get('prerequisites', [])}"
        )

        print(
            "Evidence:"
        )

        for evidence in item.get(
            "evidence",
            [],
        ):
            print(
                f"  - {evidence}"
            )

        print()

    print(
        f"Saved to: {output_path.name}"
    )