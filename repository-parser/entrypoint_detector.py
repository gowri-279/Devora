from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    "target",
}


def should_ignore(path: Path) -> bool:
    return any(
        part in IGNORED_DIRECTORIES
        for part in path.parts
    )


def detect_entrypoints(
    repository_path: str,
    files: list
):

    root = Path(repository_path)

    entrypoints = []

    for file_info in files:

        file_path = Path(file_info["path"])

        if should_ignore(file_path):
            continue

        name = file_path.name.lower()

        language = file_info.get(
            "language",
            "Unknown"
        )

        # Python entrypoints
        if language == "Python" and name in {
            "main.py",
            "app.py",
            "run.py",
        }:

            entrypoints.append({
                "file": file_info["path"],
                "type": "application"
            })

        # JavaScript / TypeScript entrypoints
        elif language in {
            "JavaScript",
            "TypeScript"
        } and name in {
            "index.js",
            "index.ts",
            "main.js",
            "main.ts",
            "server.js",
            "server.ts",
            "app.js",
            "app.ts",
        }:

            entrypoints.append({
                "file": file_info["path"],
                "type": "application"
            })

        # GitHub Actions
        elif name in {
            "action.yml",
            "action.yaml"
        }:

            entrypoints.append({
                "file": file_info["path"],
                "type": "github_action"
            })

    return entrypoints