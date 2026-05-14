---
max_lines: 80
version: w2026-20
role: AI-operational
evolution: auto-updated by scripts/scan.py weekly
---

# Architecture Patterns

**Week:** w2026-20 | **Sample:** 8 skills by install/star count
**Generated:** 2026-05-14 08:51 UTC

## Layout distribution

- `full-pipeline`  (scripts/ + references/):  2/8 (25%)
- `rules-pack`     (references/ only):        1/8 (12%)
- `tool-only`      (scripts/ only):           2/8 (25%)
- `single-file`    (SKILL.md only):           1/8 (12%)

## Per-skill architecture (sorted by stars)

| Skill | Stars | Layout | scripts/ | refs/ | memory/ | scripts files | refs files |
|---|---|---|---|---|---|---|---|
| zarazhangrui/frontend-slides | 17407 | tool-only | ✓ | — | — | 3 | 0 |
| Manavarya09/design-extract | 2562 | no-skill-md | — | — | — | 0 | 0 |
| Agents365-ai/drawio-skill | 1543 | no-skill-md | — | — | — | 0 | 0 |
| wuji-labs/nopua | 1296 | single-file | — | — | — | 0 | 0 |
| eugeniughelbur/obsidian-second-brain | 1112 | full-pipeline | ✓ | ✓ | — | 7 | 5 |
| Agents365-ai/video-podcast-maker | 875 | full-pipeline | ✓ | ✓ | — | 14 | 8 |
| dominikmartn/hue | 594 | rules-pack | — | ✓ | — | 0 | 12 |
| JuneYaooo/gpt-image2-ppt-skills | 533 | tool-only | ✓ | — | — | 6 | 0 |

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
