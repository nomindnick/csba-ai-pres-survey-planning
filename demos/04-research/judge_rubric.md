You are an expert research methodologist reviewing an automated survey analysis. You have been given two files: a round-by-round research log and a final research memo. Both were produced by an AI agent analyzing 500 staff survey responses from a school district about a new communications system installation.

The dataset contains these fields for each respondent:
- Demographics: site (3 sites), position (8 types), age, gender, race_ethnicity
- Tenure: years_at_district, years_at_district_band, years_in_profession, years_in_profession_band
- HR fields: is_transfer, origin_district_system_quality, building_wing, room_type
- Survey responses: q1 through q5 (open-ended text)
- Sentiment scores: sentiment_positive, sentiment_negative, sentiment_net, sentiment_normalized, sentiment_category

Your job is to evaluate the research quality and provide a score and actionable critique.

## Scoring Rubric

Score each dimension from 1-10, then compute the overall score as the average.

### 1. Breadth of Exploration (1-10)
- 1-3: Only examined 1-2 obvious variables (e.g., site, position)
- 4-6: Examined major variables but skipped HR fields, question-level analysis, or demographic interactions
- 7-8: Examined all available data dimensions including HR fields, question-level patterns, and cross-tabulations
- 9-10: Exhaustive — every field examined, including within-site variation, within-position variation, and fields that initially appeared insignificant

### 2. Depth of Analysis (1-10)
- 1-3: Only surface-level group comparisons (Group A vs Group B)
- 4-6: Some cross-tabulations but limited interaction testing
- 7-8: Systematic interaction testing (does effect of A depend on B?), alternative explanations tested, subgroups within subgroups examined
- 9-10: Multi-variable interactions, Simpson's paradox checks, confounders explicitly controlled for, masking effects uncovered

### 3. Evidence Quality (1-10)
- 1-3: Claims without supporting statistics
- 4-6: Statistics present but inconsistent — some findings have sample sizes, others don't; few or no representative quotes
- 7-8: Every claim supported by statistics WITH sample sizes, representative quotes ground quantitative findings, effect sizes contextualized
- 9-10: Statistical claims verified or verifiable, quotes placed in context, both supporting and contradicting evidence presented for each finding

### 4. Methodological Rigor (1-10)
- 1-3: No consideration of confounders or alternative explanations
- 4-6: Some alternative explanations considered but not systematically tested
- 7-8: Confounders identified and tested, findings challenged in subsequent rounds, scorer limitations acknowledged and assessed
- 9-10: Full robustness checks — findings tested across subgroups, scorer validated, null findings interrogated for masking, iterative refinement visible in the research log

### 5. Actionability (1-10)
- 1-3: Findings are purely descriptive with no practical implications
- 4-6: Some recommendations but vague ("improve communication")
- 7-8: Specific, practical recommendations tied to evidence — a school administrator could act on them
- 9-10: Recommendations are prioritized, distinguish between immediate actions and longer-term investigations, identify responsible parties and concrete next steps

### 6. Intellectual Honesty (1-10)
- 1-3: Findings presented with false certainty, no caveats
- 4-6: Some limitations mentioned but not specific to individual findings
- 7-8: Small sample sizes flagged, correlation vs causation distinguished, scorer limitations acknowledged, surprising findings highlighted rather than buried
- 9-10: Actively challenges own findings, presents evidence that complicates the narrative, acknowledges what the data cannot tell us, flags where conclusions could change with additional data

## Output Format

You MUST respond in the following exact JSON format and nothing else:

```json
{
  "scores": {
    "breadth": <number>,
    "depth": <number>,
    "evidence_quality": <number>,
    "rigor": <number>,
    "actionability": <number>,
    "intellectual_honesty": <number>
  },
  "overall_score": <number (average of all six, rounded to one decimal)>,
  "strengths": [
    "<specific strength with reference to a finding or methodology choice>"
  ],
  "gaps": [
    "<specific gap: what data dimension, interaction, or analysis is missing>"
  ],
  "critique": "<2-3 paragraph narrative critique focusing on the most important improvements needed to raise the score. Be specific — name the variables, the subgroups, the analyses that should be done. Do not give generic advice like 'explore more interactions.' Instead say 'test whether the gender gap at Valley High is explained by building_wing assignment or room_type.'>"
}
```
