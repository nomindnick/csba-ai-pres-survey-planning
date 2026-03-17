#!/usr/bin/env python3
"""Tenure vs. Sentiment Analysis for Tri-Valley USD Survey Data."""

import json
import re
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "survey_full_dataset.json"

with open(DATA_PATH) as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# --- 1. Sentiment scoring via keyword matching ---

POS_WORDS = re.compile(
    r"\b(improved|better|great|smooth|easy|easier|helpful|clear|clearer|"
    r"intuitive|excellent|appreciate|love|wonderful|seamless|efficient|"
    r"comfortable|confident|positive|well|good)\b",
    re.IGNORECASE,
)
NEG_WORDS = re.compile(
    r"\b(frustrated|frustrating|disrupted|disruption|poor|problem|problems|"
    r"issue|issues|difficult|rushed|confused|confusing|worse|struggle|"
    r"overwhelmed|inadequate|lacking|chaotic|terrible|annoying|"
    r"blindsided|complained|broken|failed|failure|clunky|nightmare)\b",
    re.IGNORECASE,
)

QUESTIONS = ["q1", "q2", "q3", "q4", "q5"]


def sentiment_score(text: str) -> float:
    """Return sentiment as (pos - neg) / (pos + neg), or 0 if no keywords."""
    if not text:
        return 0.0
    pos = len(POS_WORDS.findall(text))
    neg = len(NEG_WORDS.findall(text))
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def avg_sentiment(record) -> float:
    """Average sentiment across all 5 questions for one respondent."""
    scores = [sentiment_score(record.get(q, "")) for q in QUESTIONS]
    return sum(scores) / len(scores)


# Attach sentiment to each record
for r in data:
    r["_sentiment"] = avg_sentiment(r)
    for q in QUESTIONS:
        r[f"_{q}_sent"] = sentiment_score(r.get(q, "") or "")

# --- 2. Group statistics by tenure bands ---

def group_stats(records, label="group"):
    """Compute mean sentiment and per-question means for a list of records."""
    n = len(records)
    if n == 0:
        return None
    overall = sum(r["_sentiment"] for r in records) / n
    per_q = {}
    for q in QUESTIONS:
        per_q[q] = sum(r[f"_{q}_sent"] for r in records) / n
    return {"label": label, "n": n, "mean_sentiment": overall, "per_question": per_q}


# Group by years_at_district_band
district_bands = defaultdict(list)
for r in data:
    district_bands[r["years_at_district_band"]].append(r)

# Group by years_in_profession_band
profession_bands = defaultdict(list)
for r in data:
    profession_bands[r["years_in_profession_band"]].append(r)

DISTRICT_ORDER = ["0-3", "4-10", "11-20", "20+"]
PROFESSION_ORDER = ["0-5", "6-15", "16-25", "25+"]

print("\n" + "=" * 70)
print("YEARS AT DISTRICT — Sentiment by Band")
print("=" * 70)
for band in DISTRICT_ORDER:
    s = group_stats(district_bands[band], band)
    if s:
        print(f"  {band:>5}  (n={s['n']:>3})  mean_sentiment = {s['mean_sentiment']:+.3f}   "
              f"| q1={s['per_question']['q1']:+.3f}  q2={s['per_question']['q2']:+.3f}  "
              f"q3={s['per_question']['q3']:+.3f}  q4={s['per_question']['q4']:+.3f}  "
              f"q5={s['per_question']['q5']:+.3f}")

print("\n" + "=" * 70)
print("YEARS IN PROFESSION — Sentiment by Band")
print("=" * 70)
for band in PROFESSION_ORDER:
    s = group_stats(profession_bands[band], band)
    if s:
        print(f"  {band:>5}  (n={s['n']:>3})  mean_sentiment = {s['mean_sentiment']:+.3f}   "
              f"| q1={s['per_question']['q1']:+.3f}  q2={s['per_question']['q2']:+.3f}  "
              f"q3={s['per_question']['q3']:+.3f}  q4={s['per_question']['q4']:+.3f}  "
              f"q5={s['per_question']['q5']:+.3f}")

# --- 3. Tenure × Site interaction ---

sites = sorted(set(r["site"] for r in data))

