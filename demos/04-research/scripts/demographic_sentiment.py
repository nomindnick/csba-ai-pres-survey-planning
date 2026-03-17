#!/usr/bin/env python3
"""Analyze sentiment by gender and race_ethnicity, with tenure/site controls."""

import json
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

POSITIVE = {"great","excellent","improved","better","smooth","helpful","good","easy","appreciate","intuitive","clear"}
NEGATIVE = {"frustrated","terrible","poor","difficult","disruption","problem","issue","confusing","rushed","broken","fail","worse","struggle","complaint","disappointed"}

SMALL_N = 10  # flag groups below this

def score_text(text):
    if not text:
        return 0
    words = text.lower().split()
    # strip basic punctuation from each token
    tokens = []
    for w in words:
        clean = "".join(c for c in w if c.isalpha())
        if clean:
            tokens.append(clean)
    pos = sum(1 for t in tokens if t in POSITIVE)
    neg = sum(1 for t in tokens if t in NEGATIVE)
    return pos - neg

def score_record(rec):
    total = 0
    for q in ["q1","q2","q3","q4","q5"]:
        total += score_text(rec[q])
    return total

def group_stats(records, key_fn, label=""):
    """Return {group: {n, mean, pos_pct, neg_pct, neutral_pct}} sorted by mean."""
    buckets = defaultdict(list)
    for r in records:
        k = key_fn(r)
        if k is None:
            continue
        buckets[k].append(r["_sentiment"])

    results = {}
    for k, vals in sorted(buckets.items(), key=lambda x: -len(x[1])):
        n = len(vals)
        mean = sum(vals) / n
        pos = sum(1 for v in vals if v > 0)
        neg = sum(1 for v in vals if v < 0)
        neu = n - pos - neg
        flag = " *** SMALL N ***" if n < SMALL_N else ""
        results[k] = {"n": n, "mean": round(mean, 2),
                       "pos_pct": round(100*pos/n, 1),
                       "neg_pct": round(100*neg/n, 1),
                       "neu_pct": round(100*neu/n, 1),
                       "small": n < SMALL_N}
    return results

def print_table(title, stats, indent=0):
    prefix = "  " * indent
    print(f"\n{prefix}{'='*60}")
    print(f"{prefix}{title}")
    print(f"{prefix}{'='*60}")
    print(f"{prefix}{'Group':<30} {'N':>5} {'Mean':>7} {'%Pos':>6} {'%Neg':>6} {'%Neu':>6}")
    print(f"{prefix}{'-'*60}")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]['mean']):
        flag = " *" if v['small'] else ""
        print(f"{prefix}{str(k):<30} {v['n']:>5} {v['mean']:>7.2f} {v['pos_pct']:>5.1f}% {v['neg_pct']:>5.1f}% {v['neu_pct']:>5.1f}%{flag}")
    print(f"{prefix}(* = sample size < {SMALL_N}, interpret with caution)")

# ---- Load & score ----
with open(DATA) as f:
    data = json.load(f)

for r in data:
    r["_sentiment"] = score_record(r)

print(f"Total records: {len(data)}")
overall_mean = sum(r["_sentiment"] for r in data) / len(data)
print(f"Overall mean sentiment: {overall_mean:.2f}")

# ---- 1. Gender distribution ----
print("\n\n### GENDER DISTRIBUTION ###")
gender_counts = defaultdict(int)
for r in data:
    gender_counts[r["gender"]] += 1
for g, c in sorted(gender_counts.items(), key=lambda x: -x[1]):
    print(f"  {g}: {c}")

# ---- 2. Sentiment by gender ----
stats = group_stats(data, lambda r: r["gender"])
print_table("SENTIMENT BY GENDER", stats)

# ---- 3. Race/ethnicity distribution ----
print("\n\n### RACE/ETHNICITY DISTRIBUTION ###")
race_counts = defaultdict(int)
for r in data:
    race_counts[r["race_ethnicity"]] += 1
for g, c in sorted(race_counts.items(), key=lambda x: -x[1]):
    print(f"  {g}: {c}")

# ---- 4. Sentiment by race_ethnicity ----
stats = group_stats(data, lambda r: r["race_ethnicity"])
print_table("SENTIMENT BY RACE/ETHNICITY", stats)

