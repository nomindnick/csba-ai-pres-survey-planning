#!/usr/bin/env python3
"""Refined hedging analysis — filter false positives from 'at least' used quantitatively."""

import json
import re
from collections import Counter, defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA) as f:
    data = json.load(f)

questions = ["q1", "q2", "q3", "q4", "q5"]

# Phrases that are almost always genuine hedging
STRONG_HEDGE = [
    r"it'?s fine", r"it\u2019s fine",
    r"i guess",
    r"i suppose",
    r"not terrible",
    r"could be worse", r"could have been worse",
    r"it'?s okay", r"it\u2019s okay",
    r"it'?s alright", r"it\u2019s alright",
    r"good enough",
    r"can'?t complain", r"can\u2019t complain",
    r"not the worst",
]

# "at least" is hedging only when NOT followed by a number/quantifier
# e.g., "at least it works" = hedging; "at least three times" = not hedging
AT_LEAST_HEDGE = re.compile(r"at least(?!\s+\d|\s+once|\s+twice|\s+three|\s+four|\s+five|\s+six|\s+seven|\s+eight|\s+nine|\s+ten|\s+one|\s+two|\s+a\s+(few|couple|dozen))", re.IGNORECASE)

STRONG_RE = re.compile("|".join(STRONG_HEDGE), re.IGNORECASE)

print(f"Total records: {len(data)}")

hedger_ids = set()
hedger_records = []
hedge_details = []

for rec in data:
    found_any = False
    for q in questions:
        text = rec.get(q)
        if not text:
            continue
        # Check strong phrases
        strong_matches = STRONG_RE.findall(text)
        for m in strong_matches:
            hedge_details.append((rec["employee_id"], q, m.lower(), text))
            found_any = True
        # Check "at least" with context filter
        at_least_matches = AT_LEAST_HEDGE.findall(text)
        # findall won't work well here since it's a zero-width lookahead; use finditer
        for m in AT_LEAST_HEDGE.finditer(text):
            hedge_details.append((rec["employee_id"], q, "at least [hedging]", text))
            found_any = True
    if found_any:
        hedger_ids.add(rec["employee_id"])
        hedger_records.append(rec)

non_hedgers = [r for r in data if r["employee_id"] not in hedger_ids]

print(f"Hedgers (refined): {len(hedger_records)} ({100*len(hedger_records)/len(data):.1f}%)")
print(f"Hedging instances: {len(hedge_details)}")

phrase_counts = Counter(d[2] for d in hedge_details)
print("\nPhrase frequency (refined):")
for phrase, cnt in phrase_counts.most_common():
    print(f"  '{phrase}': {cnt}")

# ── Disproportionality ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("HEDGER RATE BY GROUP (with over/under-representation)")
print(f"{'='*60}")
baseline = len(hedger_records) / len(data)
print(f"Overall hedger rate: {100*baseline:.1f}%\n")

for field in ["site", "position", "years_at_district_band", "gender",
              "race_ethnicity", "is_transfer", "sentiment_category",
              "room_type", "building_wing"]:
    print(f"  {field}:")
    groups = defaultdict(lambda: {"total": 0, "hedgers": 0})
    for rec in data:
        val = str(rec.get(field, "N/A"))
        groups[val]["total"] += 1
        if rec["employee_id"] in hedger_ids:
            groups[val]["hedgers"] += 1
    for val, g in sorted(groups.items(), key=lambda x: -x[1]["hedgers"]/max(x[1]["total"],1)):
        rate = g["hedgers"] / g["total"] if g["total"] else 0
        ratio = rate / baseline if baseline else 0
        marker = ""
        if ratio > 1.3:
            marker = " ** OVER"
        elif ratio < 0.7:
            marker = " ** UNDER"
        print(f"    {val}: {g['hedgers']}/{g['total']} = {100*rate:.1f}% (ratio={ratio:.2f}){marker}")
    print()

# ── Numeric comparisons ──────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("HEDGERS vs NON-HEDGERS: Key metrics")
print(f"{'='*60}")

for field in ["age", "years_at_district", "years_in_profession",
              "sentiment_net", "sentiment_normalized"]:
    h_vals = [r[field] for r in hedger_records if r.get(field) is not None]
    n_vals = [r[field] for r in non_hedgers if r.get(field) is not None]
    h_mean = sum(h_vals)/len(h_vals) if h_vals else 0
    n_mean = sum(n_vals)/len(n_vals) if n_vals else 0
    print(f"  {field}: hedgers={h_mean:.2f} (n={len(h_vals)}) vs non-hedgers={n_mean:.2f} (n={len(n_vals)}), diff={h_mean-n_mean:+.2f}")

# ── Sentiment recategorization ────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SENTIMENT RECATEGORIZATION")
print(f"{'='*60}")

