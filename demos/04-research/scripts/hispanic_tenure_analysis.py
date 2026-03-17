#!/usr/bin/env python3
"""
Investigate why Hispanic/Latino staff in the 11-20 year district tenure band
have the lowest sentiment of any race x tenure cell (reported as 0.80).
"""

import json
import statistics
from collections import Counter
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon', quiet=True)

DATA_PATH = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA_PATH) as f:
    data = json.load(f)

sia = SentimentIntensityAnalyzer()

# --- Compute sentiment for every record ---
for r in data:
    combined = " ".join(r[q] or "" for q in ["q1","q2","q3","q4","q5"])
    scores = sia.polarity_scores(combined)
    r["sentiment_compound"] = scores["compound"]
    # Also per-question
    for q in ["q1","q2","q3","q4","q5"]:
        r[f"{q}_sent"] = sia.polarity_scores(r[q] or "")["compound"]

# --- 1. Filter to target group ---
target = [r for r in data if r["race_ethnicity"] == "Hispanic/Latino" and r["years_at_district_band"] == "11-20"]
all_hispanic = [r for r in data if r["race_ethnicity"] == "Hispanic/Latino"]

print("=" * 80)
print("INVESTIGATION: Hispanic/Latino, District Tenure 11-20 years")
print("=" * 80)
print(f"\nTarget group size: {len(target)}")
print(f"All Hispanic/Latino: {len(all_hispanic)}")
print(f"Total dataset: {len(data)}")

# --- 2. Demographics of target group ---
print("\n" + "-" * 60)
print("DEMOGRAPHIC PROFILE OF TARGET GROUP (Hispanic/Latino, 11-20yr)")
print("-" * 60)

print("\n--- Site Distribution ---")
site_counts = Counter(r["site"] for r in target)
for site, n in site_counts.most_common():
    pct = n / len(target) * 100
    print(f"  {site}: {n} ({pct:.0f}%)")

print("\n--- Position Breakdown ---")
pos_counts = Counter(r["position"] for r in target)
for pos, n in pos_counts.most_common():
    print(f"  {pos}: {n} ({n/len(target)*100:.0f}%)")

print("\n--- Building Wing ---")
wing_counts = Counter(r["building_wing"] if r["building_wing"] else "None/NA" for r in target)
for wing, n in wing_counts.most_common():
    print(f"  {wing}: {n} ({n/len(target)*100:.0f}%)")

print("\n--- Room Type ---")
room_counts = Counter(r["room_type"] for r in target)
for rt, n in room_counts.most_common():
    print(f"  {rt}: {n} ({n/len(target)*100:.0f}%)")

print("\n--- Is Transfer ---")
transfer_counts = Counter(r["is_transfer"] for r in target)
for t, n in transfer_counts.most_common():
    print(f"  {t}: {n} ({n/len(target)*100:.0f}%)")

print("\n--- Origin District System Quality (transfers only) ---")
transfers = [r for r in target if r["is_transfer"]]
if transfers:
    oq = Counter(r["origin_district_system_quality"] for r in transfers if r["origin_district_system_quality"])
    for q, n in oq.most_common():
        print(f"  {q}: {n}")
else:
    print("  No transfers in target group")

print("\n--- Gender ---")
gender_counts = Counter(r["gender"] for r in target)
for g, n in gender_counts.most_common():
    print(f"  {g}: {n} ({n/len(target)*100:.0f}%)")

print("\n--- Age Distribution ---")
ages = [r["age"] for r in target]
print(f"  Mean: {statistics.mean(ages):.1f}, Median: {statistics.median(ages)}, Range: {min(ages)}-{max(ages)}")

# --- 3. Sentiment comparison across tenure bands ---
print("\n" + "-" * 60)
print("SENTIMENT BY TENURE BAND — Hispanic/Latino only")
print("-" * 60)

tenure_bands = sorted(set(r["years_at_district_band"] for r in all_hispanic),
                      key=lambda x: int(x.split("-")[0]) if "-" in x else int(x.rstrip("+")))
for band in tenure_bands:
    group = [r for r in all_hispanic if r["years_at_district_band"] == band]
    sents = [r["sentiment_compound"] for r in group]
    avg = statistics.mean(sents)
    print(f"  {band:>8}: n={len(group):3d}, mean_sentiment={avg:.3f}")

# Per-question breakdown
print("\n--- Per-Question Sentiment (Hispanic/Latino by tenure band) ---")
for q in ["q1","q2","q3","q4","q5"]:
    print(f"\n  {q}:")
    for band in tenure_bands:
        group = [r for r in all_hispanic if r["years_at_district_band"] == band]
        sents = [r[f"{q}_sent"] for r in group]
        avg = statistics.mean(sents)
        print(f"    {band:>8}: n={len(group):3d}, mean={avg:.3f}")

# --- Compare to same tenure band, other races ---
print("\n" + "-" * 60)
print("SENTIMENT BY RACE — 11-20 year tenure band only")
print("-" * 60)

