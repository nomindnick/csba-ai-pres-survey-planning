# Act 4: Agentic Research

## Context

You are analyzing 500 staff survey responses from Tri-Valley Unified School
District about a new communications system installation. The data has already
been extracted, tagged, and joined with HR demographic data. Your job is to
conduct autonomous research — discover patterns, anomalies, and insights that
simple reporting wouldn't reveal.

## Data

`data/survey_full_dataset.json` — 500 records, each with:
- Demographics: site, position, age, gender, race_ethnicity
- Tenure: years_at_district, years_in_profession (exact + banded)
- HR fields: is_transfer, origin_district_system_quality, building_wing, room_type
- Survey responses: q1 through q5 (open-ended text about the installation experience)

## Research Loop

Your research is driven by an iterative loop with external scoring. The loop
continues until the judge score reaches **8.0 or higher**, or you have completed
**12 rounds** (whichever comes first).

### Loop Structure

```
REPEAT:
  1. Read output/experiment_log.tsv and latest judge feedback
  2. Plan hypotheses based on judge critique + emerging questions
  3. Investigate (subagents in parallel)
  4. Update output/round_log.md (append)
  5. Update output/research_memo.md (rewrite — this is your evolving product)
  6. Append one line to output/experiment_log.tsv
  7. Invoke the judge (see below)
  8. Save judge output to output/judge_feedback/round_N.md
  9. Update experiment_log.tsv with scores
  10. If overall_score >= 8.0 → STOP. Otherwise → next round.
```

### Invoking the Judge

After each round, run the judge by executing this command:

```bash
cat output/round_log.md output/research_memo.md | claude -p "$(cat judge_rubric.md)" --output-format json
```

Parse the JSON response to extract scores and critique. Save the full response
to `output/judge_feedback/round_N.md`. Update `output/experiment_log.tsv` with
the scores from that round.

The judge evaluates six dimensions: breadth, depth, evidence quality, rigor,
actionability, and intellectual honesty. Read the judge's `gaps` and `critique`
carefully — they tell you exactly what to investigate next.

### State Files

| File | Purpose | Update pattern |
|---|---|---|
| `output/experiment_log.tsv` | One-line-per-round score trajectory | Append after judge |
| `output/round_log.md` | Detailed findings per round | Append each round |
| `output/research_memo.md` | The evolving final report | Rewrite each round |
| `output/judge_feedback/round_N.md` | Raw judge output | Write once per round |
| `scripts/*.py` | Analysis scripts | Keep all; never delete |

The experiment log is your quick-reference orientation file. Read it at the
start of each round to understand your trajectory and what the last critique
said. You only need to read the **latest** judge feedback file in detail —
older feedback is summarized in the experiment log.

## Round Structure

Each round follows this structure:

### 1. Hypothesize
Based on the judge's critique and what you know so far, formulate 3-5 specific,
testable hypotheses. Good hypotheses target:
- Group differences (does group X differ from group Y on dimension Z?)
- Anomalies (does a subgroup deviate from its parent group's trend?)
- Interactions (is the effect of A different depending on B?)
- Within-group variation (does a site-level average mask internal differences?)
- Alternative explanations (is the effect really driven by X, or by Y which correlates with X?)
- Gaps identified by the judge (these take priority)

### 2. Investigate
Spin up subagents to test your hypotheses in parallel. Each subagent should:
- **Quantify**: Write and run a Python script to compute group statistics,
  cross-tabulations, or comparisons relevant to the hypothesis
- **Qualify**: Read representative responses from the relevant subgroup to
  understand the *why* behind the numbers
- Return a structured finding: hypothesis, result (supported/refuted/partially
  supported), key statistics, representative quotes, and caveats

### 3. Synthesize
Review all subagent findings. Append the round's results to
`output/round_log.md`. Then rewrite `output/research_memo.md` incorporating
the new findings. The memo should always represent your best current
understanding — not just the latest round.

## Research Memo Format

`output/research_memo.md` should contain:
- **Executive Summary** — top findings in plain language
- **Key Findings** — each with evidence (statistics + quotes), significance,
  and caveats
- **Surprises** — findings that contradicted initial expectations
- **Limitations** — sample sizes, correlation vs. causation, what this data
  can't tell us
- **Recommended Follow-up** — what a human researcher should investigate next

Write for a non-technical audience (school business officials). Translate
statistical language into plain English. Flag small sample sizes explicitly.

## Important

- Examine ALL available fields in the dataset, including less obvious ones.
  Don't stop at site and position — the HR fields may reveal important patterns.
- Look for patterns WITHIN sites, not just between them. Site averages can mask
  important subgroup differences.
- When you find a demographic correlation (e.g., older staff are more negative),
  don't stop there. Test whether the effect holds across subgroups — does it
  look the same for newer vs. long-tenured staff? For different positions? The
  most interesting patterns in workforce data are often interactions where two
  variables together tell a different story than either alone.
- When a variable shows no overall correlation with sentiment, that does not
  mean it is irrelevant. A zero overall effect can mean the variable works in
  opposite directions for different subgroups — canceling out in the aggregate.
  Before dismissing any variable, test whether it has different effects within
  tenure bands, position groups, or other subgroups.
- Include sample sizes with every comparison. A dramatic difference in a group
  of 3 is not the same as in a group of 50.
