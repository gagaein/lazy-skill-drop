#!/usr/bin/env python3
"""
length_guard.py — enforce max_lines from frontmatter on append-only logs.

Used by scan.py (formula-history.md) and propose.py (evolution-log.md) to
prevent unbounded growth of self-evolution state. When a file exceeds its
declared max_lines, the oldest entries are moved to a sibling archive file.

Usage:
    from length_guard import enforce_max_lines

    enforce_max_lines(
        target=Path("references/formula-history.md"),
        archive=Path("memory/formula-history-archive.md"),
        entry_separator="─" * 60,  # "──────────────"
        keep_frontmatter=True,
    )
"""

import re
from pathlib import Path


def read_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file.

    Returns (frontmatter_dict, body_text). If no frontmatter, returns ({}, text).
    Simple line-based parser; no external yaml dep.
    """
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}, text
    meta_block = m.group(1)
    body = text[m.end():]
    meta = {}
    for line in meta_block.splitlines():
        if ":" in line and not line.startswith("#"):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body


def read_max_lines(file_path: Path, default: int | None = None) -> int | None:
    """Extract max_lines from a file's frontmatter. Returns None if not set."""
    if not file_path.exists():
        return default
    text = file_path.read_text(encoding="utf-8")
    meta, _ = read_frontmatter(text)
    v = meta.get("max_lines")
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def enforce_max_lines(
    target: Path,
    archive: Path | None = None,
    entry_separator: str = "",
    keep_frontmatter: bool = True,
    verbose: bool = True,
) -> dict:
    """Truncate target file to max_lines (from frontmatter).

    If archive path is provided, truncated content is prepended there.
    If no archive, truncated content is discarded.

    Strategy: find the split point as close to max_lines as possible while
    respecting entry_separator boundaries (so entries aren't cut in half).
    The oldest entries (at the END of the file — because append_history
    PREPENDS) get moved to archive.

    Wait — re-reading scan.py: it writes `entry + existing`, so NEWEST is at
    the TOP, OLDEST at the BOTTOM. Truncating means: keep the TOP, move the
    BOTTOM to archive.

    Returns dict with: lines_before, lines_after, entries_archived.
    """
    if not target.exists():
        return {"lines_before": 0, "lines_after": 0, "entries_archived": 0}

    text = target.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    before = len(lines)

    max_lines = read_max_lines(target)
    if max_lines is None or before <= max_lines:
        return {"lines_before": before, "lines_after": before, "entries_archived": 0}

    # Split frontmatter off so we don't count/cut it
    meta, body = read_frontmatter(text)
    if keep_frontmatter and meta:
        # Reconstruct frontmatter string exactly as it was
        fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        fm_text = fm_match.group(0) if fm_match else ""
        body_lines = body.splitlines(keepends=True)
        fm_line_count = fm_text.count("\n")
        # Available budget for body
        body_budget = max_lines - fm_line_count
    else:
        fm_text = ""
        body_lines = lines
        body_budget = max_lines

    if body_budget < 1:
        body_budget = 1

    if len(body_lines) <= body_budget:
        return {"lines_before": before, "lines_after": before, "entries_archived": 0}

    # Find split point. If separator is given, snap to the nearest separator
    # boundary at or BEFORE body_budget, so we don't cut mid-entry.
    split_at = body_budget
    if entry_separator:
        # Walk backwards from body_budget to find a separator line
        for i in range(min(body_budget, len(body_lines) - 1), -1, -1):
            if entry_separator in body_lines[i]:
                split_at = i
                break

    keep_body = body_lines[:split_at]
    archive_body = body_lines[split_at:]

    # Count entries archived (by separator occurrences)
    entries_archived = 0
    if entry_separator:
        entries_archived = sum(1 for ln in archive_body if entry_separator in ln)

    # Write truncated target
    new_target = fm_text + "".join(keep_body)
    target.write_text(new_target, encoding="utf-8")

    # Write archive (prepend, newest-archived-first matches target's ordering)
    if archive is not None and archive_body:
        archive.parent.mkdir(parents=True, exist_ok=True)
        existing_archive = archive.read_text(encoding="utf-8") if archive.exists() else ""
        # Give archive its own lightweight header if empty
        if not existing_archive:
            existing_archive = (
                "# Archive — rotated entries\n\n"
                "Entries rotated out of the active log by `length_guard.py`. "
                "Newest archived entry is at the top.\n\n"
            )
        archive_text = "".join(archive_body)
        archive.write_text(existing_archive + archive_text, encoding="utf-8")

    after = len(new_target.splitlines())
    if verbose:
        loc = str(target.name)
        if archive is not None:
            print(f"  ↳ length_guard: {loc} {before}→{after} lines, "
                  f"{entries_archived} entr{'y' if entries_archived == 1 else 'ies'} archived")
        else:
            print(f"  ↳ length_guard: {loc} {before}→{after} lines, "
                  f"{entries_archived} entr{'y' if entries_archived == 1 else 'ies'} dropped")

    return {
        "lines_before": before,
        "lines_after": after,
        "entries_archived": entries_archived,
    }


if __name__ == "__main__":
    # CLI test harness
    import sys
    if len(sys.argv) < 2:
        print("Usage: length_guard.py <file> [--archive <archive_file>] [--sep <separator>]")
        sys.exit(1)
    target = Path(sys.argv[1])
    archive = None
    sep = ""
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--archive" and i + 1 < len(sys.argv):
            archive = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--sep" and i + 1 < len(sys.argv):
            sep = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    result = enforce_max_lines(target, archive, sep)
    print(result)
