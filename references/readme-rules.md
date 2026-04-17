---
max_lines: 60
version: w2026-17
role: AI-operational
---

# README.md Rules

Rules for generating any README.md. Reader is humans, not Claude.

## Voice

- Conversational tone. Personality welcome.
- Second person ("you") OK. First person OK in moderation.
- Narrative hooks OK.
- Humor and memes OK if matching skill vibe.

## Required sections (in order)

1. Hook (1 line, ≤15 words, imperative verb first)
2. Install command (within first 8 lines, code-fenced)
3. What it does (1-3 sentences, concrete)
4. Concrete example or demo (before/after, GIF, or command trace)
5. Why this exists / positioning (from Phase R)
6. How it differs (vs top 2 adjacent competitors)
7. Non-goals (optional but recommended)
8. License + author (1 line each, bottom)

## Length

- Total ≤ 300 lines. Word count 200-400 (exact target in viral-patterns.md).
- Hook 8-12 words. Install line ≤ line 8. Each section ≤ 50 words.

## Viral formula (from viral-patterns.md)

- Hook starts with imperative verb (Turn, Ship, Find, Skip, Stop).
- Install position line 8 ± 2.
- Prefer prose over bullet lists.
- One concrete example minimum.

## Banned in README.md

- Chatbot openers ("Certainly!", "Of course!").
- Workflow-summary verbs as primary framing.
- Tier 1 anti-ai words (see anti-ai-patterns.md) — unless viral formula requires.
- Three-strawman resolution, era statement, command pair.
- Em-dash > 3 per paragraph.
- Title Case in subheadings (use sentence case).

## Viral vs anti-ai conflict

- Try synonym that preserves viral formula.
- If no synonym works → keep the word, viral wins.
- Never break the formula to avoid Tier 2/3 words.

## Reveal in README

- Problem (user's own words, `problem` field).
- Mechanism (`mechanism` field).
- Install command (`install_cmd` field).
- Position vs competitors (`position_statement` field).

## Do not reveal in README

- Internal phase names (Phase A, Phase B, ...).
- Reference file paths.
- YAML frontmatter specs beyond user-facing.
- Audit weights, thresholds, algorithm details.

## Social proof

Use if real: install count, stars, user logos. Do not fabricate, do not use generic "trusted by thousands".

## Precedence

viral-patterns > readme-rules > anti-ai Tier 1 > anti-ai Tier 2/3.

## Source

Pattern derived from high-install skills (anthropics/xlsx, conorbronsdon/avoid-ai-writing, obra/superpowers).
