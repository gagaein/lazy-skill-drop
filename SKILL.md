---
name: lazy-skill-drop
description: Use when the user wants help bringing a new Claude skill to life — says
  "I want to build a skill that [does X]", "我想开发一个 [X] 技能", "I want to develop
  a [name] skill", "我想做一个能 [X] 的 skill", "帮我设计一个 skill", "I'm building a
  skill for [purpose]", "/lazydrop", or otherwise wants competitor recon, a
  differentiated design, viral-formula docs, and one-confirm GitHub release. Also
  triggers (back-compat) on "ship it" / "发布这个 skill" / "publish this" / "push to
  github" / "我想把它开源" when the user has finished designing in the conversation
  and just wants the release pipeline.
version: 4.0.0
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

If `gh auth status` already passes and `gh api user --jq .login` returns the correct account, skip this setup entirely and proceed to Phase D.

---

## Phase A — Capture intent (two stages, silent, no forms)

The trigger can be either of two patterns. Phase A behaves differently per pattern:

**Pattern 1 — "I want to build" (primary, idea-stage)**
Examples: `I want to build a skill that [does X]`, `我想开发一个 [X] 技能`, `I want to develop a [name] skill`, `帮我设计一个 skill`.

Run Phase A in **two stages**:

- **A1 — light intent capture (before Phase R):** extract just `problem` (1 sentence: who, what pain). If the user only named the skill ("I want to build a doodle parser") without a problem, ask ONE question: "What's the core problem this skill solves?" Then proceed to Phase R immediately — don't continue extracting.
- **A2 — detail extract (after Phase R):** with the recon verdict in hand, return and extract `mechanism` / `result` / `miss` / `install_cmd` from the conversation. Ask at most one question per genuinely-missing field; never ask all four as a form.

**Pattern 2 — "ship it" (back-compat, finished-stage)**
Examples: `ship it`, `发布这个 skill`, `publish this`, `push to github`, `我想把它开源`.

The user has already designed the skill earlier in this conversation. Run Phase A in **one pass** — extract all five fields from prior context. If a required field is genuinely missing, ask ONE question per field. Never ask all five as a form. Proceed to Phase R after extract; Recon is still required.

**Field map (both patterns):**

- **problem**: the specific pain this skill solves (1 sentence) → feeds Phase C + README hook
- **mechanism**: what the skill does internally (1 sentence) → feeds Phase B2 workflow section
- **result**: the concrete outcome after using this skill (1 sentence) → feeds README bullets
- **miss**: what existing tools miss (1 sentence) → optional if Phase R surfaces it; only extract if user explicitly stated it
- **install_cmd**: any `git clone` / `cp` / `npx` command mentioned → feeds README line 2

**Common rule:** never ask the user to repeat what they already said; mine the conversation first.

---

## Phase R — Recon (market verdict + Go/No-Go before forging)

Read `references/recon-patterns.md`. Run 4-axis search, classify each candidate as `bucket=Direct|Adjacent|Tangential, status=Live|Dead`, assess own skill against the 5-item Moats checklist, emit verdict + `position_statement` draft.

Write `{verdict, top-3 adjacent, moats y/n/partial, position draft}` to `memory/recon-log.md`. propose.py reads this to detect category-level drift across weeks.

**Go/No-Go surface (idea-stage trigger only):**

When the trigger was Pattern 1 ("I want to build…"), the user hasn't committed time yet — this is the cheap point to redirect them. Show the recon summary before proceeding to Phase C:

```
Recon: {verdict}
Top-3 adjacent (live):
  - {skill1} ({installs}) — {one-line scope}
  - {skill2} ({installs}) — {one-line scope}
  - {skill3} ({installs}) — {one-line scope}
Moats checklist: {n_yes}/5 yes
Position draft: "{sentence}"
```

Then:

- If verdict is `SATURATED` / `HEAD_ON_COLLISION` **and** Moats has ≤1 Yes → ask: "This space is crowded and your moats are thin. Continue anyway, pivot the scope, or stop here? (continue / pivot / stop)"
- If verdict is `CROWDED_BUT_DIFFERENTIABLE` / `EMERGING` / `UNCLAIMED` → proceed to Phase C silently after showing the summary.
- If user answers `stop` → save recon-log and exit cleanly. Do not auto-block — user may also have a valid 10x thesis and answer `continue`.

