#!/usr/bin/env python3
"""Polarization analysis: variance and extremes by site."""

import json
import statistics
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA) as f:
    records = json.load(f)

print(f"Total records: {len(records)}")
print(f"Fields: {list(records[0].keys())}\n")

# ── 1. Standard deviation of sentiment_normalized by site ──────────────
print("=" * 70)
print("1. SENTIMENT STANDARD DEVIATION BY SITE")
print("=" * 70)

by_site = defaultdict(list)
for r in records:
    by_site[r["site"]].append(r["sentiment_normalized"])

site_stats = []
for site, vals in sorted(by_site.items()):
    m = statistics.mean(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0
    site_stats.append((site, len(vals), m, sd))

site_stats.sort(key=lambda x: -x[3])  # sort by SD descending
print(f"{'Site':<30} {'N':>5} {'Mean':>7} {'StDev':>7}")
print("-" * 55)
for site, n, m, sd in site_stats:
    print(f"{site:<30} {n:>5} {m:>7.3f} {sd:>7.3f}")

# ── 2. Distribution shape: strongly pos / neg / moderate by site ───────
print("\n" + "=" * 70)
print("2. DISTRIBUTION SHAPE BY SITE (% strongly pos / moderate / strongly neg)")
print("   Strongly positive: > 0.5 | Moderate: -0.5 to 0.5 | Strongly negative: < -0.5")
print("=" * 70)

print(f"{'Site':<30} {'N':>5} {'Str.Neg%':>9} {'Moderate%':>10} {'Str.Pos%':>9}")
print("-" * 68)
for site, vals in sorted(by_site.items()):
    n = len(vals)
    neg = sum(1 for v in vals if v < -0.5)
    mod = sum(1 for v in vals if -0.5 <= v <= 0.5)
    pos = sum(1 for v in vals if v > 0.5)
    print(f"{site:<30} {n:>5} {100*neg/n:>8.1f}% {100*mod/n:>9.1f}% {100*pos/n:>8.1f}%")

# ── 3. 10 most negative records ───────────────────────────────────────
print("\n" + "=" * 70)
print("3. 10 MOST NEGATIVE RECORDS")
print("=" * 70)

sorted_recs = sorted(records, key=lambda r: r["sentiment_normalized"])
print(f"{'ID':<10} {'Site':<28} {'Position':<22} {'Tenure Band':<10} {'Sent':>6}")
print("-" * 80)
for r in sorted_recs[:10]:
    print(f"{r['employee_id']:<10} {r['site']:<28} {r['position']:<22} {r['years_at_district_band']:<10} {r['sentiment_normalized']:>6.3f}")

# Site breakdown of bottom 10
neg_sites = defaultdict(int)
neg_positions = defaultdict(int)
neg_tenure = defaultdict(int)
for r in sorted_recs[:10]:
    neg_sites[r["site"]] += 1
    neg_positions[r["position"]] += 1
    neg_tenure[r["years_at_district_band"]] += 1

print("\nBottom 10 — Site breakdown:", dict(neg_sites))
print("Bottom 10 — Position breakdown:", dict(neg_positions))
print("Bottom 10 — Tenure band breakdown:", dict(neg_tenure))

# ── 4. 10 most positive records ──────────────────────────────────────
print("\n" + "=" * 70)
print("4. 10 MOST POSITIVE RECORDS")
print("=" * 70)

print(f"{'ID':<10} {'Site':<28} {'Position':<22} {'Tenure Band':<10} {'Sent':>6}")
print("-" * 80)
for r in sorted_recs[-10:]:
    print(f"{r['employee_id']:<10} {r['site']:<28} {r['position']:<22} {r['years_at_district_band']:<10} {r['sentiment_normalized']:>6.3f}")

pos_sites = defaultdict(int)
pos_positions = defaultdict(int)
pos_tenure = defaultdict(int)
for r in sorted_recs[-10:]:
    pos_sites[r["site"]] += 1
    pos_positions[r["position"]] += 1
    pos_tenure[r["years_at_district_band"]] += 1

print("\nTop 10 — Site breakdown:", dict(pos_sites))
print("Top 10 — Position breakdown:", dict(pos_positions))
print("Top 10 — Tenure band breakdown:", dict(pos_tenure))

# ── 5. Subgroups with near-zero variance ─────────────────────────────
print("\n" + "=" * 70)
print("5. SUBGROUPS WITH LOW VARIANCE (potential uniform sentiment)")
print("   Checking site x position, site x tenure_band combos with N >= 5")
print("=" * 70)

# site x position
subgroups = defaultdict(list)
for r in records:
    subgroups[(r["site"], r["position"])].append(r["sentiment_normalized"])
    subgroups[(r["site"], r["years_at_district_band"])].append(r["sentiment_normalized"])

low_var = []
for key, vals in subgroups.items():
    if len(vals) >= 5:
        sd = statistics.stdev(vals)
        m = statistics.mean(vals)
        low_var.append((key, len(vals), m, sd))

low_var.sort(key=lambda x: x[3])
print(f"\n{'Subgroup':<55} {'N':>4} {'Mean':>7} {'StDev':>7}")
print("-" * 78)
for key, n, m, sd in low_var[:15]:
    label = f"{key[0]} / {key[1]}"
    print(f"{label:<55} {n:>4} {m:>7.3f} {sd:>7.3f}")

print("\n\nHighest variance subgroups (N >= 5):")
print(f"{'Subgroup':<55} {'N':>4} {'Mean':>7} {'StDev':>7}")
print("-" * 78)
for key, n, m, sd in low_var[-15:]:
    label = f"{key[0]} / {key[1]}"
    print(f"{label:<55} {n:>4} {m:>7.3f} {sd:>7.3f}")

# ── 6. Bonus: polarization index (% extreme / total) by site ────────
print("\n" + "=" * 70)
print("6. POLARIZATION INDEX BY SITE (% of responses that are extreme)")
print("   Extreme = |sentiment_normalized| > 0.5")
print("=" * 70)

print(f"{'Site':<30} {'N':>5} {'Extreme%':>9} {'Extreme N':>10}")
print("-" * 58)
for site, vals in sorted(by_site.items()):
    n = len(vals)
    extreme = sum(1 for v in vals if abs(v) > 0.5)
    print(f"{site:<30} {n:>5} {100*extreme/n:>8.1f}% {extreme:>10}")
