from github_clone import clone_repository
from scanner import scan_repository
from module_detector import detect_modules
from dependency_detector import detect_dependencies
from entrypoint_detector import detect_entrypoints
from symbol_detector import detect_symbols
from tech_stack_detector import detect_tech_stack
from zip_handler import create_zip


def parse_repository(repo_url: str):
    print("1. Cloning repository...")
    repository_path = clone_repository(repo_url)

    print("2. Scanning files...")
    files = scan_repository(repository_path)

    print("3. Detecting modules...")
    modules = detect_modules(repository_path)

    print("4. Detecting dependencies...")
    dependencies = detect_dependencies(repository_path, files)

    print("5. Detecting tech stack...")
    tech_stack = detect_tech_stack(repository_path)

    print("6. Detecting entrypoints...")
    entrypoints = detect_entrypoints(repository_path, files)

    print("7. Detecting symbols...")
    symbols = detect_symbols(repository_path, files)

    print("8. Creating source artifact...")
    source_zip = create_zip(repository_path)

    languages = sorted(
        {
            file["language"]
            for file in files
            if file["language"] != "Unknown"
        }
    )

    return {
        "repository": repo_url,
        "languages": languages,
        "modules": modules,
        "files": files,
        "dependencies": dependencies,
        "tech_stack": tech_stack,
        "entrypoints": entrypoints,
        "symbols": symbols,
        "source_artifact": {
            "type": "archive",
            "format": "zip",
            "path": source_zip,
        },
    }