print("\n" + "=" * 70)
print("YEARS AT DISTRICT × SITE — Mean Sentiment")
print("=" * 70)
header = f"{'Site':<30}" + "".join(f"{b:>12}" for b in DISTRICT_ORDER)
print(header)
print("-" * len(header))
for site in sites:
    row = f"{site:<30}"
    for band in DISTRICT_ORDER:
        subset = [r for r in data if r["site"] == site and r["years_at_district_band"] == band]
        if subset:
            m = sum(r["_sentiment"] for r in subset) / len(subset)
            row += f"  {m:+.3f}({len(subset):>2})"
        else:
            row += f"{'---':>12}"
    print(row)

print("\n" + "=" * 70)
print("YEARS IN PROFESSION × SITE — Mean Sentiment")
print("=" * 70)
header = f"{'Site':<30}" + "".join(f"{b:>12}" for b in PROFESSION_ORDER)
print(header)
print("-" * len(header))
for site in sites:
    row = f"{site:<30}"
    for band in PROFESSION_ORDER:
        subset = [r for r in data if r["site"] == site and r["years_in_profession_band"] == band]
        if subset:
            m = sum(r["_sentiment"] for r in subset) / len(subset)
            row += f"  {m:+.3f}({len(subset):>2})"
        else:
            row += f"{'---':>12}"
    print(row)

# --- 4. Thematic analysis: "old system" mentions and "training" focus ---

OLD_SYSTEM_RE = re.compile(r"\b(old system|old one|previous system|used to|before the change|what we had|how it was)\b", re.IGNORECASE)
TRAINING_RE = re.compile(r"\b(training|learn|learning|tutorial|instruction|workshop|onboarding|hands-on)\b", re.IGNORECASE)

print("\n" + "=" * 70)
print("THEMATIC: 'Old system' mentions by district tenure band")
print("=" * 70)
for band in DISTRICT_ORDER:
    recs = district_bands[band]
    n = len(recs)
    mentions = sum(1 for r in recs if any(OLD_SYSTEM_RE.search(r.get(q, "") or "" or "") for q in QUESTIONS))
    pct = mentions / n * 100 if n else 0
    print(f"  {band:>5}  (n={n:>3})  mentions 'old system': {mentions:>3} ({pct:.1f}%)")

print("\n" + "=" * 70)
print("THEMATIC: 'Training' focus by district tenure band")
print("=" * 70)
for band in DISTRICT_ORDER:
    recs = district_bands[band]
    n = len(recs)
    # Count total training mentions per person, then average
    counts = [sum(len(TRAINING_RE.findall(r.get(q, "") or "")) for q in QUESTIONS) for r in recs]
    avg_count = sum(counts) / n if n else 0
    mentions = sum(1 for c in counts if c > 0)
    pct = mentions / n * 100 if n else 0
    print(f"  {band:>5}  (n={n:>3})  people mentioning training: {mentions:>3} ({pct:.1f}%)  avg mentions/person: {avg_count:.2f}")

print("\n" + "=" * 70)
print("THEMATIC: 'Training' focus by profession tenure band")
print("=" * 70)
for band in PROFESSION_ORDER:
    recs = profession_bands[band]
    n = len(recs)
    counts = [sum(len(TRAINING_RE.findall(r.get(q, "") or "")) for q in QUESTIONS) for r in recs]
    avg_count = sum(counts) / n if n else 0
    mentions = sum(1 for c in counts if c > 0)
    pct = mentions / n * 100 if n else 0
    print(f"  {band:>5}  (n={n:>3})  people mentioning training: {mentions:>3} ({pct:.1f}%)  avg mentions/person: {avg_count:.2f}")

# --- 5. Representative quotes ---

def get_extreme_quotes(records, band_label, n_quotes=3):
    """Get most positive and most negative respondents and pull quotes."""
    sorted_recs = sorted(records, key=lambda r: r["_sentiment"])
    most_neg = sorted_recs[:n_quotes]
    most_pos = sorted_recs[-n_quotes:]
    return most_neg, most_pos


