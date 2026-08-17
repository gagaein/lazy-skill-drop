---
max_lines: 80
version: w2026-34
role: AI-operational
evolution: auto-updated by scripts/scan.py weekly
---

# Architecture Patterns

**Week:** w2026-34 | **Sample:** 8 skills by install/star count
**Generated:** 2026-08-17 09:33 UTC

## Layout distribution

- `full-pipeline`  (scripts/ + references/):  2/8 (25%)
- `rules-pack`     (references/ only):        0/8 (0%)
- `tool-only`      (scripts/ only):           4/8 (50%)
- `single-file`    (SKILL.md only):           0/8 (0%)

## Per-skill architecture (sorted by stars)

| Skill | Stars | Layout | scripts/ | refs/ | memory/ | scripts files | refs files |
|---|---|---|---|---|---|---|---|
| zarazhangrui/frontend-slides | 27658 | tool-only | ✓ | — | — | 3 | 0 |
| tt-a1i/archify | 13699 | tool-only | ✓ | — | — | 11 | 0 |
| guillaumemeyer/watermarks-remover | 12524 | no-skill-md | — | — | — | 0 | 0 |
| op7418/guizang-social-card-skill | 6388 | full-pipeline | ✓ | ✓ | — | 5 | 16 |
| chuspeeism/dashi-ppt-skill | 5184 | no-skill-md | — | — | — | 0 | 0 |
| eugeniughelbur/obsidian-second-brain | 4056 | full-pipeline | ✓ | ✓ | — | 27 | 10 |
| 0xNyk/council-of-high-intelligence | 3968 | tool-only | ✓ | — | — | 4 | 0 |
| gamedev-skills/awesome-gamedev-agent-skills | 531 | tool-only | ✓ | — | — | 3 | 0 |

## Reference selection rule for Phase DA

Read this file in Phase DA. Pick 2–3 reference skills as follows:

1. Filter to skills whose `layout` matches the user's proposed scope.
   - If the user is building a pipeline (scripts + rules): prefer `full-pipeline` skills.
   - If the user is building a rules pack: prefer `rules-pack` skills.
   - If the user is building a single tool: prefer `tool-only` or `single-file`.
2. Within the filtered set, pick top 2–3 by stars.
3. For each picked skill, state in plain language the one dimension it's the reference for (e.g. "directory layout", "references/ file count", "scripts/ size"). Do not surface raw counts to the user.
4. If filtering produces <2 results, fall back to top 2–3 overall by stars and note the layout mismatch in `memory/design-log.md` (internal only).

## Fabrication red line

Never invent a skill name or star count. Every reference cited in Phase DA must appear in the per-skill table above. If this file is empty or stale (>14 days since last scan), tell the user "structural references are unavailable this week" rather than fabricate.
