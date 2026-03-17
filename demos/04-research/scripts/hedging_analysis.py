#!/usr/bin/env python3
"""Identify and profile 'hedgers' — respondents using resigned-dissatisfaction language."""

import json
import re
from collections import Counter, defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

HEDGING_PHRASES = [
    "it's fine", "it\u2019s fine",
    "i guess",
    "at least",
    "i suppose",
    "not terrible",
    "could be worse", "could have been worse",
    "it's okay", "it\u2019s okay",
    "it's alright", "it\u2019s alright",
    "good enough",
    "can't complain", "can\u2019t complain",
    "not the worst",
]

# Build a single regex pattern (case-insensitive)
HEDGE_RE = re.compile("|".join(re.escape(p) for p in HEDGING_PHRASES), re.IGNORECASE)

with open(DATA) as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# ── 1. Identify hedgers ──────────────────────────────────────────────────────
questions = ["q1", "q2", "q3", "q4", "q5"]

hedger_ids = set()
hedger_records = []
hedge_details = []  # (employee_id, question, matched_phrase, full_text)

for rec in data:
    found_any = False
    for q in questions:
        text = rec.get(q)
        if not text:
            continue
        matches = HEDGE_RE.findall(text.lower())
        if matches:
            found_any = True
            for m in matches:
                hedge_details.append((rec["employee_id"], q, m, text))
    if found_any:
        hedger_ids.add(rec["employee_id"])
        hedger_records.append(rec)

print(f"\nHedgers found: {len(hedger_records)} ({100*len(hedger_records)/len(data):.1f}%)")
print(f"Total hedging instances: {len(hedge_details)}")

# Which phrases are most common?
phrase_counts = Counter(d[2] for d in hedge_details)
print("\nPhrase frequency:")
for phrase, cnt in phrase_counts.most_common():
    print(f"  '{phrase}': {cnt}")

# Which questions have the most hedging?
q_counts = Counter(d[1] for d in hedge_details)
print("\nHedging by question:")
for q in questions:
    print(f"  {q}: {q_counts.get(q, 0)}")

