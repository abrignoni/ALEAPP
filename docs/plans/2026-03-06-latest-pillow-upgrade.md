# Latest Pillow Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move ALEAPP's tracked runtime contract on `main` to the latest Pillow path by pinning Pillow 12.1.1, documenting Python 3.10+, and adding CI-backed regression coverage for those declarations.

**Architecture:** Keep the change small and policy-focused. The repo's Pillow call sites do not need refactoring, so the implementation should update the tracked version declarations and add a lightweight test plus workflow that fail if those declarations drift in future PRs.

**Tech Stack:** Python, `unittest`, GitHub Actions, requirements.txt, Markdown docs

---

### Task 1: Add a failing runtime contract test

**Files:**
- Create: `admin/test/scripts/test_runtime_requirements.py`

**Step 1: Write the failing test**

```python
class TestRuntimeRequirements(unittest.TestCase):
    def test_readme_documents_python_3_10_or_above(self):
        self.assertIn("**Python 3.10 or above**", readme)

    def test_requirements_pin_latest_pillow(self):
        self.assertEqual(pillow_lines, ["pillow==12.1.1"])

    def test_runtime_contract_workflow_covers_python_3_10(self):
        self.assertIn("3.10", workflow_yaml)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s admin/test/scripts -p 'test_runtime_requirements.py' -v`
Expected: FAIL because `README.md` still says Python 3.9+, `requirements.txt` still allows Pillow <12, and the runtime-contract workflow does not exist yet.

**Step 3: Write minimal implementation**

No production changes in this task.

**Step 4: Run test to verify it fails correctly**

Run: `python3 -m unittest discover -s admin/test/scripts -p 'test_runtime_requirements.py' -v`
Expected: FAIL on the intended version assertions, not on import errors or path errors.

**Step 5: Commit**

```bash
git add admin/test/scripts/test_runtime_requirements.py
git commit -m "test: add runtime contract regression coverage"
```

### Task 2: Update tracked version declarations

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`

**Step 1: Implement the minimal declaration changes**

```text
requirements.txt -> pillow==12.1.1
README.md -> Python 3.10 or above
```

**Step 2: Run targeted test to verify it still fails**

Run: `python3 -m unittest discover -s admin/test/scripts -p 'test_runtime_requirements.py' -v`
Expected: FAIL only on the workflow assertion because CI coverage is not added yet.

**Step 3: Commit**

```bash
git add requirements.txt README.md
git commit -m "build: require Python 3.10 for latest Pillow"
```

### Task 3: Add CI enforcement for the runtime contract

**Files:**
- Create: `.github/workflows/python_runtime_contract.yml`

**Step 1: Add the workflow**

```yaml
name: Python Runtime Contract
on:
  pull_request:
    paths:
      - '.github/workflows/python_runtime_contract.yml'
      - 'README.md'
      - 'requirements.txt'
      - 'admin/test/scripts/test_runtime_requirements.py'
jobs:
  runtime-contract:
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
```

**Step 2: Run targeted test to verify it passes**

Run: `python3 -m unittest discover -s admin/test/scripts -p 'test_runtime_requirements.py' -v`
Expected: PASS

**Step 3: Run full verification**

Run: `python3 -m unittest discover -s admin/test/scripts -p 'test_*.py'`
Expected: PASS

**Step 4: Commit**

```bash
git add .github/workflows/python_runtime_contract.yml
git commit -m "ci: enforce Python and Pillow runtime contract"
```
