#!/usr/bin/env python3
"""
Qualitative deep-dive: Food Service + Custodial/Facilities staff by tenure band.
Focus on 20+ year veterans vs. 0-3 year newcomers.
"""

import json
from collections import Counter, defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

# ── 1. Filter to target positions ──────────────────────────────────────────
TARGET_POS = {"Food Service", "Custodial/Facilities"}
ops = [r for r in data if r["position"] in TARGET_POS]

print(f"Total records: {len(data)}")
print(f"Food Service + Custodial/Facilities records: {len(ops)}")
print()

# ── 2. Split by tenure band ────────────────────────────────────────────────
by_tenure = defaultdict(list)
for r in ops:
    by_tenure[r["years_at_district_band"]].append(r)

print("=== TENURE BAND DISTRIBUTION ===")
for band in sorted(by_tenure.keys(), key=lambda b: int(b.split("-")[0].replace("+", ""))):
    positions = Counter(r["position"] for r in by_tenure[band])
    print(f"  {band}: {len(by_tenure[band])} staff  {dict(positions)}")
print()

# ── 3 & 4. Print ALL q1-q5 for 20+ year group and 0-3 year group ──────────
QUESTIONS = ["q1", "q2", "q3", "q4", "q5"]
Q_LABELS = {
    "q1": "Overall experience with the new system",
    "q2": "Training adequacy",
    "q3": "Communication about the change",
    "q4": "What worked well",
    "q5": "Concerns / suggestions",
}

def print_all_responses(group, label):
    print(f"\n{'='*80}")
    print(f"  {label} — {len(group)} respondents")
    print(f"{'='*80}")
    for r in group:
        print(f"\n--- {r['employee_id']} | {r['name']} | {r['position']} | "
              f"Site: {r['site']} | Age: {r['age']} | "
              f"District yrs: {r['years_at_district']} | Profession yrs: {r['years_in_profession']} | "
              f"Transfer: {r['is_transfer']} ---")
        for q in QUESTIONS:
            print(f"  [{q} - {Q_LABELS[q]}]")
            print(f"    {r[q]}")
        print()

# 20+ year veterans
veterans = by_tenure.get("20+", [])
print_all_responses(veterans, "20+ YEAR VETERANS (Food Service + Custodial/Facilities)")

# 0-3 year newcomers
newcomers = by_tenure.get("0-3", [])
print_all_responses(newcomers, "0-3 YEAR NEWCOMERS (Food Service + Custodial/Facilities)")

# ── 6. Site distribution ───────────────────────────────────────────────────
print(f"\n{'='*80}")
print("  SITE DISTRIBUTION")
print(f"{'='*80}")

print("\nAll ops staff by site:")
site_counts = Counter(r["site"] for r in ops)
for site, count in site_counts.most_common():
    print(f"  {site}: {count}")

print("\n20+ year veterans by site:")
vet_sites = Counter(r["site"] for r in veterans)
for site, count in vet_sites.most_common():
    print(f"  {site}: {count}")

print("\n0-3 year newcomers by site:")
new_sites = Counter(r["site"] for r in newcomers)
for site, count in new_sites.most_common():
    print(f"  {site}: {count}")

# ── 7. Complaint theme analysis ───────────────────────────────────────────
print(f"\n{'='*80}")
print("  COMPLAINT THEME ANALYSIS — 20+ YEAR VETERANS")
print(f"{'='*80}")

# Keyword buckets
SYSTEM_KEYWORDS = ["glitch", "broken", "doesn't work", "unreliable", "malfunction",
                   "sound quality", "static", "cut out", "interface", "confusing",
                   "complicated", "hard to use", "difficult", "clunky", "buggy",
                   "worse than", "old system was", "downgrade"]
ROLLOUT_KEYWORDS = ["rushed", "timeline", "schedule", "installation", "disruption",
                    "disruptive", "construction", "noise", "mess", "contractors",
                    "during school", "during class", "timing", "poorly planned",
                    "no warning", "last minute", "short notice"]
OVERLOOKED_KEYWORDS = ["ignored", "overlooked", "forgot", "forgotten", "afterthought",
                       "didn't ask", "never asked", "no input", "no say", "not consulted",
                       "left out", "not included", "nobody asked", "didn't consider",
                       "invisible", "don't matter", "doesn't matter", "second class",
                       "not a priority", "not important", "kitchen", "cafeteria",
                       "custodial", "our spaces", "our areas", "break room",
                       "didn't think about", "weren't considered", "weren't included"]

