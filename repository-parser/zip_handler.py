import zipfile
import tempfile


def extract_zip(zip_path: str) -> str:
    temp_dir = tempfile.mkdtemp(prefix="repository_")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    return temp_dir