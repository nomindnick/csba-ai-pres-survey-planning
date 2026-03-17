# Act 4: Manual Research Loop — Process Notes

How we designed and iterated on the "manual" agentic research approach for Act 4,
working interactively in Claude Code across three experiment runs on 2026-03-15.

This covers one of two approaches tested for Act 4. The other is the
auto-research loop with LLM judge scoring, documented separately. Both
approaches are intended to be presented to the audience.

---

## Starting Point

The goal for Act 4 is the showpiece of the presentation: fully agentic AI
conducting autonomous research on 500 survey responses joined with HR data,
discovering hidden patterns that no simple query would find. Four hidden
patterns were engineered into the synthetic corpus at varying difficulty levels:

1. **Hillcrest wing anomaly** — 30 staff in the north wing have hardware
   problems masked by site-level averages (requires `building_wing` field)
2. **Transfer paradox** — staff from districts with worse systems are the most
   positive; staff from better systems are more negative (requires
   `origin_district_system_quality` field)
3. **Experienced newcomer effect** — older staff negativity is driven by age ×
   tenure interaction, not age alone; older newcomers are surprisingly positive
4. **Valley High bright spot** — performing arts/CTE teachers in large rooms
   rate the system highly despite overall VH negativity (requires `room_type`
   field)

## Design Process

### Initial Design Conversation

Before writing any code or prompts, we spent time thinking through the
architecture of the agentic research loop. The core structure we landed on:

1. **Main agent formulates hypotheses** about the data
2. **Subagents test hypotheses in parallel** using a mix of quantitative
   (Python scripts) and qualitative (reading actual responses) methods
3. **Main agent synthesizes results**, identifies surprises and open questions
4. **Repeat** with refined hypotheses targeting the most promising leads
5. **Main agent writes a research memo** with findings, evidence, caveats, and
   recommendations

Key design decisions made during this conversation:

- **Hybrid quant+qual subagents** — each subagent both runs Python for
  statistics and reads representative responses for the "why." This mirrors
  real research methodology and produces richer output than either alone.
- **Instructions live in CLAUDE.md** — the Act 4 directory's CLAUDE.md serves
  as the research methodology. On stage, the presenter just says "begin your
  research" and the CLAUDE.md (invisible to audience) provides the structure.
- **Non-technical audience framing** — the memo is written for school business
  officials, not engineers. This constraint was baked into every iteration.
- **Experiment tracking structure** — we set up `experiments/act4-research-loop/`
  with a running log, per-run directories (config + notes + output), and a
  findings tracker to learn across runs.

### The Instruction vs. Scripting Tension

A recurring theme throughout the design process: how much scaffolding to
provide without crossing from "research methodology" into "scripted answers."
The audience needs to believe the AI is discovering things autonomously. Too
little instruction and the agent meanders or misses key patterns. Too much and
it's just following a recipe.

We navigated this by:
- Describing the *process* (hypothesize → test → synthesize → repeat) without
  hinting at specific patterns
- Nudging the agent to *examine all fields* and *look within sites* without
  naming which fields or sites would be interesting
- Adding methodological principles (check confounders, question null results)
  rather than specific analytical steps

---

## Experiment Runs

### Run 01 — Baseline

**CLAUDE.md approach:** Moderate scaffolding. Described the loop, said "2-3
rounds," told it to use hybrid quant+qual subagents. No hints about specific
patterns or fields beyond listing what's in the dataset.

**Results:**
- Found 3/4 hidden patterns: Hillcrest wing anomaly, transfer paradox
  (partial), Valley High bright spot
- Missed: experienced newcomer effect (age × tenure interaction)
- Agent stopped at 2 rounds (minimum of the "2-3" range)
- Report quality was excellent — plain language, caveats, sample sizes
- ~25 minutes total

**Key learning:** The agent gravitates to the minimum number of rounds. Given a
range, it picks the low end, writes a solid report, and stops. The experienced
newcomer effect requires deeper investigation that only happens with more
rounds. Also, the confounders nudge ("is this the real driver?") was too
abstract to trigger interaction-term analysis.

### Run 02 — More Rounds, Novelty Requirement

**Changes from Run 01:**
1. Minimum 6 rounds (was "2-3")
2. Each round must investigate something new — cannot re-test confirmed hypotheses
3. Later rounds must challenge earlier findings
4. "When quantitative analysis stops distinguishing groups, go qualitative"
5. Stronger confounders nudge with concrete example: "does it look the same for
   newer vs. long-tenured staff?"

**Results:**
- Same 3/4 hidden patterns, but more findings overall (9 vs 7)
- Found intermediate patterns: counselor disruption, district office positivity,
  food service scheduling chaos
- Agent found age r=-0.015 (evidence OF the interaction effect) but interpreted
  it as "age doesn't matter" instead of investigating within subgroups
- Better methodology overall — tested alternative explanations for tenure effect
- ~45 minutes total

**Key learning:** More rounds produce more findings and better methodology, but
don't automatically produce the hardest findings. The agent's blind spot is
interpreting zero overall correlation as "irrelevant" rather than "might be an
interaction hiding opposite effects." The novelty requirement worked — no
repetition or filler across 6 rounds.

### Run 03 — Null-Result Follow-Up Nudge + Round Logging

