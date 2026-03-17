#!/usr/bin/env python3
"""
Masking Effects Analysis
Test for variables that show no overall correlation with sentiment
but work in opposite directions for different subgroups.
"""

import json
import sys
from collections import defaultdict
from itertools import combinations

DATA_PATH = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA_PATH) as f:
    data = json.load(f)

def group_stats(records):
    if not records:
        return {"n": 0, "mean": None, "stdev": None}
    vals = [r["sentiment_normalized"] for r in records]
    n = len(vals)
    mean = sum(vals) / n
    if n > 1:
        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
        stdev = var ** 0.5
    else:
        stdev = None
    return {"n": n, "mean": round(mean, 3), "stdev": round(stdev, 3) if stdev else None}

def group_by(records, field):
    groups = defaultdict(list)
    for r in records:
        groups[r.get(field)].append(r)
    return dict(groups)

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

# ============================================================
# 1. Race/Ethnicity × Tenure Band — masking test
# ============================================================
print_header("1. RACE/ETHNICITY × TENURE BAND — Masking Test")

# Overall race stats
print("\n--- Overall sentiment by race_ethnicity ---")
race_groups = group_by(data, "race_ethnicity")
for race in sorted(race_groups):
    s = group_stats(race_groups[race])
    print(f"  {race:25s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# Race within each tenure band
tenure_groups = group_by(data, "years_at_district_band")
tenure_order = ["0-3", "4-10", "11-20", "20+"]
print("\n--- Race/ethnicity sentiment WITHIN each tenure band ---")
for band in tenure_order:
    print(f"\n  Tenure band: {band}")
    band_records = tenure_groups.get(band, [])
    race_within = group_by(band_records, "race_ethnicity")
    for race in sorted(race_within):
        s = group_stats(race_within[race])
        print(f"    {race:25s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# Compute the range (max - min race mean) within each tenure band
print("\n--- Range of race means within each tenure band ---")
for band in tenure_order:
    band_records = tenure_groups.get(band, [])
    race_within = group_by(band_records, "race_ethnicity")
    means = {race: group_stats(recs)["mean"] for race, recs in race_within.items() if len(recs) >= 5}
    if means:
        max_r = max(means, key=means.get)
        min_r = min(means, key=means.get)
        spread = means[max_r] - means[min_r]
        print(f"  {band:8s}  spread={spread:.3f}  (most positive: {max_r} {means[max_r]:+.3f}, most negative: {min_r} {means[min_r]:+.3f})")

# ============================================================
# 2. Gender × Site × Transfer Status
# ============================================================
print_header("2. GENDER × SITE — and Gender × Transfer × Site")

# Gender within each site
site_groups = group_by(data, "site")
print("\n--- Gender sentiment within each site ---")
for site in sorted(site_groups):
    print(f"\n  {site}")
    gender_within = group_by(site_groups[site], "gender")
    for g in sorted(gender_within):
        s = group_stats(gender_within[g])
        print(f"    {g:15s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# Gender × Transfer within each site
print("\n--- Gender × Transfer Status within each site ---")
for site in sorted(site_groups):
    print(f"\n  {site}")
    for g in ["Male", "Female"]:
        for transfer in [True, False]:
            subset = [r for r in site_groups[site]
                       if r["gender"] == g and r["is_transfer"] == transfer]
            if subset:
                s = group_stats(subset)
                label = f"{g}, {'transfer' if transfer else 'non-transfer'}"
                print(f"    {label:30s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# What makes Riverside males positive? Check their demographics
print("\n--- Riverside Male deep-dive: tenure and transfer breakdown ---")
riverside_males = [r for r in data if r["site"] == "Riverside Elementary" and r["gender"] == "Male"]
for band in tenure_order:
    subset = [r for r in riverside_males if r["years_at_district_band"] == band]
    if subset:
        s = group_stats(subset)
        transfers = sum(1 for r in subset if r["is_transfer"])
        print(f"    Tenure {band:8s}  n={s['n']:3d}  mean={s['mean']:+.3f}  transfers={transfers}")

print("\n--- Valley High Male deep-dive: tenure and transfer breakdown ---")
vh_males = [r for r in data if r["site"] == "Valley High School" and r["gender"] == "Male"]
for band in tenure_order:
    subset = [r for r in vh_males if r["years_at_district_band"] == band]
    if subset:
        s = group_stats(subset)
        transfers = sum(1 for r in subset if r["is_transfer"])
        print(f"    Tenure {band:8s}  n={s['n']:3d}  mean={s['mean']:+.3f}  transfers={transfers}")

# ============================================================
# 3. Room Type × Tenure — masking within Large/Specialized
# ============================================================
print_header("3. ROOM TYPE × TENURE — Large/Specialized Split")

room_groups = group_by(data, "room_type")
for rt in sorted(room_groups):
    s = group_stats(room_groups[rt])
    print(f"  {rt:25s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n--- Large/Specialized by tenure band ---")
large_spec = [r for r in data if r["room_type"] == "Large/Specialized"]
for band in tenure_order:
    subset = [r for r in large_spec if r["years_at_district_band"] == band]
    if subset:
        s = group_stats(subset)
        print(f"    Tenure {band:8s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n--- Large/Specialized by site ---")
for site in sorted(set(r["site"] for r in large_spec)):
    subset = [r for r in large_spec if r["site"] == site]
    s = group_stats(subset)
    print(f"    {site:30s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n--- Large/Specialized by position ---")
for pos in sorted(set(r["position"] for r in large_spec)):
    subset = [r for r in large_spec if r["position"] == pos]
    s = group_stats(subset)
    print(f"    {pos:30s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# Standard rooms by tenure for comparison
print("\n--- Standard rooms by tenure band (for comparison) ---")
standard = [r for r in data if r["room_type"] == "Standard"]
for band in tenure_order:
    subset = [r for r in standard if r["years_at_district_band"] == band]
    if subset:
        s = group_stats(subset)
        print(f"    Tenure {band:8s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# ============================================================
# 4. Building Wing — full inventory
# ============================================================
print_header("4. BUILDING WING — Full Inventory")

wing_groups = group_by(data, "building_wing")
for wing, recs in sorted(wing_groups.items(), key=lambda x: str(x[0])):
    s = group_stats(recs)
    label = str(wing) if wing else "(null/no wing)"
    print(f"  {label:25s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# North Wing breakdown
print("\n--- North Wing breakdown by site ---")
north = [r for r in data if r.get("building_wing") == "North Wing"]
for site in sorted(set(r["site"] for r in north)):
    subset = [r for r in north if r["site"] == site]
    s = group_stats(subset)
    print(f"    {site:30s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n--- North Wing breakdown by tenure ---")
for band in tenure_order:
    subset = [r for r in north if r["years_at_district_band"] == band]
    if subset:
        s = group_stats(subset)
        print(f"    Tenure {band:8s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n--- North Wing breakdown by position ---")
for pos in sorted(set(r["position"] for r in north)):
    subset = [r for r in north if r["position"] == pos]
    s = group_stats(subset)
    print(f"    {pos:30s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

# ============================================================
# 5. Double-Variable Extremes
# ============================================================
print_header("5. DOUBLE-VARIABLE EXTREMES")

# Define categorical variables and their values
cat_vars = {
    "site": sorted(set(r["site"] for r in data)),
    "gender": sorted(set(r["gender"] for r in data)),
    "race_ethnicity": sorted(set(r["race_ethnicity"] for r in data)),
    "years_at_district_band": tenure_order,
    "position": sorted(set(r["position"] for r in data)),
    "is_transfer": [True, False],
    "room_type": sorted(set(r["room_type"] for r in data)),
    "building_wing": sorted(set(str(r["building_wing"]) for r in data)),
    "origin_district_system_quality": sorted(set(str(r["origin_district_system_quality"]) for r in data)),
}

# Generate all 2-variable combos
results = []
var_names = list(cat_vars.keys())
for v1, v2 in combinations(var_names, 2):
    for val1 in cat_vars[v1]:
        for val2 in cat_vars[v2]:
            subset = []
            for r in data:
                rv1 = str(r.get(v1)) if v1 in ("building_wing", "origin_district_system_quality") else r.get(v1)
                rv2 = str(r.get(v2)) if v2 in ("building_wing", "origin_district_system_quality") else r.get(v2)
                if rv1 == val1 and rv2 == val2:
                    subset.append(r)
            if len(subset) >= 5:  # minimum sample size
                s = group_stats(subset)
                results.append({
                    "combo": f"{v1}={val1} + {v2}={val2}",
                    "n": s["n"],
                    "mean": s["mean"]
                })

results.sort(key=lambda x: x["mean"])

print("\n--- 10 MOST NEGATIVE 2-variable combinations (n >= 5) ---")
for r in results[:10]:
    print(f"  mean={r['mean']:+.3f}  n={r['n']:3d}  {r['combo']}")

print("\n--- 10 MOST POSITIVE 2-variable combinations (n >= 5) ---")
for r in results[-10:]:
    print(f"  mean={r['mean']:+.3f}  n={r['n']:3d}  {r['combo']}")

# Also do triple-variable for the single most extreme
print("\n\n--- TRIPLE-VARIABLE extremes (n >= 5) ---")
triple_results = []
# Only test the most promising triples based on top doubles
# Use top variables from extreme doubles
for v1, v2, v3 in combinations(var_names, 3):
    # Skip slow combos - only test combos involving site + one of the strong vars
    if "site" not in (v1, v2, v3):
        continue
    for val1 in cat_vars[v1]:
        for val2 in cat_vars[v2]:
            for val3 in cat_vars[v3]:
                subset = []
                for r in data:
                    rv1 = str(r.get(v1)) if v1 in ("building_wing", "origin_district_system_quality") else r.get(v1)
                    rv2 = str(r.get(v2)) if v2 in ("building_wing", "origin_district_system_quality") else r.get(v2)
                    rv3 = str(r.get(v3)) if v3 in ("building_wing", "origin_district_system_quality") else r.get(v3)
                    if rv1 == val1 and rv2 == val2 and rv3 == val3:
                        subset.append(r)
                if len(subset) >= 5:
                    s = group_stats(subset)
                    triple_results.append({
                        "combo": f"{v1}={val1} + {v2}={val2} + {v3}={val3}",
                        "n": s["n"],
                        "mean": s["mean"]
                    })

triple_results.sort(key=lambda x: x["mean"])
print("\n  5 MOST NEGATIVE triple combos (n >= 5):")
for r in triple_results[:5]:
    print(f"    mean={r['mean']:+.3f}  n={r['n']:3d}  {r['combo']}")

print("\n  5 MOST POSITIVE triple combos (n >= 5):")
for r in triple_results[-5:]:
    print(f"    mean={r['mean']:+.3f}  n={r['n']:3d}  {r['combo']}")

# ============================================================
# 6. Key Masking Summary — variables with near-zero overall
#    but divergent subgroup effects
# ============================================================
print_header("6. MASKING SUMMARY — Near-zero overall, divergent subgroups")

# For each categorical var, compute overall correlation direction,
# then check if subgroups within tenure bands diverge
overall = group_stats(data)
print(f"\n  Overall dataset: n={overall['n']}, mean={overall['mean']:+.3f}")

# Check gender overall
print("\n--- Gender overall vs. within-site divergence ---")
gender_overall = group_by(data, "gender")
for g in ["Male", "Female"]:
    s = group_stats(gender_overall[g])
    print(f"  {g:15s} overall: n={s['n']:3d} mean={s['mean']:+.3f}")
# Male at each site
for site in sorted(site_groups):
    males = [r for r in site_groups[site] if r["gender"] == "Male"]
    females = [r for r in site_groups[site] if r["gender"] == "Female"]
    ms = group_stats(males)
    fs = group_stats(females)
    gap = ms["mean"] - fs["mean"] if ms["mean"] and fs["mean"] else 0
    print(f"  {site:30s}  M-F gap = {gap:+.3f}  (M: {ms['mean']:+.3f} n={ms['n']}, F: {fs['mean']:+.3f} n={fs['n']})")

# Transfer status overall vs within tenure
print("\n--- Transfer status overall vs. within-tenure divergence ---")
transfer_overall = group_by(data, "is_transfer")
for t in [True, False]:
    s = group_stats(transfer_overall[t])
    label = "Transfer" if t else "Non-transfer"
    print(f"  {label:15s} overall: n={s['n']:3d} mean={s['mean']:+.3f}")

for band in tenure_order:
    band_recs = tenure_groups[band]
    transfers = [r for r in band_recs if r["is_transfer"]]
    non_transfers = [r for r in band_recs if not r["is_transfer"]]
    ts = group_stats(transfers)
    ns = group_stats(non_transfers)
    if ts["n"] >= 3 and ns["n"] >= 3:
        gap = ts["mean"] - ns["mean"]
        print(f"  Tenure {band:8s}  T-NT gap = {gap:+.3f}  (T: {ts['mean']:+.3f} n={ts['n']}, NT: {ns['mean']:+.3f} n={ns['n']})")

# Origin district system quality among transfers only
print("\n--- Origin system quality among transfers ---")
transfers_only = [r for r in data if r["is_transfer"]]
origin_groups = group_by(transfers_only, "origin_district_system_quality")
for orig in ["worse", "comparable", "better"]:
    if orig in origin_groups:
        s = group_stats(origin_groups[orig])
        print(f"  From {orig:12s} system:  n={s['n']:3d}  mean={s['mean']:+.3f}")

# Origin quality within tenure bands
print("\n--- Origin system quality × tenure among transfers ---")
for band in tenure_order:
    band_transfers = [r for r in transfers_only if r["years_at_district_band"] == band]
    if len(band_transfers) >= 3:
        print(f"  Tenure {band}:")
        for orig in ["worse", "comparable", "better"]:
            subset = [r for r in band_transfers if r.get("origin_district_system_quality") == orig]
            if len(subset) >= 2:
                s = group_stats(subset)
                print(f"    From {orig:12s}  n={s['n']:3d}  mean={s['mean']:+.3f}")

print("\n\nDone.")
