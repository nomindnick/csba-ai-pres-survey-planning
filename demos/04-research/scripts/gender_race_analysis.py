#!/usr/bin/env python3
"""
Hypothesis: Gender and race/ethnicity show sentiment differences,
but these may be confounded by position and site distributions.
"""

import json
import statistics
from collections import defaultdict

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# Helper
def stats_for(group):
    vals = [r["sentiment_normalized"] for r in group]
    if not vals:
        return {"n": 0}
    return {
        "n": len(vals),
        "mean": round(statistics.mean(vals), 3),
        "median": round(statistics.median(vals), 3),
        "stdev": round(statistics.stdev(vals), 3) if len(vals) > 1 else 0,
    }

def cat_dist(group):
    cats = defaultdict(int)
    for r in group:
        cats[r["sentiment_category"]] += 1
    total = len(group)
    return {k: f"{v} ({round(100*v/total,1)}%)" for k, v in sorted(cats.items())}

overall = stats_for(data)
print(f"\n{'='*70}")
print(f"OVERALL: n={overall['n']}, mean={overall['mean']}, median={overall['median']}")
print(f"{'='*70}")

# ── 1. GENDER ────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("1. SENTIMENT BY GENDER")
print(f"{'='*70}")

by_gender = defaultdict(list)
for r in data:
    by_gender[r["gender"]].append(r)

for g in sorted(by_gender, key=lambda x: -len(by_gender[x])):
    s = stats_for(by_gender[g])
    cats = cat_dist(by_gender[g])
    diff = round(s["mean"] - overall["mean"], 3)
    print(f"\n  {g}: n={s['n']}, mean={s['mean']} (diff from overall: {diff:+.3f}), median={s['median']}, sd={s['stdev']}")
    print(f"    Categories: {cats}")

# ── 2. RACE/ETHNICITY ───────────────────────────────────────────────────
print(f"\n{'='*70}")
print("2. SENTIMENT BY RACE/ETHNICITY")
print(f"{'='*70}")

by_race = defaultdict(list)
for r in data:
    by_race[r["race_ethnicity"]].append(r)

for g in sorted(by_race, key=lambda x: -len(by_race[x])):
    s = stats_for(by_race[g])
    cats = cat_dist(by_race[g])
    diff = round(s["mean"] - overall["mean"], 3)
    print(f"\n  {g}: n={s['n']}, mean={s['mean']} (diff from overall: {diff:+.3f}), median={s['median']}, sd={s['stdev']}")
    print(f"    Categories: {cats}")

# ── 3. CONTROL FOR SITE × GENDER and SITE × RACE ────────────────────────
print(f"\n{'='*70}")
print("3. CONTROLLING FOR SITE — SITE × GENDER")
print(f"{'='*70}")

sites = sorted(set(r["site"] for r in data))

# Site × Gender
for site in sites:
    site_data = [r for r in data if r["site"] == site]
    site_stats = stats_for(site_data)
    print(f"\n  {site} (n={site_stats['n']}, mean={site_stats['mean']}):")
    by_g = defaultdict(list)
    for r in site_data:
        by_g[r["gender"]].append(r)
    for g in sorted(by_g, key=lambda x: -len(by_g[x])):
        s = stats_for(by_g[g])
        diff = round(s["mean"] - site_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from site: {diff:+.3f})")

print(f"\n{'='*70}")
print("3b. CONTROLLING FOR SITE — SITE × RACE/ETHNICITY")
print(f"{'='*70}")

for site in sites:
    site_data = [r for r in data if r["site"] == site]
    site_stats = stats_for(site_data)
    print(f"\n  {site} (n={site_stats['n']}, mean={site_stats['mean']}):")
    by_r = defaultdict(list)
    for r in site_data:
        by_r[r["race_ethnicity"]].append(r)
    for g in sorted(by_r, key=lambda x: -len(by_r[x])):
        s = stats_for(by_r[g])
        diff = round(s["mean"] - site_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from site: {diff:+.3f})")

# ── 3c. CONTROL FOR POSITION × GENDER and POSITION × RACE ───────────────
print(f"\n{'='*70}")
print("3c. CONTROLLING FOR POSITION — POSITION × GENDER")
print(f"{'='*70}")

positions = sorted(set(r["position"] for r in data))
for pos in positions:
    pos_data = [r for r in data if r["position"] == pos]
    pos_stats = stats_for(pos_data)
    print(f"\n  {pos} (n={pos_stats['n']}, mean={pos_stats['mean']}):")
    by_g = defaultdict(list)
    for r in pos_data:
        by_g[r["gender"]].append(r)
    for g in sorted(by_g, key=lambda x: -len(by_g[x])):
        s = stats_for(by_g[g])
        diff = round(s["mean"] - pos_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from position: {diff:+.3f})")

print(f"\n{'='*70}")
print("3d. CONTROLLING FOR POSITION — POSITION × RACE/ETHNICITY")
print(f"{'='*70}")

for pos in positions:
    pos_data = [r for r in data if r["position"] == pos]
    pos_stats = stats_for(pos_data)
    print(f"\n  {pos} (n={pos_stats['n']}, mean={pos_stats['mean']}):")
    by_r = defaultdict(list)
    for r in pos_data:
        by_r[r["race_ethnicity"]].append(r)
    for g in sorted(by_r, key=lambda x: -len(by_r[x])):
        s = stats_for(by_r[g])
        diff = round(s["mean"] - pos_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from position: {diff:+.3f})")

