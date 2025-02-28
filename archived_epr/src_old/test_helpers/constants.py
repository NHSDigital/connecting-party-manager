from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Duck-type the project root
assert (PROJECT_ROOT / "README.md").exists()
assert (PROJECT_ROOT / "infrastructure").exists()
assert (PROJECT_ROOT / "src").exists()
