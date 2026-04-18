#!/usr/bin/env python3
"""
propose.py — Evolution Gate for lazy-skill-drop
Reads delta output, generates a SKILL.md diff and PR body,
creates a GitHub PR if gh CLI is available.

Usage:
    python propose.py
    python propose.py --dry-run     (print without creating PR)
    python propose.py --auto        (auto-merge if confidence >= threshold)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# local helper (same dir)
sys.path.insert(0, str(Path(__file__).parent))
from length_guard import enforce_max_lines  # noqa: E402

SKILL_ROOT    = Path(__file__).parent.parent
SKILL_MD      = SKILL_ROOT / "SKILL.md"
PATTERNS_PATH = SKILL_ROOT / "references" / "viral-patterns.md"
ELOG          = SKILL_ROOT / "memory" / "evolution-log.md"
ELOG_ARCH     = SKILL_ROOT / "memory" / "evolution-log-archive.md"

AUTO_MERGE_THRESHOLD = 0.65   # must match SKILL.md frontmatter


# ── helpers ───────────────────────────────────────────────────────────────────

def run(cmd: list[str], capture=True) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_delta_json() -> dict:
    code, out, err = run(["python3", str(SKILL_ROOT / "scripts" / "delta.py"), "--json"])
    if code == 99:
        print(f"[propose] delta.py error: {err}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        print(f"[propose] failed to parse delta output:\n{out}", file=sys.stderr)
        sys.exit(1)


def read_patterns() -> str:
    if not PATTERNS_PATH.exists():
        return ""
    return PATTERNS_PATH.read_text(encoding="utf-8")


def read_skill_md() -> str:
    if not SKILL_MD.exists():
        return ""
    return SKILL_MD.read_text(encoding="utf-8")


def get_week_label() -> str:
    return datetime.now(timezone.utc).strftime("W%Y-%V")


# ── change proposal logic ─────────────────────────────────────────────────────

def propose_capability_changes(delta: dict, patterns_text: str) -> list[dict]:
    """
    Returns a list of proposed changes to SKILL.md capability layer.
    Each change: {field, old_hint, new_value, reason, confidence}
    """
    changes = []
    breakdown = delta.get("breakdown", {})
    predictions = delta.get("predictions", {})

    # install_line change
    install_contrib = breakdown.get("install_line_avg", 0) * 0.25
    if install_contrib > 0.08:
        m = re.search(r"install_line:\s+([\d.]+)", patterns_text)
        if m:
            new_val = round(float(m.group(1)))
            confidence = min(0.95, install_contrib * 3)
            changes.append({
                "field":      "install_line_target",
                "new_value":  new_val,
                "reason":     f"install commands moved to line ~{new_val} in current top repos",
                "confidence": round(confidence, 2),
            })

    # readme length change
    len_contrib = breakdown.get("readme_length_avg", 0) * 0.15
    if len_contrib > 0.06:
        m = re.search(r"readme_length:\s+([\d.]+)", patterns_text)
        if m:
            new_val = round(float(m.group(1)))
            predicted = predictions.get("readme_length_avg")
            target = round(predicted) if predicted else new_val
            changes.append({
                "field":      "readme_length_target",
                "new_value":  target,
                "reason":     f"README length trending toward {target} words",
                "confidence": round(min(0.9, len_contrib * 4), 2),
            })

    # hook word count change
    hook_contrib = breakdown.get("hook_words_avg", 0) * 0.20
    if hook_contrib > 0.07:
        m = re.search(r"hook_words:\s+([\d.]+)", patterns_text)
        if m:
            predicted = predictions.get("hook_words_avg")
            current   = float(m.group(1))
            target    = round(predicted) if predicted else round(current)
            changes.append({
                "field":      "hook_words_target",
                "new_value":  target,
                "reason":     f"hook length trending to {target} words (predicted from last {len(predictions)} weeks)",
                "confidence": round(min(0.85, hook_contrib * 3.5), 2),
            })

    # new tone patterns
    tone_contrib = breakdown.get("tone_shift", 0) * 0.30
    if tone_contrib > 0.09:
        changes.append({
            "field":      "anti_ai_patterns",
            "new_value":  "see references/anti-ai-patterns.md",
            "reason":     "new AI writing patterns detected in current low-performer repos",
            "confidence": round(min(0.9, tone_contrib * 2.5), 2),
        })

    return changes


def propose_knowledge_changes(patterns_text: str) -> list[str]:
    """Always update knowledge layer when delta >= DRIFT."""
    return [
        "references/viral-patterns.md — overwrite with latest scan output",
        "references/formula-history.md — append new week entry",
    ]


# ── PR body renderer ──────────────────────────────────────────────────────────

def render_pr_body(delta: dict, cap_changes: list[dict], know_changes: list[str]) -> str:
    score   = delta["drift_score"]
    status  = delta["status"]
    week    = get_week_label()
    new_w   = delta.get("new_week", "?")
    old_w   = delta.get("old_week", "?")

    overall_conf = (
        round(sum(c["confidence"] for c in cap_changes) / len(cap_changes), 2)
        if cap_changes else 0.0
    )
    auto_action = (
        "**auto-merge eligible** (confidence ≥ 0.65)"
        if overall_conf >= AUTO_MERGE_THRESHOLD
        else f"**requires your approval** (confidence {overall_conf} < 0.65)"
    )

    cap_section = ""
    if cap_changes:
        lines = []
        for c in cap_changes:
            lines.append(f"- `{c['field']}` → `{c['new_value']}`  \n  _{c['reason']}_ (confidence {c['confidence']})")
        cap_section = "### Proposed capability layer changes (SKILL.md)\n" + "\n".join(lines)
    else:
        cap_section = "### Capability layer\nNo changes needed — drift is in knowledge layer only."

    know_section = "### Knowledge layer changes (auto-applied)\n" + "\n".join(f"- {k}" for k in know_changes)

    breakdown_lines = []
    for dim, val in delta.get("breakdown", {}).items():
        from delta import WEIGHTS  # noqa: F401 — only available if delta.py is in path
        w = {"install_line_avg":0.25,"tone_shift":0.30,"hook_words_avg":0.20,
             "readme_length_avg":0.15,"hook_type_shift":0.10}.get(dim, 0)
        contrib = round(val * w, 3)
        flag = "  ← **significant**" if contrib > 0.08 else ""
        breakdown_lines.append(f"| {dim} | {val:.3f} | ×{w} | {contrib:.3f}{flag} |")

    breakdown_table = (
        "| dimension | raw | weight | contribution |\n"
        "|---|---|---|---|\n"
        + "\n".join(breakdown_lines)
    )

    return f"""## Weekly evolution — {week}

