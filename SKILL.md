---
name: lazy-skill-drop
description: Use when the user just finished designing a Claude skill and says "ship
  it", "/drop", "发布这个skill", "publish this", "help me ship this", "push to github",
  "我想把它开源", "write the README for my skill", "lazydrop", or otherwise wants a
  finished skill design turned into a released GitHub repo without filling out
  forms. Also triggers on "how do I get others to find my skill".
version: 3.0.0
formula_version: w2026-17
last_scanned: 2026-04-17
drift_threshold: 0.20
shift_threshold: 0.45
auto_merge_threshold: 0.65
---

# lazy-skill-drop

Discuss the idea. lazydrop handles everything else.

---

## Python invocation

Use `python3 scripts/X.py`. On Windows try `python` if `python3` fails. Do this silently.

---

## On activation — silent startup checks

Before doing anything visible, run silently:

1. Check if today > `last_scanned` + 7 days
   - If yes: run `scripts/scan.py` in the background
   - Update `last_scanned` in frontmatter after scan completes
2. Read `references/viral-patterns.md` — this is the current formula
3. Read `memory/performance-log.md` — check if recent publishes underperformed
4. **Check first-time state:**
   - Run `gh --version` — if it fails, user needs setup
   - Run `gh auth status` — if it fails, user needs auth
   - Check if `memory/performance-log.md` has any entries
   - If ANY of these indicate first-time use, DO NOT silently skip — trigger the First-time setup flow below when the user asks to publish
5. **Run self-audit (graduated response):**
   - `python3 scripts/audit_self.py --json` → parse the result
   - Read `severity` field, which is one of: `PASS` / `SOFT_WARN` / `HARD_BLOCK`
   - **PASS** (score ≥ 0.70) → continue silently. Do not narrate anything about the audit.
   - **SOFT_WARN** (0.55–0.70) → at the start of your FIRST response this session, prepend a single line: "Heads up — lazydrop's own audit scored {total_score}. {human_notes[0]} Doesn't affect your publish; I'll flag this for a later refresh." Then continue with the user's actual task normally. Do not mention it again.
   - **HARD_BLOCK** (< 0.55) → still do not block the current conversation. At the start of your first response, say plainly: "Heads up — lazydrop's own docs are failing its own audit (score {total_score}). Publishing will continue normally; I'll log the override so the next evolve cycle picks it up." Then continue with the user's task. Publishing itself is NOT gated on this — see Hard rules.

Do NOT narrate steps 1–3 and 5-when-PASS to the user. DO narrate step 4 and step 5-when-not-PASS when they're relevant.

---

## First-time setup (only runs when prerequisites are missing)

If the user hasn't published before (no gh CLI, not authenticated, or empty performance-log), walk them through this before attempting Phase D. Do it once, save nobody from having to do it twice.

Show this exact message, then wait for them to report completion before proceeding:

```
First publish on this machine — quick setup (~5 min, one time only):

1. Install gh CLI
   macOS:    brew install gh
   Windows:  winget install GitHub.cli
   Linux:    see https://cli.github.com

2. Log into the GitHub account you want to publish to:
   gh auth login
   (pick: GitHub.com → HTTPS → browser → paste the code)

3. Confirm you're logged into the right account:
   gh api user --jq .login

If the username printed by step 3 is NOT the account you want to publish to,
run: gh auth switch  (to pick a different logged-in account)
or:  gh auth login   (to add a new one)

Reply "done" when step 3 prints the correct username.
Reply "help" if any step errors.
```

After user replies "done":
- Run `gh auth status` yourself to verify
- If verified, proceed to Phase D Stage 1
- If not verified, re-show the steps that failed

Do NOT skip this setup on the grounds that "user probably knows". The cost of one unnecessary setup pass is small. The cost of a silent publish to the wrong account is bad.

---

## Phase A — Extract (silent, no form)

Read the full current conversation. Extract:

- **problem**: the specific pain this skill solves (1 sentence)
- **miss**: what existing tools miss (1 sentence, concrete)
- **result**: the concrete outcome after using this skill (1 sentence)
- **install_cmd**: any `git clone` / `cp` / `npx` command mentioned

