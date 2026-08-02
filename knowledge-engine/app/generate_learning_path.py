import json
from pathlib import Path

from document_loader import load_documents

DATA_DIR = Path(__file__).parent.parent / "data"


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
            grouped[1]["sources"].append(source)

        elif "readme" in name:
            grouped[2]["sources"].append(source)

        elif "local_setup" in name or "developing_locally" in name:
            grouped[3]["sources"].append(source)

        elif "contributing" in name:
            grouped[4]["sources"].append(source)

        elif "api" in name:
            grouped[5]["sources"].append(source)

        elif "refund" in name or "bugs" in name:
            grouped[6]["sources"].append(source)

    modules = []

    for order, item in grouped.items():
        if item["sources"]:
            modules.append({
                "title": item["title"],
                "sources": item["sources"],
                "order": order
            })

    return modules


if __name__ == "__main__":
    files = [str(p) for p in DATA_DIR.iterdir()]
    docs = load_documents(files)

    path = build_learning_path(docs)

    output_path = DATA_DIR / "learning_path.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(path, f, indent=2)

    print("Generated personalized learning path\\n")

    for item in path:
        print(f"Module {item['order']}: {item['title']}")

        for src in item["sources"]:
            print(f"   - {src}")

        print()

    print(f"Saved to: {output_path.name}")