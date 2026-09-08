import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scanner import scan_repository
from module_detector import detect_modules


class RepositoryFilteringTests(unittest.TestCase):
    def test_scan_repository_skips_placeholder_and_test_only_paths(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)

            (root / ".github" / "workflows.not").mkdir(parents=True)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "actions").mkdir(parents=True)

            (root / "wtf.jpg").write_text("image")
            (root / "RANDOM.md").write_text("noise")
            (root / "hello.txt").write_text("hello")
            (root / "test.js").write_text("console.log('ok');")
            (root / ".github" / "workflows.not" / "build-pr.yml").write_text("name: build")
            (root / ".github" / "workflows" / "pull-request.yml").write_text("name: pr")
            (root / ".github" / "actions" / "test-action").mkdir(parents=True)
            (root / ".github" / "actions" / "test-action" / "action.yml").write_text("name: action")

            files = scan_repository(str(root))
            relative_paths = {file_data["path"] for file_data in files}

            self.assertNotIn("wtf.jpg", relative_paths)
            self.assertNotIn("RANDOM.md", relative_paths)
            self.assertNotIn("hello.txt", relative_paths)
            self.assertNotIn(".github/workflows.not/build-pr.yml", relative_paths)
            self.assertIn(".github/workflows/pull-request.yml", relative_paths)
            self.assertIn(".github/actions/test-action/action.yml", relative_paths)

    def test_detect_modules_ignores_workflows_not_module(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / ".github" / "workflows.not").mkdir(parents=True)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "actions").mkdir(parents=True)

            modules = detect_modules(str(root))
            module_paths = {module["path"] for module in modules}

            self.assertNotIn(".github/workflows.not", module_paths)
            self.assertIn(".github/workflows", module_paths)
            self.assertIn(".github/actions", module_paths)


if __name__ == "__main__":
    unittest.main()
