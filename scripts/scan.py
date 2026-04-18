#!/usr/bin/env python3
"""
scan.py — Signal Scanner for lazy-skill-drop
Fetches top trending Claude skill repos from GitHub,
extracts structural DNA, writes viral-patterns.md.

Usage:
    python scan.py
    python scan.py --token ghp_xxxx   (higher rate limits)
    python scan.py --dry-run           (print without writing)
"""

import argparse
import json
import math
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# local helper (same dir)
sys.path.insert(0, str(Path(__file__).parent))
from length_guard import enforce_max_lines  # noqa: E402

# ── paths ────────────────────────────────────────────────────────────────────
SKILL_ROOT    = Path(__file__).parent.parent
PATTERNS_OUT  = SKILL_ROOT / "references" / "viral-patterns.md"
HISTORY_OUT   = SKILL_ROOT / "references" / "formula-history.md"
HISTORY_ARCH  = SKILL_ROOT / "memory" / "formula-history-archive.md"
SKILL_MD      = SKILL_ROOT / "SKILL.md"
ENTRY_SEP     = "─" * 60  # same as append_history's separator

# ── config ───────────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
    "topic:claude-skill",
    "topic:agent-skill",
    "topic:claude-code skill SKILL.md",
]
REPOS_PER_QUERY = 4          # fetch top N per query, deduplicate → ~8 unique
MIN_STARS       = 10         # ignore noise repos with very few stars
README_MAX_BYTES = 32_000    # cap to avoid huge files

FORBIDDEN_WORDS = [
    "seamlessly", "powerful", "comprehensive", "cutting-edge",
    "robust", "leverage", "utilize", "facilitate",
    "innovative", "revolutionary", "game-changer",
    "state-of-the-art", "best-in-class", "world-class",
    "effortlessly", "intuitive", "streamline",
]

HOOK_TYPE_VERBS = {
    "command":   r"^(Stop|Build|Drop|Fix|Run|Get|Make|Use|Add|Write|Turn|Let|Skip|Save|Ship|Kill|Try)\b",
    "question":  r"\?$",
    "statement": r".",  # fallback
}


# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh_get(url: str, token: str | None) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "lazy-skill-drop/1.0")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def search_repos(query: str, token: str | None, n: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "q":        query,
        "sort":     "stars",
        "order":    "desc",
        "per_page": n,
    })
    url = f"https://api.github.com/search/repositories?{params}"
    try:
        data = gh_get(url, token)
        return data.get("items", [])
    except Exception as e:
        print(f"  [warn] search failed for '{query}': {e}", file=sys.stderr)
        return []


def fetch_readme(repo_full_name: str, token: str | None) -> str:
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    try:
        data = gh_get(url, token)
        import base64
        raw = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return raw[:README_MAX_BYTES]
    except Exception as e:
        print(f"  [warn] readme fetch failed for {repo_full_name}: {e}", file=sys.stderr)
        return ""


# ── DNA extractors ────────────────────────────────────────────────────────────

def extract_hook(readme: str) -> dict:
    """First non-empty, non-badge line."""
    for raw_line in readme.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # skip badge lines (shields.io) and HTML comments
        if "![" in line and "badge" in line.lower():
            continue
        if line.startswith("<!--"):
            continue
        # strip markdown formatting
        clean = re.sub(r"[#*`_>]", "", line).strip()
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)  # links
        if len(clean) < 3:
            continue
        words = clean.split()
        hook_type = "statement"
        for htype, pattern in HOOK_TYPE_VERBS.items():
            if re.search(pattern, clean, re.IGNORECASE):
                hook_type = htype
                break
        opening_verb = words[0].rstrip(".,!") if hook_type == "command" else None
        return {
            "text":         clean,
            "words":        len(words),
            "type":         hook_type,
            "opening_verb": opening_verb,
        }
    return {"text": "", "words": 0, "type": "unknown", "opening_verb": None}


