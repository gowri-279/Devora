from pathlib import Path
import re


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


def should_ignore_file(file_path: str) -> bool:
    path = Path(file_path)

    if any(part in IGNORED_DIRECTORIES for part in path.parts):
        return True

    return False


PYTHON_PATTERNS = [
    (r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", "function"),
    (r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:\(]", "class"),
]


JAVASCRIPT_PATTERNS = [
    (
        r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(",
        "function",
    ),
    (
        r"\bclass\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*[{\s]",
        "class",
    ),
    (
        r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\(",
        "function",
    ),
]


def detect_file_symbols(file_path: str, language: str):
    if should_ignore_file(file_path):
        return []

    path = Path(file_path)

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except OSError:
        return []

    symbols = []

    if language == "Python":
        patterns = PYTHON_PATTERNS

    elif language in {"JavaScript", "TypeScript"}:
        patterns = JAVASCRIPT_PATTERNS

    else:
        return []

    for pattern, symbol_type in patterns:

        matches = re.findall(
            pattern,
            content,
            re.MULTILINE
        )

        for name in matches:
            symbols.append({
                "name": name,
                "type": symbol_type
            })

    # Remove duplicates while preserving order
    seen = set()
    unique_symbols = []

    for symbol in symbols:
        key = (symbol["name"], symbol["type"])

        if key not in seen:
            seen.add(key)
            unique_symbols.append(symbol)

    return unique_symbols


def detect_symbols(repository_path: str, files: list):
    results = []

    root = Path(repository_path)

    for file_info in files:

        language = file_info.get("language", "Unknown")

        if language not in {
            "Python",
            "JavaScript",
            "TypeScript",
        }:
            continue

        relative_path = file_info["path"]

        full_path = root / relative_path

        symbols = detect_file_symbols(
            str(full_path),
            language
        )

        if symbols:
            results.append({
                "file": relative_path,
                "symbols": symbols
            })

    return results