def classify_themes(records, label):
    system_hits = []
    rollout_hits = []
    overlooked_hits = []

    for r in records:
        all_text = " ".join((r[q] or "").lower() for q in QUESTIONS)

        if any(kw in all_text for kw in SYSTEM_KEYWORDS):
            system_hits.append(r)
        if any(kw in all_text for kw in ROLLOUT_KEYWORDS):
            rollout_hits.append(r)
        if any(kw in all_text for kw in OVERLOOKED_KEYWORDS):
            overlooked_hits.append(r)

    print(f"\n{label}:")
    print(f"  System complaints:  {len(system_hits)}/{len(records)} "
          f"({100*len(system_hits)/max(len(records),1):.0f}%)")
    print(f"  Rollout complaints: {len(rollout_hits)}/{len(records)} "
          f"({100*len(rollout_hits)/max(len(records),1):.0f}%)")
    print(f"  Feeling overlooked: {len(overlooked_hits)}/{len(records)} "
          f"({100*len(overlooked_hits)/max(len(records),1):.0f}%)")

    return system_hits, rollout_hits, overlooked_hits

vet_sys, vet_roll, vet_over = classify_themes(veterans, "20+ year veterans")
new_sys, new_roll, new_over = classify_themes(newcomers, "0-3 year newcomers")

# Also classify the middle bands for comparison
for band_name in ["4-10", "11-20"]:
    if band_name in by_tenure:
        classify_themes(by_tenure[band_name], f"{band_name} year staff")

# ── Highlight the most negative veteran responses ─────────────────────────
print(f"\n{'='*80}")
print("  MOST NEGATIVE VETERAN QUOTES (20+ years)")
print(f"{'='*80}")

# Simple negativity score: count negative keywords across all responses
NEGATIVE_WORDS = ["frustrated", "frustrating", "angry", "upset", "terrible",
                  "awful", "worst", "waste", "unacceptable", "disappointed",
                  "disappointing", "ignored", "overlooked", "disrespect",
                  "insulting", "ridiculous", "absurd", "incompetent",
                  "nobody", "never", "nothing", "broken", "useless",
                  "pointless", "afterthought", "forgotten", "invisible",
                  "didn't care", "don't care", "doesn't care",
                  "not once", "not a single", "slap in the face"]

scored = []
for r in veterans:
    all_text = " ".join((r[q] or "").lower() for q in QUESTIONS)
    score = sum(1 for kw in NEGATIVE_WORDS if kw in all_text)
    scored.append((score, r))

scored.sort(key=lambda x: -x[0])

print("\nTop negative respondents by keyword density:")
for score, r in scored[:10]:
    print(f"\n  Score: {score} | {r['employee_id']} | {r['name']} | {r['position']} | "
          f"{r['site']} | {r['years_at_district']} yrs district")
    for q in QUESTIONS:
        text = r[q]
        # Bold any negative words found
        print(f"    {q}: {text}")

# ── Cross-tab: overlooked theme by position ───────────────────────────────
print(f"\n{'='*80}")
print("  'OVERLOOKED' THEME — POSITION BREAKDOWN AMONG 20+ YR VETERANS")
print(f"{'='*80}")
if vet_over:
    pos_counts = Counter(r["position"] for r in vet_over)
    for pos, count in pos_counts.most_common():
        total_in_pos = sum(1 for r in veterans if r["position"] == pos)
        print(f"  {pos}: {count}/{total_in_pos} mention feeling overlooked")
else:
    print("  No 'overlooked' theme hits found.")

# ── Additional: check room_type and building_wing for ops staff ───────────
print(f"\n{'='*80}")
print("  ROOM TYPE & BUILDING WING — OPS STAFF")
print(f"{'='*80}")
print("\nRoom types (all ops staff):")
room_counts = Counter(r["room_type"] for r in ops)
for rt, count in room_counts.most_common():
    print(f"  {rt}: {count}")

print("\nBuilding wings (all ops staff):")
wing_counts = Counter(str(r["building_wing"]) for r in ops)
for w, count in wing_counts.most_common():
    print(f"  {w}: {count}")

print("\n20+ yr veterans — room types:")
vet_room = Counter(r["room_type"] for r in veterans)
for rt, count in vet_room.most_common():
    print(f"  {rt}: {count}")

print("\nDone.")