tenure_1120 = [r for r in data if r["years_at_district_band"] == "11-20"]
races = sorted(set(r["race_ethnicity"] for r in tenure_1120))
for race in races:
    group = [r for r in tenure_1120 if r["race_ethnicity"] == race]
    sents = [r["sentiment_compound"] for r in group]
    avg = statistics.mean(sents)
    print(f"  {race:>30}: n={len(group):3d}, mean_sentiment={avg:.3f}")

# --- 4. Five most negative responses ---
print("\n" + "-" * 60)
print("5 MOST NEGATIVE RESPONSES (Hispanic/Latino, 11-20yr)")
print("-" * 60)

target_sorted = sorted(target, key=lambda r: r["sentiment_compound"])
for i, r in enumerate(target_sorted[:5], 1):
    print(f"\n--- #{i}: {r['employee_id']} | sentiment={r['sentiment_compound']:.3f} ---")
    print(f"  Site: {r['site']} | Position: {r['position']} | Age: {r['age']}")
    print(f"  Wing: {r['building_wing']} | Room: {r['room_type']} | Transfer: {r['is_transfer']}")
    print(f"  District tenure: {r['years_at_district']}yr | Profession: {r['years_in_profession']}yr")
    for q in ["q1","q2","q3","q4","q5"]:
        print(f"\n  {q.upper()} (sent={r[f'{q}_sent']:.3f}):")
        print(f"    {r[q]}")

# --- 5. North Wing overlap ---
print("\n" + "-" * 60)
print("NORTH WING OVERLAP ANALYSIS")
print("-" * 60)

north_wing_target = [r for r in target if r["building_wing"] == "North"]
print(f"  Target group in North Wing: {len(north_wing_target)} of {len(target)}")
if north_wing_target:
    nw_sents = [r["sentiment_compound"] for r in north_wing_target]
    non_nw = [r for r in target if r["building_wing"] != "North"]
    non_nw_sents = [r["sentiment_compound"] for r in non_nw]
    print(f"  North Wing sentiment: {statistics.mean(nw_sents):.3f} (n={len(north_wing_target)})")
    if non_nw_sents:
        print(f"  Other wings sentiment: {statistics.mean(non_nw_sents):.3f} (n={len(non_nw)})")

# All North Wing for comparison
all_north = [r for r in data if r["building_wing"] == "North"]
if all_north:
    print(f"\n  All North Wing staff: n={len(all_north)}, mean_sentiment={statistics.mean([r['sentiment_compound'] for r in all_north]):.3f}")
    print(f"  All non-North staff: n={len(data)-len(all_north)}, mean_sentiment={statistics.mean([r['sentiment_compound'] for r in data if r['building_wing'] != 'North']):.3f}")

# Check other known subgroups
print("\n--- Overlap with other subgroups ---")
# Maintenance/custodial
maint = [r for r in target if r["position"] in ("Custodian", "Maintenance")]
print(f"  Custodian/Maintenance: {len(maint)} of {len(target)}")
if maint:
    print(f"    Sentiment: {statistics.mean([r['sentiment_compound'] for r in maint]):.3f}")

# Transfers from poor systems
poor_transfers = [r for r in target if r["is_transfer"] and r.get("origin_district_system_quality") in ("Poor", "Very Poor")]
print(f"  Transfers from poor systems: {len(poor_transfers)} of {len(target)}")

# --- 6. Theme analysis ---
print("\n" + "-" * 60)
print("THEME ANALYSIS: What makes this group's responses distinctive?")
print("-" * 60)

# Keyword/phrase frequencies — compare target to all others
import re

def count_phrases(records, phrases):
    counts = Counter()
    for r in records:
        text = " ".join((r[q] or "").lower() for q in ["q1","q2","q3","q4","q5"])
        for phrase in phrases:
            if phrase in text:
                counts[phrase] += 1
    return counts

theme_phrases = [
    "disruption", "disruptive", "frustrated", "frustrating", "frustration",
    "ignored", "not consulted", "no input", "wasn't asked", "weren't asked",
    "rushed", "too fast", "poorly planned", "poorly communicated",
    "no follow-up", "no support", "inadequate training", "insufficient",
    "old system", "worked fine", "didn't need", "unnecessary",
    "glitch", "malfunction", "broken", "doesn't work", "not working",
    "noise", "loud", "too loud", "echo",
    "respected", "not respected", "disrespect", "dismissed",
    "seniority", "experience", "years", "veteran",
    "maintenance", "custod",
    "communication", "communicated",
    "training", "professional development",
    "workflow", "routine", "adjustment",
    "improvement", "better", "worse",
    "construction", "installation",
    "classroom", "office", "hallway",
    "safety", "security", "emergency",
    "trust", "distrust", "skeptic",
    "overwhelm", "stressed", "stress",
    "morale", "valued", "undervalued",
]

target_phrases = count_phrases(target, theme_phrases)
others = [r for r in data if not (r["race_ethnicity"] == "Hispanic/Latino" and r["years_at_district_band"] == "11-20")]
others_phrases = count_phrases(others, theme_phrases)

