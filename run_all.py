from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "analysis" / script)], check=True)


if __name__ == "__main__":
    run("run_analysis.py")
    run("validate_release.py")
