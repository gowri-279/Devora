from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build",
    ".next",
    "coverage",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".go",
    ".rs",
}


IMPORTANT_KEYWORDS = {
    "controller",
    "service",
    "repository",
    "module",
    "router",
    "route",
    "model",
    "config",
    "middleware",
    "api",
}


def detect_modules(repository_path: str):
    root = Path(repository_path)
    modules = []

    for directory in root.rglob("*"):

        if not directory.is_dir():
            continue

        # Ignore unwanted directories
        if any(part in IGNORED_DIRECTORIES for part in directory.parts):
            continue

        source_files = []

        # Look at files directly inside this directory
        for file in directory.iterdir():

            if not file.is_file():
                continue

            if file.suffix.lower() in SOURCE_EXTENSIONS:
                source_files.append(file)

        # A directory needs source code to be considered a module
        if not source_files:
            continue

        important_files = []

        for file in source_files:
            filename = file.name.lower()

            if any(keyword in filename for keyword in IMPORTANT_KEYWORDS):
                important_files.append(file.name)

        # Only consider it a module if it has meaningful module evidence
        if important_files:
            relative_path = directory.relative_to(root)

            modules.append({
                "name": directory.name,
                "path": str(relative_path),
                "important_files": important_files
            })

    return modules