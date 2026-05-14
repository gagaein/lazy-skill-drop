---
name: lazy-skill-drop iteration spec
version: w2026-20-v3
iteration_started: 2026-05-14
applies_to: README.md + SKILL.md trigger/flow
---

# Iteration spec — v3 PM-friendly rewrite

This file is the iteration anchor for README + SKILL.md. Per the project's
HTML/landing-page iteration discipline: each new generation must verify
every `must_keep`, every `arguments[].claim`, every `arguments[].evidence`,
and every `arguments[].anchor` is still present.

## Sections — ordered

README:
1. H1 + install (line 2 inline backtick)
2. Hook (9–16 words, imperative)
3. 4-bullet summary
4. How it works (4 numbered steps, plain English, no Phase jargon)
5. When to use this (3 bullets)
6. Quick start (one command + one phrase)
7. Footer (MIT + author + agent-compat one-liner)

SKILL.md:
- frontmatter description (rewritten — see decisions/d2)
- On activation — silent startup checks (unchanged)
- First-time setup (unchanged)
- Phase A — Capture intent (LIGHTER; sets up Phase R)
- Phase R — Recon (Go/No-Go) (PROMOTED earlier in flow)
- Phase A-detail — Extract mechanism / result / install_cmd (resumes post-recon)
- Phase C — Position (unchanged)
- Phase N — Name (unchanged)
- Phase DA — Differentiated Architecture (NEW, between N and B)
- Phase B — Forge (unchanged)
- Phase P — Polish (unchanged)
- Phase D — Confirm (unchanged)
- Phase E — Publish (unchanged)
- everything below "Hard rules for publishing" unchanged

## must_keep — these phrases (case-insensitive) must remain in README OR SKILL.md

- "I want to build a skill" — primary trigger phrase
- "我想开发一个" — primary CN trigger phrase
- "competitor" — recon thesis
- "differentiated" or "different" or "where the gap is" — diff thesis (new)
- "this week" or "top-installed" — viral-formula thesis
- "README + SKILL.md" — dual-artifact contract
- "one yes" or "one confirm" — publish thesis
- "gh repo create" or "GitHub repo" — publish mechanism

## arguments — 4 claims README must make

### arg_competitor_check
- claim: lazydrop checks GitHub for existing skills BEFORE the user writes code
- evidence:
  - SKILL.md Phase R: 4 search axes, 6 verdicts, bucket+status taxonomy
  - references/recon-patterns.md
- anchor: README "How it works" step 1; bullet 1
- core_insight: "If the space is saturated and you don't have a 10x angle, you'll know before you write code."
- sources: [SKILL.md L110-L117, recon-patterns.md L50-L62]

### arg_differentiated_design
- claim: lazydrop drafts your skill's scope from competitor gaps + your skill's file structure from top-installed skills' structure
- evidence:
  - SKILL.md Phase DA (NEW)
  - viral-patterns.md current top-N skills with install/star counts
- anchor: README "How it works" step 2; bullet 2
- core_insight: "Not a generic template — a template shaped by what's actually winning."
- sources: [SKILL.md Phase DA, viral-patterns.md top skills list]

### arg_viral_docs
- claim: README + SKILL.md are written to the structural shape of currently-winning skill docs
- evidence:
  - SKILL.md Phase B + viral-patterns.md (weekly auto-updated)
  - audit_self.py 7 regression-calibrated dimensions
- anchor: README "How it works" step 3; bullet 3
- core_insight: "Sentence length, install line position, hook structure, length budget all match this week's top quartile."
- sources: [viral-patterns.md, audit_self.py DIM_WEIGHTS]

### arg_one_yes_publish
- claim: GitHub repo + 3 awesome-list PRs created automatically after one user confirmation
- evidence:
  - SKILL.md Phase D + E + publish.py
- anchor: README "How it works" step 4; bullet 4
- core_insight: "No forms, no clicking."
- sources: [SKILL.md L245-L298, publish.py]

## decisions — this iteration's design choices

