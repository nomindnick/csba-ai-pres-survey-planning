#!/usr/bin/env python3
"""
Investigate Hillcrest 0-3 year staff anomaly:
- Is low sentiment driven by North Wing or transfers?
- Is the North Wing effect about audio/physical issues or demographics?
"""

import json
import sys
from collections import Counter

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

# ============================================================
# 1. PROFILE HILLCREST 0-3 YEAR GROUP
# ============================================================
print("=" * 70)
print("1. PROFILE: HILLCREST 0-3 YEAR STAFF")
print("=" * 70)

hillcrest = [r for r in data if r["site"] == "Hillcrest Elementary"]
hc_03 = [r for r in hillcrest if r["years_at_district_band"] == "0-3"]

print(f"\nHillcrest total: {len(hillcrest)}")
print(f"Hillcrest 0-3 year: {len(hc_03)}")

# Wing breakdown
wing_counts = Counter(r.get("building_wing") or "None" for r in hc_03)
print(f"\nWing distribution (0-3 yr):")
for wing, count in wing_counts.most_common():
    members = [r for r in hc_03 if (r.get("building_wing") or "None") == wing]
    avg_sent = sum(r["sentiment_normalized"] for r in members) / len(members)
    print(f"  {wing}: n={count}, avg_sentiment={avg_sent:.3f}")

# Transfer status
transfers = [r for r in hc_03 if r["is_transfer"]]
non_transfers = [r for r in hc_03 if not r["is_transfer"]]
print(f"\nTransfers: {len(transfers)}")
if transfers:
    avg_t = sum(r["sentiment_normalized"] for r in transfers) / len(transfers)
    print(f"  Avg sentiment (transfers): {avg_t:.3f}")
if non_transfers:
    avg_nt = sum(r["sentiment_normalized"] for r in non_transfers) / len(non_transfers)
    print(f"  Avg sentiment (non-transfers): {avg_nt:.3f}")

# Transfer origin quality
origin_counts = Counter(r.get("origin_district_system_quality") for r in transfers)
print(f"  Origin system quality: {dict(origin_counts)}")

# Position breakdown
pos_counts = Counter(r["position"] for r in hc_03)
print(f"\nPositions (0-3 yr):")
for pos, count in pos_counts.most_common():
    members = [r for r in hc_03 if r["position"] == pos]
    avg_s = sum(r["sentiment_normalized"] for r in members) / len(members)
    print(f"  {pos}: n={count}, avg_sentiment={avg_s:.3f}")

# ============================================================
# 2. HILLCREST 0-3 SENTIMENT WITH vs WITHOUT NORTH WING
# ============================================================
print("\n" + "=" * 70)
print("2. HILLCREST 0-3 SENTIMENT: WITH vs WITHOUT NORTH WING")
print("=" * 70)

hc_03_north = [r for r in hc_03 if r.get("building_wing") == "North Wing"]
hc_03_not_north = [r for r in hc_03 if r.get("building_wing") != "North Wing"]

if hc_03:
    avg_all = sum(r["sentiment_normalized"] for r in hc_03) / len(hc_03)
    print(f"\nAll 0-3 yr: n={len(hc_03)}, avg={avg_all:.3f}")
if hc_03_north:
    avg_n = sum(r["sentiment_normalized"] for r in hc_03_north) / len(hc_03_north)
    print(f"North Wing only: n={len(hc_03_north)}, avg={avg_n:.3f}")
if hc_03_not_north:
    avg_nn = sum(r["sentiment_normalized"] for r in hc_03_not_north) / len(hc_03_not_north)
    print(f"Excluding North Wing: n={len(hc_03_not_north)}, avg={avg_nn:.3f}")

# Compare to other Hillcrest tenure bands (excluding North Wing)
print("\nHillcrest sentiment by tenure (EXCLUDING North Wing):")
hc_no_north = [r for r in hillcrest if r.get("building_wing") != "North Wing"]
bands = sorted(set(r["years_at_district_band"] for r in hc_no_north),
               key=lambda x: int(x.split("-")[0].replace("+", "")))