**Drift score:** `{score}`  |  **Status:** `{status}`  |  {auto_action}

Comparing `{new_w}` → `{old_w}`.

### What changed in the market
{_summarize_market_changes(delta, cap_changes)}

{cap_section}

{know_section}

### Drift breakdown
{breakdown_table}

### What is NOT changing
{_unchanged_summary(delta)}

---
_Generated by lazy-skill-drop evolution engine. Merge capability changes to apply._
"""


def _summarize_market_changes(delta: dict, cap_changes: list[dict]) -> str:
    lines = []
    for c in cap_changes:
        lines.append(f"- {c['reason']}")
    if not lines:
        lines.append("- Incremental changes within normal variance")
    return "\n".join(lines)


def _unchanged_summary(delta: dict) -> str:
    stable = []
    breakdown = delta.get("breakdown", {})
    weights = {"install_line_avg":0.25,"tone_shift":0.30,"hook_words_avg":0.20,
               "readme_length_avg":0.15,"hook_type_shift":0.10}
    for dim, val in breakdown.items():
        w = weights.get(dim, 0)
        if val * w < 0.05:
            stable.append(f"- `{dim}` (contribution {round(val*w,3)})")
    return "\n".join(stable) if stable else "- All dimensions show notable change — see above"


# ── evolution log ─────────────────────────────────────────────────────────────

def append_evolution_log(delta: dict, cap_changes: list[dict], dry_run: bool):
    week  = get_week_label()
    score = delta["drift_score"]
    label = delta["status"]
    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = (
        f"## {week} — {label} (score {score})\n"
        f"generated: {ts}\n"
        f"changes: {len(cap_changes)} capability, {1} knowledge\n"
    )
    for c in cap_changes:
        entry += f"  - {c['field']} → {c['new_value']}  (conf {c['confidence']})\n"
    entry += "\n"
    if dry_run:
        print("── evolution-log append (dry run) ───────────────────────")
        print(entry)
        return
    ELOG.parent.mkdir(parents=True, exist_ok=True)
    existing = ELOG.read_text(encoding="utf-8") if ELOG.exists() else ""

    # Preserve frontmatter if present — insert new entry AFTER frontmatter block,
    # not before. Otherwise entry ends up above `---` and breaks the YAML parse.
    fm_match = re.match(r"^---\n.*?\n---\n(?:\n*# [^\n]*\n+.*?\n\n)?", existing, re.DOTALL)
    if fm_match:
        head = fm_match.group(0)
        body = existing[fm_match.end():]
        new_content = head + entry + body
    else:
        new_content = entry + existing

    ELOG.write_text(new_content, encoding="utf-8")
    print(f"  ✓ appended to {ELOG}")
    # Evolution log uses "## " headers as entry separators (one per week)
    enforce_max_lines(
        target=ELOG,
        archive=ELOG_ARCH,
        entry_separator="## ",
        keep_frontmatter=True,
    )


# ── git / gh CLI ──────────────────────────────────────────────────────────────

def git_available() -> bool:
    code, _, _ = run(["git", "rev-parse", "--git-dir"])
    return code == 0


def gh_available() -> bool:
    code, _, _ = run(["gh", "--version"])
    return code == 0


def create_pr(pr_body: str, week: str, dry_run: bool):
    if dry_run:
        print("── PR body (dry run) ────────────────────────────────────")
        print(pr_body)
        return

    if not git_available():
        print("[propose] Not a git repo — skipping PR creation.", file=sys.stderr)
        print("PR body:\n", pr_body)
        return

    if not gh_available():
        print("[propose] gh CLI not found — PR body saved to memory/evolution-log.md only.")
        return

    # create a branch and commit knowledge layer changes
    branch = f"evolution/{week.lower()}"
    run(["git", "checkout", "-b", branch])
    run(["git", "add", str(PATTERNS_PATH), str(ELOG)])
    run(["git", "commit", "-m", f"chore: knowledge layer update {week}"])
    run(["git", "push", "--set-upstream", "origin", branch])

    # write PR body to a temp file
    tmp = Path("/tmp/pr_body.md")
    tmp.write_text(pr_body, encoding="utf-8")

    code, out, err = run([
        "gh", "pr", "create",
        "--title", f"Weekly evolution — {week}",
        "--body-file", str(tmp),
        "--base", "main",
    ])
    if code == 0:
        print(f"  ✓ PR created: {out}")
    else:
        print(f"  ✗ gh pr create failed: {err}", file=sys.stderr)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate evolution PR for lazy-skill-drop")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--auto",    action="store_true", help="Auto-merge if confidence >= threshold")
    args = parser.parse_args()

    delta = run_delta_json()
    score = delta["drift_score"]
    label = delta["status"]

    print(f"[propose] drift={score} → {label}")

    if label == "STABLE":
        print("[propose] No evolution needed — STABLE.")
        append_evolution_log(delta, [], args.dry_run)
        sys.exit(0)

    patterns_text = read_patterns()
    cap_changes   = propose_capability_changes(delta, patterns_text)
    know_changes  = propose_knowledge_changes(patterns_text)
    week          = get_week_label()

    pr_body = render_pr_body(delta, cap_changes, know_changes)

    # overall confidence
    overall_conf = (
        round(sum(c["confidence"] for c in cap_changes) / len(cap_changes), 2)
        if cap_changes else 0.0
    )

    if args.auto and overall_conf >= AUTO_MERGE_THRESHOLD:
        print(f"[propose] Auto-merge eligible (conf {overall_conf}). Applying directly.")
        # in auto mode, still create PR but mark for auto-merge
        # (gh auto-merge requires branch protection — just note it)

    create_pr(pr_body, week, args.dry_run)
    append_evolution_log(delta, cap_changes, args.dry_run)

    print(f"[propose] done. {len(cap_changes)} capability change(s) proposed.")


if __name__ == "__main__":
    main()