- **d1**: drop "recon" / "forge" / "Phase R/B/etc" / "bucket+status" / "verdict" jargon from README. These stay in SKILL.md as internal phase names.
- **d2**: trigger phrase change is **replacement, not addition**. New primary triggers built around "I want to build" / "我想开发"; "ship it" / "发布这个 skill" / "publish this" preserved only as narrow back-compat for users who already finished design in conversation.
- **d3**: Phase DA's user-facing Architecture display is simplified — just "modeled on: skill1 (Xk installs), skill2 (Y stars), skill3 (Z stars)" with 1-line "why" each. Full structural stats (mode, median, n=...) stay internal in memory/design-log.md.
- **d4**: scan.py extension to scan directory/phase/scripts structure DEFERRED to follow-up commit. Phase DA v1 uses install-count ranking from existing viral-patterns.md to pick reference skills.
- **d5**: 350-450 word README budget kept (readme-rules.md).
- **d6**: identity_guard adds new family_differentiate to protect the differentiation thesis from being silently dropped in future formula iterations.
- **d7**: old README archived to history/v2/README.md (the prior "Recon competitors, forge..." version). This is v3.
- **d8** (v3.1 patch, 2026-05-14): user flagged "MIT" in README footer as readable as "麻省理工 affiliation" in CN context. Two fixes: (a) own README footer changed to `Open-source under the [MIT License](LICENSE) — license name, not an institutional affiliation`; (b) readme-rules.md + skill-md-rules.md gain banned-content bullets covering fabricated institutional affiliation, endorsements, certifications, and (README only) short-form license names. These rules govern any skill lazydrop forges in Phase B.
- **d9** (v3.2, 2026-05-14): d4 lifted — scan.py now fetches each repo's recursive git tree and extracts structural shape (scripts/ / references/ / memory/ presence + file counts + layout label: full-pipeline / rules-pack / tool-only / single-file). Writes `references/architecture-patterns.md` per scan; file carries its own "Reference selection rule for Phase DA" section. Phase DA (SKILL.md) now reads architecture-patterns.md as primary source for "modeled on" picks, falling back to viral-patterns.md if architecture-patterns is empty/stale. architecture-patterns.md added to workflow's AUTO-UPDATE allowlist and propose.py's stage_targets (mirrors the existing 3 knowledge-layer files).

## cases — concrete examples surfaced in README

- case_install: `git clone https://github.com/gagaein/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`
- case_first_use: in any Claude conversation, say `"I want to build a skill that [your idea]"`
- case_auth_once: `gh auth login`

## data_points — kept verbatim

- 3 awesome-lists (per publish.py — confirmed)
- "this week's top installs" (no specific star counts in body; surface only in Phase DA's user output)
- macOS / Linux / Windows for privacy scan — kept in original wording

## tone

- Second person ("you"), imperative verbs ("Build", "Tell", "Check")
- Plain English; **no internal phase names in README** (Phase R / Phase B / Phase DA stay in SKILL.md only)
- No Tier-1 anti-AI words (seamless, leverage, robust, delve, utilize, elevate, unlock, empower, comprehensive, innovative, revolutionize, cutting-edge, streamline, foster, harness)
- No "X and Y do A but assume B" — that's project-internal positioning-statement format, doesn't read naturally to first-time visitors. Position implicitly via bullets.

## condensation_policy

- Keep numbers ("3 lists", "350-450", "9-16") in original form; never abstract to "several" / "many"
- Keep skill name examples verbatim when listed inline
- Keep `code` formatting on every command, file path, env var
- If a bullet must shrink, drop the explanatory clause first, never the claim
- Never drop a "core_insight" — those are what make the bullet specific not generic

## Identity guard family check (new family_differentiate must pass after rewrite)

The identity_guard.py runs after every workflow tick. The 5 families below must each have ≥1 match across README + SKILL.md after this iteration:

- family_recon → "competitor" / "recon"
- family_forge → "viral" / "this week" / "trending" / "real install" / "formula"
- family_publish → "ship" / "publish" / "one confirm" / "gh repo create" / "awesome"
- family_dual_artifact → "README + SKILL.md" / "README.*SKILL.md" / "two-document"
- family_differentiate (NEW) → "differentiated" / "different" / "modeled on" / "gap" / "positioned"

## What this spec does NOT govern

- SKILL.md sections after "Hard rules for publishing" — unchanged
- scripts/* — unchanged this iteration (scan.py extension is d4 deferred)
- references/ rules files (readme-rules.md, skill-md-rules.md, etc.) — unchanged
- workflow + identity_guard.py — only core-identity.md gets a new family added
