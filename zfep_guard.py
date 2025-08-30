#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from typing import List, Tuple, Dict

CANVAS_PATH = os.environ.get("CANVAS_PATH", "canvas.md")
BASE_REF = os.environ.get("GITHUB_BASE_REF", "")
HEAD_REF = os.environ.get("GITHUB_HEAD_REF", "")

START_RE = re.compile(r"<!--\s*START:\s*([A-Za-z0-9_\- ]+)\s*-->")
END_RE = re.compile(r"<!--\s*END:\s*([A-Za-z0-9_\- ]+)\s*-->")

def load_file_from_git(ref: str, path: str) -> List[str]:
    # returns list of lines for the file at given git ref
    try:
        blob = subprocess.check_output(["git", "show", f"origin/{ref}:{path}"], text=True, stderr=subprocess.STDOUT)
        return blob.splitlines(keepends=True)
    except subprocess.CalledProcessError:
        # If it doesn't exist on base (new file), return empty
        return []

def load_working_copy(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines(keepends=True)

def detect_anchors(lines: List[str]) -> Dict[str, Tuple[int, int]]:
    """
    Returns a dict: {anchor_name: (start_line_index, end_line_index)}, inclusive of markers.
    Line indices are 0-based.
    """
    anchors = {}
    stack = []
    for i, line in enumerate(lines):
        m = START_RE.search(line)
        if m:
            name = m.group(1).strip()
            stack.append((name, i))
            continue
        m = END_RE.search(line)
        if m:
            name = m.group(1).strip()
            if not stack or stack[-1][0] != name:
                raise ValueError(f"Mismatched END marker for '{name}' at line {i+1}")
            start_name, start_idx = stack.pop()
            anchors[name] = (start_idx, i)
    if stack:
        raise ValueError("Unclosed START anchors: " + ", ".join([s[0] for s in stack]))
    return anchors

def in_same_anchor(anchor_map: Dict[str, Tuple[int,int]], start: int, end: int) -> str:
    """Return anchor name if [start,end) lies fully inside a single anchor (excluding markers), else ''."""
    for name, (s, e) in anchor_map.items():
        inner_start = s + 1  # exclude START marker
        inner_end = e        # exclude END marker
        if start >= inner_start and end <= inner_end:
            return name
    return ""

def changed_hunks(base_ref: str, head_ref: str, path: str):
    """
    Returns list of (tag, a_start, a_end, b_start, b_end) hunks using 'git diff --unified=0'.
    a = base (origin/base_ref), b = head (working copy)
    """
    # Ensure we have base ref fetched
    subprocess.check_call(["git", "fetch", "--no-tags", "--prune", "origin", base_ref], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # diff between base file and working copy
    try:
        diff_text = subprocess.check_output(["git", "diff", "--unified=0", f"origin/{base_ref}...HEAD", "--", path], text=True)
    except subprocess.CalledProcessError as e:
        print("::error:: git diff failed", e.output)
        sys.exit(1)

    hunks = []
    # Parse unified diff hunk headers: @@ -a_start,a_len +b_start,b_len @@
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            # Example: @@ -12,0 +13,5 @@
            m = re.search(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if not m:
                continue
            a_start = int(m.group(1))
            a_len = int(m.group(2) or "1")
            b_start = int(m.group(3))
            b_len = int(m.group(4) or "1")
            # convert to 0-based half-open
            a0, a1 = (a_start - 1, a_start - 1 + a_len)
            b0, b1 = (b_start - 1, b_start - 1 + b_len)
            tag = classify_hunk(a_len, b_len)
            hunks.append((tag, a0, a1, b0, b1))
    return hunks

def classify_hunk(a_len: int, b_len: int) -> str:
    if a_len == 0 and b_len > 0:
        return "insert"
    if a_len > 0 and b_len == 0:
        return "delete"
    return "replace"

def contains_marker(lines, start: int, end: int) -> bool:
    region = "".join(lines[start:end])
    return "<!-- START:" in region or "<!-- END:" in region

def main():
    if not BASE_REF or not HEAD_REF:
        print("::warning:: Not a pull_request event or missing refs; skipping strict checks.")
        return

    base_lines = load_file_from_git(BASE_REF, CANVAS_PATH)
    head_lines = load_working_copy(CANVAS_PATH)
    if not head_lines:
        print(f"::error:: {CANVAS_PATH} missing in PR head.")
        sys.exit(1)

    try:
        base_anchors = detect_anchors(base_lines) if base_lines else {}
        head_anchors = detect_anchors(head_lines)
    except Exception as e:
        print(f"::error:: Anchor parse error: {e}")
        sys.exit(1)

    hunks = changed_hunks(BASE_REF, HEAD_REF, CANVAS_PATH)

    if not hunks:
        print("No changes detected in canvas; guard passing.")
        return

    violations = []

    for tag, a0, a1, b0, b1 in hunks:
        # Disallow touching marker lines anywhere
        if base_lines and contains_marker(base_lines, max(a0,0), max(a1,0)):
            violations.append(f"{tag} hunk modifies anchor markers in BASE lines {a0+1}-{a1}")
        if contains_marker(head_lines, max(b0,0), max(b1,0)):
            violations.append(f"{tag} hunk modifies anchor markers in HEAD lines {b0+1}-{b1}")

        base_name = in_same_anchor(base_anchors, a0, a1) if base_lines else ""
        head_name = in_same_anchor(head_anchors, b0, b1)

        if tag == "insert":
            if not head_name:
                violations.append(f"Insert at lines {b0+1}-{b1} is outside any anchor.")
        elif tag == "delete":
            if not base_name:
                violations.append(f"Delete of base lines {a0+1}-{a1} is outside any anchor.")
            elif base_name not in head_anchors:
                violations.append(f"Anchor '{base_name}' deleted or missing in HEAD.")
        else:  # replace
            if not base_name or not head_name:
                violations.append(f"Replace at base {a0+1}-{a1} / head {b0+1}-{b1} not fully inside anchors.")
            elif base_name != head_name:
                violations.append(f"Replace crosses anchors: base in '{base_name}', head in '{head_name}'.")

        # Enforce ZFEP-lite: keep hunks within a single anchor and avoid touching more than 200 lines
        if (b1 - b0) > 200 or (a1 - a0) > 200:
            violations.append(f"Hunk too large (>200 lines): base {a0+1}-{a1}, head {b0+1}-{b1}.")

    if violations:
        print("::group::Canvas Guard Violations")
        for v in violations:
            print(f"::error::{v}")
        print("::endgroup::")
        print("Guard failed. Only single-anchor edits are allowed; anchors cannot be changed.")
        sys.exit(1)
    else:
        print("Canvas guard passed: all changes are confined within anchors, markers untouched, and hunk sizes acceptable.")

if __name__ == "__main__":
    main()