for band in bands:
    members = [r for r in hc_no_north if r["years_at_district_band"] == band]
    if members:
        avg = sum(r["sentiment_normalized"] for r in members) / len(members)
        print(f"  {band}: n={len(members)}, avg={avg:.3f}")

# Compare to other sites' 0-3 year staff
print("\n0-3 year staff sentiment by site:")
sites_03 = {}
for r in data:
    if r["years_at_district_band"] == "0-3":
        sites_03.setdefault(r["site"], []).append(r)
for site in sorted(sites_03):
    members = sites_03[site]
    avg = sum(r["sentiment_normalized"] for r in members) / len(members)
    print(f"  {site}: n={len(members)}, avg={avg:.3f}")

# ============================================================
# 3. NORTH WING DEMOGRAPHICS vs REST OF HILLCREST
# ============================================================
print("\n" + "=" * 70)
print("3. NORTH WING DEMOGRAPHICS vs REST OF HILLCREST")
print("=" * 70)

hc_north = [r for r in hillcrest if r.get("building_wing") == "North Wing"]
hc_other = [r for r in hillcrest if r.get("building_wing") != "North Wing"]

print(f"\nNorth Wing: n={len(hc_north)}")
print(f"Rest of Hillcrest: n={len(hc_other)}")

for label, group in [("North Wing", hc_north), ("Rest of Hillcrest", hc_other)]:
    print(f"\n--- {label} ---")
    avg_sent = sum(r["sentiment_normalized"] for r in group) / len(group) if group else 0
    avg_age = sum(r["age"] for r in group) / len(group) if group else 0
    print(f"  Avg sentiment: {avg_sent:.3f}")
    print(f"  Avg age: {avg_age:.1f}")

    print(f"  Tenure bands:")
    for band in ["0-3", "4-10", "11-20", "21+"]:
        members = [r for r in group if r["years_at_district_band"] == band]
        if members:
            avg = sum(r["sentiment_normalized"] for r in members) / len(members)
            print(f"    {band}: n={len(members)}, avg_sent={avg:.3f}")

    print(f"  Positions:")
    for pos, count in Counter(r["position"] for r in group).most_common():
        members = [r for r in group if r["position"] == pos]
        avg = sum(r["sentiment_normalized"] for r in members) / len(members)
        print(f"    {pos}: n={count}, avg_sent={avg:.3f}")

    transfers = [r for r in group if r["is_transfer"]]
    print(f"  Transfers: {len(transfers)} ({100*len(transfers)/len(group):.0f}%)")

    room_types = Counter(r.get("room_type") or "None" for r in group)
    print(f"  Room types: {dict(room_types)}")

# ============================================================
# 4. READ ALL NORTH WING q1 AND q4 RESPONSES — CATEGORIZE COMPLAINTS
# ============================================================
print("\n" + "=" * 70)
print("4. ALL NORTH WING q1 AND q4 RESPONSES (COMPLAINT CATEGORIZATION)")
print("=" * 70)

# Keywords for categorization
audio_kw = ["audio", "sound", "echo", "static", "hear", "hearing", "speaker",
            "volume", "noise", "intercom", "feedback", "buzz", "crackl", "acoust",
            "muffled", "distort", "faint", "loud", "quiet", "unclear"]
process_kw = ["communicat", "told", "inform", "schedule", "timeline", "notice",
              "consult", "plan", "decision", "surprise", "blindsided", "warn"]
disruption_kw = ["disrupt", "interrupt", "class time", "routine", "construction",
                 "install", "noise during", "pulled out", "lost time", "chaos",
                 "mess", "dust", "debris"]

def categorize(text):
    if not text:
        return ["NO_RESPONSE"]
    text_lower = text.lower()
    cats = []
    if any(kw in text_lower for kw in audio_kw):
        cats.append("AUDIO/PHYSICAL")
    if any(kw in text_lower for kw in process_kw):
        cats.append("PROCESS/COMMUNICATION")
    if any(kw in text_lower for kw in disruption_kw):
        cats.append("DISRUPTION")
    if not cats:
        cats.append("OTHER")
    return cats

q1_cats = Counter()
q4_cats = Counter()
all_cats = Counter()

