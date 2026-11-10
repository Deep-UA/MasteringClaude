"""Stop hook: if tests/ or framework/ changed, make sure the suite still collects.

Runs `pytest --collect-only` (no network, no browser). Exit 0 = allow stop,
exit 2 = block stop (stderr is shown to Claude so it can fix the breakage).
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return 0  # already continuing because of this hook: don't loop

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    changed = subprocess.run(
        ["git", "status", "--porcelain", "--", "tests", "framework"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not changed:
        return 0

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    # 0 = collected, 5 = no tests collected (fine while the suite is still empty)
    if result.returncode in (0, 5):
        return 0

    print("pytest collection fails after your changes; fix before finishing:", file=sys.stderr)
    print((result.stdout + result.stderr)[-3000:], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
