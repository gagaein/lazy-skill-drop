#!/usr/bin/env python3
"""
delta.py — Drift Detector for lazy-skill-drop
Compares the two most recent entries in formula-history.md,
computes a weighted drift score, determines evolution status,
and optionally predicts next-week values from trend.

Exit codes:
    0 = STABLE   (delta < 0.20)
    1 = DRIFT    (0.20–0.45)
    2 = SHIFT    (0.45–0.65)
    3 = PARADIGM (> 0.65)
    99 = error

Usage:
    python delta.py
    python delta.py --verbose
    python delta.py --json        (machine-readable output)
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT   = Path(__file__).parent.parent
HISTORY_PATH = SKILL_ROOT / "references" / "formula-history.md"
PATTERNS_PATH = SKILL_ROOT / "references" / "viral-patterns.md"

# ── thresholds ────────────────────────────────────────────────────────────────
THRESHOLD_STABLE   = 0.20
THRESHOLD_DRIFT    = 0.45
THRESHOLD_SHIFT    = 0.65

# ── field weights (must sum to 1.0) ───────────────────────────────────────────
WEIGHTS = {
    "install_line_avg":  0.25,
    "tone_shift":        0.30,   # derived from forbidden_seen changes
    "hook_words_avg":    0.20,
    "readme_length_avg": 0.15,
    "hook_type_shift":   0.10,   # hook type distribution change
}

# ── parser ────────────────────────────────────────────────────────────────────

def parse_entry(text: str) -> dict:
    """
    Parse one formula-history.md entry block into a dict.
    Returns empty dict if parsing fails.
    """
    d: dict = {}

    def grab(pattern, cast=float, default=None):
        m = re.search(pattern, text, re.MULTILINE)
        if not m:
            return default
        try:
            return cast(m.group(1))
        except (ValueError, TypeError):
            return default

    d["week"]              = grab(r"^## (w\d{4}-\d+)", str)
    d["hook_words_avg"]    = grab(r"hook_words:\s+([\d.]+)")
    d["install_line_avg"]  = grab(r"install_line:\s+([\d.]+)")
    d["readme_length_avg"] = grab(r"readme_length:\s+([\d.]+)")

    # hook type — pull dominant (first) type
    m = re.search(r"hook_type:\s+(\w+)", text)
    d["dominant_hook_type"] = m.group(1) if m else None

    # forbidden words seen — count total mentions
    forbidden_block = re.search(r"forbidden_seen:(.*?)(?=\n###|\Z)", text, re.DOTALL)
    if forbidden_block:
        words = re.findall(r'"([^"]+)"', forbidden_block.group(1))
        d["forbidden_words"] = words
        counts = re.findall(r"in (\d+)/", forbidden_block.group(1))
        d["forbidden_total"] = sum(int(c) for c in counts)
    else:
        d["forbidden_words"] = []
        d["forbidden_total"] = 0

    return d


def load_entries() -> list[dict]:
    """Load all entries from formula-history.md, newest first."""
    if not HISTORY_PATH.exists():
        return []
    text = HISTORY_PATH.read_text(encoding="utf-8")
    # split on separator lines or on ## w entries
    blocks = re.split(r"─{40,}\n", text)
    entries = []
    for block in blocks:
        if "## w" not in block:
            continue
        parsed = parse_entry(block)
        if parsed.get("week"):
            entries.append(parsed)
    return entries  # newest first (history file is prepended)


# ── delta calculations ────────────────────────────────────────────────────────

def relative_change(new, old):
    """Relative change, capped at 1.0 to avoid outlier spikes."""
    if old is None or new is None or old == 0:
        return 0.0
    return min(1.0, abs(new - old) / abs(old))


def tone_shift(new: dict, old: dict) -> float:
    """
    Score how much the forbidden-word landscape changed.
    New forbidden words appearing = bad (market shifting away from AI slop).
    Score = (new_unique + changed_count) / max_possible
    """
    old_words = set(old.get("forbidden_words", []))
    new_words = set(new.get("forbidden_words", []))
    newly_appeared = new_words - old_words
    disappeared    = old_words - new_words
    # each new pattern = 0.15 delta, each disappeared = 0.05 (less impactful)
    score = len(newly_appeared) * 0.15 + len(disappeared) * 0.05
    return min(1.0, score)


def hook_type_shift(new: dict, old: dict) -> float:
    """Change in dominant hook type (command vs statement vs question)."""
    if new.get("dominant_hook_type") != old.get("dominant_hook_type"):
        return 0.4  # dominant type changed — notable shift
    return 0.0


def compute_delta(new: dict, old: dict) -> tuple[float, dict]:
    """
    Returns (drift_score, breakdown_dict).
    drift_score is weighted sum of all dimension deltas.
    """
    dims = {
        "install_line_avg":  relative_change(new.get("install_line_avg"),  old.get("install_line_avg")),
        "tone_shift":        tone_shift(new, old),
        "hook_words_avg":    relative_change(new.get("hook_words_avg"),    old.get("hook_words_avg")),
        "readme_length_avg": relative_change(new.get("readme_length_avg"), old.get("readme_length_avg")),
        "hook_type_shift":   hook_type_shift(new, old),
    }
    score = sum(dims[k] * WEIGHTS[k] for k in dims)
    return round(score, 3), dims


def status(score: float) -> tuple[str, int]:
    if score < THRESHOLD_STABLE:
        return "STABLE", 0
    if score < THRESHOLD_DRIFT:
        return "DRIFT", 1
    if score < THRESHOLD_SHIFT:
        return "SHIFT", 2
    return "PARADIGM", 3


# ── trend prediction ──────────────────────────────────────────────────────────

def linear_predict(values: list[float]) -> float | None:
    """Simple linear regression, returns predicted next value."""
    n = len(values)
    if n < 3:
        return None
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(values) / n
    numerator   = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values))
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return None
    slope = numerator / denominator
    predicted = y_mean + slope * (n - x_mean)
    return round(predicted, 1)


def build_predictions(entries: list[dict]) -> dict:
    """
    Use up to 6 weeks of history to predict next-week values.
    Returns dict of field → predicted_value (or None).
    """
    predictions = {}
    for field in ["hook_words_avg", "install_line_avg", "readme_length_avg"]:
        values = [e[field] for e in entries if e.get(field) is not None]
        if len(values) >= 3:
            predictions[field] = linear_predict(list(reversed(values)))  # oldest→newest
    return predictions


# ── output ────────────────────────────────────────────────────────────────────

def render_report(new: dict, old: dict, score: float, breakdown: dict,
                  label: str, predictions: dict, verbose: bool) -> str:
    lines = [
        f"drift_score: {score}",
        f"status:      {label}",
        "",
        "breakdown:",
    ]
    for dim, val in breakdown.items():
        weight = WEIGHTS[dim]
        contribution = round(val * weight, 3)
        flag = "  ← significant" if contribution > 0.08 else ""
        lines.append(f"  {dim:<22} raw={val:.3f} × {weight:.2f} = {contribution:.3f}{flag}")

    if verbose:
        lines += ["", "raw values:"]
        for field in ["hook_words_avg", "install_line_avg", "readme_length_avg"]:
            o = old.get(field, "?")
            n = new.get(field, "?")
            arrow = "→" if o == n else ("↑" if (n or 0) > (o or 0) else "↓")
            lines.append(f"  {field:<22} {o} {arrow} {n}")
        lines += ["", "tone:"]
        old_w = set(old.get("forbidden_words", []))
        new_w = set(new.get("forbidden_words", []))
        if new_w - old_w:
            lines.append(f"  newly appearing: {list(new_w - old_w)}")
        if old_w - new_w:
            lines.append(f"  disappeared:     {list(old_w - new_w)}")

    if predictions:
        lines += ["", "trend predictions (next week):"]
        for field, val in predictions.items():
            if val is not None:
                lines.append(f"  {field:<22} ≈ {val}")

    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compute drift score between two latest formula entries")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json",    "-j", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    entries = load_entries()

    if len(entries) < 2:
        print(f"[delta] Not enough history ({len(entries)} entries). Run scan.py first.", file=sys.stderr)
        sys.exit(99)

    new, old = entries[0], entries[1]
    score, breakdown = compute_delta(new, old)
    label, code = status(score)
    predictions = build_predictions(entries[:6])

    if args.json:
        output = {
            "drift_score": score,
            "status":      label,
            "exit_code":   code,
            "breakdown":   {k: round(v, 3) for k, v in breakdown.items()},
            "predictions": predictions,
            "new_week":    new.get("week"),
            "old_week":    old.get("week"),
        }
        print(json.dumps(output, indent=2))
    else:
        print(render_report(new, old, score, breakdown, label, predictions, args.verbose))

    sys.exit(code)


if __name__ == "__main__":
    main()
