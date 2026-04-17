#!/usr/bin/env python3
"""
audit_self.py — eat our own dogfood.

Scores this skill's own README.md and SKILL.md against the current formula.
Runs weekly (cron), pre-publish (gate mode), and on-demand.

If total score is below threshold, either:
  - gate mode   → exit non-zero, block publishing new skills
  - weekly mode → open a PR proposing fixes
  - CLI mode    → print the scorecard for the user

Usage:
    python audit_self.py                # print scorecard
    python audit_self.py --json         # machine-readable
    python audit_self.py --gate         # exit non-zero if below threshold
    python audit_self.py --target README # audit a specific file, e.g. when
                                         # auditing a user's generated skill

The point: this skill is a viral-README tool. If its own README fails the
rules it enforces on others, it should be caught and fixed automatically
rather than silently rotting while still publishing new skills.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
# audit_self.py lives either at skill root or in scripts/ — handle both
if (SCRIPT_DIR / "SKILL.md").exists():
    SKILL_ROOT = SCRIPT_DIR
else:
    SKILL_ROOT = SCRIPT_DIR.parent
README_PATH = SKILL_ROOT / "README.md"
SKILL_MD    = SKILL_ROOT / "SKILL.md"
PATTERNS    = SKILL_ROOT / "references" / "viral-patterns.md"
FORBIDDEN   = SKILL_ROOT / "references" / "anti-ai-patterns.md"

PASS_THRESHOLD = 0.70

DEFAULT_FORMULA = {
    "hook_words_target":       12,    # real data: 12.1 install-weighted (was 10)
    "hook_words_tolerance":    4,
    "install_line_target":     2,     # real data: ALL top skills put install on line 2 (was 8!)
    "install_line_tolerance":  2,
    "readme_length_target":    210,   # real data: 209 install-weighted (was 247)
    "readme_length_tolerance": 60,
    "description_max":         120,
}

DEFAULT_FORBIDDEN = {
    "seamless", "leverage", "robust", "unlock", "unleash",
    "craft", "journey", "holistic", "elevate", "harness",
    "delve", "comprehensive", "cutting-edge", "innovative",
    "empower", "supercharge", "revolutionize", "streamline",
}

BANNED_HEADERS = {"overview", "introduction", "features", "getting started"}

# Verbs that turn a description into a workflow summary (obra anti-pattern).
# Presence means description is describing WHAT the skill does internally
# instead of WHEN it should trigger.
WORKFLOW_SUMMARY_VERBS = {
    "reads", "extracts", "analyzes", "researches", "writes",
    "generates", "publishes", "creates", "produces", "renders",
    "installs", "flags", "shows", "builds", "processes",
    "scans", "detects", "applies", "outputs", "exports",
}

DIM_WEIGHTS = {
    # ── Regression-calibrated weights (w2026-17, n=40, R²=0.69, LogReg acc=92.5%) ──
    #
    # Key changes vs seed weights:
    #   install_position  0.15 → 0.30  ← strongest binary predictor (LogReg 0.467)
    #   word_count        0.15 → 0.20  ← highest OLS coefficient (2.87), sweet-spot matters
    #   hook_quality      0.25 → 0.15  ← still top-3 but was overweighted
    #   banned_headers    0.05 → 0.00  ← near-zero signal in both models (LogReg 0.001);
    #                                     still scored and shown in output, not counted
    #   token_budget kept at 0.05 as operational guard (not in regression sample)
    # Sum = 1.00
    "install_position":     0.30,   # target: README.md — #1 binary predictor
    "word_count":           0.20,   # target: README.md — #1 OLS predictor (sweet spot ~210w)
    "hook_quality":         0.15,   # target: README.md — important but was over-indexed
    "description_triggers": 0.15,   # target: SKILL.md frontmatter — unchanged
    "forbidden_words":      0.10,   # target: README + SKILL.md — unchanged (negative OLS coeff)
    "description_length":   0.05,   # target: SKILL.md frontmatter — weak but non-zero
    "token_budget":         0.05,   # target: SKILL.md + refs — operational guard, not in regression
    "burstiness":           0.00,   # informational only — LogReg 0.036, below threshold
    "banned_headers":       0.00,   # informational only — LogReg 0.001, no predictive value
    # Sum = 1.00
# Sum = 1.00
# Scorer signature encodes target file:
#   score_X(readme_text, ...)      → looks at README only
#   score_X(skill_md_text, ...)    → looks at SKILL.md only
#   score_X(combined_text, ...)    → looks at both concatenated
#   score_X(skill_md_path, ...)    → reads multiple files from disk (e.g. token_budget)

# Plain-language templates for each failing dimension. {note} is the raw
# note from the scorer. These get composed into human_notes when a dim
# scores below 0.70, so the SKILL.md consumer can quote them directly
# without re-interpreting numbers.
DIM_DIAGNOSTICS = {
    "hook_quality":
        "The first line of the README isn't doing its job — {note}. "
        "Current formula wants a short imperative hook (about 10 words, starting with a verb).",
    "install_position":
        "The install command is in the wrong place — {note}. "
        "Readers expect it within the first ~8 lines, right after the hook.",
    "word_count":
        "README length is off formula — {note}. "
        "Shorter than target reads thin; longer than target reads like AI filler.",
    "forbidden_words":
        "AI-slop words detected in the docs: {note}. "
        "These trigger 'obviously AI-generated' pattern matchers on sight.",
    "description_length":
        "The SKILL.md description is too long — {note}. "
        "Anthropic's metadata scan truncates past ~200 chars; triggering gets unreliable.",
    "description_triggers":
        "The SKILL.md description contains workflow-summary verbs ({note}). "
        "This is the exact anti-pattern lazy-skill-drop audits in others — obra's research "
        "shows Claude follows the description summary and skips the skill body when this happens.",
    "banned_headers":
        "README uses generic AI-slop headers: {note}. "
        "'Overview', 'Features', 'Introduction' are the top three tells.",
    "burstiness":
        "Paragraph rhythm is too uniform — {note}. "
        "Real human writing varies sentence/paragraph length. "
        "AI text optimizes for consistency, which detectors flag.",
    "token_budget":
        "Default context is too large — {note}. "
        "SKILL.md + default-read references should stay ≤7000 tokens "
        "so metadata matching and activation stay reliable. "
        "Compress short-version references or move content to -full.md.",
}


# ── formula loading ───────────────────────────────────────────────────────────

def read_formula() -> dict:
    f = dict(DEFAULT_FORMULA)
    if not PATTERNS.exists():
        return f
    try:
        text = PATTERNS.read_text(encoding="utf-8")
    except Exception:
        return f
    for key in ("hook_words", "install_line", "readme_length"):
        m = re.search(rf"{key}:\s+([\d.]+)", text)
        if m:
            try:
                f[f"{key}_target"] = float(m.group(1))
            except ValueError:
                pass
    return f


def read_forbidden() -> set:
    """
    Parse anti-ai-patterns.md for banned words.

    Only reads the 'Tier 1' section — Tier 2+ words need context to judge and
    would produce false positives if added here (e.g. "paradigm" is fine in a
    sentence about paradigm shifts; it's only a tell when clustered with other
    tier-2 words).
    """
    if not FORBIDDEN.exists():
        return set(DEFAULT_FORBIDDEN)
    try:
        text = FORBIDDEN.read_text(encoding="utf-8")
    except Exception:
        return set(DEFAULT_FORBIDDEN)

    # Isolate the Tier 1 section: "## Tier 1" header through next "##" or EOF.
    m = re.search(r"^##\s+Tier\s*1.*?$", text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return set(DEFAULT_FORBIDDEN)
    start = m.end()
    m2 = re.search(r"^##\s+", text[start:], re.MULTILINE)
    tier1 = text[start:start + (m2.start() if m2 else len(text) - start)]

    words = set()
    # Match "- word" or '- "word"' at start of bullet lines only
    for line in tier1.splitlines():
        s = line.strip()
        if not s.startswith(("-", "*")):
            continue
        s = s.lstrip("-*").strip().strip('"').strip("'")
        # Allow simple words and hyphenated ("cutting-edge")
        if re.fullmatch(r"[a-z][a-z-]{3,}", s.lower()):
            words.add(s.lower())
    return words or set(DEFAULT_FORBIDDEN)


# ── dimension scorers ─────────────────────────────────────────────────────────

def score_hook(readme_text: str, formula: dict) -> tuple[float, str]:
    lines = readme_text.splitlines()
    hook = None
    for line in lines[1:]:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("```") and not s.startswith("_"):
            hook = s
            break
    if not hook:
        return 0.0, "no hook line found"

    words = hook.split()
    target = formula["hook_words_target"]
    tol = formula["hook_words_tolerance"]
    diff = abs(len(words) - target)
    length_score = max(0.0, 1.0 - diff / (tol * 2))

    first = words[0].lower().rstrip(",.!?\"")
    imperative_verbs = {
        "stop", "turn", "ship", "use", "make", "build", "get", "write",
        "skip", "save", "discuss", "pick", "run", "check", "avoid",
        "start", "decide", "find", "keep", "never", "always", "drop",
        "forget", "rewrite", "learn", "generate", "publish", "design",
    }
    is_question = hook.rstrip().endswith("?")
    style_score = 1.0 if (first in imperative_verbs or is_question) else 0.4

    total = (length_score + style_score) / 2
    return total, f"{len(words)}w (target {int(target)}), first='{first}', imperative={first in imperative_verbs}"


def score_install_position(readme_text: str, formula: dict) -> tuple[float, str]:
    target = int(formula["install_line_target"])
    tol = int(formula["install_line_tolerance"])
    lines = readme_text.splitlines()
    install_line = None
    for i, line in enumerate(lines, 1):
        if re.search(r"\bgit clone\b", line) or re.search(r"^\s*(npm i|npx|brew install)\b", line):
            install_line = i
            break
    if install_line is None:
        return 0.3, "no install command found"
    diff = abs(install_line - target)
    score = max(0.0, 1.0 - diff / (tol * 2))
    return score, f"line {install_line} (target {target} ±{tol})"


def score_word_count(readme_text: str, formula: dict) -> tuple[float, str]:
    no_code = re.sub(r"```.*?```", "", readme_text, flags=re.DOTALL)
    no_headers = re.sub(r"^#+ .*$", "", no_code, flags=re.MULTILINE)
    words = len(no_headers.split())
    target = int(formula["readme_length_target"])
    tol = int(formula["readme_length_tolerance"])
    diff = abs(words - target)
    score = max(0.0, 1.0 - diff / (tol * 2))
    return score, f"{words}w (target {target} ±{tol})"


def score_forbidden(combined_text: str, forbidden: set) -> tuple[float, str]:
    text_lower = combined_text.lower()
    hits = [w for w in forbidden if re.search(rf"\b{re.escape(w)}\b", text_lower)]
    if not hits:
        return 1.0, "clean"
    score = max(0.0, 1.0 - 0.15 * len(hits))
    return score, f"found: {', '.join(sorted(hits)[:5])}"


def _extract_description(skill_md_text: str) -> str:
    m = re.search(r"^---\s*$", skill_md_text, re.MULTILINE)
    if not m:
        return ""
    fm_start = m.end()
    m2 = re.search(r"^---\s*$", skill_md_text[fm_start:], re.MULTILINE)
    if not m2:
        return ""
    fm = skill_md_text[fm_start:fm_start + m2.start()]
    # find description block (may span multiple lines with YAML continuation)
    m3 = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:)", fm, re.MULTILINE | re.DOTALL)
    if not m3:
        return ""
    return re.sub(r"\s+", " ", m3.group(1)).strip()


def score_description_length(skill_md_text: str, formula: dict) -> tuple[float, str]:
    desc = _extract_description(skill_md_text)
    if not desc:
        return 0.0, "no description field"
    words = len(desc.split())
    max_w = int(formula["description_max"])
    if words <= max_w:
        return 1.0, f"{words}w (max {max_w})"
    over = words - max_w
    score = max(0.0, 1.0 - over / max_w)
    return score, f"{words}w exceeds max {max_w}"


def score_description_triggers(skill_md_text: str) -> tuple[float, str]:
    desc = _extract_description(skill_md_text).lower()
    if not desc:
        return 0.0, "no description"
    # Split description at phrases that signal transition from triggers to workflow:
    # after "or is ... to ..." / "or has ..." — anything BEYOND an "OR" clause
    # that starts describing internal behavior is a workflow leak.
    # Heuristic: find workflow verbs appearing outside quoted strings.
    outside_quotes = re.sub(r'"[^"]*"', "", desc)
    hits = [v for v in WORKFLOW_SUMMARY_VERBS if re.search(rf"\b{v}\b", outside_quotes)]
    if not hits:
        return 1.0, "pure trigger (no workflow leak)"
    score = max(0.0, 1.0 - 0.2 * len(hits))
    return score, f"workflow verbs: {', '.join(sorted(hits)[:5])}"


def score_banned_headers(readme_text: str) -> tuple[float, str]:
    headers = re.findall(r"^##+ (.+)$", readme_text, re.MULTILINE)
    hits = [h for h in headers if h.strip().lower() in BANNED_HEADERS]
    if not hits:
        return 1.0, "clean"
    score = max(0.0, 1.0 - 0.3 * len(hits))
    return score, f"banned: {', '.join(hits)}"


def score_burstiness(readme_text: str) -> tuple[float, str]:
    paragraphs = []
    for p in readme_text.split("\n\n"):
        s = p.strip()
        if not s or s.startswith("```") or s.startswith("#") or s.startswith("_"):
            continue
        if s.startswith("-") or s.startswith("*"):
            continue  # skip lists — they're naturally uniform
        paragraphs.append(s)
    if len(paragraphs) < 3:
        return 0.5, "too few paragraphs for signal"
    lens = [len(p.split()) for p in paragraphs]
    mean = sum(lens) / len(lens)
    if mean == 0:
        return 0.5, "empty paragraphs"
    variance = sum((l - mean) ** 2 for l in lens) / len(lens)
    cv = (variance ** 0.5) / mean
    score = min(1.0, cv / 0.5)
    return score, f"paragraph-length CV={cv:.2f} (>0.5 is good)"


def score_token_budget(skill_md_path: Path) -> tuple[float, str]:
    """Sum words across SKILL.md + default-read short references.

    Target: ≤ 7000 tokens (≈ 5400 words with 1.3 tokens/word factor).
    Fail linearly from 5400 words (1.0) to 7700 words (0.0).

    Does NOT count *-full.md files (they are not loaded by default).
    """
    skills_root = skill_md_path.parent
    default_read = [
        skill_md_path,
        skills_root / "references" / "viral-patterns.md",
        skills_root / "references" / "anti-ai-patterns.md",
        skills_root / "references" / "naming-patterns.md",
        skills_root / "references" / "recon-patterns.md",
        skills_root / "references" / "extract-patterns.md",
        skills_root / "references" / "formula-history.md",
    ]
    total_words = 0
    for p in default_read:
        if p.exists():
            total_words += len(p.read_text(encoding="utf-8").split())

    approx_tokens = int(total_words * 1.3)

    # Target: ≤5400 words = ≤7000 tokens. Linear dropoff to 0 at 7700 words.
    if total_words <= 5400:
        score = 1.0
    elif total_words >= 7700:
        score = 0.0
    else:
        score = 1.0 - (total_words - 5400) / (7700 - 5400)

    return score, f"default context ≈{approx_tokens} tokens ({total_words}w, target ≤7000)"


# ── main audit ────────────────────────────────────────────────────────────────

def audit(readme_path: Path = README_PATH, skill_md_path: Path = SKILL_MD) -> dict:
    formula = read_formula()
    forbidden = read_forbidden()
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    skill_md = skill_md_path.read_text(encoding="utf-8") if skill_md_path.exists() else ""
    combined = readme + "\n" + skill_md

    scorers = {
        "hook_quality":         lambda: score_hook(readme, formula),
        "install_position":     lambda: score_install_position(readme, formula),
        "word_count":           lambda: score_word_count(readme, formula),
        "forbidden_words":      lambda: score_forbidden(combined, forbidden),
        "description_length":   lambda: score_description_length(skill_md, formula),
        "description_triggers": lambda: score_description_triggers(skill_md),
        "banned_headers":       lambda: score_banned_headers(readme),
        "burstiness":           lambda: score_burstiness(readme),
        "token_budget":         lambda: score_token_budget(skill_md_path),
    }

    dims = {name: fn() for name, fn in scorers.items()}
    total = sum(dims[d][0] * DIM_WEIGHTS[d] for d in dims)

    # Severity gating — matches SKILL.md's graduated response policy
    if total >= 0.70:
        severity = "PASS"
    elif total >= 0.55:
        severity = "SOFT_WARN"
    else:
        severity = "HARD_BLOCK"

    # Human-readable diagnostics for dimensions that failed (< 0.70).
    # Ordered by weighted loss (most impactful first) so the top 1-2 lines
    # are what matters most.
    failing = [(d, dims[d][0], dims[d][1]) for d in dims if dims[d][0] < 0.70]
    failing.sort(key=lambda x: (0.70 - x[1]) * DIM_WEIGHTS[x[0]], reverse=True)
    human_notes = [
        DIM_DIAGNOSTICS.get(d, "").format(note=note)
        for d, _score, note in failing
        if DIM_DIAGNOSTICS.get(d)
    ]

    return {
        "total_score":   round(total, 3),
        "pass":          total >= PASS_THRESHOLD,
        "severity":      severity,
        "threshold":     PASS_THRESHOLD,
        "readme_path":   str(readme_path),
        "skill_md_path": str(skill_md_path),
        "formula":       formula,
        "human_notes":   human_notes,
        "dimensions":  {
            d: {
                "score":  round(dims[d][0], 3),
                "note":   dims[d][1],
                "weight": DIM_WEIGHTS[d],
                "weighted_contribution": round(dims[d][0] * DIM_WEIGHTS[d], 3),
            }
            for d in dims
        },
    }


def _use_unicode() -> bool:
    """
    Return True if stdout can handle the nice unicode marks (✓ ✗ ~ ─).
    On Windows cmd.exe with legacy code pages this is False — fall back to ASCII.
    """
    enc = (sys.stdout.encoding or "").lower()
    return "utf" in enc


def render_human(result: dict) -> str:
    lines = []
    uni = _use_unicode()
    if uni:
        marks = {"PASS": "✓ PASS", "SOFT_WARN": "~ SOFT WARN", "HARD_BLOCK": "✗ HARD BLOCK"}
        ok, fail, mid, bullet = "✓", "✗", "~", "·"
    else:
        marks = {"PASS": "[OK] PASS", "SOFT_WARN": "[WARN] SOFT WARN", "HARD_BLOCK": "[FAIL] HARD BLOCK"}
        ok, fail, mid, bullet = "[+]", "[!]", "[~]", "*"

    severity = result.get("severity", "PASS")
    status = marks.get(severity, severity)
    times = "×" if uni else "x"
    lines.append(f"Self-audit: {status}  score={result['total_score']}  threshold={result['threshold']}")
    lines.append(f"  readme:  {result['readme_path']}")
    lines.append(f"  skill:   {result['skill_md_path']}")
    lines.append("")
    for dim, info in result["dimensions"].items():
        mark = ok if info["score"] >= 0.7 else (fail if info["score"] < 0.5 else mid)
        lines.append(f"  {mark} {dim:<22} {info['score']:.2f} {times} {info['weight']:.2f} = {info['weighted_contribution']:.3f}   {info['note']}")
    if result.get("human_notes"):
        lines.append("")
        lines.append("  What this means for the user:")
        for note in result["human_notes"]:
            lines.append(f"    {bullet} {note}")
    if severity == "HARD_BLOCK":
        lines.append("")
        lines.append("  Recommended: fix the above before publishing new skills via publish.py.")
    elif severity == "SOFT_WARN":
        lines.append("")
        lines.append("  Publishing is NOT blocked. Consider refreshing the above when you have time.")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Audit own README/SKILL.md against the current formula")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--gate", action="store_true", help="exit non-zero if below threshold (pre-publish guard)")
    p.add_argument("--readme", default=str(README_PATH), help="path to README to audit (default: own)")
    p.add_argument("--skill-md", default=str(SKILL_MD), help="path to SKILL.md to audit (default: own)")
    args = p.parse_args()

    result = audit(Path(args.readme), Path(args.skill_md))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_human(result))
    if args.gate and result.get("severity") == "HARD_BLOCK":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