Rules:
- Extract from the conversation — do not ask the user to repeat what they already said
- If one item is genuinely missing and can't be inferred, ask ONE question to fill it
- Never ask all four as a form or checklist
- If the user said "ship it" with no prior context, ask: "Which skill should I publish, and what does it do?"

---

## Phase R — Recon (market verdict before forging)

Read `references/recon-patterns.md`. Run 4-axis search, classify each candidate as `bucket=Direct|Adjacent|Tangential, status=Live|Dead`, assess own skill against the 5-item Moats checklist, emit verdict + `position_statement` draft.

Write `{verdict, top-3 adjacent, moats y/n/partial, position draft}` to `memory/recon-log.md`. propose.py reads this to detect category-level drift across weeks.

If verdict is `HEAD_ON_COLLISION` and Moats checklist has ≤1 Yes, surface this to the user at Phase D. Do not auto-block — user may have a valid 10x thesis.

---

## Phase N — Name (semantic naming)

Read `references/naming-patterns.md`. If the extracted skill already has a name in the conversation, skip — use that name.

Otherwise, generate 3 candidates using the 6 semantic structures, pick one by the pre-ship checklist. The chosen name becomes the repo slug in Phase E.

---

## Phase C — Position (one sentence, the backbone)

**This sentence is the skeleton. Everything written in Phase B traces back to it.**

Using the Recon verdict and top-3 adjacent tools from `memory/recon-log.md`, forge one positioning sentence. Template by verdict:

```
CROWDED_BUT_DIFFERENTIABLE:
  "{adj1} and {adj2} do [A] but assume [B]. This one does [B] directly."
  "{adj1} lets you [X] but skips [Y]. {adj2} does [Y] but requires [Z]. This does both."

EMERGING:
  "Built for [wedge] — the part of [category] no existing skill handles yet."

UNCLAIMED:
  "[Problem] has no dedicated skill. This is the first one built around [specific constraint]."

SATURATED:
  "Every [category] skill does [A]. This one does [A] and [specific differentiator] in one pass."
```

Rules for the sentence:
- Name the top 1-2 competitors explicitly — vague "other tools" is weaker
- Name their specific limitation, not just "they don't do X"
- The sentence must fit in one breath — if it needs a semicolon to survive, it's two sentences
- Do NOT fabricate competitor limitations. If you can't name a real one, use the UNCLAIMED template instead

Show the sentence to the user as:

```
Positioning: "{sentence}"

This is the backbone — README hook, SKILL.md description, and bullet copy
will all be written to support this claim. Change it now if it's wrong.
```

Then ask: **"Positioning locked? (y / change it)"**

- `y` → proceed to Phase B with this sentence as anchor
- change → rewrite and ask again
- If verdict is `HEAD_ON_COLLISION` with ≤1 moat: surface the collision before asking.

---

## Phase B — Forge (apply current formula)

Read `references/viral-patterns.md` + `references/readme-rules.md` (B1) and `references/skill-md-rules.md` (B2).

**The Phase C positioning sentence is the first constraint.** Hook, bullets, and SKILL.md description must all support it. If a bullet contradicts or ignores the positioning, cut it.

### B1 — Forge README.md

Build per current week's viral formula. Place positioning sentence as the first prose line after the 4-bullet summary (or as the hook if it fits the word count).

### B2 — Forge SKILL.md

Write description field to trigger on the same user pain the positioning names. Do not summarize the mechanism — trigger on the symptom.

---

## Phase P — Polish (anti-AI two-pass)

Read `references/anti-ai-patterns.md` for the current forbidden word list.

