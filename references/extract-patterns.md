---
max_lines: 50
version: w2026-17
role: AI-operational
---

# Extract Patterns

Phase A pulls these from the conversation. Do not ask all at once.

## Required fields (Phase A extracts these)

| Field | Content | Length | Feeds |
|---|---|---|---|
| `problem` | Symptom the user experiences | 1-2 sentences | README hook, Phase C input |
| `mechanism` | What the skill does internally | 1-2 sentences | Phase B2 workflow section |
| `result` | Concrete outcome after using the skill | 1-2 sentences | README bullet summary |
| `install_cmd` | Literal command user runs | 1 line | README line 2 |

**Not extracted in Phase A:**
- `position_statement` — generated in Phase C from Recon output, not extracted from conversation
- `trigger_description` — derived from `problem`; Phase B2 writes it as "Use when [problem phrasing]"

**`miss` field:** extract if user explicitly states what competitors miss. If not stated, Phase R surfaces this through competitive analysis. Do not ask for it.

## Optional fields (add when conversation supplies)

| Field | Feeds |
|---|---|
| `miss`: what existing tools miss | Phase C as additional input |
| `concrete_example`: before/after or command demo | README example section |
| `non_goals`: things the skill explicitly doesn't do | README |
| `platform_compat`: Claude Code / Cursor / Codex / Gemini CLI | README |
| `dependencies`: runtime requirements | README |

## Missing-field rule

If a required field is missing: ask ONE question, not a form.
Priority: problem → mechanism → install_cmd.

## Quote user wording

For `problem`, quote the user's phrasing verbatim where possible.
Their own words have more signal than your paraphrase.

## Compaction rule

Each field must fit the length spec. If the user gave a 5-sentence problem,
pick the most concrete 2. If they gave a vague 1-line problem, ask.

## Precedence

When a user supplies a full draft of one field (e.g. a hand-written hook),
use it verbatim even if it violates anti-ai-patterns. User intent > audit.
