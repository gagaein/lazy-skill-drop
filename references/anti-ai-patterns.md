---
max_lines: 50
version: w2026-17
role: AI-operational
---

# Anti-AI Patterns

## Tier 1 words — flag each occurrence

seamless, leverage, robust, delve, utilize, elevate, unlock, empower,
comprehensive, innovative, revolutionize, cutting-edge, streamline, foster, harness

- 1 occurrence: warn (may be literal technical use)
- 3+ per 500 words: fail

## Overused phrases — flag on sight (no density threshold)

"complex tapestry", "a testament to", "crucial role", "ever-evolving landscape",
"intricate balance", "navigate the challenges", "delve into", "in the realm of",
"the world of"

## Tier 2 words — flag when 2+ cluster in one paragraph

journey, ecosystem, landscape, paradigm, testament, tapestry, vibrant, nestled,
thriving, watershed, intricate, navigate, endeavor, ascertain, commence,
facilitate, holistic, crucial, ever-evolving

## Structural patterns — each counts as a fail

1. Chatbot openers: "Certainly!", "Of course!", "Absolutely!"
2. Em-dash >3 per paragraph
3. Negative parallelism: "It's not X, it's Y"
4. Three-strawman: "Not X. Not Y. It's Z."
5. Era statement: "It's never been easier to X. It's never been harder to Y."
6. Command pair: "Stop X. Start Y."
7. Synonym cycling: 4+ synonyms for same noun in one paragraph
8. Copula avoidance: "serves as", "functions as", "featuring", "boasting"
9. Vague attribution: "Experts believe", "Studies show"
10. Conclusion cliché: "In summary", "In conclusion", "The future looks bright"
11. Model leak: "As of my last update", "I don't have real-time data"
12. Title Case in subheadings

## Rhythm check (weak secondary signal)

- Sentence length CV < 0.4 → flag as uniform
- Paragraph length CV < 0.4 → flag as uniform

## Does not apply

- Technical literal usage ("robust against adversarial inputs")
- Non-English writing
- Creative / fiction output

## Precedence

When this file conflicts with viral-patterns.md (structural formula), viral wins.
This file is a soft filter, not a hard gate.