**Pattern 2 ("ship it") path:** the user has already invested in building, so the Go/No-Go question is moot. Still run recon and write `recon-log.md` (so propose.py can track drift), but skip the user-facing summary unless `HEAD_ON_COLLISION` + ≤1 moat — in which case still surface, since they're about to publish a likely-duplicate.

---

## Phase C — Position (one sentence, the backbone)

**This sentence is the skeleton. Everything written in Phase B — and the name in Phase N — traces back to it.**

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

This is the backbone — README hook, SKILL.md description, bullet copy,
and the skill name will all be written to support this claim.
Change it now if it's wrong.
```

Then ask: **"Positioning locked? (y / change it)"**

- `y` → proceed to Phase N with this sentence as context
- change → rewrite and ask again
- If verdict is `HEAD_ON_COLLISION` with ≤1 moat: surface the collision before asking.

---

## Phase N — Name (semantic naming)

Read `references/naming-patterns.md`. If the extracted skill already has a name in the conversation, skip — use that name.

**The positioning sentence from Phase C is the primary input.** The name should reflect the differentiation, not describe a mechanism.

Generate 3 candidates, one per direction from naming-patterns.md viral section. Show them to the user like this:

```
Name candidates (can change in the final confirm):
→ [name-1]  [one-line rationale]  ← recommended
  [name-2]  [one-line rationale]
  [name-3]  [one-line rationale]
```

Pick the recommended one and proceed to Phase DA. The user can change the name during Phase D — no separate confirmation needed here.

---

## Phase DA — Differentiated Architecture (between Name and Forge)

This is the heart of the new flow. After Recon + Position + Name, but before writing any files, lazydrop drafts the **scope** and **file structure** of the user's skill so it (a) avoids duplicating Direct competitors and (b) inherits the structural shape of currently top-installed skills.

**Inputs:**
- `memory/recon-log.md` — top-3 adjacent skills + their in-scope/out-of-scope
- `references/architecture-patterns.md` — per-skill layout + the file's own reference-selection rule (primary source for "modeled on" picks)
- `references/viral-patterns.md` — current top-N skills by install count (fallback when architecture-patterns is empty or stale)
- Phase A extract — `problem`, `mechanism`, `result`
- Phase C — locked position sentence

**Internal output (write to `memory/design-log.md`, never shown to user):**
- Full scope diff against each adjacent competitor
- Full structural references — every dimension borrowed from a top-installed skill, with that skill's install count and the source dimension
- Phase / scripts / references file recommendations with statistical backing where available

**User-facing output (keep it short — name the references, not the stats):**

```
Proposed design for "{skill_name}":

  Scope:
    - In:  {3–5 bullets, plain English}
    - Not in scope (use {competitor} for these):
      - {competitor1} handles {their_in_scope}
      - {competitor2} handles {their_in_scope}

  Modeled on:
    - {skill1} ({install_count}) — reference for {dimension, plain language}
    - {skill2} ({install_count}) — reference for {dimension, plain language}
    - {skill3} ({install_count}) — reference for {dimension, plain language}

  Proposed files:
    - SKILL.md
    - scripts/{x}.py
    - references/{y}.md
    - references/{z}.md