for r in hc_north:
    print(f"\n--- {r['employee_id']} | {r['position']} | {r['years_at_district_band']} yr | "
          f"sent={r['sentiment_normalized']:.3f} ({r['sentiment_category']}) | "
          f"transfer={r['is_transfer']} | room={r.get('room_type')} ---")

    q1_c = categorize(r["q1"])
    q4_c = categorize(r["q4"])

    print(f"  Q1 categories: {q1_c}")
    print(f"  Q1: {(r['q1'] or '(none)')[:200]}...")
    print(f"  Q4 categories: {q4_c}")
    print(f"  Q4: {(r['q4'] or '(none)')[:200]}...")

    for c in q1_c:
        q1_cats[c] += 1
    for c in q4_c:
        q4_cats[c] += 1
    for c in set(q1_c + q4_c):
        all_cats[c] += 1

print(f"\n\nCOMPLAINT CATEGORY SUMMARY (across q1 + q4):")
print(f"  Records mentioning each category (out of {len(hc_north)}):")
for cat, count in all_cats.most_common():
    print(f"    {cat}: {count} ({100*count/len(hc_north):.0f}%)")

print(f"\n  Q1 category hits: {dict(q1_cats)}")
print(f"  Q4 category hits: {dict(q4_cats)}")

# ============================================================
# 5. NORTH WING SENTIMENT BY POSITION AND TENURE
# ============================================================
print("\n" + "=" * 70)
print("5. NORTH WING SENTIMENT BY POSITION x TENURE")
print("=" * 70)

# By position
print("\nBy Position:")
for pos, count in Counter(r["position"] for r in hc_north).most_common():
    members = [r for r in hc_north if r["position"] == pos]
    avg = sum(r["sentiment_normalized"] for r in members) / len(members)
    cats = Counter(r["sentiment_category"] for r in members)
    print(f"  {pos}: n={count}, avg={avg:.3f}, categories={dict(cats)}")

# By tenure
print("\nBy Tenure:")
for band in ["0-3", "4-10", "11-20", "21+"]:
    members = [r for r in hc_north if r["years_at_district_band"] == band]
    if members:
        avg = sum(r["sentiment_normalized"] for r in members) / len(members)
        cats = Counter(r["sentiment_category"] for r in members)
        print(f"  {band}: n={len(members)}, avg={avg:.3f}, categories={dict(cats)}")

# Cross-tab
print("\nPosition x Tenure (North Wing):")
positions = sorted(set(r["position"] for r in hc_north))
bands = ["0-3", "4-10", "11-20", "21+"]
for pos in positions:
    for band in bands:
        members = [r for r in hc_north
                   if r["position"] == pos and r["years_at_district_band"] == band]
        if members:
            avg = sum(r["sentiment_normalized"] for r in members) / len(members)
            print(f"  {pos} / {band}: n={len(members)}, avg={avg:.3f}")

# ============================================================
# 6. TRANSFER EFFECT WITHIN HILLCREST (controlling for wing)
# ============================================================
print("\n" + "=" * 70)
print("6. TRANSFER EFFECT WITHIN HILLCREST (controlling for wing)")
print("=" * 70)

for wing_label, wing_group in [("North Wing", hc_north), ("Other Wings", hc_other)]:
    transfers = [r for r in wing_group if r["is_transfer"]]
    non_transfers = [r for r in wing_group if not r["is_transfer"]]
    print(f"\n{wing_label}:")
    if transfers:
        avg_t = sum(r["sentiment_normalized"] for r in transfers) / len(transfers)
        print(f"  Transfers: n={len(transfers)}, avg={avg_t:.3f}")
        # By origin quality
        for qual in sorted(set(r.get("origin_district_system_quality") for r in transfers if r.get("origin_district_system_quality"))):
            subset = [r for r in transfers if r.get("origin_district_system_quality") == qual]
            avg_q = sum(r["sentiment_normalized"] for r in subset) / len(subset)
            print(f"    Origin '{qual}': n={len(subset)}, avg={avg_q:.3f}")
    else:
        print(f"  Transfers: n=0")
    if non_transfers:
        avg_nt = sum(r["sentiment_normalized"] for r in non_transfers) / len(non_transfers)
        print(f"  Non-transfers: n={len(non_transfers)}, avg={avg_nt:.3f}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
