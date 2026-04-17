# CHANGELOG — two-stage publish confirmation

## Why this change

The original `lazy-skill-drop` had a real safety gap:

- Phase D asked the user "Ready to drop?" (content review)
- But `publish.py` then immediately ran `gh repo create` using whichever gh account happened to be currently authenticated
- The user never saw "you're about to publish to `github.com/<which-account>/<repo>`"

For people with multiple gh accounts (personal + company + bot), one wrong "y" pushes a side project into the wrong org. That's the bug this patch closes.

The same issue existed in `pick-design-md` Phase 3: "Install DESIGN.md?" didn't show the cwd the file would land in.

## Changes

### lazy-skill-drop

**`scripts/publish.py`** (replaces original)

- Added `check_gh_auth()` — fails fast if gh CLI not installed or not logged in. Previously `gh_available()` only checked install, not auth.
- Added `confirm_target(username, repo_name, hook, topics)` — prints a publish-target card and blocks on interactive input. Supports four replies: `y` / `switch` / `rename` / `cancel`. Rename recurses with the new name.
- Renumbered steps to `[0/6] Auth → [0.5] Target confirm → [1/6] Privacy scan → [2/6] Create repo → …`
- Added `--yes` flag for scripted use, with a docstring warning: "DO NOT use when invoked by Claude."
- Replaced `get_gh_username()` with `check_gh_auth()`, which does the same thing but also validates auth status.
- Minor: graceful `EOFError`/`KeyboardInterrupt` handling on input() so Ctrl-C doesn't leave the terminal in a weird state.

**`SKILL.md`** (replaces original)

- Phase D split into Stage 1 (content) and Stage 2 (target). Stage 2 explicitly delegates to publish.py's own confirmation.
- Added a dedicated "Hard rules for publishing" section. The rules that matter:
  - Never pass `--yes` to publish.py
  - Never answer publish.py's interactive prompts on behalf of the user
  - Silence is not consent
  - No timer-based auto-proceed
  - If user isn't there to type, stop and tell them to run publish.py themselves

### pick-design-md

**`SKILL.md`** (updated in place)

- Phase 3 now computes `cwd` and shows the absolute install path in the confirmation prompt:
  ```
  Install {brand} design system?
    → writes:  /Users/&lt;you&gt;/projects/my-app/DESIGN.md
    → size:    ~4 KB
    → command: cp ~/.claude/skills/awesome-design-md/references/vercel.md ./DESIGN.md
    → will not modify any other file in your project

  Confirm? (y / show me the DESIGN.md first / pick another / cancel)
  ```
- Added two new hard rules:
  - Always show the absolute install path — never let cwd be implicit
  - Never treat silence, "ok", or "sure" as consent

## What did NOT change

- `delta.py`, `propose.py`, `scan.py` — untouched
- `evolve.yml` — untouched (the over-permissioned GITHUB_TOKEN concern from earlier is a separate, lower-priority issue; can fix in a later patch)
- `pick-design-md/scripts/scan_project.py` — untouched (read-only, no write path)
- `references/brands-manifest.json` — untouched

## v2.1 addendum — audit_self.py + self-audit gate

After shipping v2, an audit of lazy-skill-drop's own README and SKILL.md against its own formula revealed that lazydrop was failing the rules it enforces on others. Specifically:

- Original description contained a workflow summary ("Reads the conversation, extracts..., researches..., writes..., publishes...") — the exact anti-pattern obra/superpowers documented would cause Claude to skip the skill body and follow the description instead.
- Original README had install command duplicated at line 6 and line 78.
- README word count was ~370, 50% over formula target of 247.

Same issue was found in pick-design-md: description had `installs, reads, renders, shows` workflow verbs.

### Added

**`scripts/audit_self.py`**

Scores own README and SKILL.md on 8 dimensions (hook quality, install position, word count, forbidden words, description length, description triggers, banned headers, burstiness). Weighted sum; passes at ≥ 0.70.

Key dimension: `description_triggers` catches workflow-summary verbs leaking into the SKILL.md description, which is the exact trap lazy-skill-drop originally fell into.

Three usage modes:
- `audit_self.py` → print human-readable scorecard
- `audit_self.py --json` → machine-readable, for CI
- `audit_self.py --gate` → exit non-zero if below threshold

Can also audit any other README/SKILL.md pair:
- `audit_self.py --readme path/to/README.md --skill-md path/to/SKILL.md`

### Changed

**`SKILL.md`**
- `On activation` step 5 added: run self-audit on activation, mark internal state but do not block
- New hard rule: publish.py is gated on audit_self.py passing. If the tool can't keep its own README compliant with the current formula, it refuses to ship other people's skills. Dogfooding enforced mechanically.
- New manual command: `/lazy-skill-drop:audit`

### Before / after audit scores

- lazy-skill-drop v2 original: ~0.60 estimated, FAIL (description_triggers 0.20, word_count poor, burstiness poor)
- lazy-skill-drop v2 polished: **0.971 PASS** (all 8 dimensions green)
- pick-design-md original: 0.826 PASS but description_triggers 0.20 (workflow verbs leak)
- pick-design-md polished: **0.986 PASS** (all 8 dimensions green)

Both fixes were found by running audit_self.py, not by human review. The value of the tool is that it catches regressions the author's own eyes miss.

## How to apply

### For lazy-skill-drop
1. Replace `scripts/publish.py` with this v2 file
2. Replace `SKILL.md` with this v2 file
3. No data migration needed. Existing `memory/*.md` and `references/*.md` keep working.
4. Test with: `python scripts/publish.py --name test-skill --hook "test" --dry-run`

### For pick-design-md
Already applied in `/mnt/user-data/outputs/pick-design-md/SKILL.md`. Re-download the zip to pick up the change.

## Testing checklist before publishing anything real

- [ ] `gh auth status` shows the expected account
- [ ] Run publish.py with `--dry-run` first, read the target card
- [ ] If the account shown is wrong, pick `switch` and log in to the right one
- [ ] If the repo name looks bad, pick `rename`
- [ ] Only type `y` when both account AND repo name are correct