**Pass 1 — structural:**
- Delete section headers named: Overview, Introduction, Features, Getting Started
- Bullet list >4 items → convert to 2 sentences of prose (unless it's a rules-directory skill)
- Delete sentences starting with "This skill"
- Delete "whether you're X or Y" constructions

**Pass 2 — language:**
- Replace Tier 1 forbidden words with specific numbers or examples
- Every adjective claim must have a number or example backing it
- Check first line: must start with a verb or be a question

**Self-check:**
```
✓ Positioning sentence survives intact into final README
✓ Hook is ≤16 words, verb-first
✓ Install command on line 2-3
✓ No Tier 1 forbidden words
✓ Word count 350–450
```

---

## Phase D — Confirm (ONE stage, content only)

Publishing has exactly one gate: the user approves the content. Target account, repo creation, and awesome-list PRs all run automatically after that gate passes.

### Stage 1 — content confirm

Show the user, in order:

1. The README draft (full text, not folded)
2. The SKILL.md draft (full text, not folded)
3. Proposed repo name (default: skill's `name` field from frontmatter)
4. A target summary line: `Will publish to github.com/{username}/{repo} and auto-submit PRs to 3 awesome lists as {username}.`
   (Resolve `{username}` with `gh api user --jq .login` before showing. If auth fails, trigger First-time setup and come back.)

Then ask exactly: **"Content looks good? (y / tell me what to change)"**

- If user says `y` / `yes` / `go` / `ok` → proceed to Phase E (fully automatic)
- If user says "change X" → apply the change, re-show Stage 1 from the top
- Never skip Stage 1. Silence is not consent.

Claude MUST resolve and show the target username in step 4. That is the one piece of information the user loses by removing Stage 2 — surface it once here so a wrong account is still catchable before `y`.

---

## Phase E — Publish (fully automatic)

Once Stage 1 passes, invoke publish.py with `--yes` and let it run end-to-end. No further user input.

```bash
python3 scripts/publish.py \
  --name "{skill_name}" \
  --hook "{hook_line}" \
  --install "{install_cmd}" \
  --skill-dir "{path_to_skill}" \
  --yes
```

`publish.py` performs, non-interactively:

1. `gh auth status` check (fail fast if broken — then tell user to rerun First-time setup)
2. Privacy scan (blocks on secrets / personal paths / emails)
3. `gh repo create` + topics
4. `git init / commit / push`
5. **Auto-submit PRs** to each of the 3 awesome lists: `gh repo fork` → clone → insert entry under the target section → push branch → `gh pr create`. Per-list failures do NOT abort — they are logged and reported at the end.
6. Append to `memory/performance-log.md`

When it returns, show the user:

1. The GitHub repo URL (clickable)
2. One line per awesome list: either the PR URL or "failed — see memory/pr-bodies.md to submit manually"
3. The performance-log entry

If any awesome-list PR failed, surface that clearly — do not pretend all three went through. The saved `memory/pr-bodies.md` is the fallback so the user can paste the entry into a browser PR if needed.

---

## Hard rules for publishing

These rules protect the one remaining gate: the user must see and approve the content (including which account it goes to) before anything is created.

- **Never call `publish.py` before Stage 1 content confirm has passed.** Stage 1 is "did the user approve the text + target account". It is the only gate.
- **Always pass `--yes` to `publish.py`.** The whole point of v3 is that publish.py runs end-to-end without human input once Stage 1 passes.
- **Always show the target account in Stage 1's step 4.** Resolve `gh api user --jq .login` before asking "Content looks good?". Removing Stage 2 means the user's last chance to catch a wrong account is here — don't skip it.
- **Never treat silence, "ok", "sure", or "looks fine" as Stage 1 consent.** Only literal `y` / `yes` / `go` / `ok` from the user's most recent message counts. If uncertain, ask again.
- **Never auto-proceed on a timer.** There is no "if no response in N seconds, continue". Stage 1 waits indefinitely.
- **Async is fine after Stage 1.** Once the user has approved content, publish.py is safe to run in the background / async — the stdin interaction no longer exists.
- **Self-audit does not gate publishing.** `audit_self.py` still runs on activation for telemetry:
  - `severity: PASS` → proceed silently.
  - `severity: SOFT_WARN` → proceed; add one line when showing Stage 1: "FYI lazydrop's own audit is at {score}; worth refreshing later."
  - `severity: HARD_BLOCK` → proceed; add one line when showing Stage 1: "Note: lazydrop's own docs are failing its own audit ({score}) — publish will continue and log the override for next evolve cycle."
  - In all non-PASS cases, after publish completes, append an `audit-overridden: true` line to `memory/performance-log.md` for the evolve workflow to pick up.

---

## Manual evolution commands

```
/lazy-skill-drop:scan     → run scripts/scan.py now (force refresh)
/lazy-skill-drop:status   → show current formula_version + drift score
/lazy-skill-drop:evolve   → run full scan → delta → propose cycle
/lazy-skill-drop:audit    → run scripts/audit_self.py, show scorecard
/lazy-skill-drop:rollback → revert to last known good formula
```

---

## Rule precedence (when conflicts arise)

When rules from different reference files conflict, resolve top-down:

| # | Rule source | Weight |
|---|---|---|
| 1 | `viral-patterns.md` (structural formula: hook, install, length) | Highest |
| 2 | `naming-patterns.md` | High |
| 3 | `extract-patterns.md` (Phase A required fields) | High |
| 4 | `recon-patterns.md` (verdict → strategy mapping) | High |
| 5 | Phase C positioning sentence (backbone constraint for Phase B) | High |
| 6 | `anti-ai-patterns.md` Tier 1 (hard red flags) | Medium |
| 7 | `anti-ai-patterns.md` Tier 2/3 (soft signals) | Low |
| 8 | Rhythm / burstiness checks | Lowest |

**In plain terms:** match the current viral formula first. Anti-AI patterns
are filters to run *after* the structure is right, not constraints that
block you from writing an on-formula README. A README that hits the viral
formula with one Tier 2 word is better than a clean-of-AI-words README that
misses the structural target.

When a user-supplied hook / name / description already exists, their words
win over all rules above.

---

## Two-document rule

Every skill generates two files with different rule sets:

| File | Reader | Governing rules |
|------|--------|-----------------|
| `SKILL.md` | Claude | `references/skill-md-rules.md` |
| `README.md` | humans | `references/readme-rules.md` + `references/viral-patterns.md` |

Rules derived from Anthropic skill-creator SKILL.md and obra/superpowers.

### Phase B splits into B1 + B2

Both are anchored to the Phase C positioning sentence.

- Phase B1 → Forge README.md. Read `viral-patterns.md` + `readme-rules.md`. Positioning sentence goes in first prose line after 4-bullet summary.
- Phase B2 → Forge SKILL.md. Read `skill-md-rules.md`. Description triggers on the pain the positioning names.

---

## Reference files

All reference files are AI-operational: rules only, no citations, no methodology. Max 80 lines each.

| File | When Claude reads it |
|------|-------------|
| `references/viral-patterns.md` | Phase B1 (Forge README) — always |
| `references/readme-rules.md` | Phase B1 (Forge README) — always |
| `references/skill-md-rules.md` | Phase B2 (Forge SKILL.md) — always |
| `references/anti-ai-patterns.md` | Phase P (Polish) — always |
| `references/naming-patterns.md` | Phase N (Name) — when naming a new skill |
| `references/recon-patterns.md` | Phase R (Recon) — before Phase C |
| `references/extract-patterns.md` | Phase A (Extract) — always |
| `references/formula-history.md` | Phase B when predicting trend |
| `memory/performance-log.md` | On activation (startup) |
| `memory/recon-log.md` | Phase C (Position) — read to pull verdict + top adjacent |
| `memory/evolution-log.md` | Only when debugging evolution |
| `memory/pr-bodies.md` | Only when user asks to see PR text |

### Token budget

Default activation (SKILL.md + all references) targets ≤7000 tokens. If exceeded, `audit_self.py` fails the `token_budget` dimension.

---

## Description field rule

**Description = When to Use, NOT What the Skill Does.**

### Do

- Start with "Use when..."
- List triggering conditions and symptoms.
- Include phrases the user would actually say.
- Keep under 120 words.

### Don't

- Start with "I can help you..." (first person).
- Summarize workflow or steps.
- Describe internals or mechanism.
- Pack description with every function verb.

### Enforcement

`audit_self.py` `description_triggers` dimension detects workflow-summary verbs and fails the skill. Override only via explicit `override audit` phrase.

## Source

Description rule derived from obra/superpowers writing-skills SKILL.md.
