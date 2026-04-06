import unittest
import os
import subprocess
import sys
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

    def test_requirements_pin_secure_protobuf(self):
        requirement_lines = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        protobuf_lines = [line.strip() for line in requirement_lines if line.strip().lower().startswith("protobuf")]
        self.assertEqual(protobuf_lines, ["protobuf==5.29.6"])

    def test_requirements_use_maintained_blackboxprotobuf_package(self):
        requirement_lines = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        package_lines = [line.strip() for line in requirement_lines if "blackboxprotobuf" in line.lower() or line.strip().lower().startswith("bbpb")]
        self.assertEqual(package_lines, ["bbpb==1.4.2"])

    def test_scripts_package_sets_protobuf_runtime_mode(self):
        env = dict(os.environ)
        env.pop("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", None)

        result = subprocess.run(
            [sys.executable, "-c", "import os, scripts; print(os.environ.get('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', ''))"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stdout.strip(), "python")

    def test_runtime_contract_workflow_covers_python_3_10_and_3_11(self):
        workflow_path = REPO_ROOT / ".github" / "workflows" / "python_runtime_contract.yml"
        self.assertTrue(workflow_path.exists(), "runtime contract workflow should exist")

        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("'3.10'", workflow)
        self.assertIn("'3.11'", workflow)
        self.assertIn("python -m pip install -r requirements.txt", workflow)
        self.assertIn("test_*.py", workflow)


if __name__ == "__main__":
    unittest.main()