print("\nPhrase frequency comparison (target vs rest-of-dataset):")
print(f"  {'Phrase':<25} {'Target':>10} {'Target%':>10} {'Others':>10} {'Others%':>10} {'Ratio':>8}")
for phrase in sorted(theme_phrases):
    tc = target_phrases[phrase]
    oc = others_phrases[phrase]
    tp = tc / len(target) * 100
    op = oc / len(others) * 100 if oc > 0 else 0
    ratio = tp / op if op > 0 else float('inf') if tc > 0 else 0
    if tc > 0 or oc > 2:
        print(f"  {phrase:<25} {tc:>10} {tp:>9.1f}% {oc:>10} {op:>9.1f}% {ratio:>7.1f}x")

# --- Deep comparison: target vs other Hispanic tenure bands ---
print("\n" + "-" * 60)
print("DISTINCTIVE THEMES: Hispanic 11-20yr vs Hispanic other bands")
print("-" * 60)

hisp_other = [r for r in all_hispanic if r["years_at_district_band"] != "11-20"]
target_ph = count_phrases(target, theme_phrases)
hisp_other_ph = count_phrases(hisp_other, theme_phrases)

print(f"\n  {'Phrase':<25} {'Target':>10} {'Target%':>10} {'H-Other':>10} {'H-Other%':>10} {'Ratio':>8}")
for phrase in sorted(theme_phrases):
    tc = target_ph[phrase]
    oc = hisp_other_ph[phrase]
    tp = tc / len(target) * 100
    op = oc / len(hisp_other) * 100 if oc > 0 else 0
    ratio = tp / op if op > 0 else float('inf') if tc > 0 else 0
    if tc > 0:
        print(f"  {phrase:<25} {tc:>10} {tp:>9.1f}% {oc:>10} {op:>9.1f}% {ratio:>7.1f}x")

# --- Confounders: site composition ---
print("\n" + "-" * 60)
print("CONFOUNDER CHECK: Is this a site effect or a tenure effect?")
print("-" * 60)

for site in site_counts:
    hisp_1120_site = [r for r in target if r["site"] == site]
    all_site = [r for r in data if r["site"] == site]
    hisp_other_site = [r for r in all_hispanic if r["site"] == site and r["years_at_district_band"] != "11-20"]
    non_hisp_1120_site = [r for r in data if r["site"] == site and r["years_at_district_band"] == "11-20" and r["race_ethnicity"] != "Hispanic/Latino"]

    print(f"\n  {site}:")
    print(f"    Hispanic 11-20yr: n={len(hisp_1120_site)}, sent={statistics.mean([r['sentiment_compound'] for r in hisp_1120_site]):.3f}" if hisp_1120_site else f"    Hispanic 11-20yr: n=0")
    print(f"    All site staff:   n={len(all_site)}, sent={statistics.mean([r['sentiment_compound'] for r in all_site]):.3f}")
    if hisp_other_site:
        print(f"    Hispanic other:   n={len(hisp_other_site)}, sent={statistics.mean([r['sentiment_compound'] for r in hisp_other_site]):.3f}")
    if non_hisp_1120_site:
        print(f"    Non-Hisp 11-20yr: n={len(non_hisp_1120_site)}, sent={statistics.mean([r['sentiment_compound'] for r in non_hisp_1120_site]):.3f}")

# --- Position-controlled comparison ---
print("\n" + "-" * 60)
print("CONFOUNDER CHECK: Is this a position effect?")
print("-" * 60)

for pos in pos_counts:
    hisp_1120_pos = [r for r in target if r["position"] == pos]
    hisp_other_pos = [r for r in all_hispanic if r["years_at_district_band"] != "11-20" and r["position"] == pos]
    non_hisp_1120_pos = [r for r in data if r["years_at_district_band"] == "11-20" and r["race_ethnicity"] != "Hispanic/Latino" and r["position"] == pos]

    print(f"\n  {pos}:")
    if hisp_1120_pos:
        print(f"    Hispanic 11-20yr: n={len(hisp_1120_pos)}, sent={statistics.mean([r['sentiment_compound'] for r in hisp_1120_pos]):.3f}")
    if hisp_other_pos:
        print(f"    Hispanic other:   n={len(hisp_other_pos)}, sent={statistics.mean([r['sentiment_compound'] for r in hisp_other_pos]):.3f}")
    if non_hisp_1120_pos:
        print(f"    Non-Hisp 11-20yr: n={len(non_hisp_1120_pos)}, sent={statistics.mean([r['sentiment_compound'] for r in non_hisp_1120_pos]):.3f}")

# --- Room type effect ---
print("\n" + "-" * 60)
print("CONFOUNDER CHECK: Room type effect?")
print("-" * 60)
for rt in room_counts:
    grp = [r for r in target if r["room_type"] == rt]
    all_rt = [r for r in data if r["room_type"] == rt]
    print(f"  {rt}: target n={len(grp)}, sent={statistics.mean([r['sentiment_compound'] for r in grp]):.3f}  |  all n={len(all_rt)}, sent={statistics.mean([r['sentiment_compound'] for r in all_rt]):.3f}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