# ── 4. CONTROLLING FOR TENURE BAND ──────────────────────────────────────
print(f"\n{'='*70}")
print("4. TENURE BAND × GENDER")
print(f"{'='*70}")

tenure_bands = sorted(set(r["years_at_district_band"] for r in data),
                       key=lambda x: int(x.split("-")[0]) if "-" in x else int(x.rstrip("+")))

for tb in tenure_bands:
    tb_data = [r for r in data if r["years_at_district_band"] == tb]
    tb_stats = stats_for(tb_data)
    print(f"\n  Tenure {tb} (n={tb_stats['n']}, mean={tb_stats['mean']}):")
    by_g = defaultdict(list)
    for r in tb_data:
        by_g[r["gender"]].append(r)
    for g in sorted(by_g, key=lambda x: -len(by_g[x])):
        s = stats_for(by_g[g])
        diff = round(s["mean"] - tb_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from band: {diff:+.3f})")

print(f"\n{'='*70}")
print("4b. TENURE BAND × RACE/ETHNICITY")
print(f"{'='*70}")

for tb in tenure_bands:
    tb_data = [r for r in data if r["years_at_district_band"] == tb]
    tb_stats = stats_for(tb_data)
    print(f"\n  Tenure {tb} (n={tb_stats['n']}, mean={tb_stats['mean']}):")
    by_r = defaultdict(list)
    for r in tb_data:
        by_r[r["race_ethnicity"]].append(r)
    for g in sorted(by_r, key=lambda x: -len(by_r[x])):
        s = stats_for(by_r[g])
        diff = round(s["mean"] - tb_stats["mean"], 3)
        print(f"    {g}: n={s['n']}, mean={s['mean']} (diff from band: {diff:+.3f})")

# ── 5. REPRESENTATIVE QUOTES FROM STANDOUT SUBGROUPS ────────────────────
print(f"\n{'='*70}")
print("5. REPRESENTATIVE QUOTES FROM STANDOUT SUBGROUPS")
print(f"{'='*70}")

# Find standout groups: sort each gender/race by mean sentiment, pick extremes
def show_quotes(label, group, n_quotes=3):
    """Show quotes from most negative and most positive in group."""
    sorted_g = sorted(group, key=lambda r: r["sentiment_normalized"])
    print(f"\n  --- {label} (n={len(group)}, mean={stats_for(group)['mean']}) ---")

    # Most negative
    print(f"\n  Most negative responses:")
    for r in sorted_g[:min(n_quotes, len(sorted_g))]:
        print(f"    [{r['employee_id']}] sent={r['sentiment_normalized']:.3f}, {r['position']}, {r['site']}, tenure={r['years_at_district']}yr")
        # Show q1 (general experience) truncated
        q1 = r["q1"][:200] + "..." if len(r["q1"]) > 200 else r["q1"]
        print(f"      Q1: \"{q1}\"")

    # Most positive
    print(f"\n  Most positive responses:")
    for r in sorted_g[-min(n_quotes, len(sorted_g)):]:
        print(f"    [{r['employee_id']}] sent={r['sentiment_normalized']:.3f}, {r['position']}, {r['site']}, tenure={r['years_at_district']}yr")
        q1 = r["q1"][:200] + "..." if len(r["q1"]) > 200 else r["q1"]
        print(f"      Q1: \"{q1}\"")

# Nonbinary (small group, check if notable)
show_quotes("Nonbinary", by_gender.get("Nonbinary", []))

# Check each race group
for race in sorted(by_race, key=lambda x: stats_for(by_race[x])["mean"]):
    s = stats_for(by_race[race])
    if abs(s["mean"] - overall["mean"]) > 0.02:  # notable deviation
        show_quotes(f"Race: {race}", by_race[race])

# ── 6. SUMMARY STATISTICS TABLE ─────────────────────────────────────────
print(f"\n{'='*70}")
print("6. SUMMARY: EFFECT SIZE COMPARISON")
print(f"{'='*70}")

print(f"\n  Overall mean: {overall['mean']}")
print(f"\n  Gender effect (max - min):")
gender_means = {g: stats_for(by_gender[g])["mean"] for g in by_gender}
print(f"    Range: {min(gender_means.values()):.3f} to {max(gender_means.values()):.3f} = {max(gender_means.values()) - min(gender_means.values()):.3f}")
for g, m in sorted(gender_means.items(), key=lambda x: x[1]):
    print(f"    {g}: {m:.3f} (n={len(by_gender[g])})")

print(f"\n  Race/ethnicity effect (max - min):")
race_means = {g: stats_for(by_race[g])["mean"] for g in by_race}
print(f"    Range: {min(race_means.values()):.3f} to {max(race_means.values()):.3f} = {max(race_means.values()) - min(race_means.values()):.3f}")
for g, m in sorted(race_means.items(), key=lambda x: x[1]):
    print(f"    {g}: {m:.3f} (n={len(by_race[g])})")

# Compare to site effect for context
print(f"\n  Site effect for context (max - min):")
by_site = defaultdict(list)
for r in data:
    by_site[r["site"]].append(r)
site_means = {s: stats_for(by_site[s])["mean"] for s in by_site}
print(f"    Range: {min(site_means.values()):.3f} to {max(site_means.values()):.3f} = {max(site_means.values()) - min(site_means.values()):.3f}")
for s, m in sorted(site_means.items(), key=lambda x: x[1]):
    print(f"    {s}: {m:.3f} (n={len(by_site[s])})")
