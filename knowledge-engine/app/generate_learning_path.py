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
    modules = [] 
    PRIORITY = [ 
        (["team_foundations"], "Team Foundations", 
         "Understand collaboration workflow and engineering standards."), 
        (["readme"], "Project Overview", 
          "Understand the project purpose, architecture, and key components."), 
        (["architecture"], "Architecture", 
         "Understand the system architecture and major components."), 
        (["setup", "developing_locally"], 
          "Local Setup", "Set up the development environment and run the project locally."), 
        (["api"], "API Integration", "Explore APIs, contracts and integration points."), 
        (["refund"], "Refund Flow", "Learn the refund lifecycle and related business logic."), 
        (["bug"], "Debugging & KT", "Review common issues and troubleshooting guidance."), 
    ]
    used = set()
    step = 1 
    for keyword, title, description in PRIORITY: 
        matched = [
            f for f in source_files 
            if any(k in f.lower() for k in keyword) and f not in used
        ] 
        if matched:
            modules.append({ 
                "step": step, 
                "title": title, 
                "description": description, 
                "sources": matched 
            }) 
            used.update(matched) 
            step += 1 
    for f in source_files: 
        if f in used: 
            continue 
        name = f.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title() 
        modules.append({ 
            "step": step, 
            "title": name, 
            "description": "Learn the concepts and implementation details covered in this document.", 
            "sources": [f] 
        }) 
        step += 1 
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
