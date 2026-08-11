from pathlib import Path
from pydantic import BaseModel
from typing import Optional

from app.raw_storage import list_raw_documents


class LearningPathRequest(BaseModel):
    project_id: str
    repo_metadata: Optional[dict] = None  # hook for modules.json once Repo Parser lead delivers it


def build_learning_path(source_files: list):
    """
    source_files: list of filenames (strings) actually ingested for this
    project + team scope — from raw_storage.list_raw_documents(), NOT a
    filesystem glob. This is the fix: the old version globbed data/*.md
    regardless of project_id, so every project returned the identical
    learning path.
    """
    grouped = {
        1: {"title": "Team Foundations", "sources": []},
        2: {"title": "Project Overview", "sources": []},
        3: {"title": "Run the Project Locally", "sources": []},
        4: {"title": "Contribution Workflow", "sources": []},
        5: {"title": "API Understanding", "sources": []},
        6: {"title": "Debugging & KT", "sources": []},
    }

    for name in source_files:
        lower = name.lower()

        if "team_foundations" in lower:
            grouped[1]["sources"].append(name)
        elif "readme" in lower:
            grouped[2]["sources"].append(name)
        elif "local_setup" in lower or "developing_locally" in lower:
            grouped[3]["sources"].append(name)
        elif "contributing" in lower:
            grouped[4]["sources"].append(name)
        elif "api" in lower:
            grouped[5]["sources"].append(name)
        elif "refund" in lower or "bugs" in lower:
            grouped[6]["sources"].append(name)

    modules = []
    for order, item in grouped.items():
        if item["sources"]:
            modules.append({
                "step": order,
                "title": item["title"],
                "sources": item["sources"],
            })

    return modules


def generate_learning_path(project_id: str, repo_metadata: Optional[dict] = None):
    """
    repo_metadata: pass through whatever Repo Parser Lead's modules.json
    contains once it's ready. Not used yet (heuristic-only for now) — this
    is the hook to make the path module-aware later without changing the
    call signature your Backend/Bob teammates already integrate against.
    """
    docs = list_raw_documents(project_id=project_id)
    source_files = [d["source_file"] for d in docs]

    modules = build_learning_path(source_files)

    # TODO once modules.json is available: prepend a "Codebase Overview"
    # module built from repo_metadata, similar to how the doc-based
    # modules are built above. Left as a hook rather than guessing at the
    # shape before Repo Parser Lead confirms it.

    return {
        "project_id": project_id,
        "learning_path": modules,
    }


if __name__ == "__main__":
    import json

    result = generate_learning_path("refund-service")

    data_dir = Path(__file__).parent.parent / "data"
    output_path = data_dir / "learning_path.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Generated learning path\n")
    for item in result["learning_path"]:
        print(f"Step {item['step']}: {item['title']}")
        for src in item["sources"]:
            print(f"   - {src}")
        print()

    print(f"Saved to: {output_path.name}")
