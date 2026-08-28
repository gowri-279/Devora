from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from app.raw_storage import (
    list_raw_documents,
    list_raw_document_content,
)
from app.repository_intelligence import (
    build_repository_modules,
    repository_summary,
)


class LearningPathRequest(BaseModel):
    project_id: str
    repo_metadata: Optional[dict] = None


# ==========================================================
# DOCUMENT / SOURCE HELPERS
# ==========================================================


def _source_name(source_file: str) -> str:
    """
    Convert a source path into a readable filename.

    Example:
        fastapi/security/oauth2.py
        ->
        oauth2.py
    """

    return Path(source_file).name


def _source_belongs_to_module(
    source_file: str,
    module_path: str,
) -> bool:
    """
    Determine whether a stored source file belongs to a
    repository module.

    Matching is based on the directory containing the file.

    Examples:

        module:
            fastapi/security

        matches:
            fastapi/security/__init__.py
            fastapi/security/oauth2.py

        does NOT match:
            fastapi/openapi/models.py
            fastapi/security/utils/helper.py

    This keeps module content aligned with the repository
    module structure instead of recursively swallowing every
    nested module.

    For the root package:

        fastapi

    files directly under:

        fastapi/

    are included.
    """

    source_path = Path(
        source_file.replace("\\", "/")
    )

    module = Path(
        module_path.replace("\\", "/").rstrip("/")
    )

    try:
        parent = source_path.parent

        return parent == module

    except Exception:
        return False


def _collect_module_sources(
    module_path: str,
    raw_documents: list,
) -> list:
    """
    Find all actual raw source documents belonging to a
    repository module.

    Returns complete raw-document records so the learner
    can eventually access the original source content.
    """

    matches = []

    for document in raw_documents:

        source_file = document.get(
            "source_file",
            "",
        )

        if not source_file:
            continue

        if _source_belongs_to_module(
            source_file,
            module_path,
        ):
            matches.append(document)

    matches.sort(
        key=lambda d: d.get(
            "source_file",
            "",
        )
    )

    return matches


def _build_course_content(
    source_documents: list,
) -> list:
    """
    Convert raw source documents into learner-facing course
    content records.

    The original text is preserved.

    No AI-generated content is inserted here.

    The repository/document itself remains the source of truth.
    """

    content = []

    for document in source_documents:

        source_file = document.get(
            "source_file",
            "",
        )

        text = document.get(
            "text",
            "",
        )

        if not source_file:
            continue

        content.append({
            "source_file": source_file,

            "filename":
                _source_name(
                    source_file
                ),

            "scope":
                document.get(
                    "scope",
                    "project",
                ),

            "content":
                text,
        })

    return content


# ==========================================================
# DOCUMENTATION-ONLY FALLBACK
# ==========================================================


