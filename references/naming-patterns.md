---
max_lines: 80
version: w2026-17
role: AI-operational
---

# Naming Patterns

## Length distribution (target)

- 1-word: 30% (`brainstorming`, `sanitize`, `remotion`)
- 2-word: 50% ← **preferred**
- 3-word: 15%
- 4+: 5% (only when disambiguation required)

## Character style

kebab-case only. ASCII only. ≤30 chars. No numbers unless version literal.

## Six semantic structures (by frequency)

| Structure | Share | Example | Pick when |
|---|---|---|---|
| verb-noun | 35% | find-skills, code-review | Function is the selling point |
| single-metaphor | 20% | brainstorming, sanitize | Concept needs memorable anchor |
| domain-noun | 20% | frontend-design, aws-skills | SEO-driven audience |
| portmanteau | 10% | plannotator, crowdcast | Unique brand handle needed |
| domain-skill suffix | 10% | aws-skills, taste-skill | Collection repo, NOT single skill |
| ironic | 5% | lazy-skill-drop, superpowers | Product 10x better than name suggests |

## Forbidden words (Tier 1 — zero in top 20)

viral, ultimate, amazing, super-*, revolutionary, innovative, next-gen,
cutting-edge, magic, wizard, genius, smart, intelligent, ai-powered,
gpt-powered, my-*, simple-*, easy-*

## Weak-signal suffixes (drop unless required)

-skill, -skills, -tool, -tools, -cli (only keep if literally applies)

## Verb sets (different from hook verbs)

Name verbs (functional): find, write, execute, fix, review, build, enhance,
design, debug, sanitize, attach, read, install, audit, scan, ship, publish,
forge, pick, extract

Do NOT use hook verbs (Stop, Turn, Skip, Drop) in names.

## Memorability check (all 3 should pass)

1. 2-3 syllables
2. Contains one distinctive sound (unusual consonant cluster or vowel)
3. Hooks to a known concept (metaphor, anchor)

## Collision check (must all 3 pass before commit)

1. GitHub search top 3 is not same-category competitor
2. npm package name available
3. Google first page not dominated by trademark conflict

## Pre-publish checklist (10 items, 9+ must pass)

- [ ] 1-3 words
- [ ] kebab-case, ASCII only, ≤30 chars
- [ ] No Tier 1 forbidden words
- [ ] No weak-signal suffix unless applies
- [ ] No version numbers
- [ ] GitHub top 3 clear of same-category
- [ ] npm available (if relevant)
- [ ] Pronounceable on first read
- [ ] At least one memorability anchor
- [ ] Description can be short because name carries meaning

If 9+ pass, ship. If 7-8, reconsider. If ≤6, regenerate.

## Project-stage match

- Anthropic / big-brand official → 1-word or short kebab
- Community established (>500⭐) → verb-noun
- Experimental / personal / v0.x → metaphor or ironic

Matching stage to style prevents LARPing authority.

## Precedence

When length target conflicts with memorability (e.g., best name is 4 words),
pick memorability. When ironic conflicts with product stage (v0.1 using
ironic name), pick stage match.
