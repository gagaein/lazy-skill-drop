---
max_lines: 50
version: w2026-17
role: AI-operational
---

# Extract Patterns

Phase A pulls these from the conversation. Do not ask all at once.

## 4 required fields (Phase A extracts these)

| Field | Content | Length | Destination |
|---|---|---|---|
| `problem` | Symptom the user experiences | 1-2 sentences | README.md |
| `mechanism` | What the skill does internally | 1-2 sentences | README.md |
| `install_cmd` | Literal command user runs | 1 line | README.md |
| `trigger_description` | "Use when..." phrase | <120 words | SKILL.md frontmatter |

**Note:** `position_statement` is NOT a Phase A field — it is generated in Phase C from Recon output. Do not try to extract it from conversation.

## Optional fields (add when conversation supplies)

| Field | Destination |
|---|---|
| `concrete_example`: before/after or command demo | README.md |
| `non_goals`: things the skill explicitly doesn't do | README.md |
| `platform_compat`: Claude Code / Cursor / Codex / Gemini CLI | README.md |
| `dependencies`: runtime requirements | README.md |

## Missing-field rule

If a required field is missing: ask ONE question, not a form.
Priority: problem → mechanism → install_cmd.
Never ask about trigger_description — derive from problem.

## Quote user wording

For `problem`, quote the user's phrasing verbatim where possible.
Their own words have more signal than your paraphrase.

## Compaction rule

Each field must fit the length spec. If the user gave a 5-sentence problem,
pick the most concrete 2. If they gave a vague 1-line problem, ask.

## Precedence

When a user supplies a full draft of one field (e.g. a hand-written hook),
use it verbatim even if it violates anti-ai-patterns. User intent > audit.
