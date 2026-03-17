#!/usr/bin/env python3
"""Qualitative deep-dive: 10 most negative vs 10 most positive Riverside staff."""

import json, textwrap
from collections import Counter

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA) as f:
    data = json.load(f)

riverside = [r for r in data if r["site"] == "Riverside Elementary"]
riverside.sort(key=lambda r: r["sentiment_normalized"])

most_neg = riverside[:10]
most_pos = riverside[-10:]

def print_group(label, group):
    print(f"\n{'='*90}")
    print(f"  {label}")
    print(f"{'='*90}")
    for i, r in enumerate(group, 1):
        print(f"\n--- #{i}: {r['name']} ({r['employee_id']}) | sentiment_normalized={r['sentiment_normalized']:.3f} ---")
        print(f"  Position: {r['position']}  |  Age: {r['age']}  |  Gender: {r['gender']}  |  Race/Eth: {r['race_ethnicity']}")
        print(f"  Yrs at district: {r['years_at_district']} ({r['years_at_district_band']})  |  Yrs in profession: {r['years_in_profession']} ({r['years_in_profession_band']})")
        print(f"  Transfer: {r['is_transfer']}  |  Origin system quality: {r['origin_district_system_quality']}  |  Wing: {r['building_wing']}  |  Room: {r['room_type']}")
        for q in ["q1", "q5"]:
            text = r.get(q) or "(no response)"
            wrapped = textwrap.fill(text, width=85, initial_indent="    ", subsequent_indent="    ")
            print(f"  {q.upper()}:\n{wrapped}")
    print()

print_group("10 MOST NEGATIVE RIVERSIDE RESPONSES", most_neg)
print_group("10 MOST POSITIVE RIVERSIDE RESPONSES", most_pos)

# ── Profile summary ──
def summarize(label, group):
    print(f"\n{'='*90}")
    print(f"  PROFILE SUMMARY: {label}")
    print(f"{'='*90}")
    positions = Counter(r["position"] for r in group)
    tenure_bands = Counter(r["years_at_district_band"] for r in group)
    prof_bands = Counter(r["years_in_profession_band"] for r in group)
    transfers = Counter(r["is_transfer"] for r in group)
    origin_q = Counter(r["origin_district_system_quality"] for r in group if r["origin_district_system_quality"])
    ages = [r["age"] for r in group]
    genders = Counter(r["gender"] for r in group)
    rooms = Counter(r["room_type"] for r in group)
    wings = Counter(r["building_wing"] for r in group if r["building_wing"])

    print(f"  Positions:          {dict(positions)}")
    print(f"  District tenure:    {dict(tenure_bands)}")
    print(f"  Profession tenure:  {dict(prof_bands)}")
    print(f"  Transfers:          {dict(transfers)}")
    print(f"  Origin sys quality: {dict(origin_q) if origin_q else 'n/a (no transfers)'}")
    print(f"  Age range:          {min(ages)}-{max(ages)}, mean={sum(ages)/len(ages):.1f}")
    print(f"  Gender:             {dict(genders)}")
    print(f"  Room type:          {dict(rooms)}")
    print(f"  Building wing:      {dict(wings) if wings else 'n/a'}")
    print()

summarize("MOST NEGATIVE", most_neg)
summarize("MOST POSITIVE", most_pos)

# ── Quick theme extraction from q1+q5 text ──
print(f"\n{'='*90}")
print("  KEYWORD / THEME SCAN")
print(f"{'='*90}")

theme_keywords = {
    "disruption/routine":    ["disrupt", "routine", "thrown off", "adjustment", "adjusting"],
    "communication/blindsided": ["blindsided", "didn't know", "surprised", "no warning", "not told", "wasn't informed", "sprung"],
    "training concerns":     ["training", "wasn't enough", "too fast", "didn't cover"],
    "old system was fine":   ["old system", "didn't need", "worked fine", "wasn't broken", "unnecessary"],
    "installation issues":   ["install", "noise", "dust", "construction", "ceiling"],
    "positive comparison":   ["better than", "improvement", "upgrade", "clearer", "easier"],
    "transfer/prior system": ["previous district", "old district", "compared to", "where I came from", "transfer"],
    "safety concerns":       ["safety", "emergency", "lockdown", "fire", "evacuation"],
    "glitches/reliability":  ["glitch", "cut out", "unreliable", "malfunction", "broke", "doesn't work"],
    "classroom impact":      ["classroom", "students", "instruction", "teaching", "learning"],
}

for label, group in [("NEGATIVE", most_neg), ("POSITIVE", most_pos)]:
    print(f"\n  --- {label} group themes ---")
    for theme, keywords in theme_keywords.items():
        matches = []
        for r in group:
            text = " ".join([(r.get(f"q{i}") or "") for i in range(1,6)]).lower()
            if any(kw in text for kw in keywords):
                matches.append(r["name"])
        if matches:
            print(f"    {theme}: {len(matches)}/10 — {', '.join(matches)}")
    print()