def extract_install_line(readme: str) -> int | None:
    """Line number of first code block containing an install command."""
    install_patterns = [
        r"git clone",
        r"npx skills",
        r"npx add-skill",
        r"cp.*SKILL\.md",
        r"pip install",
    ]
    lines = readme.splitlines()
    in_block = False
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
        if in_block:
            for pat in install_patterns:
                if re.search(pat, stripped, re.IGNORECASE):
                    return i
    return None


def extract_readme_length(readme: str) -> int:
    """Word count of readme, excluding code blocks."""
    in_block = False
    words = 0
    for line in readme.splitlines():
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        if not in_block:
            words += len(line.split())
    return words


def extract_code_blocks(readme: str) -> int:
    return len(re.findall(r"```", readme)) // 2


def extract_has_demo(readme: str) -> bool:
    patterns = [r"\.gif", r"\.mp4", r"asciinema\.org", r"demo", r"screencast"]
    return any(re.search(p, readme, re.IGNORECASE) for p in patterns)


def extract_badge_count(readme: str) -> int:
    return len(re.findall(r"!\[.*?\]\(https?://", readme))


def extract_forbidden_hits(readme: str) -> list[str]:
    text_lower = readme.lower()
    return [w for w in FORBIDDEN_WORDS if w in text_lower]


def extract_active_passive_ratio(readme: str) -> float:
    """Rough proxy: sentences starting with a noun vs. verb."""
    passive_patterns = [r"\b(is|are|was|were|been|being) \w+ed\b"]
    sentences = re.split(r"[.!?]", readme)
    passive = sum(1 for s in sentences
                  if any(re.search(p, s, re.IGNORECASE) for p in passive_patterns))
    active = max(1, len(sentences) - passive)
    return round(active / max(1, passive), 1)


def extract_numbers_in_first_lines(readme: str) -> bool:
    """Do the first 3 lines contain at least one number?"""
    lines = [l for l in readme.splitlines() if l.strip()][:3]
    text = " ".join(lines)
    return bool(re.search(r"\b\d+\b", text))


def get_star_velocity(repo: dict) -> float:
    """Approximate stars/day from creation date and current star count."""
    try:
        created = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
        days = max(1, (datetime.now(timezone.utc) - created).days)
        return round(repo.get("stargazers_count", 0) / days, 1)
    except Exception:
        return 0.0


# ── aggregation ───────────────────────────────────────────────────────────────

def aggregate(repo_dnas: list[dict]) -> dict:
    """Compute per-field averages + distributions across all repos."""
    n = len(repo_dnas)
    if n == 0:
        return {}

    def avg(field, default=0):
        vals = [r[field] for r in repo_dnas if r.get(field) is not None]
        return round(sum(vals) / max(1, len(vals)), 1) if vals else default

    def count(field, value):
        return sum(1 for r in repo_dnas if r.get(field) == value)

    # hook type distribution
    hook_counts = {t: count("hook_type", t) for t in ["command", "question", "statement", "unknown"]}
    dominant_hook = max(hook_counts, key=hook_counts.get)

    # opening verbs frequency
    verb_counts: dict[str, int] = {}
    for r in repo_dnas:
        v = r.get("opening_verb")
        if v:
            verb_counts[v] = verb_counts.get(v, 0) + 1
    top_verbs = sorted(verb_counts.items(), key=lambda x: -x[1])[:5]

    # forbidden words across all repos
    all_forbidden = {}
    for r in repo_dnas:
        for w in r.get("forbidden_hits", []):
            all_forbidden[w] = all_forbidden.get(w, 0) + 1
    # only report words appearing in 2+ repos
    notable_forbidden = {w: c for w, c in all_forbidden.items() if c >= 2}

    has_demo_count  = sum(1 for r in repo_dnas if r.get("has_demo"))
    has_number_count = sum(1 for r in repo_dnas if r.get("numbers_in_first_lines"))

    return {
        "n":                  n,
        "hook_words_avg":     avg("hook_words"),
        "hook_words_range":   (
            min(r["hook_words"] for r in repo_dnas if r.get("hook_words")),
            max(r["hook_words"] for r in repo_dnas if r.get("hook_words")),
        ),
        "dominant_hook_type": dominant_hook,
        "hook_type_dist":     hook_counts,
        "top_verbs":          top_verbs,
        "install_line_avg":   avg("install_line"),
        "readme_length_avg":  avg("readme_length"),
        "code_blocks_avg":    avg("code_blocks"),
        "has_demo_count":     has_demo_count,
        "numbers_in_first_lines_count": has_number_count,
        "badge_count_avg":    avg("badge_count"),
        "star_velocity_avg":  avg("star_velocity"),
        "active_passive_avg": avg("active_passive_ratio"),
        "notable_forbidden":  notable_forbidden,
    }


