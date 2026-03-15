# CASBO 2026 Demo: Synthetic Survey Corpus

Synthetic survey corpus for the CASBO 2026 presentation on agentic AI. Simulates 500 staff responses from Tri-Valley Unified School District about a new communications system installation.

The corpus has engineered patterns at three difficulty levels (obvious, intermediate, hidden) designed for agentic discovery during the live demo.

## Data Files

### `survey_pdfs/` — Repo 1 (Raw Surveys → Structured Data)
500 individual PDF survey forms. Each contains the respondent's name, site, position, years bands, and open-ended answers to 5 questions. 75 PDFs (15%) use a handwriting-style font; the rest use varied standard fonts with randomized formatting.

This is the raw starting point for the extraction demo.

### `data/extracted_surveys.json` — Repo 2 & 3 (Tagging & Reports)
What the extraction pipeline would produce from the PDFs. One record per respondent with:

| Field | Example |
|---|---|
| `respondent_id` | `1` |
| `name` | `"Eduardo Gutierrez"` |
| `site` | `"Riverside Elementary"` |
| `position` | `"Teacher"` |
| `years_at_district_band` | `"11-20"` |
| `years_in_profession_band` | `"16-25"` |
| `q1` through `q5` | Open-ended text or `null` |

Use this file for the tagging phase (sentiment, theme discovery, theme application) and for generating reports. It contains only what a survey extraction would give you — no HR demographics.

### `data/hr_database.json` — Repo 4 (Auto-Research, joined with extracted surveys)
Simulates the district HR system. One record per employee with:

| Field | Example |
|---|---|
| `employee_id` | `"TV-0001"` |
| `name` | `"Eduardo Gutierrez"` |
| `site` | `"Riverside Elementary"` |
| `position` | `"Teacher"` |
| `age` | `43` |
| `gender` | `"Male"` |
| `race_ethnicity` | `"Hispanic/Latino"` |
| `years_at_district` | `11` (exact, not banded) |
| `years_in_profession` | `22` (exact, not banded) |
| `is_transfer` | `false` |
| `origin_district_system_quality` | `null` / `"worse"` / `"comparable"` / `"better"` |
| `building_wing` | `null` or `"North Wing"` |
| `room_type` | `"Standard"` or `"Large/Specialized"` |

Joining this with `extracted_surveys.json` on `name` is what unlocks the hidden patterns in Phase 4.

### `data/survey_full_dataset.json` — Repo 4 (Pre-joined, ready to use)
The extracted surveys and HR database already joined into a single file. 500 records, 20 fields each — all survey responses plus all HR demographics. Use this if you don't want to demo the join step.

### `data/population_roster.json` — QC Only
Ground truth with attitude scores (1-5 scale) that drove response generation, plus all demographic fields and special flags. Not used in any demo repo — only for verifying that patterns were correctly embedded.

## Engineered Patterns

### Obvious (discoverable from extracted surveys alone)
- **Valley High workflow disruption** — VH staff more negative on workflow impact than elementary sites
- **Long-tenured communication gap** — 20+ year staff feel administration didn't inform them
- **Classified staff training gap** — paras, custodial, food service rate reliability higher but training lower than certificated staff

### Intermediate (require cross-tabulation or theme analysis)
- **Food service scheduling chaos** — lowest workflow scores of any group, driven by bell schedule changes disrupting lunch timing (not system quality)
- **Counselor split** — high on reliability/safety features, low on workflow due to intercom interruptions during confidential student sessions
- **District office positivity** — most positive group overall (involved in vendor selection)

### Hidden (require HR data join + subgroup analysis)
- **Hillcrest wing anomaly** — 30 staff in the north wing have hardware problems masked by site-level averages. Only surfaces by analyzing within Hillcrest (`building_wing` field)
- **Transfer paradox** — staff from districts with worse systems are among the most positive; staff from better systems are more negative than even long-tenured staff (`origin_district_system_quality` field)
- **Experienced newcomer effect** — older staff negativity is driven by age × tenure interaction, not age alone. Older staff who are new to the district are surprisingly positive
- **Valley High bright spot** — performing arts/CTE teachers in large rooms rate the system highly despite overall VH negativity (`room_type` field)
