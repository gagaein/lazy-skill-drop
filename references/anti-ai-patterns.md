---
max_lines: 55
version: w2026-17
role: AI-operational
---

# Anti-AI Patterns

## Tier 1 words — flag each occurrence

seamless, leverage, robust, delve, utilize, elevate, unlock, empower,
comprehensive, innovative, revolutionize, cutting-edge, streamline, foster, harness

- 1 occurrence: warn (may be literal technical use)
- 3+ per 500 words: fail
- Exception: "comprehensive" is OK when immediately followed by a count ("comprehensive guide with 50+ rules")

## Overused phrases — flag on sight (no density threshold)

"complex tapestry", "a testament to", "crucial role", "ever-evolving landscape",
"intricate balance", "navigate the challenges", "delve into", "in the realm of",
"the world of"

## Tier 2 words — flag when 2+ cluster in one paragraph

journey, ecosystem, landscape, paradigm, testament, tapestry, vibrant, nestled,
thriving, watershed, intricate, navigate, endeavor, ascertain, commence,
facilitate, holistic, crucial, ever-evolving

## Structural patterns

### Hard blocks (each occurrence = fail)

1. Chatbot openers: "Certainly!", "Of course!", "Absolutely!"
2. Em-dash >3 per paragraph
3. Synonym cycling: 4+ synonyms for the same noun in one paragraph
4. Vague attribution: "Experts believe", "Studies show"
5. Conclusion cliché: "In summary", "In conclusion", "The future looks bright"
6. Model leak: "As of my last update", "I don't have real-time data"
7. Title Case in subheadings

### Soft flags (flag once, explain, do not block)

These patterns appear occasionally in high-quality technical writing. Flag once if found,
but do not treat as a fail on their own:

1. Negative parallelism: "It's not X, it's Y" — fine once; repetitive use is the tell
2. Three-strawman: "Not X. Not Y. It's Z." — only a problem when done 3+ times per page
3. Era statement: "It's never been easier to X" — rare; flag if present but don't block
4. Command pair: "Stop X. Start Y." — legitimate in instructional content; flag if formulaic
5. Copula avoidance: "serves as", "functions as" — common in technical docs; only flag if 3+

## Rhythm check

Do NOT surface to user. Informational only.

- Sentence length CV < 0.4 → note internally, do not flag
- Paragraph length CV < 0.4 → note internally, do not flag

## Does not apply

- Technical literal usage ("robust against adversarial inputs", "serves as a proxy")
- Non-English writing
- Creative / fiction output

## Precedence

When this file conflicts with viral-patterns.md (structural formula), viral wins.
This file is a soft filter, not a hard gate.
