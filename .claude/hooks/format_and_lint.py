"""PostToolUse hook (Edit|Write): ruff format + autofix the edited file in tests/ or framework/.

Exit 0 = clean (or nothing to do), exit 2 = lint errors remain (stderr is shown to Claude).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GUARDED_DIRS = ("tests", "framework")


def main() -> int:
    data = json.load(sys.stdin)
    file_path = Path(data.get("tool_input", {}).get("file_path", ""))
    if file_path.suffix != ".py" or not file_path.is_file():
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    try:
        rel = file_path.resolve().relative_to(project_dir)
    except ValueError:
        return 0
    if rel.parts[0] not in GUARDED_DIRS:
        return 0

    ruff = shutil.which("ruff")
    if ruff is None:
        return 0  # ruff not installed: skip rather than break every edit

    subprocess.run([ruff, "check", "--fix", "--quiet", str(file_path)], cwd=project_dir, capture_output=True, check=False)
    subprocess.run([ruff, "format", "--quiet", str(file_path)], cwd=project_dir, check=False)
    result = subprocess.run(
        [ruff, "check", "--quiet", str(file_path)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return 0

    print(f"ruff found issues in {rel} that need a manual fix:", file=sys.stderr)
    print(result.stdout + result.stderr, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
