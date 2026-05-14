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
- Humor and memes OK if matching skill vibe.

## Required sections (in order)

1. **Install** — line 2–3, right after H1, inline or code-fenced (see below)
2. **Hook** — 1 sentence, 9–16 words, imperative verb preferred
3. **What it does** — 4 bullets with specific numbers ("64 rules", "30+ files")
4. **Concrete example** — code block, curl, or before/after (83% of top skills have this)
5. **Position statement** — 1 sentence: what adjacent tools miss (83% of top skills have this)
6. **H2 body** — When to Apply / How It Works / Rule categories / etc.
7. **Non-goals** — optional; add if the scope is ambiguous
8. **License + author** — 1 line each, bottom

## Length

- Word count **350–450** words (sweet spot from n=6 README study; range 312–668)
- Hook: 9–16 words. Install: line 2–3. No ceiling on lines — some reference skills are longer.

## Install placement rule (100% signal — no exceptions observed)

```
# skill-name
$ npx skills add owner/repo --skill skill-name   ← line 2: inline shell command

OR

# skill-name
`git clone https://github.com/you/skill ...`     ← line 2: inline backtick code

OR

# skill-name
                                                 ← blank line OK
```bash
git clone ...                                    ← line 3–4 inside code fence
```
```

Never put the install command after paragraph text. The H1 → install → hook order is fixed.

## Bullet rules (type-dependent, not a single number)

- **Instructional skills** (frontend-design, superpowers): 10–25 bullets
- **Rules directory skills** (vercel-react, ui-ux-pro-max): 30–70 bullets
- **Tool/API skills** (soultrace, web-design-guidelines): 15–30 bullets

"Prefer prose over bullets" is wrong — top skills average 30 bullets. Use bullets freely.
The only constraint: each bullet should be specific (a number, an example, or a concrete scope).

## Position statement — write one (83% rate)

One sentence naming what the top 1–2 adjacent tools miss:

```
"X and Y do A but assume B. This does B directly."
"Unlike X, no Z required."
"X handles A. This handles the part X leaves to you."
```

Do NOT fabricate competitors. If you cannot name real adjacent tools, skip this section.

## Banned in README.md

- Chatbot openers ("Certainly!", "Of course!", "Absolutely!")
- Workflow-summary verbs as primary framing ("This skill reads X, extracts Y, publishes Z")
- Tier-1 anti-ai words without a number backing them (see anti-ai-patterns.md)
- Title Case in subheadings — use sentence case
- Fabricated institutional affiliation ("built at MIT", "developed at Anthropic / OpenAI / Google", "from Stanford lab") — only state when user explicitly confirmed in conversation
- Fabricated endorsements or partnerships ("endorsed by X", "official partner of Y", "in collaboration with Z") — only when user provided evidence
- Fabricated certifications or compliance claims ("OWASP-certified", "SOC 2 compliant", "GDPR ready") — only when user can show proof
- License short-form that reads as institutional ("MIT" alone, "BSD" alone, "Apache" alone) — spell the full license name and link the LICENSE file ("[MIT License](LICENSE)", "[Apache License 2.0](LICENSE)", "[BSD-3-Clause](LICENSE)"). The bare three-letter forms get misread as university/company names in non-English contexts.

## Viral vs anti-ai conflict

- If no synonym preserves the formula, keep the word — viral wins.
- Never remove a number or example to avoid a Tier-2 word.

## Precedence

viral-patterns > readme-rules > anti-ai Tier 1 > anti-ai Tier 2/3
