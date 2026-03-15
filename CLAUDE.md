# CSBA AI Presentation — Planning & Experimental Repo

## Project Overview

Planning repo for a CASBO 2026 conference presentation demonstrating agentic AI
in a practical school district context. The demo walks the audience through
analyzing 500 synthetic staff survey responses about a new communications system
installation at "Tri-Valley Unified School District."

The presentation is structured as four acts, each in its own directory under
`demos/`, opened on a separate virtual desktop (Ubuntu) during the live talk.
A companion webapp provides visual explanations alongside live Claude Code demos.

## Repo Layout

- `corpus/` — Read-only reference data from the corpus generation repo. Do not modify.
- `demos/01-extraction/` — Act 1: PDF survey forms → structured JSON
- `demos/02-tagging/` — Act 2: Raw text → sentiment + theme taxonomy
- `demos/03-analysis/` — Act 3: Tagged data + HR join → pattern discovery & reports
- `demos/04-research/` — Act 4: Agentic deep-dive into hidden patterns
- `webapp/` — Presentation companion app (shared across all acts)
- `experiments/` — Scratch work, prompt iteration, throwaway scripts
- `notes/` — Presentation outline, script, timing notes

## Key Context

- The corpus has engineered patterns at three difficulty levels (obvious,
  intermediate, hidden). See `corpus/README.md` for the full list.
- Each `demos/0X-*/` directory should be self-contained — it's what gets opened
  on stage. Each has its own CLAUDE.md with stage-specific instructions.
- The webapp is a single app with route-per-stage, pre-navigated in each desktop's browser.
- Early stages lean on the webapp for visuals; later stages lean on live Claude Code.

## Principles

- This is a teaching presentation: clarity and narrative matter more than technical sophistication.
- "Responsible AI" is a core theme — show guardrails, human oversight, verification.
- The audience is school business officials, not engineers. Jargon needs translation.
