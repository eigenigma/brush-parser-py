"""The stubs describe exactly the compiled module."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_stubtest_reports_no_issues():
    completed = subprocess.run(
        [sys.executable, "-m", "mypy.stubtest", "brush_parser._core"],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_every_stub_stays_navigable():
    for stub in (ROOT / "src" / "brush_parser").glob("*.pyi"):
        lines = stub.read_text().count("\n")
        assert lines < 400, f"{stub.name} has {lines} lines"
