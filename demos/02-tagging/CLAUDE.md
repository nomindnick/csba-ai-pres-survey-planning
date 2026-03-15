# Act 2: Tagging & Taxonomy

## Context

Second stage of the CASBO 2026 demo. The audience starts with clean extracted
survey data and sees it get enriched with sentiment and thematic tags.

## Data

- `data/extracted_surveys.json` — 500 survey records with open-ended responses (q1–q5)

## Goal

Demonstrate two approaches to tagging survey responses:
1. **Simple sentiment** — positive/negative/neutral per response
2. **Theme discovery** — have AI explore the data to suggest a taxonomy,
   then apply it systematically across all responses

## What to Show

- The difference between top-down (preset taxonomy) vs. bottom-up (AI-discovered) approaches
- How to iterate on a taxonomy with human oversight
- Consistency and quality of AI-applied tags at scale
- This stage balances webapp visuals with live Claude Code interaction.
