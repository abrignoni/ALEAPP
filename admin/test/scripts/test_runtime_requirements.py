import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class TestRuntimeRequirements(unittest.TestCase):
    def test_readme_documents_python_3_10_or_above(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("**Python 3.10 or above**", readme)

    def test_requirements_pin_latest_pillow(self):
        requirement_lines = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        pillow_lines = [line.strip() for line in requirement_lines if line.strip().lower().startswith("pillow")]
        self.assertEqual(pillow_lines, ["pillow==12.1.1"])

    def test_runtime_contract_workflow_covers_python_3_10_and_3_11(self):
        workflow_path = REPO_ROOT / ".github" / "workflows" / "python_runtime_contract.yml"
        self.assertTrue(workflow_path.exists(), "runtime contract workflow should exist")

        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("'3.10'", workflow)
        self.assertIn("'3.11'", workflow)


if __name__ == "__main__":
    unittest.main()
