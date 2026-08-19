from pathlib import Path
import json


FRAMEWORK_RULES = {
    "React": {
        "files": ["package.json"],
        "dependencies": ["react", "react-dom"]
    },

    "Next.js": {
        "files": ["package.json"],
        "dependencies": ["next"]
    },

    "Express": {
        "files": ["package.json"],
        "dependencies": ["express"]
    },

    "Vue": {
        "files": ["package.json"],
        "dependencies": ["vue"]
    },

    "Angular": {
        "files": ["package.json"],
        "dependencies": ["@angular/core"]
    },

    "Django": {
        "files": ["requirements.txt", "pyproject.toml"],
        "dependencies": ["django"]
    },

    "Flask": {
        "files": ["requirements.txt", "pyproject.toml"],
        "dependencies": ["flask"]
    },

    "Spring Boot": {
        "files": ["pom.xml"],
        "dependencies": ["spring-boot"]
    },
}


def read_package_json(root: Path):

    package_file = root / "package.json"

    if not package_file.exists():
        return {}

    try:
        with open(package_file, "r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return {}


def detect_tech_stack(repository_path: str):

    root = Path(repository_path)

    languages = set()
    frameworks = set()
    databases = set()

    package_json = read_package_json(root)

    dependencies = {}

    dependencies.update(
        package_json.get("dependencies", {})
    )

    dependencies.update(
        package_json.get("devDependencies", {})
    )

    dependency_names = set(dependencies.keys())

    # JavaScript / TypeScript
    if package_json:
        if any(
            root.rglob("*.ts")
        ) or any(
            root.rglob("*.tsx")
        ):
            languages.add("TypeScript")

        if any(
            root.rglob("*.js")
        ) or any(
            root.rglob("*.jsx")
        ):
            languages.add("JavaScript")

    # Python
    if any(root.rglob("*.py")):
        languages.add("Python")

    # Java
    if any(root.rglob("*.java")):
        languages.add("Java")

    # Detect frameworks
    for framework, rule in FRAMEWORK_RULES.items():

        for dependency in rule["dependencies"]:

            if dependency in dependency_names:
                frameworks.add(framework)

    # Database detection
    database_rules = {
        "MongoDB": ["mongoose", "mongodb"],
        "PostgreSQL": ["pg", "psycopg2"],
        "MySQL": ["mysql", "mysql2"],
        "SQLite": ["sqlite3"],
        "Redis": ["redis"],
    }

    for database, packages in database_rules.items():

        if dependency_names.intersection(packages):
            databases.add(database)

    return {
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "databases": sorted(databases)
    }