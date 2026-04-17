#!/usr/bin/env python3
"""
publish.py — Publisher for lazy-skill-drop (v3, fully automatic after Stage 1)

Flow:
  [0/6] Auth check        — verify gh CLI installed AND authenticated
  [1/6] Privacy scan      — block if secrets/paths/emails found
  [2/6] Create GitHub repo
  [3/6] Push files
  [4/6] Auto-submit PRs to 3 awesome lists (fork → edit → push → gh pr create)
  [5/6] Log publish

Usage:
    python publish.py --name my-skill --hook "Stop writing X from scratch." --yes
    python publish.py --name my-skill --hook "..." --dry-run

Flags:
    --dry-run    simulate everything, write nothing
    --yes        no-op kept for backwards compatibility; v3 is always non-interactive
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import json
from datetime import datetime, timezone
from pathlib import Path

# ── Cross-platform output markers ─────────────────────────────────────────────
# Windows cmd.exe with legacy code page doesn't render ✓ ✗ ─ …
# Fall back to ASCII when stdout encoding isn't UTF-8.
_UNICODE_OK = "utf" in (sys.stdout.encoding or "").lower()
OK_MARK   = "✓" if _UNICODE_OK else "[+]"
FAIL_MARK = "✗" if _UNICODE_OK else "[!]"
RULE      = ("─" if _UNICODE_OK else "-") * 56
ELLIPSIS  = "…" if _UNICODE_OK else "..."

SKILL_ROOT = Path(__file__).parent.parent
PERF_LOG   = SKILL_ROOT / "memory" / "performance-log.md"

AWESOME_LISTS = [
    {
        "repo":    "BehiSecc/awesome-claude-skills",
        "url":     "https://github.com/BehiSecc/awesome-claude-skills",
        "section": "🛠 Development & Code Tools",
    },
    {
        "repo":    "VoltAgent/awesome-agent-skills",
        "url":     "https://github.com/VoltAgent/awesome-agent-skills",
        "section": "Community Skills",
    },
    {
        "repo":    "travisvn/awesome-claude-skills",
        "url":     "https://github.com/travisvn/awesome-claude-skills",
        "section": "Skills",
    },
]

TOPICS = ["claude-skill", "skill", "agent-skill", "claude-code", "lazydrop", "lazy-skill-drop"]


# ── privacy scanner (unchanged from v1) ───────────────────────────────────────

PRIVACY_PATTERNS = [
    (r"[A-Za-z0-9]{40}",               "GitHub token (40-char string)"),
    (r"sk-[a-zA-Z0-9]{32,}",           "OpenAI API key"),
    (r"ANTHROPIC_API_KEY\s*=\s*\S+",   "Anthropic API key"),
    (r"ghp_[A-Za-z0-9]{36}",           "GitHub personal access token"),
    (r"/Users/[A-Za-z0-9_.-]+/",       "macOS personal path"),
    (r"/home/[A-Za-z0-9_.-]+/",        "Linux personal path"),
    (r"[Cc]:[/\\]Users[/\\][A-Za-z0-9_.-]+[/\\]",  "Windows personal path"),
    (r"-----BEGIN .{1,20} PRIVATE KEY", "Private key"),
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "Email address"),
]

SAFE_EXCEPTIONS = [
    r"example\.com",
    r"user@",
    r"your-",
    r"<your",
    r"YOUR_",
]


def is_safe_match(text: str, start: int, end: int) -> bool:
    context = text[max(0, start-20):end+20].lower()
    return any(re.search(exc, context) for exc in SAFE_EXCEPTIONS)


def scan_file(path: Path) -> list[dict]:
    issues = []
    if not path.exists() or not path.is_file():
        return issues
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return issues
    for pattern, label in PRIVACY_PATTERNS:
        for m in re.finditer(pattern, text):
            if not is_safe_match(text, m.start(), m.end()):
                line_no = text[:m.start()].count("\n") + 1
                issues.append({
                    "file":    str(path),
                    "line":    line_no,
                    "label":   label,
                    "snippet": m.group()[:40],
                })
    return issues


def scan_directory(skill_dir: Path) -> list[dict]:
    issues = []
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "scripts"}
    scan_exts  = {".md", ".txt", ".yaml", ".yml", ".json", ".env", ".toml", ".ini", ".cfg"}
    for item in skill_dir.rglob("*"):
        if any(part in skip_dirs for part in item.parts):
            continue
        if item.is_file() and item.suffix in scan_exts:
            issues.extend(scan_file(item))
    return issues


# ── gh CLI helpers ────────────────────────────────────────────────────────────

def run(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def gh_available() -> bool:
    try:
        code, _, _ = run(["gh", "--version"])
        return code == 0
    except FileNotFoundError:
        return False


def git_available() -> bool:
    try:
        code, _, _ = run(["git", "--version"])
        return code == 0
    except FileNotFoundError:
        return False


def check_gh_auth() -> tuple[bool, str]:
    """Return (True, username) if authenticated, else (False, error_message)."""
    if not gh_available():
        return False, "gh CLI not installed. Install from https://cli.github.com"
    code, _, _ = run(["gh", "auth", "status"])
    if code != 0:
        return False, "gh not authenticated. Run: gh auth login"
    code, user, _ = run(["gh", "api", "user", "--jq", ".login"])
    if code != 0 or not user:
        return False, "Could not fetch username from gh"
    return True, user


# ── README generator ──────────────────────────────────────────────────────────

def generate_readme(name: str, hook: str, install_cmd: str,
                    description: str, week_formula: str) -> str:
    return f"""# {name}