# ── writers ───────────────────────────────────────────────────────────────────

ISO_WEEK = datetime.now(timezone.utc).strftime("w%Y-%V")
GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

NAMING_OUT  = SKILL_ROOT / "references" / "naming-patterns.md"
SCAN_START  = "<!-- SCAN_SECTION_START — do not edit below this line manually -->"
SCAN_END    = "<!-- SCAN_SECTION_END -->"


def classify_name_structure(name: str) -> str:
    parts = name.lower().split("-")
    known_brands = {"vercel","microsoft","anthropic","remotion","google",
                    "github","aws","azure","openai","cloudflare"}
    if parts[0] in known_brands:
        return "brand-prefixed"
    if len(parts) == 1:
        return "portmanteau"
    verb_indicators = {"find","create","build","run","fix","review","write",
                       "check","scan","audit","design","forge","pick","ship"}
    if len(parts) == 2 and parts[0] in verb_indicators:
        return "verb-noun"
    return "domain-noun"


def render_naming_section(repos: list[dict], week: str) -> str:
    """Render the SCAN_SECTION for naming-patterns.md. Only this block auto-updates."""
    from collections import defaultdict
    struct_dna: dict = defaultdict(list)
    for repo in repos:
        slug = repo.get("name", repo.get("full_name","").split("/")[-1])
        struct_dna[classify_name_structure(slug)].append(slug)

    n = len(repos)
    rows = []
    for struct in ["domain-noun","verb-noun","brand-prefixed","portmanteau"]:
        names = struct_dna.get(struct, [])
        cnt   = len(names)
        share = f"{round(cnt/n*100)}%" if n else "0%"
        examples = ", ".join(names[:3]) if names else "—"
        rows.append(f"| {struct:<20} | {cnt:>5} | {share:>5} | {examples} |")
    table = "\n".join(rows)

    velocity_repos = sorted(repos, key=lambda r: r.get("star_velocity", 0), reverse=True)[:3]
    velocity_str = ", ".join(
        r.get("name", r.get("full_name","").split("/")[-1]) for r in velocity_repos
    ) or "n/a"

    return f"""{SCAN_START}
**Week:** {week} | **Sample:** top-{n} skills by install count

### Structure distribution (top-{n})

| Structure            | Count | Share | Examples |
|---|---|---|---|
{table}

### High-velocity names this week (fastest growing)

{velocity_str}

### Direction: what tends to produce hits

1. **Exact function, verb-first** — works when your differentiator IS the function (`find-skills`, `skill-creator`). Name the thing you do if you do ONE thing extremely well.
2. **Experience/metaphor, single word** — works when the differentiator is how it *feels* (`soultrace`, `superpowers`). Creates identity, not description.
3. **Domain-noun, clear audience** — SEO-optimized, high discovery, lower memorability (`frontend-design`, `web-design-guidelines`).
4. **Tight portmanteau / verb-as-noun** — works when the action IS the product (`skilldrop`, `dispatch`). Must pass: "let me {{name}} this skill."

Avoid names that describe an internal step the user never sees (scan-forge, readme-factory).

{SCAN_END}"""