print("\n" + "=" * 70)
print("REPRESENTATIVE QUOTES — Newest staff (0-3 years at district)")
print("=" * 70)
newest = district_bands["0-3"]
neg, pos = get_extreme_quotes(newest, "0-3")
print("\n  Most POSITIVE newest staff:")
for r in pos:
    print(f"\n  [{r['employee_id']}] {r['name']} — {r['position']} at {r['site']}")
    print(f"  District tenure: {r['years_at_district']}y | Profession: {r['years_in_profession']}y | Sentiment: {r['_sentiment']:+.3f}")
    # Pick the question with highest sentiment
    best_q = max(QUESTIONS, key=lambda q: r[f"_{q}_sent"])
    print(f"  ({best_q}): \"{r[best_q][:200]}...\"" if len(r[best_q]) > 200 else f"  ({best_q}): \"{r[best_q]}\"")

print("\n  Most NEGATIVE newest staff:")
for r in neg:
    print(f"\n  [{r['employee_id']}] {r['name']} — {r['position']} at {r['site']}")
    print(f"  District tenure: {r['years_at_district']}y | Profession: {r['years_in_profession']}y | Sentiment: {r['_sentiment']:+.3f}")
    worst_q = min(QUESTIONS, key=lambda q: r[f"_{q}_sent"])
    print(f"  ({worst_q}): \"{r[worst_q][:200]}...\"" if len(r[worst_q]) > 200 else f"  ({worst_q}): \"{r[worst_q]}\"")

print("\n" + "=" * 70)
print("REPRESENTATIVE QUOTES — Most veteran staff (20+ years at district)")
print("=" * 70)
veterans = district_bands["20+"]
neg, pos = get_extreme_quotes(veterans, "20+")
print("\n  Most POSITIVE veterans:")
for r in pos:
    print(f"\n  [{r['employee_id']}] {r['name']} — {r['position']} at {r['site']}")
    print(f"  District tenure: {r['years_at_district']}y | Profession: {r['years_in_profession']}y | Sentiment: {r['_sentiment']:+.3f}")
    best_q = max(QUESTIONS, key=lambda q: r[f"_{q}_sent"])
    print(f"  ({best_q}): \"{r[best_q][:200]}...\"" if len(r[best_q]) > 200 else f"  ({best_q}): \"{r[best_q]}\"")

print("\n  Most NEGATIVE veterans:")
for r in neg:
    print(f"\n  [{r['employee_id']}] {r['name']} — {r['position']} at {r['site']}")
    print(f"  District tenure: {r['years_at_district']}y | Profession: {r['years_in_profession']}y | Sentiment: {r['_sentiment']:+.3f}")
    worst_q = min(QUESTIONS, key=lambda q: r[f"_{q}_sent"])
    print(f"  ({worst_q}): \"{r[worst_q][:200]}...\"" if len(r[worst_q]) > 200 else f"  ({worst_q}): \"{r[worst_q]}\"")

# --- 6. Summary statistics ---

print("\n" + "=" * 70)
print("SUMMARY: Spread within tenure bands (std dev of sentiment)")
print("=" * 70)
import statistics
for band in DISTRICT_ORDER:
    recs = district_bands[band]
    sentiments = [r["_sentiment"] for r in recs]
    if len(sentiments) > 1:
        sd = statistics.stdev(sentiments)
        print(f"  {band:>5}  (n={len(recs):>3})  mean={statistics.mean(sentiments):+.3f}  stdev={sd:.3f}")

print("\n" + "=" * 70)
print("OVERALL DATASET SENTIMENT DISTRIBUTION")
print("=" * 70)
all_sents = [r["_sentiment"] for r in data]
print(f"  Mean: {statistics.mean(all_sents):+.3f}")
print(f"  Median: {statistics.median(all_sents):+.3f}")
print(f"  Stdev: {statistics.stdev(all_sents):.3f}")
print(f"  Min: {min(all_sents):+.3f}  Max: {max(all_sents):+.3f}")

# Positive / negative / neutral breakdown
n_pos = sum(1 for s in all_sents if s > 0.05)
n_neg = sum(1 for s in all_sents if s < -0.05)
n_neu = len(all_sents) - n_pos - n_neg
print(f"  Positive (>0.05): {n_pos} ({n_pos/len(data)*100:.1f}%)")
print(f"  Neutral: {n_neu} ({n_neu/len(data)*100:.1f}%)")
print(f"  Negative (<-0.05): {n_neg} ({n_neg/len(data)*100:.1f}%)")
