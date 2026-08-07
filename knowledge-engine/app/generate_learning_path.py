import json
from pathlib import Path
from pydantic import BaseModel

from app.document_loader import load_documents

DATA_DIR = Path(__file__).parent.parent / "data"


class LearningPathRequest(BaseModel):
    project_id: str


def build_learning_path(documents):
    grouped = {
        1: {"title": "Team Foundations", "sources": []},
        2: {"title": "Project Overview", "sources": []},
        3: {"title": "Run the Project Locally", "sources": []},
        4: {"title": "Contribution Workflow", "sources": []},
        5: {"title": "API Understanding", "sources": []},
        6: {"title": "Debugging & KT", "sources": []},
    }

    for source, _ in documents:
        name = Path(source).name.lower()

        if "team_foundations" in name:
            grouped[1]["sources"].append(Path(source).name)

        elif "readme" in name:
            grouped[2]["sources"].append(Path(source).name)

        elif "local_setup" in name or "developing_locally" in name:
            grouped[3]["sources"].append(Path(source).name)

        elif "contributing" in name:
            grouped[4]["sources"].append(Path(source).name)

        elif "api" in name:
            grouped[5]["sources"].append(Path(source).name)

        elif "refund" in name or "bugs" in name:
            grouped[6]["sources"].append(Path(source).name)

    modules = []

    for order, item in grouped.items():
        if item["sources"]:
            modules.append({
                "step": order,
                "title": item["title"],
                "sources": item["sources"]
            })

    return modules


def generate_learning_path(project_id: str):
    files = [str(p) for p in DATA_DIR.glob("*.md")]
    docs = load_documents(files)

    return {
        "project_id": project_id,
        "learning_path": build_learning_path(docs)
    }


if __name__ == "__main__":
    result = generate_learning_path("refund-service")

    output_path = DATA_DIR / "learning_path.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Generated learning path\\n")

    for item in result["learning_path"]:
        print(f"Step {item['step']}: {item['title']}")

        for src in item["sources"]:
            print(f"   - {src}")

        print()

    print(f"Saved to: {output_path.name}")