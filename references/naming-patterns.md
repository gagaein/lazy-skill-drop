---
max_lines: 90
version: w2026-17
role: AI-operational
---

# Naming Patterns

Claude skill names live in two contexts simultaneously — optimizing only one produces bad names.

**Context 1 — Discovery** (skills.sh slug, GitHub URL, awesome-list):
Scanned quickly. Must signal category and scope fast. Short wins.

**Context 2 — Activation** (user says it in conversation, description field triggers):
Must feel natural to say aloud and appear in the phrases users actually reach for.
Names that are awkward to speak ("readme-forge" requires a pause) fail here.

---

## Scope honesty rule

**Name the outcome, not the mechanism.**

For a multi-phase pipeline (research → generate → audit → ship → evolve):
- Bad: `readme-forge` — names one middle step
- Bad: `skill-publisher` — names the last step only
- Good: names that capture "from idea to live, automatically"

If the product is a pipeline, the name should feel like a pipeline noun, not a tool noun.
Verb-noun works for single-function utilities; metaphor or portmanteau works better for
full pipelines because a single verb undersells scope.

---

## Six semantic structures

| Structure | Share | Best when |
|---|---|---|
| verb-noun | 35% | Single function is the draw (find-skills, code-review) |
| single-metaphor | 20% | Product is hard to describe but easy to feel (superpowers) |
| domain-noun | 20% | SEO matters; audience is domain-defined (frontend-design) |
| portmanteau | 10% | Need a unique brand handle (skilldrop) |
| domain-skill suffix | 10% | Collection repos only, NOT single skills (aws-skills) |
| ironic | 5% | Product 10x better than name implies (lazy-skill-drop) |

---

## Forbidden

- Hook verbs as first word: stop, skip, drop, turn, ship (reserved for README hooks, not names)
- Tier 1 AI slop: viral, ultimate, amazing, revolutionary, smart, ai-powered
- Weak suffixes unless literally accurate: -skill, -skills, -tool, -tools, -cli
- Version numbers or years

These are mechanical filters. A name passing all of them can still be wrong.

---

## Memorability (3 questions, all "yes" required)

1. Say it aloud without hesitation?
2. Spell it from hearing once?
3. Hooks to a single clear concept — metaphor, action, place?

---

## Activation test (Claude-specific)

Would a user naturally say this in a sentence when they want the skill?
- "lazydrop my skill" — works as verb, memorable ✓
- "use scan-forge on this" — awkward, sounds like a command ✗

For skills invoked by intent rather than name: test the description trigger instead.

---

## Scope calibration

| Product scope | Name guidance |
|---|---|
| Single-function utility | verb-noun; name the function directly |
| Multi-step workflow | metaphor or portmanteau; name the outcome |
| Full pipeline | metaphor wins; the name is a brand, not a description |
| Official / org-backed | 1-word or tight kebab |
| Experimental / personal | ironic or metaphor OK; don't LARP authority |

---

## Pre-ship checklist (gut-check, not binary filter)

A name scoring 7/10 feeling right > 10/10 feeling wrong.

- [ ] Both contexts work (discovery + activation)
- [ ] Scope honest — name doesn't imply narrower function than product delivers
- [ ] 1-3 words, pronounceable, spellable from hearing
- [ ] No Tier 1 forbidden words or weak-signal suffix
- [ ] No hook verbs
- [ ] GitHub top 3 in category not same-bucket competitor with this name
- [ ] Memorable anchor: metaphor, concept, or distinctive sound
- [ ] Natural in a sentence (activation test passes)

---

## Project-stage match

- Anthropic / major org: 1-word or tight kebab, no irony
- Community-established (>500⭐): verb-noun, credibility signal  
- Experimental / personal: metaphor or ironic fine; matches actual authority level