# ---- 5. Cross-tab: gender × site ----
print("\n\n### CROSS-TAB: GENDER × SITE ###")
sites = sorted(set(r["site"] for r in data))
genders = sorted(set(r["gender"] for r in data))

for site in sites:
    site_data = [r for r in data if r["site"] == site]
    stats = group_stats(site_data, lambda r: r["gender"], label=site)
    print_table(f"Gender sentiment at {site} (site n={len(site_data)})", stats, indent=1)

# ---- 6. Cross-tab: race_ethnicity × tenure_band ----
print("\n\n### CROSS-TAB: RACE/ETHNICITY × TENURE BAND ###")
tenure_bands = sorted(set(r["years_at_district_band"] for r in data))
races = sorted(set(r["race_ethnicity"] for r in data))

# First show the count matrix
print(f"\n{'Band':<12}", end="")
for race in races:
    print(f" {race[:12]:>12}", end="")
print()
for band in tenure_bands:
    band_data = [r for r in data if r["years_at_district_band"] == band]
    print(f"{band:<12}", end="")
    for race in races:
        n = sum(1 for r in band_data if r["race_ethnicity"] == race)
        print(f" {n:>12}", end="")
    print()

# ---- 7. Within each tenure band, sentiment by race ----
print("\n\n### WITHIN TENURE BAND: SENTIMENT BY RACE/ETHNICITY ###")
for band in tenure_bands:
    band_data = [r for r in data if r["years_at_district_band"] == band]
    stats = group_stats(band_data, lambda r: r["race_ethnicity"])
    print_table(f"Race/ethnicity sentiment in tenure band '{band}' (band n={len(band_data)})", stats, indent=1)

# ---- 8. Within each tenure band, sentiment by gender ----
print("\n\n### WITHIN TENURE BAND: SENTIMENT BY GENDER ###")
for band in tenure_bands:
    band_data = [r for r in data if r["years_at_district_band"] == band]
    stats = group_stats(band_data, lambda r: r["gender"])
    print_table(f"Gender sentiment in tenure band '{band}' (band n={len(band_data)})", stats, indent=1)

# ---- 9. Summary: largest gaps ----
print("\n\n### SUMMARY: KEY GAPS ###")
print("\nGender gap (overall):")
g_stats = group_stats(data, lambda r: r["gender"])
if "Male" in g_stats and "Female" in g_stats:
    gap = g_stats["Male"]["mean"] - g_stats["Female"]["mean"]
    print(f"  Male mean: {g_stats['Male']['mean']:.2f} (n={g_stats['Male']['n']})")
    print(f"  Female mean: {g_stats['Female']['mean']:.2f} (n={g_stats['Female']['n']})")
    print(f"  Gap (M-F): {gap:+.2f}")

print("\nRace/ethnicity range (overall):")
r_stats = group_stats(data, lambda r: r["race_ethnicity"])
means = [(k, v["mean"], v["n"]) for k, v in r_stats.items()]
means.sort(key=lambda x: x[1])
print(f"  Lowest:  {means[0][0]} = {means[0][1]:.2f} (n={means[0][2]})")
print(f"  Highest: {means[-1][0]} = {means[-1][1]:.2f} (n={means[-1][2]})")
print(f"  Range: {means[-1][1] - means[0][1]:.2f}")

# Check if race gap persists within largest tenure bands
print("\nRace gap within largest tenure bands (n>=30):")
for band in tenure_bands:
    band_data = [r for r in data if r["years_at_district_band"] == band]
    if len(band_data) < 30:
        continue
    stats = group_stats(band_data, lambda r: r["race_ethnicity"])
    viable = {k: v for k, v in stats.items() if v["n"] >= SMALL_N}
    if len(viable) >= 2:
        vals = [(k, v["mean"], v["n"]) for k, v in viable.items()]
        vals.sort(key=lambda x: x[1])
        print(f"  Band '{band}' (n={len(band_data)}):")
        for k, m, n in vals:
            print(f"    {k}: mean={m:.2f} (n={n})")
        print(f"    Range: {vals[-1][1] - vals[0][1]:.2f}")