hedge_sent = Counter(r["sentiment_category"] for r in hedger_records)
print(f"\nHedger sentiment breakdown:")
for cat in ["positive", "neutral", "negative"]:
    cnt = hedge_sent.get(cat, 0)
    print(f"  {cat}: {cnt} ({100*cnt/len(hedger_records):.1f}%)")

overall_sent = Counter(r["sentiment_category"] for r in data)
print(f"\nOverall sentiment breakdown:")
for cat in ["positive", "neutral", "negative"]:
    cnt = overall_sent.get(cat, 0)
    print(f"  {cat}: {cnt} ({100*cnt/len(data):.1f}%)")

# Recategorize: neutral hedgers → mildly negative, positive hedgers → neutral
print(f"\n--- WHAT-IF: Reclassify neutral hedgers as negative, positive hedgers as neutral ---")
new_sent = Counter(r["sentiment_category"] for r in data)
neutral_hedge_n = sum(1 for r in hedger_records if r["sentiment_category"] == "neutral")
positive_hedge_n = sum(1 for r in hedger_records if r["sentiment_category"] == "positive")
new_sent["neutral"] -= neutral_hedge_n
new_sent["negative"] += neutral_hedge_n
new_sent["positive"] -= positive_hedge_n
new_sent["neutral"] += positive_hedge_n

print(f"\n  Original → Adjusted district sentiment:")
for cat in ["positive", "neutral", "negative"]:
    orig = overall_sent[cat]
    adj = new_sent[cat]
    print(f"    {cat}: {orig} ({100*orig/500:.1f}%) → {adj} ({100*adj/500:.1f}%)")

# Site-level and position-level impact with -0.3 shift
print(f"\n--- Site-level means: original vs adjusted (hedgers shifted -0.3) ---")
for site in sorted(set(r["site"] for r in data)):
    recs = [r for r in data if r["site"] == site]
    orig = sum(r["sentiment_normalized"] for r in recs)/len(recs)
    adj_scores = [r["sentiment_normalized"] - (0.3 if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral","positive") else 0) for r in recs]
    adj = sum(adj_scores)/len(adj_scores)
    nh = sum(1 for r in recs if r["employee_id"] in hedger_ids)
    print(f"  {site}: {orig:.3f} → {adj:.3f} (delta={adj-orig:+.3f}, {nh} hedgers/{len(recs)})")

print(f"\n--- Position-level means: original vs adjusted ---")
for pos in sorted(set(r["position"] for r in data)):
    recs = [r for r in data if r["position"] == pos]
    orig = sum(r["sentiment_normalized"] for r in recs)/len(recs)
    adj_scores = [r["sentiment_normalized"] - (0.3 if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral","positive") else 0) for r in recs]
    adj = sum(adj_scores)/len(adj_scores)
    nh = sum(1 for r in recs if r["employee_id"] in hedger_ids)
    print(f"  {pos}: {orig:.3f} → {adj:.3f} (delta={adj-orig:+.3f}, {nh}/{len(recs)})")

print(f"\n--- Tenure-level means: original vs adjusted ---")
for band in ["0-3", "4-10", "11-20", "20+"]:
    recs = [r for r in data if r["years_at_district_band"] == band]
    if not recs: continue
    orig = sum(r["sentiment_normalized"] for r in recs)/len(recs)
    adj_scores = [r["sentiment_normalized"] - (0.3 if r["employee_id"] in hedger_ids and r["sentiment_category"] in ("neutral","positive") else 0) for r in recs]
    adj = sum(adj_scores)/len(adj_scores)
    nh = sum(1 for r in recs if r["employee_id"] in hedger_ids)
    print(f"  {band}: {orig:.3f} → {adj:.3f} (delta={adj-orig:+.3f}, {nh}/{len(recs)})")

# ── 10 genuine hedging examples ──────────────────────────────────────────────
print(f"\n{'='*60}")
print("10 REPRESENTATIVE HEDGING RESPONSES (genuine hedging only)")
print(f"{'='*60}")

# Prioritize non-"at least" phrases for clearer examples
import random
random.seed(42)
# Sort: strong phrases first, then at least
strong = [d for d in hedge_details if d[2] != "at least [hedging]"]
weak = [d for d in hedge_details if d[2] == "at least [hedging]"]
random.shuffle(strong)
random.shuffle(weak)
candidates = strong + weak

shown = set()
count = 0
for eid, q, phrase, text in candidates:
    if eid in shown:
        continue
    shown.add(eid)
    rec = next(r for r in data if r["employee_id"] == eid)
    print(f"\n--- {eid} | {rec['position']} | {rec['site']} | tenure={rec['years_at_district']}yr | sent={rec['sentiment_category']} (net={rec['sentiment_net']}, norm={rec['sentiment_normalized']:.2f}) ---")
    # Truncate to ~250 chars
    display = text if len(text) <= 300 else text[:297] + "..."
    print(f"  [{q}] \"{display}\"")
    print(f"  Phrase: \"{phrase}\"")
    count += 1
    if count >= 10:
        break

print("\n\nDone.")
