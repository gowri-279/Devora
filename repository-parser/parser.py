import json

from github_clone import clone_repository
from scanner import scan_repository
from module_detector import detect_modules


def parse_repository(repo_url: str):

    print("1. Cloning repository...")
    repository_path = clone_repository(repo_url)

    print("2. Scanning files...")
    files = scan_repository(repository_path)

    print("3. Detecting modules...")
    modules = detect_modules(repository_path)

    print("4. Detecting languages...")
    languages = sorted(
        {
            file["language"]
            for file in files
            if file["language"] != "Unknown"
        }
    )

    print("5. Creating result...")

    result = {
        "repository": repo_url,
        "languages": languages,
        "modules": modules,
        "files": files
    }

    return result