**Changes from Run 02:**
1. Added null-result nudge to Important section: "A zero overall effect can mean
   the variable works in opposite directions for different subgroups — canceling
   out in the aggregate. Before dismissing any variable, test whether it has
   different effects within tenure bands, position groups, or other subgroups."
2. Added round logging — agent writes `output/round_log.md` documenting each
   round's hypotheses and findings

**Results:**
- 3.5/4 hidden patterns — best yet
- The experienced newcomer effect appeared as a qualitative observation: the
  memo states "A 60-year-old who is new to the district is among the most
  positive respondents." The insight is correct but framed as supporting
  evidence for "tenure matters, not age" rather than as a distinct interaction
  finding with cross-tabulation statistics.
- Transfer paradox sharper — 39% negative rate for "better" transfers now
  reported
- New sophisticated findings: "quiet dissenters" (hedging language analysis),
  Riverside polarization, scorer self-validation, race × tenure and gender ×
  site interactions
- Round log showed clear research progression: broad → interactions → within-
  site → qualitative deep-dive → challenge findings → edge cases
- ~60 minutes total

**Key learning:** The null-result nudge partially worked — the agent
investigated age within tenure contexts and arrived at the right qualitative
conclusion. But it still didn't formalize it as a cross-tabulated interaction
finding. The round log is extremely valuable for understanding the research
process. Diminishing returns on prompt engineering are approaching — further
nudging toward the experienced newcomer effect risks crossing into scripting.

---

## Accumulated Insights

### What Works Well
- **Hybrid quant+qual subagents** produce rich findings with both statistical
  evidence and human-readable quotes
- **The "Important" section nudges are effective** — the agent examines fields
  and patterns you point it toward
- **Report quality is high out of the box** with the audience instruction
- **6 rounds produces genuine research progression** with no repetition
- **The agent self-validates** methodology when given enough rounds (compared
  keyword scoring against context-aware assessment)
- **Bonus findings emerge naturally** — hedging analysis, polarization patterns,
  question-level analysis weren't engineered but are genuinely useful

### Systematic Blind Spots
- **Zero correlation = "doesn't matter"** — the agent consistently interprets
  null main effects as irrelevant rather than potentially masking interactions
- **Comparison baselines are soft** — the agent compares subgroups against
  overall averages rather than the specific comparison groups that would reveal
  the sharpest contrasts
- **Minimum viable effort** — given a range of rounds, the agent picks the low
  end. Explicit minimums are needed.

### Pattern Discovery Reliability

| Pattern | Run 01 | Run 02 | Run 03 |
|---|---|---|---|
| Hillcrest wing anomaly | YES | YES | YES |
| Transfer paradox | PARTIAL | PARTIAL | STRONGER |
| Experienced newcomer effect | NO | NO | PARTIAL |
| Valley High bright spot | YES | YES | YES |

### Timing

| Run | Duration | Rounds |
|---|---|---|
| 01 | ~25 min | 2 |
| 02 | ~45 min | 6+ |
| 03 | ~60 min | 6 |

---

## How We Worked

This section documents the collaborative process between the human (Nick) and
Claude Code for designing and iterating on the research loop.

**The collaboration pattern:**
1. Nick described the high-level goal and his initial thinking on the approach
2. Claude Code thought through the design in detail — loop structure, subagent
   design, what to experiment with, what could go wrong
3. We aligned on the approach, then Claude Code set up the experiment
   infrastructure (directory structure, tracking files, CLAUDE.md)
4. Nick ran the experiment in a separate Claude Code session (so the research
   agent had clean context, not our design conversation)
5. Back in this session, Claude Code analyzed the results against the four
   hidden patterns and identified what worked, what didn't, and why
6. We discussed what to change, Claude Code drafted the next iteration, and
   Nick ran it again

**Claude Code's role was dual:**
- **System designer** — thinking through the CLAUDE.md instructions, subagent
  architecture, experiment structure, and what to track
- **Analyst** — reading the research agent's output, assessing pattern
  discovery, identifying blind spots, and proposing targeted fixes

**What made this effective:**
- Each run changed only 1-2 things, so we could attribute improvements to
  specific changes
- The experiment tracking (LOG.md, findings.md, per-run notes) kept us oriented
  across iterations
- The human decided when to stop iterating — after run-03, we discussed whether
  to keep refining or accept 3.5/4 and move on. The human judgment call was
  that further prompt engineering had diminishing returns and risked crossing
  from instruction into scripting.

---

## Relevance to Presentation

This process illustrates several themes relevant to the CASBO audience:

1. **Agentic AI requires system design, not just prompting.** The CLAUDE.md
   file is a methodology document — it defines how the AI approaches research,
   what tools it uses, and what standards it applies. This is design work that
   a human has to do thoughtfully.

2. **Iterative refinement based on results.** We didn't get the best version on
   the first try. Each run taught us something about how the agent thinks, and
   we adjusted the instructions based on observed behavior — not unlike
   coaching a new employee.

3. **The human role shifts but doesn't disappear.** The human isn't doing the
   analysis — the AI is. But the human is designing the research methodology,
   evaluating the quality of findings, identifying blind spots, and deciding
   when the output is good enough. This is a higher-level role, not no role.

4. **There are real decisions with real tradeoffs.** How many rounds? How much
   scaffolding? When does a nudge become a script? When do you stop iterating?
   These aren't technical questions — they're judgment calls that require
   understanding both the AI's capabilities and the domain.
