#!/usr/bin/env python3
"""
Hypothesis: Tenure (years_at_district) and age are correlated with sentiment —
longer-tenured or older staff are more negative about the change.
"""

import json
import statistics
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA) as f:
    records = json.load(f)

print(f"Total records: {len(records)}\n")

# 1. Mean sentiment_normalized by years_at_district_band
print("=" * 70)
print("1. MEAN SENTIMENT BY YEARS-AT-DISTRICT BAND")
print("=" * 70)

band_order = ["0-3", "4-10", "11-20", "20+"]
by_district_band = defaultdict(list)
for r in records:
    by_district_band[r["years_at_district_band"]].append(r["sentiment_normalized"])

for band in band_order:
    vals = by_district_band[band]
    if vals:
        mean = statistics.mean(vals)
        stdev = statistics.stdev(vals) if len(vals) > 1 else 0
        print(f"  {band:>5s}:  n={len(vals):3d}  mean={mean:+.3f}  sd={stdev:.3f}")

# 2. Mean sentiment_normalized by years_in_profession_band
print(f"\n{'=' * 70}")
print("2. MEAN SENTIMENT BY YEARS-IN-PROFESSION BAND")
print("=" * 70)

prof_band_order = ["0-5", "6-15", "16-25", "26+"]
by_prof_band = defaultdict(list)
for r in records:
    by_prof_band[r["years_in_profession_band"]].append(r["sentiment_normalized"])

for band in prof_band_order:
    vals = by_prof_band[band]
    if vals:
        mean = statistics.mean(vals)
        stdev = statistics.stdev(vals) if len(vals) > 1 else 0
        print(f"  {band:>5s}:  n={len(vals):3d}  mean={mean:+.3f}  sd={stdev:.3f}")

# 3. Correlation: age vs sentiment_normalized
print(f"\n{'=' * 70}")
print("3. CORRELATION: AGE vs SENTIMENT")
print("=" * 70)

ages = [r["age"] for r in records]
sents = [r["sentiment_normalized"] for r in records]

n = len(ages)
mean_age = statistics.mean(ages)
mean_sent = statistics.mean(sents)
sd_age = statistics.stdev(ages)
sd_sent = statistics.stdev(sents)

cov = sum((a - mean_age) * (s - mean_sent) for a, s in zip(ages, sents)) / (n - 1)
r_val = cov / (sd_age * sd_sent)

print(f"  Pearson r = {r_val:+.4f}  (n={n})")
print(f"  Mean age = {mean_age:.1f}, SD = {sd_age:.1f}")
print(f"  Mean sentiment = {mean_sent:+.3f}, SD = {sd_sent:.3f}")

# Bucket by age decade
print("\n  Sentiment by age decade:")
by_age_decade = defaultdict(list)
for r in records:
    decade = (r["age"] // 10) * 10
    by_age_decade[decade].append(r["sentiment_normalized"])

for decade in sorted(by_age_decade):
    vals = by_age_decade[decade]
    mean = statistics.mean(vals)
    print(f"    {decade}s:  n={len(vals):3d}  mean={mean:+.3f}")

# Continuous correlations
district_years = [r["years_at_district"] for r in records]
mean_dy = statistics.mean(district_years)
sd_dy = statistics.stdev(district_years)
cov_dy = sum((d - mean_dy) * (s - mean_sent) for d, s in zip(district_years, sents)) / (n - 1)
r_dy = cov_dy / (sd_dy * sd_sent)
print(f"\n  Pearson r (years_at_district vs sentiment) = {r_dy:+.4f}")

prof_years = [r["years_in_profession"] for r in records]
mean_py = statistics.mean(prof_years)
sd_py = statistics.stdev(prof_years)
cov_py = sum((p - mean_py) * (s - mean_sent) for p, s in zip(prof_years, sents)) / (n - 1)
r_py = cov_py / (sd_py * sd_sent)
print(f"  Pearson r (years_in_profession vs sentiment) = {r_py:+.4f}")

# 4. Tenure effect by site
print(f"\n{'=' * 70}")
print("4. TENURE EFFECT BY SITE")
print("=" * 70)

sites = sorted(set(r["site"] for r in records))
for site in sites:
    print(f"\n  {site}:")
    site_records = [r for r in records if r["site"] == site]
    for band in band_order:
        vals = [r["sentiment_normalized"] for r in site_records if r["years_at_district_band"] == band]
        if vals:
            mean = statistics.mean(vals)
            print(f"    {band:>5s}:  n={len(vals):3d}  mean={mean:+.3f}")
        else:
            print(f"    {band:>5s}:  n=  0  (no data)")

print(f"\n{'=' * 70}")
print("4b. TENURE EFFECT BY POSITION")
print("=" * 70)

positions = sorted(set(r["position"] for r in records))
for pos in positions:
    print(f"\n  {pos}:")
    pos_records = [r for r in records if r["position"] == pos]
    for band in band_order:
        vals = [r["sentiment_normalized"] for r in pos_records if r["years_at_district_band"] == band]
        if vals:
            mean = statistics.mean(vals)
            print(f"    {band:>5s}:  n={len(vals):3d}  mean={mean:+.3f}")
        else:
            print(f"    {band:>5s}:  n=  0  (no data)")

# 5. Positive outliers among 20+ tenure staff
print(f"\n{'=' * 70}")
print("5. POSITIVE OUTLIERS: 20+ YEARS AT DISTRICT WITH POSITIVE SENTIMENT")
print("=" * 70)

long_tenure_positive = [
    r for r in records
    if r["years_at_district_band"] == "20+"
    and r["sentiment_normalized"] > 0.1
]
long_tenure_positive.sort(key=lambda r: r["sentiment_normalized"], reverse=True)

total_20plus = len([r for r in records if r["years_at_district_band"] == "20+"])
print(f"\n  Found {len(long_tenure_positive)} staff with 20+ years and sentiment > 0.1")
print(f"  (Out of {total_20plus} total 20+ year staff)\n")

for r in long_tenure_positive[:8]:
    print(f"  --- {r['name']} ({r['position']}, {r['site']}) ---")
    print(f"      Age: {r['age']}, District years: {r['years_at_district']}, Profession years: {r['years_in_profession']}")
    print(f"      Sentiment: {r['sentiment_normalized']:+.3f} ({r['sentiment_category']})")
    print(f"      Transfer: {r['is_transfer']}, Origin system quality: {r['origin_district_system_quality']}")
    for qnum in ["q1", "q4"]:
        text = r[qnum]
        if len(text) > 250:
            text = text[:250] + "..."
        print(f"      {qnum}: {text}")
    print()

# Most negative 20+ year staff for contrast
print(f"\n{'=' * 70}")
print("5b. MOST NEGATIVE 20+ YEAR STAFF (for contrast)")
print("=" * 70)

long_tenure_neg = [r for r in records if r["years_at_district_band"] == "20+"]
long_tenure_neg.sort(key=lambda r: r["sentiment_normalized"])

for r in long_tenure_neg[:5]:
    print(f"\n  --- {r['name']} ({r['position']}, {r['site']}) ---")
    print(f"      Age: {r['age']}, District years: {r['years_at_district']}, Profession years: {r['years_in_profession']}")
    print(f"      Sentiment: {r['sentiment_normalized']:+.3f} ({r['sentiment_category']})")
    print(f"      Transfer: {r['is_transfer']}, Origin system quality: {r['origin_district_system_quality']}")
    for qnum in ["q1", "q5"]:
        text = r[qnum]
        if len(text) > 250:
            text = text[:250] + "..."
        print(f"      {qnum}: {text}")