{hook}

## Install

```bash
{install_cmd}
```

## Usage

{description}

## Why different

Generated with [lazy-skill-drop](https://github.com/lazy-skill-drop/lazy-skill-drop) using {week_formula} formula.

---
_Works with Claude Code, Cursor, Codex, Gemini CLI, and any agent that supports the [Agent Skills](https://agentskills.io) format._
"""


# ── awesome list PR body (unchanged) ──────────────────────────────────────────

def generate_pr_body(skill_name: str, hook: str, repo_url: str,
                     install_cmd: str, target: dict) -> str:
    desc_words = hook.rstrip(".!?").split()
    if len(desc_words) > 3:
        desc = " ".join(desc_words).lower().capitalize()
    else:
        desc = hook.rstrip(".!?")
    entry_line = f"- [{skill_name}]({repo_url}) — {desc}"
    return f"""## Add {skill_name} to {target['repo']}

Hi! I'd like to add my skill to the list.

**Entry to add** (in section `{target['section']}`):

```markdown
{entry_line}
```

**Checklist:**
- [x] Skill has a SKILL.md with name + description frontmatter
- [x] Install command is one line: `{install_cmd[:80]}`
- [x] Repo is public and MIT licensed
- [x] README follows current viral formula

Thanks for maintaining this list!
"""


# ── automatic awesome-list PR submission ──────────────────────────────────────

def _find_section_insert_index(lines: list[str], section: str) -> int | None:
    """
    Find the line index at which to insert a new entry for a given section.
    Returns the index where the new line should be inserted, or None if the
    section heading can't be found.

    Strategy: locate the heading line (any `#`-prefixed line whose stripped
    text equals `section`), then place the new entry at the end of that
    section's list (just before the next heading or EOF).
    """
    target_idx = None
    section_norm = section.strip()
    for i, ln in enumerate(lines):
        stripped = ln.lstrip("#").strip()
        if not ln.lstrip().startswith("#"):
            continue
        if stripped == section_norm:
            target_idx = i
            break
    if target_idx is None:
        return None

    heading_level = len(lines[target_idx]) - len(lines[target_idx].lstrip("#"))

    # Walk forward to the next heading of same-or-higher level (i.e. same or fewer #'s)
    end = target_idx + 1
    while end < len(lines):
        ln = lines[end]
        if ln.lstrip().startswith("#"):
            level = len(ln) - len(ln.lstrip("#"))
            if level <= heading_level:
                break
        end += 1

    # Trim trailing blank lines within the section
    while end > target_idx + 1 and lines[end - 1].strip() == "":
        end -= 1
    return end


def auto_submit_pr(target: dict, skill_name: str, repo_url: str, hook: str,
                   install_cmd: str, username: str, dry_run: bool) -> tuple[bool, str]:
    """
    Fork the awesome list, add the skill entry under the target section,
    push a branch, and open a PR — all non-interactively.

    Returns (ok, detail). On success detail is the PR URL. On failure detail
    is a short error string for logging. Never raises on PR-submission failure;
    the caller is expected to surface the failure and fall back to pr-bodies.md.
    """
    awesome_repo = target["repo"]           # "owner/repo"
    section      = target["section"]
    fork_name    = awesome_repo.split("/", 1)[1]
    branch       = f"add-{skill_name}"

    desc_words = hook.rstrip(".!?").split()
    desc       = " ".join(desc_words).lower().capitalize() if len(desc_words) > 3 else hook.rstrip(".!?")
    entry_line = f"- [{skill_name}]({repo_url}) — {desc}"

    if dry_run:
        return True, f"[dry-run] would fork {awesome_repo} and open PR"

    # 1. Fork. `gh repo fork` is idempotent — succeeds even if the fork exists.
    code, _, err = run(["gh", "repo", "fork", awesome_repo,
                        "--clone=false", "--remote=false"])
    if code != 0 and "already exists" not in err.lower():
        return False, f"fork failed: {err[:120]}"

    # 2. Clone the fork into a temp dir (shallow).
    tmp = Path(tempfile.mkdtemp(prefix="lazy-awesome-"))
    fork_clone_url = f"https://github.com/{username}/{fork_name}.git"
    code, _, err = run(["git", "clone", "--depth=1", fork_clone_url, str(tmp)])
    if code != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        return False, f"clone failed: {err[:120]}"

    try:
        # 3. Edit README.md — locate section, append entry at end of that list.
        readme_path = tmp / "README.md"
        if not readme_path.exists():
            return False, "fork has no README.md"

        text  = readme_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        insert_at = _find_section_insert_index(lines, section)
        if insert_at is None:
            return False, f"section '{section}' not found in README"

        lines.insert(insert_at, entry_line)
        readme_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                               encoding="utf-8")

        # 4. Branch + commit + push.
        for cmd in (
            ["git", "-C", str(tmp), "checkout", "-b", branch],
            ["git", "-C", str(tmp), "add", "README.md"],
            ["git", "-C", str(tmp), "commit", "-m", f"Add {skill_name}"],
        ):
            code, _, err = run(cmd)
            if code != 0:
                return False, f"{cmd[3]} failed: {err[:120]}"
        code, _, err = run(["git", "-C", str(tmp), "push", "-u", "origin", branch])
        if code != 0:
            return False, f"push failed: {err[:120]}"

        # 5. Open PR against upstream.
        pr_body = generate_pr_body(skill_name, hook, repo_url, install_cmd, target)
        code, out, err = run([
            "gh", "pr", "create",
            "--repo", awesome_repo,
            "--title", f"Add {skill_name}",
            "--body", pr_body,
            "--head", f"{username}:{branch}",
        ])
        if code != 0:
            return False, f"pr create failed: {err[:120]}"

        pr_url = out.strip().splitlines()[-1] if out.strip() else f"opened on {awesome_repo}"
        return True, pr_url

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── performance log (unchanged) ───────────────────────────────────────────────

def log_publish(skill_name: str, repo_url: str, week_formula: str, dry_run: bool):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"{ts} | {skill_name} | {week_formula} | {repo_url} | tracking...\n"
    if dry_run:
        print(f"  [perf-log dry-run] would append: {entry.strip()}")
        return
    PERF_LOG.parent.mkdir(parents=True, exist_ok=True)
    existing = PERF_LOG.read_text(encoding="utf-8") if PERF_LOG.exists() else "# Performance Log\n\n"
    PERF_LOG.write_text(existing + entry, encoding="utf-8")
    print(f"  {OK_MARK} logged to {PERF_LOG}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Publish a skill to GitHub")
    parser.add_argument("--name",      required=True, help="Skill repo name (e.g. my-skill)")
    parser.add_argument("--hook",      required=True, help="One-line hook sentence")
    parser.add_argument("--install",   default="git clone https://github.com/YOU/SKILL.git ~/.claude/skills/SKILL",
                        help="Install command")
    parser.add_argument("--desc",      default="", help="Usage description")
    parser.add_argument("--skill-dir", default=".", help="Path to skill directory to publish")
    parser.add_argument("--dry-run",   action="store_true")
    parser.add_argument("--yes",       action="store_true",
                        help="No-op in v3 (kept for backwards compatibility). "
                             "v3 is always non-interactive.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    week      = datetime.now(timezone.utc).strftime("w%Y-%V")
    repo_name = args.name

    print(f"[publish] {args.name}")
    print(f"  hook:    {args.hook}")
    print(f"  dir:     {skill_dir}")

    # ── Step 0: Auth check ────────────────────────────────────────────────────
    print("\n[0/6] Auth check...")
    if args.dry_run:
        username = "you"
        print(f"  [dry-run] would authenticate as current gh user")
    else:
        ok, info = check_gh_auth()
        if not ok:
            print(f"  {FAIL_MARK} {info}", file=sys.stderr)
            print(f"\n  Fix the auth issue above, then rerun.", file=sys.stderr)
            sys.exit(1)
        username = info
        print(f"  {OK_MARK} Authenticated as {username}")

    # v3: target was confirmed upstream by Claude in Stage 1 (the SKILL.md flow
    # surfaces the gh username in the content confirm). No stdin prompt here.
    repo_url = f"https://github.com/{username}/{repo_name}"

    # ── Step 1: Privacy scan ──────────────────────────────────────────────────
    print("\n[1/6] Privacy scan...")
    issues = scan_directory(skill_dir)
    if issues:
        print(f"\n  BLOCKED — {len(issues)} issue(s) found:\n")
        for issue in issues:
            print(f"  {FAIL_MARK} {issue['label']}")
            print(f"    file: {issue['file']}:{issue['line']}")
            print(f"    snippet: {issue['snippet']!r}\n")
        print("  Fix the above before publishing.")
        sys.exit(1)
    print(f"  {OK_MARK} No sensitive data found")

    # ── Step 2: Create GitHub repo ────────────────────────────────────────────
    print("\n[2/6] Create GitHub repo...")
    if not gh_available() or not git_available():
        print("  [warn] gh or git not available — skipping repo creation")
    elif args.dry_run:
        print(f"  [dry-run] would create {repo_url}")
    else:
        code, out, err = run([
            "gh", "repo", "create", repo_name,
            "--public",
            "--description", args.hook,
            "--confirm",
        ])
        if code != 0:
            print(f"  {FAIL_MARK} repo create failed: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"  {OK_MARK} created {repo_url}")
        run(["gh", "repo", "edit", repo_name,
             "--add-topic", TOPICS[0],
             "--add-topic", TOPICS[1],
             "--add-topic", TOPICS[2]])
        print(f"  {OK_MARK} topics set: {', '.join(TOPICS[:3])}")

    # ── Step 3: Generate README and push ──────────────────────────────────────
    print("\n[3/6] Push files...")
    install_cmd = args.install.replace("YOU", username)

    if not args.dry_run:
        readme_path = skill_dir / "README.md"
        if not readme_path.exists():
            readme_content = generate_readme(
                repo_name, args.hook, install_cmd, args.desc or "See SKILL.md.", week
            )
            readme_path.write_text(readme_content, encoding="utf-8")
            print(f"  {OK_MARK} generated README.md")

        run(["git", "-C", str(skill_dir), "init"])
        run(["git", "-C", str(skill_dir), "add", "."])
        run(["git", "-C", str(skill_dir), "commit", "-m", f"Initial drop: {args.hook}"])
        run(["git", "-C", str(skill_dir), "branch", "-M", "main"])
        run(["git", "-C", str(skill_dir), "remote", "add", "origin", f"{repo_url}.git"])
        code, _, err = run(["git", "-C", str(skill_dir), "push", "-u", "origin", "main"])
        if code == 0:
            print(f"  {OK_MARK} pushed to {repo_url}")
        else:
            print(f"  {FAIL_MARK} push failed: {err}", file=sys.stderr)
    else:
        print(f"  [dry-run] would push {skill_dir} → {repo_url}")

    # ── Step 4: Auto-submit PRs to awesome lists ──────────────────────────────
    print("\n[4/6] Auto-submit awesome-list PRs...")

    # Always save the fallback bodies first — if any auto-submit fails, the
    # user has something to paste into a browser.
    if not args.dry_run:
        pr_bodies_path = SKILL_ROOT / "memory" / "pr-bodies.md"
        pr_bodies_path.parent.mkdir(parents=True, exist_ok=True)
        content = f"# Awesome list PRs — {repo_name} ({week})\n\n"
        for target in AWESOME_LISTS:
            content += f"## {target['repo']}\n\n"
            content += generate_pr_body(repo_name, args.hook, repo_url, install_cmd, target)
            content += "\n---\n\n"
        pr_bodies_path.write_text(content, encoding="utf-8")
        print(f"  {OK_MARK} fallback bodies saved to {pr_bodies_path}")

    pr_results = []  # [(repo, ok, detail)]
    for target in AWESOME_LISTS:
        ok, detail = auto_submit_pr(target, repo_name, repo_url, args.hook,
                                     install_cmd, username, args.dry_run)
        pr_results.append((target["repo"], ok, detail))
        if ok:
            print(f"  {OK_MARK} {target['repo']}: {detail}")
        else:
            print(f"  {FAIL_MARK} {target['repo']}: {detail}")
            print(f"       fallback: paste entry from memory/pr-bodies.md at {target['url']}")

    # ── Step 5: Log ───────────────────────────────────────────────────────────
    print("\n[5/6] Log publish...")
    log_publish(repo_name, repo_url, week, args.dry_run)

    ok_count   = sum(1 for _, ok, _ in pr_results if ok)
    fail_count = len(pr_results) - ok_count

    print(f"\n[publish] done.")
    print(f"  repo: {repo_url}")
    print(f"  PRs:  {ok_count}/{len(pr_results)} submitted automatically"
          + (f", {fail_count} need manual submit (memory/pr-bodies.md)" if fail_count else ""))


if __name__ == "__main__":
    main()