```

Then ask: **"Design looks right? (y / change X / drop X)"**

- `y` → lock the design; write final structure into `memory/design-log.md`; proceed to Phase B.
- `change X` → adjust the proposed bit, re-show the full block from the top.
- `drop X` → remove the proposed item, re-show.

**Reference-skill selection rule (v2):** read `references/architecture-patterns.md` and follow its "Reference selection rule for Phase DA" section (filter by layout match → top 2–3 by stars → state one plain-language dimension per reference). If `architecture-patterns.md` is empty or its frontmatter `version` is >14 days old, fall back to `references/viral-patterns.md` top-3-by-install with a note in `memory/design-log.md`. In every case: state each reference's contribution in plain language (e.g. "directory layout", "scripts/ size", "references/ file count"). **Do not surface raw stats** (mode, median, n=…) to the user — those stay in `memory/design-log.md`.

**Fabrication red line:** every reference skill named must be a real skill currently present in `references/viral-patterns.md`. Do not invent reference skills or invent install counts. If `viral-patterns.md` has fewer than 2 skills in the user's category, fall back to "Modeled on the project's own conventions; cross-category references unavailable this week." and explain why in one sentence.

---

## Phase B — Forge (apply current formula)

Read `references/viral-patterns.md` + `references/readme-rules.md` (B1) and `references/skill-md-rules.md` (B2).

**The Phase C positioning sentence is the first constraint.** Hook, bullets, and SKILL.md description must all support it. If a bullet contradicts or ignores the positioning, cut it.

### B1 — Forge README.md

Build per current week's viral formula. Positioning sentence placement: if it's ≤16 words and verb-first, use it as the hook. Otherwise place it as the first prose line after the 4-bullet summary. Never bury it below H2 headings.

**Field → README mapping (from Phase A extractions):**
- `problem` → hook line or opening sentence
- `result` → 4-bullet summary (concrete outcomes, with numbers)
- `install_cmd` → line 2-3, before hook
- `miss` → position statement (if not superseded by Phase C sentence)

### B2 — Forge SKILL.md

SKILL.md has six required sections (read `skill-md-rules.md` for rules):

1. **Frontmatter** — name (from Phase N), description (see below), version
2. **Overview** — 1-3 sentences, what it does and when (functional, no marketing)
3. **Trigger signals** — exact phrases / contexts that should activate this skill
4. **Phase / workflow instructions** — the step-by-step the agent follows
5. **Rule precedence** — which reference file wins when rules conflict
6. **Reference file table** — what to read and when

**Feed from previous phases:**
- Description field = "Use when [Phase C positioning pain]" — write it in the user's own phrasing from `problem` if available; trigger on the symptom, never summarize the workflow
- Phase / workflow ← `mechanism` from Phase A
- Name ← Phase N output

---

## Phase P — Polish (anti-AI two-pass)

**Applies to README.md only.** SKILL.md is governed by `skill-md-rules.md` and is not run through these filters.

Read `references/anti-ai-patterns.md` for the current forbidden word list.

**Pass 1 — structural:**
- Delete section headers named: Overview, Introduction, Features, Getting Started
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

- If user says `y` / `yes` / `go` → proceed to Phase E (fully automatic)
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
- **Never treat silence, "sure", "looks fine", or embedded "ok" as Stage 1 consent.** Only standalone `y` / `yes` / `go` from the user's most recent message counts. If the user says "ok so anyway..." or "ok let's go with that" — that's not consent; ask once more. A bare "ok" on its own is borderline; prefer to treat it as a request to confirm.
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

**First rule, above all others: user-supplied wording (hook, name, description, any explicit phrasing) overrides every rule below. Never rewrite what the user already wrote.**

| # | Rule source | Weight | Notes |
|---|---|---|---|
| 1 | `viral-patterns.md` (structure: hook, install, length, bullets) | Highest | Format rules first |
| 2 | Phase C positioning sentence | High | Content backbone — all copy traces back to this |
| 3 | `extract-patterns.md` (Phase A fields) | High | User's own words win |
| 4 | `recon-patterns.md` (verdict → strategy) | High | Market reality |
| 5 | `naming-patterns.md` | Medium | Applies only in Phase N |
| 6 | `anti-ai-patterns.md` Tier 1 (hard red flags) | Medium | Filter after structure |
| 7 | `anti-ai-patterns.md` Tier 2/3 (soft signals) | Low | Never block for these |

**Common conflicts and resolution:**
- Positioning sentence (Phase C) is longer than viral hook target → keep the sentence, place it after the hook
- `miss` from Phase A differs from Phase C position sentence → Phase C wins; `miss` is raw input, Phase C refines it
- Anti-AI pattern conflicts with viral formula structure → viral formula wins (always)

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

- Phase B1 → Forge README.md. Read `viral-patterns.md` + `readme-rules.md`. Positioning sentence: use as hook if ≤16 words and verb-first, otherwise first prose line after 4-bullet summary.
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
| `references/architecture-patterns.md` | Phase DA — primary source for "modeled on" reference picks |
| `references/extract-patterns.md` | Phase A (Extract) — always |
| `references/formula-history.md` | evolve cycle only (delta.py reads for trend prediction) |
| `memory/performance-log.md` | On activation (startup) |
| `memory/recon-log.md` | Phase C (Position) — read to pull verdict + top adjacent |
| `memory/design-log.md` | Phase DA — write final design; future runs may read to detect scope drift |
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