# ── 2. Profile hedgers vs overall ────────────────────────────────────────────
def profile(records, label):
    """Return distribution dicts for key fields."""
    n = len(records)
    print(f"\n{'='*60}")
    print(f"PROFILE: {label} (n={n})")
    print(f"{'='*60}")

    for field in ["site", "position", "years_at_district_band", "gender",
                   "race_ethnicity", "is_transfer", "sentiment_category",
                   "room_type", "building_wing"]:
        counts = Counter(str(r.get(field, "N/A")) for r in records)
        print(f"\n  {field}:")
        for val, cnt in counts.most_common():
            pct = 100 * cnt / n
            print(f"    {val}: {cnt} ({pct:.1f}%)")

    # Numeric summaries
    for field in ["age", "years_at_district", "years_in_profession",
                   "sentiment_net", "sentiment_normalized"]:
        vals = [r[field] for r in records if r.get(field) is not None]
        if vals:
            avg = sum(vals) / len(vals)
            vals_sorted = sorted(vals)
            med = vals_sorted[len(vals_sorted)//2]
            print(f"\n  {field}: mean={avg:.2f}, median={med}, min={min(vals)}, max={max(vals)}")

profile(data, "ALL RESPONDENTS")
profile(hedger_records, "HEDGERS")

# ── 3. Disproportionality analysis ───────────────────────────────────────────
print(f"\n{'='*60}")
print("DISPROPORTIONALITY: Hedger rate by group")
print(f"{'='*60}")

for field in ["site", "position", "years_at_district_band", "gender",
              "race_ethnicity", "is_transfer", "sentiment_category",
              "room_type"]:
    print(f"\n  {field}:")
    groups = defaultdict(lambda: {"total": 0, "hedgers": 0})
    for rec in data:
        val = str(rec.get(field, "N/A"))
        groups[val]["total"] += 1
        if rec["employee_id"] in hedger_ids:
            groups[val]["hedgers"] += 1
    for val, g in sorted(groups.items(), key=lambda x: -x[1]["hedgers"]):
        rate = 100 * g["hedgers"] / g["total"] if g["total"] else 0
        print(f"    {val}: {g['hedgers']}/{g['total']} = {rate:.1f}%")

# ── 4. Representative hedging responses ──────────────────────────────────────
print(f"\n{'='*60}")
print("10 REPRESENTATIVE HEDGING RESPONSES")
print(f"{'='*60}")

# Pick up to 10 diverse examples
import random
random.seed(42)
sample = random.sample(hedge_details, min(15, len(hedge_details)))

shown = set()
count = 0
for eid, q, phrase, text in sample:
    if eid in shown:
        continue
    shown.add(eid)
    rec = next(r for r in data if r["employee_id"] == eid)
    print(f"\n--- {eid} | {rec['position']} | {rec['site']} | {rec['years_at_district']}yr tenure | sentiment={rec['sentiment_category']} (net={rec['sentiment_net']}) ---")
    print(f"  [{q}] \"{text[:300]}{'...' if len(text)>300 else ''}\"")
    print(f"  Hedging phrase: \"{phrase}\"")
    count += 1
    if count >= 10:
        break

# ── 5. Sentiment recategorization analysis ───────────────────────────────────
print(f"\n{'='*60}")
print("SENTIMENT RECATEGORIZATION ANALYSIS")
print(f"{'='*60}")

# Current sentiment distribution of hedgers
hedge_sent = Counter(r["sentiment_category"] for r in hedger_records)
print(f"\nHedger sentiment distribution:")
for cat in ["positive", "neutral", "negative"]:
    cnt = hedge_sent.get(cat, 0)
    print(f"  {cat}: {cnt} ({100*cnt/len(hedger_records):.1f}%)")

overall_sent = Counter(r["sentiment_category"] for r in data)
print(f"\nOverall sentiment distribution:")
for cat in ["positive", "neutral", "negative"]:
    cnt = overall_sent.get(cat, 0)
    print(f"  {cat}: {cnt} ({100*cnt/len(data):.1f}%)")

# What happens if we reclassify neutral hedgers as negative?
neutral_hedgers = [r for r in hedger_records if r["sentiment_category"] == "neutral"]
positive_hedgers = [r for r in hedger_records if r["sentiment_category"] == "positive"]
print(f"\nNeutral hedgers: {len(neutral_hedgers)}")
print(f"Positive hedgers: {len(positive_hedgers)}")

# Compute site-level means: original vs adjusted
print(f"\n--- Site-level sentiment means: original vs hedgers-as-negative ---")
sites = sorted(set(r["site"] for r in data))
for site in sites:
    site_recs = [r for r in data if r["site"] == site]
    orig_mean = sum(r["sentiment_normalized"] for r in site_recs) / len(site_recs)

    # Adjusted: neutral/positive hedgers get shifted by -0.3
    adj_scores = []
    for r in site_recs:
        score = r["sentiment_normalized"]
        if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral", "positive"):
            score = score - 0.3  # shift toward negative
        adj_scores.append(score)
    adj_mean = sum(adj_scores) / len(adj_scores)

    n_hedgers_site = sum(1 for r in site_recs if r["employee_id"] in hedger_ids)
    print(f"  {site}: orig={orig_mean:.3f} adj={adj_mean:.3f} (delta={adj_mean-orig_mean:.3f}, hedgers={n_hedgers_site}/{len(site_recs)})")

# Position-level impact
print(f"\n--- Position-level sentiment means: original vs hedgers-as-negative ---")
positions = sorted(set(r["position"] for r in data))
for pos in positions:
    pos_recs = [r for r in data if r["position"] == pos]
    orig_mean = sum(r["sentiment_normalized"] for r in pos_recs) / len(pos_recs)
    adj_scores = []
    for r in pos_recs:
        score = r["sentiment_normalized"]
        if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral", "positive"):
            score = score - 0.3
        adj_scores.append(score)
    adj_mean = sum(adj_scores) / len(adj_scores)
    n_hedgers_pos = sum(1 for r in pos_recs if r["employee_id"] in hedger_ids)
    print(f"  {pos}: orig={orig_mean:.3f} adj={adj_mean:.3f} (delta={adj_mean-orig_mean:.3f}, hedgers={n_hedgers_pos}/{len(pos_recs)})")

# Tenure-level impact
print(f"\n--- Tenure-level sentiment means: original vs hedgers-as-negative ---")
bands = ["0-3", "4-10", "11-20", "21+"]
for band in bands:
    band_recs = [r for r in data if r["years_at_district_band"] == band]
    if not band_recs:
        continue
    orig_mean = sum(r["sentiment_normalized"] for r in band_recs) / len(band_recs)
    adj_scores = []
    for r in band_recs:
        score = r["sentiment_normalized"]
        if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral", "positive"):
            score = score - 0.3
        adj_scores.append(score)
    adj_mean = sum(adj_scores) / len(adj_scores)
    n_hedgers_band = sum(1 for r in band_recs if r["employee_id"] in hedger_ids)
    print(f"  {band}: orig={orig_mean:.3f} adj={adj_mean:.3f} (delta={adj_mean-orig_mean:.3f}, hedgers={n_hedgers_band}/{len(band_recs)})")

print("\n\nDone.")
