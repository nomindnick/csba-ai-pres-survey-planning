# Act 4: Auto-Research Loop with LLM Judge — Process Notes

How we designed, implemented, and evaluated the auto-research loop approach for
Act 4, working interactively in Claude Code on 2026-03-16.

This covers the second of two approaches tested for Act 4. The first is the
"manual" agentic research loop, documented in `act4-manual-research-loop-process.md`.
Both approaches are intended to be presented to the audience.

---

## Origin of the Idea

After three iterations on the manual research loop (documented in the companion
file), Nick hit a point of diminishing returns on prompt engineering. The agent
was finding 3.5 of 4 hidden patterns, producing excellent reports, but the
hardest pattern (experienced newcomer effect) resisted further nudging without
crossing from "research methodology" into "scripted answers."

Nick came into this conversation with a specific idea: apply the pattern from
Karpathy's **autoresearch** project (released March 6, 2026 — an iterative loop
where an AI agent modifies code, measures improvement against a fixed metric,
keeps or discards changes, and repeats) to the survey analysis problem. The key
insight was that autoresearch's power comes from having a **score to optimize
against**, and the question was whether that could work for qualitative research
where there's no obvious objective metric.

Nick's proposed solution: use a **second LLM as a judge** — an independent
reviewer that scores the research against a rubric and provides specific
critique, driving the next round of investigation. This was his idea from the
start; Claude Code's role was to research the autoresearch pattern in detail,
think through the architectural implications, design the rubric, implement the
system, and evaluate the results.

---

## Design Conversation

### Research Phase

Claude Code researched Karpathy's autoresearch repo in detail:

- **Core pattern:** Agent reads current state → proposes change → executes →
  measures against fixed metric (val_bpb) → keeps or discards → logs → repeats
- **Three-layer architecture:** Human writes `program.md` (goals), agent edits
  `train.py` (the artifact), scoring infrastructure is immutable
- **State management:** Remarkably minimal — `results.tsv` (append-only log),
  git history, and the LLM's own conversation context. No journal, no notes, no
  summarization.
- **~12 experiments/hour, ~100 overnight.** Shopify CEO reported 19% improvement
  on a 0.8B model after 37 experiments.

### Key Design Tensions

**Why this is harder than autoresearch:** The original works because `val_bpb`
is objective, fast, deterministic, and ungameable. Survey research has none of
these properties. And the structure is different: autoresearch hill-climbs on a
single artifact (train.py), replacing it each iteration. Research is additive —
you accumulate findings, and a null result is still a result.

**The scoring problem:** Nick initially suggested an "objective judge" LLM that
assumes the role of an expert researcher, critiques the methodology, and assigns
a 1-10 score. We discussed whether to use the Anthropic API (per-token cost) or
the Claude CLI (`claude -p`, covered by subscription). Nick chose the CLI for
cost reasons — Opus 4.6 as judge is ideal but expensive via API.

**Rubric isolation:** We discussed whether the research agent seeing the rubric
would let it game the system. Nick argued (correctly) that as long as findings
are grounded in verifiable facts (statistics, quotes), seeing the rubric can't
help you fake good research — and might actually help the agent understand what
quality looks like. This simplified the architecture significantly.

