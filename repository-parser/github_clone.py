from git import Repo
import tempfile


def clone_repository(repo_url: str) -> str:
    print("Starting clone...")

    temp_dir = tempfile.mkdtemp(prefix="repository_")

    Repo.clone_from(repo_url, temp_dir)

    print("Repository cloned successfully!")

    return temp_dir