def update_naming_patterns(repos: list[dict], dry_run: bool):
    """Replace SCAN_SECTION in naming-patterns.md. Core principles section is NEVER touched."""
    import sys
    if not NAMING_OUT.exists():
        print(f"  [warn] {NAMING_OUT} not found — skipping", file=sys.stderr)
        return
    text = NAMING_OUT.read_text(encoding="utf-8")
    s, e = text.find(SCAN_START), text.find(SCAN_END)
    if s == -1 or e == -1:
        print("  [warn] naming-patterns.md missing SCAN markers — skipping", file=sys.stderr)
        return
    new_section = render_naming_section(repos, ISO_WEEK)
    new_text = text[:s] + new_section + text[e + len(SCAN_END):]
    if dry_run:
        print("── naming SCAN_SECTION (dry run) ──")
        print(new_section[:500])
        return
    NAMING_OUT.write_text(new_text, encoding="utf-8")
    print(f"  ✓ updated SCAN_SECTION in {NAMING_OUT.name}")


def render_patterns(agg: dict, repos: list[dict]) -> str:
    def frac(count, total):
        return f"{count}/{total}"

    top_verbs_str = ", ".join(f'"{v}" ×{c}' for v, c in agg["top_verbs"]) or "n/a"
    hook_dist = agg["hook_type_dist"]
    hook_dist_str = " > ".join(
        f"{t} {frac(hook_dist[t], agg['n'])}"
        for t in sorted(hook_dist, key=lambda t: -hook_dist[t])
        if hook_dist[t] > 0
    )

    forbidden_str = (
        "\n".join(f'    "{w}" in {c}/{agg["n"]} repos' for w, c in agg["notable_forbidden"].items())
        or "    none — clean week"
    )

    sources_str = "\n".join(
        f"  - {r['full_name']} ({r.get('stargazers_count',0)} ★, {r.get('star_velocity',0)} ★/day)"
        for r in repos
    )

    return f"""## {ISO_WEEK}
generated: {GENERATED_AT}
sources: {agg['n']} repos analyzed

### Formula
hook_words:      {agg['hook_words_avg']} avg  (range {agg['hook_words_range'][0]}–{agg['hook_words_range'][1]})
hook_type:       {hook_dist_str}
install_line:    {agg['install_line_avg']} avg
readme_length:   {agg['readme_length_avg']} words avg
code_blocks:     {agg['code_blocks_avg']} avg
has_demo:        {frac(agg['has_demo_count'], agg['n'])} repos
numbers_in_hook: {frac(agg['numbers_in_first_lines_count'], agg['n'])} repos (use numbers early)

### Tone
forbidden_seen:
{forbidden_str}
active_passive:  {agg['active_passive_avg']}:1 ratio
top_opening_verbs: {top_verbs_str}

### Install convention
install_line_target: {agg['install_line_avg']}
badge_count_avg:     {agg['badge_count_avg']}
star_velocity_avg:   {agg['star_velocity_avg']} ★/day

### Sources
{sources_str}
"""


def write_patterns(content: str, dry_run: bool):
    if dry_run:
        print("── viral-patterns.md (dry run) ──────────────────────────")
        print(content)
        return
    PATTERNS_OUT.parent.mkdir(parents=True, exist_ok=True)
    PATTERNS_OUT.write_text(content, encoding="utf-8")
    print(f"  ✓ wrote {PATTERNS_OUT}")