def build_learning_path(
    source_files: list,
    raw_documents: Optional[list] = None,
):
    """
    Document-based fallback.

    Used when repository metadata is unavailable.

    The learning path is generated from uploaded documents,
    while the actual document content is preserved separately
    in the course-content field.
    """

    if raw_documents is None:
        raw_documents = []

    raw_by_source = {
        d.get("source_file"): d
        for d in raw_documents
    }

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

            course_content = []

            for source_file in matched:

                document = raw_by_source.get(
                    source_file
                )

                if document:

                    course_content.append({
                        "source_file":
                            source_file,

                        "filename":
                            _source_name(
                                source_file
                            ),

                        "scope":
                            document.get(
                                "scope",
                                "project",
                            ),

                        "content":
                            document.get(
                                "text",
                                "",
                            ),
                    })

            modules.append({
                "step":
                    step,

                "title":
                    title,

                "description":
                    description,

                "purpose":
                    description,

                "sources":
                    matched,

                "course_content":
                    course_content,
            })

            used.update(
                matched
            )

            step += 1

    # --------------------------------------------------
    # REMAINING DOCUMENTS
    # --------------------------------------------------

    for f in source_files:

        if f in used:
            continue

        name = (
            f.rsplit(".", 1)[0]
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        document = raw_by_source.get(
            f
        )

        course_content = []

        if document:

            course_content.append({
                "source_file":
                    f,

                "filename":
                    _source_name(
                        f
                    ),

                "scope":
                    document.get(
                        "scope",
                        "project",
                    ),

                "content":
                    document.get(
                        "text",
                        "",
                    ),
            })

        modules.append({
            "step":
                step,

            "title":
                name,

            "description":
                "Learn the concepts and implementation details "
                "covered in this document.",

            "purpose":
                "Learn the actual content provided by the document.",

            "sources":
                [f],

            "course_content":
                course_content,
        })

        step += 1

    return modules


# ==========================================================
# MAIN LEARNING-PATH GENERATOR
# ==========================================================


def generate_learning_path(
    project_id: str,
    repo_metadata: Optional[dict] = None,
):
    print(
        "\n🔥 GENERATE_LEARNING_PATH FUNCTION WAS CALLED 🔥"
    )

    # --------------------------------------------------
    # DOCUMENT DISCOVERY
    # --------------------------------------------------

    docs = list_raw_documents(
        project_id=project_id
    )

    source_files = [
        d["source_file"]
        for d in docs
    ]

    # --------------------------------------------------
    # COMPLETE RAW DOCUMENTS
    # --------------------------------------------------
    #
    # list_raw_documents() intentionally excludes the
    # original text.
    #
    # The course-content layer needs the actual original
    # document content, so we use:
    #
    #     list_raw_document_content()
    #
    # Team documents are included automatically because
    # raw_storage.py treats them as shared documents.
    # --------------------------------------------------

    raw_documents = (
        list_raw_document_content(
            project_id=project_id
        )
    )

    print(
        "Raw documents available:",
        len(raw_documents),
    )

    # --------------------------------------------------
    # FALLBACK: DOCUMENTATION ONLY
    # --------------------------------------------------

    if not repo_metadata:

        return {
            "project_id":
                project_id,

            "learning_path":
                build_learning_path(
                    source_files,
                    raw_documents=raw_documents,
                ),

            "repository_summary":
                None,

            "mode":
                "documentation_only",
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

            course_content = []

            for source_file in matched:

                document = next(
                    (
                        d
                        for d in raw_documents
                        if d.get(
                            "source_file"
                        ) == source_file
                    ),
                    None,
                )

                if document:

                    course_content.append({
                        "source_file":
                            source_file,

                        "filename":
                            _source_name(
                                source_file
                            ),

                        "scope":
                            document.get(
                                "scope",
                                "project",
                            ),

                        "content":
                            document.get(
                                "text",
                                "",
                            ),
                    })

            modules.append({
                "step":
                    step,

                "title":
                    title,

                "description":
                    description,

                "purpose":
                    description,

                "sources":
                    matched,

                "confidence":
                    "high",

                "evidence": [
                    "Provided directly by project/team documentation."
                ],

                "course_content":
                    course_content,
            })

            used_files.update(
                matched
            )

            step += 1

    # --------------------------------------------------
    # REPOSITORY INTELLIGENCE
    # --------------------------------------------------
    #
    # IMPORTANT:
    #
    # repo_metadata is NOT generated here.
    #
    # It is supplied externally by the Repo Parser / Backend
    # flow.
    #
    # This function only consumes that metadata.
    # --------------------------------------------------

    repo_modules = build_repository_modules(
        repo_metadata,
        max_modules=6,
        start_step=step,
    )

    print(
        "\n========== REPOSITORY MODULES DEBUG =========="
    )

    print(
        "repo_modules count:",
        len(repo_modules),
    )

    for module in repo_modules:

        print(
            f"Step {module.get('step')}: "
            f"{module.get('title')} | "
            f"score={module.get('importance_score')} | "
            f"confidence={module.get('confidence')} | "
            f"prerequisites={module.get('prerequisites')}"
        )

    print(
        "==============================================\n"
    )

    # --------------------------------------------------
    # ATTACH ACTUAL REPOSITORY CONTENT
    # --------------------------------------------------

    for module in repo_modules:

        module_path = module.get(
            "sources",
            [""],
        )[0]

        source_documents = (
            _collect_module_sources(
                module_path,
                raw_documents,
            )
        )

        course_content = (
            _build_course_content(
                source_documents
            )
        )

        module["course_content"] = (
            course_content
        )

        # Make sure sources represent the actual
        # source files belonging to the module.
        module["source_files"] = [
            item["source_file"]
            for item in course_content
        ]

        print(
            f"Course content attached: "
            f"{module.get('title')} -> "
            f"{len(course_content)} source files"
        )

    modules.extend(
        repo_modules
    )

    step += len(
        repo_modules
    )

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

        document = next(
            (
                d
                for d in raw_documents
                if d.get(
                    "source_file"
                ) == f
            ),
            None,
        )

        course_content = []

        if document:

            course_content.append({
                "source_file":
                    f,

                "filename":
                    _source_name(
                        f
                    ),

                "scope":
                    document.get(
                        "scope",
                        "project",
                    ),

                "content":
                    document.get(
                        "text",
                        "",
                    ),
            })

        modules.append({
            "step":
                step,

            "title":
                name,

            "description":
                "Learn the concepts and implementation details "
                "covered in this document.",

            "purpose":
                "Provide additional project-specific knowledge.",

            "sources":
                [f],

            "confidence":
                "medium",

            "evidence": [
                "Provided by project documentation."
            ],

            "course_content":
                course_content,
        })

        step += 1

    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    return {
        "project_id":
            project_id,

        "learning_path":
            modules,

        "repository_summary":
            repository_summary(
                repo_metadata
            ),

        "mode":
            "repository_aware",
    }


# ==========================================================
# LOCAL TEST
# ==========================================================


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
        "\nGenerated learning path\n"
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
            f"Source files: "
            f"{len(item.get('source_files', item.get('sources', [])))}"
        )

        print(
            f"Course content records: "
            f"{len(item.get('course_content', []))}"
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