# Formula History

---
max_lines: 80
rotation: keep 6 most recent weeks, archive older to memory/formula-history-archive.md
role: AI-operational (delta.py reads)
---

Each weekly scan appends a new entry here. `scripts/delta.py` reads the two most
recent entries to compute drift; `scripts/propose.py` reads up to 6 entries for
trend prediction.

Newest entries go at the top.

NOTE: All `readme_length` values are README.md word counts (human-facing file).
Entries before w2026-17 were seeded with SKILL.md lengths (shorter) and have been
corrected to estimated README equivalents for consistent delta tracking.

---

## w2026-17 (real-data rescan, README.md measured, n=6)

### structural
hook_words:      13
install_line:    2.0
readme_length:   419
hook_type:       command (7/11)
bullet_count:    30

### forbidden_seen
- "seamless"       in 4/10
- "leverage"       in 3/10
- "comprehensive"  in 3/10

────────────────────────────────────────

## w2026-16 (estimated, seed data corrected)

### structural
hook_words:      10.8
install_line:    7.4
readme_length:   390
hook_type:       imperative
bullet_count:    28

### forbidden_seen
- "seamless"      in 5/10
- "leverage"      in 4/10
- "robust"        in 2/10

────────────────────────────────────────

## w2026-15 (estimated, seed data corrected)

### structural
hook_words:      11.5
install_line:    7.0
readme_length:   375
hook_type:       imperative
bullet_count:    26

### forbidden_seen
- "seamless"      in 6/10
- "leverage"      in 4/10
- "robust"        in 3/10
- "craft"         in 2/10

────────────────────────────────────────