**Validation vs. judging:** We separated two concerns: the **judge** evaluates
research completeness and rigor (drives the loop), while a **validator** would
check factual accuracy (runs once at the end). The validator uses severity tiers
— Errors (must fix), Concerns (log but don't block), Suggestions (ignore) — to
prevent nitpicks from stalling the process. We designed but did not implement the
validator for this experiment.

### Architecture Decisions

After evaluating three loop mechanisms (the `/loop` slash command, Ralph Loop
plugin, and simply looping within a single Claude Code session), we chose the
simplest: **CLAUDE.md instructions drive the loop within a single session.** The
agent runs a research round, shells out to `claude -p` for judging, parses the
score, and continues or stops. With 1M context, this handles many rounds without
issues. Ralph Loop would be better for overnight unattended runs but was
unnecessary for the experiment.

**State file design** (the equivalent of autoresearch's `results.tsv`):

| File | Purpose | Analogy |
|---|---|---|
| `output/experiment_log.tsv` | One-line-per-round score trajectory | `results.tsv` |
| `output/round_log.md` | Detailed findings per round | Conversation context |
| `output/research_memo.md` | The evolving report (rewritten each round) | `train.py` |
| `output/judge_feedback/round_N.md` | Raw judge output per round | `run.log` |

### The Rubric

Six dimensions, each scored 1-10 with specific level descriptors:

1. **Breadth of exploration** — has every data field been examined?
2. **Depth of analysis** — interactions, subgroups within subgroups?
3. **Evidence quality** — statistics with sample sizes + representative quotes?
4. **Methodological rigor** — confounders tested, alternatives considered?
5. **Actionability** — specific recommendations a school admin could act on?
6. **Intellectual honesty** — limitations flagged, surprises highlighted?

The rubric prompt instructs the judge to return structured JSON with scores,
strengths, gaps, and a narrative critique. The critique is the key output — it
tells the research agent exactly what to investigate next.

---

## Validation Test

Before running the full loop, we tested the judge against the existing manual
research output (6 rounds, from `demos/04-research/`). Results:

- **Score: 8.3/10** — the manual research already clears a reasonable threshold
- **Critique quality: excellent** — identified specific, actionable gaps:
  no multivariate model, VH gender gap unexplained, race×tenure lacks
  qualitative grounding, question-level analysis only at site level
- **Cost: $0.17 per judge call** via Claude CLI

This confirmed the approach had legs: the judge gives useful, specific feedback,
not vague "do more" advice.

---

## Experiment Setup

We created a clean directory (`experiments/auto-research/`) isolated from the
manual run, with:

- Symlinked data files (same scored dataset)
- Fresh CLAUDE.md with the loop instructions
- Copy of the judge rubric
- Empty output directory and experiment log (header only)
- Threshold set to **9.0** (intentionally ambitious — we wanted to see if the
  loop could push beyond what the manual run achieved)

---

## Results

### Score Trajectory

| Round | Score | Breadth | Depth | Evidence | Rigor | Action | Honesty |
|---|---|---|---|---|---|---|---|
| 1 | 6.7 | 7 | 6 | 7 | 5 | 8 | 7 |
| 2 | 7.7 | 8 | 7 | 8 | 7 | 8 | 8 |
| 3 | 8.8 | 9 | 8 | 9 | 9 | 9 | 9 |
| 4 | **9.0** | 9 | 9 | 9 | 9 | 9 | 9 |

Clean monotonic improvement. 4 rounds to reach 9.0.

### What the Judge Drove

The judge's critique directly shaped each subsequent round:

- **Round 1 → 2:** Judge said "untested interactions, no multivariate, sentiment
  scorer unvalidated." Round 2 ran confounder decomposition, residual analysis,
  and scorer validation.
- **Round 2 → 3:** Judge said "need multivariate regression, per-question
  subgroup sentiment, significance testing." Round 3 ran OLS regression
  (R²=0.128, 7 significant predictors), per-question analysis, and p-values
  for all key effects.
- **Round 3 → 4:** Judge said "text analysis/clustering, non-response patterns,
  within-teacher variation." Round 4 ran TF-IDF + KMeans clustering (7
  archetypes), Q4 non-response analysis, and within-site teacher decomposition.

The feedback loop is clearly visible in the output. Each round's hypotheses map
directly to the previous round's judge gaps.

### Comparison with Manual Run

| Dimension | Manual (6 rounds) | Auto-Research (4 rounds) |
|---|---|---|
| Judge score | 8.3 (retroactive) | 9.0 |
| Rounds needed | 6 | 4 |
| Scripts produced | 43 | 16 |
| Findings | ~20 | ~32 |

**Auto-research found that manual didn't:**
- Multivariate regression (7 independent predictors, race drops out)
- Per-question regression isolating gender gap to Q2 (training)
- Residual analysis decomposing tenure confounding
- Q4 non-response as a dissatisfaction signal (t=-8.61)
- Text clustering (7 archetypes) independently confirming demographics
- Tenure decline is linear with no threshold (tested piecewise + quadratic)
- Jaccard similarity proving near-zero complaint overlap between groups
- Career-mover decomposition quantified

**Manual found that auto-research didn't:**
- Hedging/silent dissatisfaction (resigned language analysis)
- Riverside polarization (highest variance, all 10 most negative records)
- "Compliance without consent" theme
- Site admin "official voice" in anonymous surveys
- Hispanic/Latino 20+ year positivity as a distinct pattern

**Style difference:** The auto-research output is more rigorous and
quantitative — regression, residuals, significance tests, effect sizes. The
manual output is more exploratory and qualitative — hedging language, narrative
themes, reading between the lines. The auto-research memo reads like an academic
report; the manual memo reads like a school board presentation.

---

## How We Worked (Human-AI Collaboration)

This section documents the collaborative process that produced the auto-research
loop — which is itself an example of the presentation's core themes.

### The Collaboration Arc

1. **Nick brought the idea.** After three iterations on the manual loop (in a
   separate Claude Code conversation), he'd hit diminishing returns on prompt
   engineering and had been thinking about Karpathy's autoresearch pattern. He
   came into this conversation with a specific concept: an LLM judge scoring
   the research output to drive an iterative loop.

2. **Claude Code researched and pressure-tested it.** Researched the actual
   autoresearch repo (architecture, state management, results), identified why
   the survey research problem is structurally different (additive vs.
   replacement, subjective vs. objective scoring), and was honest about risks
   (score noise, gaming, audience complexity).

3. **We designed together.** The rubric dimensions, the state file architecture,
   the choice of `claude -p` over the API, the decision not to hide the rubric,
   the separation of judging from validation — these emerged from back-and-forth
   discussion where Nick made the strategic decisions and Claude Code worked
   through the implementation implications.

4. **Claude Code implemented.** Built the directory structure, wrote the
   CLAUDE.md, designed the rubric prompt, ran the validation test against
   existing output, and set everything up for the experiment run.

5. **Nick ran the experiment** in a separate Claude Code session (clean context).

6. **Claude Code analyzed the results.** Read all output files, compared against
   the manual run, identified what each approach found that the other didn't,
   and characterized the style differences.

7. **Nick synthesized the lesson.** The insight that both approaches are valuable
   for different reasons, that the design decisions matter enormously, and that
   the human's role shifts from doing the analysis to designing, directing, and
   evaluating the process — that's Nick's framing, informed by having done the
   work across both conversations.

### What This Illustrates

**The auto-research loop itself was designed using the same human-AI
collaboration pattern it's meant to demonstrate.** Nick had the strategic
insight (apply autoresearch to qualitative research). Claude Code had the
implementation capacity (research the pattern, design the rubric, build the
system, analyze results). Neither could have produced this alone:

- Without the human: Claude Code wouldn't have thought to apply autoresearch to
  survey analysis, wouldn't have known about Karpathy's recent release, and
  wouldn't have had the presentation context to frame the design decisions.
- Without the AI: Nick would have had to research autoresearch's internals
  himself, manually design and iterate on the rubric, and wouldn't have been
  able to run the comparison analysis across 40+ output files in minutes.

**The two Claude Code conversations serve different roles:**
- The first conversation (manual loop) was about designing a research
  methodology and iterating on it based on observed agent behavior — like
  coaching a researcher.
- This conversation (auto-research loop) was about designing a meta-system —
  a feedback loop that makes the research agent self-improving. Higher leverage,
  more architectural.

Nick moved to a new conversation not because the first one failed, but because
the problem shifted. The manual loop was optimized as far as prompt engineering
could take it. The next step required a different approach entirely — and fresh
context to think about it clearly.

---

## Relevance to Presentation

### Both Approaches as Examples

Showing both approaches to the audience is more powerful than showing either
alone, because the contrast carries the message:

- The **manual loop** shows agentic AI doing structured research — impressive
  but comprehensible (rounds of hypothesis → test → refine).
- The **auto-research loop** shows AI systems reviewing each other — a more
  sophisticated pattern that raises the ceiling on quality.
- The **differences in output** prove that design choices matter — same data,
  same AI, different instructions produce different insights. Neither found
  everything.

### The Two Core Lessons

**Lesson 1: Force multiplier, not replacement.** This process didn't save time
in the way most people imagine ("have AI do it!"). Nobody turned a project over
to AI and walked away. But one person, over a day of work, produced two
independent deep analyses of 500 survey responses — with multivariate
regression, text clustering, qualitative deep-dives, and scorer validation —
that would have required a research team to produce manually. The AI amplifies
what one person can do in the same amount of time.

**Lesson 2: The human role shifts but doesn't disappear.** The person directing
this work had to:
- Design the research methodology (CLAUDE.md)
- Decide how many rounds and what to nudge the agent toward
- Design the judge rubric and scoring threshold
- Choose the loop architecture
- Evaluate output quality and decide when to stop iterating
- Identify blind spots across runs and decide what's worth pursuing
- Make judgment calls about verification standards based on stakes
- Synthesize lessons across approaches

None of this is "pressing a button." It requires understanding both the AI's
capabilities and the domain. The skill set shifts from "do the analysis" to
"design, direct, and evaluate the analysis process" — a higher-level role, not
no role at all.

### Transition to Slides

After demonstrating both approaches (whether live, simulated, or walked-through),
the presenter transitions back to the PowerPoint to land the synthesis: what
we learned, what it means for school business operations, and the responsible
AI principles that make this work in practice.
