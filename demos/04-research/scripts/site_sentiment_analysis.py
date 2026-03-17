#!/usr/bin/env python3
"""Analyze sentiment variation across the three district sites."""

import json
import statistics
from collections import Counter

DATA_PATH = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA_PATH) as f:
    data = json.load(f)

# ── 1. Mean sentiment_normalized, category distribution, sample size per site ──

sites = {}
for r in data:
    s = r["site"]
    if s not in sites:
        sites[s] = {"scores": [], "categories": [], "positions": [], "records": []}
    sites[s]["scores"].append(r["sentiment_normalized"])
    sites[s]["categories"].append(r["sentiment_category"])
    sites[s]["positions"].append(r["position"])
    sites[s]["records"].append(r)

print("=" * 70)
print("SITE-LEVEL SENTIMENT SUMMARY")
print("=" * 70)

for site in sorted(sites):
    scores = sites[site]["scores"]
    cats = Counter(sites[site]["categories"])
    n = len(scores)
    mean = statistics.mean(scores)
    median = statistics.median(scores)
    stdev = statistics.stdev(scores) if n > 1 else 0
    print(f"\n{site}  (n={n})")
    print(f"  Mean sentiment_normalized: {mean:.3f}")
    print(f"  Median:                    {median:.3f}")
    print(f"  Std dev:                   {stdev:.3f}")
    print(f"  Category distribution:")
    for cat in ["positive", "neutral", "negative"]:
        count = cats.get(cat, 0)
        pct = count / n * 100
        print(f"    {cat:10s}: {count:4d}  ({pct:5.1f}%)")

# ── 2. Representative quotes from q1 per site ──

print("\n" + "=" * 70)
print("REPRESENTATIVE q1 QUOTES BY SITE")
print("=" * 70)

for site in sorted(sites):
    records = sites[site]["records"]
    # Sort by sentiment_normalized to pick representative examples
    pos = [r for r in records if r["sentiment_category"] == "positive"]
    neg = [r for r in records if r["sentiment_category"] == "negative"]
    neu = [r for r in records if r["sentiment_category"] == "neutral"]

    # Pick one near the median of each group
    def pick_median(group):
        if not group:
            return None
        group.sort(key=lambda r: r["sentiment_normalized"])
        return group[len(group) // 2]

    print(f"\n── {site} ──")
    for label, group in [("POSITIVE", pos), ("NEUTRAL", neu), ("NEGATIVE", neg)]:
        rep = pick_median(group)
        if rep:
            q1_short = rep["q1"][:300]
            print(f"\n  [{label}] ({rep['position']}, sentiment={rep['sentiment_normalized']:.3f})")
            print(f"  \"{q1_short}{'...' if len(rep['q1']) > 300 else ''}\"")
        else:
            print(f"\n  [{label}] — no responses in this category")

# ── 3. Position-mix differences across sites ──

print("\n" + "=" * 70)
print("POSITION MIX BY SITE")
print("=" * 70)

all_positions = sorted(set(r["position"] for r in data))

for site in sorted(sites):
    pos_counts = Counter(sites[site]["positions"])
    n = len(sites[site]["positions"])
    print(f"\n{site}  (n={n})")
    for p in all_positions:
        c = pos_counts.get(p, 0)
        pct = c / n * 100
        print(f"  {p:30s}: {c:4d}  ({pct:5.1f}%)")

# ── 4. Mean sentiment by position WITHIN each site (to disentangle) ──

print("\n" + "=" * 70)
print("MEAN SENTIMENT BY POSITION WITHIN EACH SITE")
print("=" * 70)

for site in sorted(sites):
    records = sites[site]["records"]
    by_pos = {}
    for r in records:
        by_pos.setdefault(r["position"], []).append(r["sentiment_normalized"])
    print(f"\n{site}")
    for p in sorted(by_pos):
        scores = by_pos[p]
        n = len(scores)
        mean = statistics.mean(scores)
        print(f"  {p:30s}: mean={mean:+.3f}  (n={n})")

# ── 5. Overall position means for comparison ──

print("\n" + "=" * 70)
print("OVERALL MEAN SENTIMENT BY POSITION (all sites)")
print("=" * 70)

by_pos_all = {}
for r in data:
    by_pos_all.setdefault(r["position"], []).append(r["sentiment_normalized"])
for p in sorted(by_pos_all):
    scores = by_pos_all[p]
    print(f"  {p:30s}: mean={statistics.mean(scores):+.3f}  (n={len(scores)})")
