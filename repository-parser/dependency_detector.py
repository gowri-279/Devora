from pathlib import Path
import re


IMPORT_PATTERNS = {

    "Python": [
        r"^\s*import\s+([a-zA-Z0-9_\.]+)",
        r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import"
    ],

    "JavaScript": [
        r"import\s+.*?\s+from\s+['\"](.+?)['\"]",
        r"require\(['\"](.+?)['\"]\)"
    ],

    "TypeScript": [
        r"import\s+.*?\s+from\s+['\"](.+?)['\"]",
        r"require\(['\"](.+?)['\"]\)"
    ]
}


PYTHON_BUILTINS = {
    "os",
    "sys",
    "json",
    "re",
    "math",
    "pathlib",
    "typing",
    "datetime",
    "collections",
    "itertools",
    "functools",
    "subprocess",
    "logging",
}


NODE_BUILTINS = {
    "assert",
    "buffer",
    "child_process",
    "crypto",
    "events",
    "fs",
    "http",
    "https",
    "net",
    "os",
    "path",
    "stream",
    "tls",
    "url",
    "util",
    "zlib",
}


def get_dependency_type(
    dependency: str,
    language: str
):

    if dependency.startswith("."):
        return "local"

    if language == "Python":
        root_name = dependency.split(".")[0]

        if root_name in PYTHON_BUILTINS:
            return "builtin"

    if language in {"JavaScript", "TypeScript"}:

        if dependency in NODE_BUILTINS:
            return "builtin"

    return "external"


def detect_file_dependencies(
    repository_path: str,
    file_info: dict
):

    root = Path(repository_path)

    file_path = root / file_info["path"]

    language = file_info["language"]

    patterns = IMPORT_PATTERNS.get(
        language,
        []
    )

    dependencies = []

    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except OSError:
        return dependencies

    for pattern in patterns:

        matches = re.findall(
            pattern,
            content,
            re.MULTILINE
        )

        for dependency in matches:

            dependencies.append({
                "name": dependency,
                "type": get_dependency_type(
                    dependency,
                    language
                )
            })

    # Remove duplicates
    unique = []
    seen = set()

    for dependency in dependencies:

        key = (
            dependency["name"],
            dependency["type"]
        )

        if key not in seen:
            seen.add(key)
            unique.append(dependency)

    return unique


def detect_dependencies(
    repository_path: str,
    files: list
):

    dependencies = []

    for file_info in files:

        imports = detect_file_dependencies(
            repository_path,
            file_info
        )

        for dependency in imports:

            dependencies.append({
                "file": file_info["path"],
                "name": dependency["name"],
                "type": dependency["type"]
            })

    return dependencies