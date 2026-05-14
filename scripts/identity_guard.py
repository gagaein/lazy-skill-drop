#!/usr/bin/env python3
"""
identity_guard.py — Verify lazy-skill-drop's own core invariants survive
each evolve-loop tick.

Reads `references/core-identity.md`, parses the `### family_*` blocks,
and confirms each family has at least one matching phrase present in
README.md OR SKILL.md (case-insensitive regex search across both).

Exit codes:
    0 — all families pass
    1 — one or more families missing (identity drift detected)
        OR config error (missing/unparseable core-identity.md)

Invoked from:
    - .github/workflows/evolve.yml (gate before scan/delta/propose)
    - manual: `python scripts/identity_guard.py`
"""

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
IDENTITY   = SKILL_ROOT / "references" / "core-identity.md"
README     = SKILL_ROOT / "README.md"
SKILL_MD   = SKILL_ROOT / "SKILL.md"


def parse_families(text: str) -> dict[str, list[str]]:
    """Parse `### family_X` blocks → {family_name: [regex_phrase, ...]}."""
    families: dict[str, list[str]] = {}
    # Split on H3 headers; first chunk before any H3 is preamble, ignore it.
    chunks = re.split(r"\n###\s+", text)
    for chunk in chunks[1:]:
        head_match = re.match(r"(family_\w+)", chunk)
        if not head_match:
            continue
        name = head_match.group(1)
        # Phrases are bulleted, quoted: `- "phrase"`
        phrases = re.findall(r'^\s*-\s+"([^"]+)"', chunk, re.MULTILINE)
        if phrases:
            families[name] = phrases
    return families


def family_passes(phrases: list[str], haystack: str) -> tuple[bool, str | None]:
    """True if any phrase regex matches haystack (case-insensitive)."""
    for p in phrases:
        try:
            if re.search(p, haystack, re.IGNORECASE):
                return True, p
        except re.error:
            # Treat malformed regex as plain substring; defensive only.
            if p.lower() in haystack.lower():
                return True, p
    return False, None


def main() -> int:
    if not IDENTITY.exists():
        print("[identity_guard] ERR core-identity.md not found at "
              f"{IDENTITY}", file=sys.stderr)
        return 1

    families = parse_families(IDENTITY.read_text(encoding="utf-8"))
    if not families:
        print("[identity_guard] ERR no `### family_*` blocks parsed from "
              "core-identity.md", file=sys.stderr)
        return 1

    readme_text   = README.read_text(encoding="utf-8")   if README.exists()   else ""
    skill_md_text = SKILL_MD.read_text(encoding="utf-8") if SKILL_MD.exists() else ""
    combined = readme_text + "\n" + skill_md_text

    failed: list[str] = []
    passed: list[str] = []
    for fam, phrases in families.items():
        ok, _ = family_passes(phrases, combined)
        (passed if ok else failed).append(fam)

    if failed:
        print(f"[identity_guard] FAIL — missing invariant families: {failed}",
              file=sys.stderr)
        print(f"[identity_guard] passing: {passed}", file=sys.stderr)
        print(f"[identity_guard] See references/core-identity.md for required "
              f"phrases — at least one phrase per family must appear in "
              f"README.md or SKILL.md.", file=sys.stderr)
        return 1

    print(f"[identity_guard] PASS — all {len(families)} invariant families "
          f"present: {passed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
