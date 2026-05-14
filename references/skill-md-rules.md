---
max_lines: 60
version: w2026-17
role: AI-operational
---

# SKILL.md Rules

Rules for generating any SKILL.md. Reader is Claude, not humans.

## Voice

- Imperative / infinitive form only. Verb-first.
- No second person ("you"). No first person ("I").
- No narrative framing, no jokes, no memes, no emotional language.

## Structure

- YAML frontmatter: `name`, `description` required.
- H1 = skill name. Overview 1-3 sentences.
- H2 = phase/section headers. Imperative subheadings.
- Body = numbered or bulleted rules. Short lines.

## Length

- Total ≤ 200 lines.
- Body after frontmatter ≤ 150 lines.
- Section > 50 lines → consider extracting to a reference file (guideline, not hard rule).
- Never duplicate content between SKILL.md and references.

## Description field

- Start with "Use when ...".
- Triggering conditions only. NO workflow verbs (reads / writes / extracts / publishes / renders).
- ≤ 120 words. ≤ 500 chars.
- Include phrases the user would actually say.

## Banned in SKILL.md

- Marketing words (powerful, seamless, comprehensive).
- Narrative hooks ("Ever wondered...", "You know the feeling...").
- Screenshots, gifs, emoji (except in examples).
- "About this skill" / "Why we built this" sections.
- Author bio, credits, crypto/coin references.
- Install commands, badges, stars (those go in README.md).
- Fabricated institutional affiliation ("at MIT", "by Anthropic / OpenAI / Google", "Stanford lab") — never insert in description / overview / phase text unless the user explicitly confirmed it in the conversation.
- Fabricated endorsements or partnerships ("endorsed by X", "official partner of Y") — only when user provided evidence.
- Fabricated certifications or compliance claims ("OWASP-certified", "SOC 2") — only when user can show proof.

## Required in SKILL.md

1. Frontmatter (name, description, version)
2. Overview (1-3 sentences, functional)
3. Trigger signals (what user says/does)
4. Phase / workflow instructions
5. Rule precedence
6. Reference file reading table

## Goes to README.md instead

- Install command
- Hook / elevator pitch
- Before/after demos
- Testimonials, social proof
- Roadmap → CHANGELOG.md
- License → LICENSE + README footer

## Reference file linking

- `Read references/X.md` — imperative, explicit path.
- Indicate trigger: "Read at Phase B start" / "Read when drift > 0.20".
- Do not inline reference content.

## Precedence

- viral-patterns.md → README only, does not apply here.
- anti-ai-patterns.md imperative-style fail rules → ignored here.
- skill-md-rules wins against anti-ai rules when they conflict inside SKILL.md.

## Source

Rules derived from Anthropic skill-creator SKILL.md and obra/superpowers writing-skills SKILL.md.