def append_history(content: str, dry_run: bool):
    separator = "─" * 60 + "\n"
    entry = separator + content
    if dry_run:
        print("── formula-history.md append (dry run) ──────────────────")
        print(entry)
        return
    HISTORY_OUT.parent.mkdir(parents=True, exist_ok=True)
    existing = HISTORY_OUT.read_text(encoding="utf-8") if HISTORY_OUT.exists() else ""
    # avoid duplicate entry for same week
    if ISO_WEEK in existing:
        print(f"  ↷ {ISO_WEEK} already in history, skipping append")
        return
    HISTORY_OUT.write_text(entry + existing, encoding="utf-8")
    print(f"  ✓ appended to {HISTORY_OUT}")
    # Enforce max_lines from formula-history's frontmatter; archive oldest entries.
    enforce_max_lines(
        target=HISTORY_OUT,
        archive=HISTORY_ARCH,
        entry_separator=ENTRY_SEP,
        keep_frontmatter=True,
    )


def enforce_patterns_length(dry_run: bool):
    """Enforce viral-patterns.md's declared max_lines. No archive (patterns is
    a snapshot — old content has no value once overwritten)."""
    if dry_run:
        return
    enforce_max_lines(
        target=PATTERNS_OUT,
        archive=None,
        entry_separator="",  # no entry boundaries in patterns; hard cut
        keep_frontmatter=True,
    )


def update_last_scanned(dry_run: bool):
    if dry_run or not SKILL_MD.exists():
        return
    text = SKILL_MD.read_text(encoding="utf-8")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updated = re.sub(r"(last_scanned:\s*)\S+", rf"\g<1>{today}", text)
    if updated != text:
        SKILL_MD.write_text(updated, encoding="utf-8")
        print(f"  ✓ updated last_scanned to {today}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scan GitHub trending skills")
    parser.add_argument("--token",   help="GitHub personal access token")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[info] No token — using unauthenticated (60 req/hr limit)", file=sys.stderr)

    print(f"[scan] {ISO_WEEK} — fetching trending skill repos...")

    # ── collect repos ─────────────────────────────────────────────────────────
    seen: set[str] = set()
    raw_repos: list[dict] = []
    for q in SEARCH_QUERIES:
        for repo in search_repos(q, token, REPOS_PER_QUERY):
            if repo["full_name"] not in seen and repo.get("stargazers_count", 0) >= MIN_STARS:
                seen.add(repo["full_name"])
                raw_repos.append(repo)
        if len(raw_repos) >= 8:
            break

    if not raw_repos:
        print("[warn] No repos found — check network or token.", file=sys.stderr)
        sys.exit(1)

    repos = raw_repos[:8]
    print(f"  → analyzing {len(repos)} repos")

    # ── extract DNA ───────────────────────────────────────────────────────────
    repo_dnas: list[dict] = []
    for repo in repos:
        name = repo["full_name"]
        print(f"  → {name} ({repo.get('stargazers_count',0)} ★)")
        readme = fetch_readme(name, token)
        if not readme:
            continue
        hook = extract_hook(readme)
        dna = {
            "full_name":              name,
            "stars":                  repo.get("stargazers_count", 0),
            "star_velocity":          get_star_velocity(repo),
            "hook_words":             hook["words"],
            "hook_type":              hook["type"],
            "opening_verb":           hook["opening_verb"],
            "install_line":           extract_install_line(readme),
            "readme_length":          extract_readme_length(readme),
            "code_blocks":            extract_code_blocks(readme),
            "has_demo":               extract_has_demo(readme),
            "badge_count":            extract_badge_count(readme),
            "forbidden_hits":         extract_forbidden_hits(readme),
            "active_passive_ratio":   extract_active_passive_ratio(readme),
            "numbers_in_first_lines": extract_numbers_in_first_lines(readme),
        }
        # propagate star_velocity to raw repo dict for rendering
        repo["star_velocity"] = dna["star_velocity"]
        repo_dnas.append(dna)

    agg = aggregate(repo_dnas)
    content = render_patterns(agg, repos)

    write_patterns(content, args.dry_run)
    enforce_patterns_length(args.dry_run)
    append_history(content, args.dry_run)
    update_naming_patterns(repos, args.dry_run)
    update_last_scanned(args.dry_run)

    print("[scan] done.")


if __name__ == "__main__":
    main()
