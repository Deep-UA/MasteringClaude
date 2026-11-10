"""PreToolUse hook (Edit|Write): block known test anti-patterns in tests/ and framework/.

Exit 0 = allow, exit 2 = block (stderr is shown to Claude).
"""

import json
import os
import re
import sys
from pathlib import Path

GUARDED_DIRS = ("tests", "framework")

RULES = [
    (re.compile(r"\btime\.sleep\("), "hard wait `time.sleep()`: use Playwright auto-waiting / `expect(...)` instead"),
    (re.compile(r"\.wait_for_timeout\("), "hard wait `wait_for_timeout()`: wait for a locator or state instead"),
    (re.compile(r"""["'](xpath=|//)"""), "XPath locator: use `get_by_test_id` (data-test), role or label"),
    (re.compile(r"welcome01"), "shared demo credentials: use the per-session `test_user` fixture"),
]


def main() -> int:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    file_path = Path(tool_input.get("file_path", ""))
    if file_path.suffix != ".py":
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    try:
        rel = file_path.resolve().relative_to(project_dir)
    except ValueError:
        return 0
    if rel.parts[0] not in GUARDED_DIRS:
        return 0

    new_code = tool_input.get("content") or tool_input.get("new_string") or ""
    problems = [msg for pattern, msg in RULES if pattern.search(new_code)]
    if not problems:
        return 0

    print(f"Blocked edit to {rel}:", file=sys.stderr)
    for msg in problems:
        print(f"- {msg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
