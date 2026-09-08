from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
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
    ".yml",
    ".yaml",
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

SPECIAL_MODULE_DIRECTORIES = {
    ".github/workflows",
    ".github/actions",
}


def detect_modules(repository_path: str):
    root = Path(repository_path)
    modules = []

    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue

        relative_path = directory.relative_to(root)
        relative_path_str = str(relative_path)

        if any(part in IGNORED_DIRECTORIES for part in directory.parts):
            continue

        if any(part.endswith(".not") for part in relative_path.parts):
            continue

        source_files = []

        for file in directory.iterdir():
            if not file.is_file():
                continue

            if file.suffix.lower() in SOURCE_EXTENSIONS:
                source_files.append(file)

        important_files = []

        for file in source_files:
            filename = file.name.lower()

            if any(keyword in filename for keyword in IMPORTANT_KEYWORDS):
                important_files.append(file.name)

        if important_files or relative_path_str in SPECIAL_MODULE_DIRECTORIES:
            modules.append(
                {
                    "name": directory.name,
                    "path": relative_path_str,
                    "important_files": important_files,
                }
            )

    return modules