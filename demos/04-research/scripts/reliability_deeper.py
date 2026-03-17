#!/usr/bin/env python3
"""Deeper analysis: primary vs secondary reliability, and North Wing deep dive."""

import json
import re
from collections import Counter

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

RELIABILITY_TERMS = [
    r"cuts?\s*out", r"sometimes", r"inconsistent", r"intermittent",
    r"unreliable", r"glitch(?:es|y|ing)?", r"static", r"drop(?:s|ped|ping)?",
    r"lag(?:s|gy|ging)?", r"delay(?:s|ed)?", r"some\s*days", r"hit\s*or\s*miss",
    r"in\s*and\s*out", r"spotty", r"flicker", r"cut\s*out",
    r"went\s*dead", r"goes\s*dead", r"goes\s*silent", r"went\s*silent",
    r"crackl(?:e|es|ing)", r"buzz(?:es|ing)?", r"feedback",
]
reliability_pattern = re.compile("|".join(RELIABILITY_TERMS), re.IGNORECASE)

# Better "primary" analysis: count reliability terms vs negative-non-reliability terms per response
NEGATIVE_NON_RELIABILITY = [
    r"poor\s*communication", r"wasn.t\s*(?:told|informed|consulted)",
    r"no\s*(?:input|voice|say)", r"blindsided", r"rushed",
    r"inadequate\s*training", r"didn.t\s*(?:learn|understand)",
    r"disrespect", r"ignored", r"not\s*(?:asked|consulted|informed)",
    r"frustrat(?:ed|ing)", r"overwhelm(?:ed|ing)", r"confus(?:ed|ing)",
]
neg_pattern = re.compile("|".join(NEGATIVE_NON_RELIABILITY), re.IGNORECASE)

def get_all_text(r):
    return " ".join(r.get(f"q{i}", "") or "" for i in range(1, 6))

# Better approach: For each reliability complainer, check if reliability
# is their DOMINANT theme in Q5 (the "what would you improve" question)
print("=" * 70)
print("PRIMARY vs SECONDARY: Is reliability the MAIN thing they'd improve?")
print("=" * 70)

reliability_respondents = []
for r in data:
    text = get_all_text(r)
    if reliability_pattern.search(text):
        reliability_respondents.append(r)

# Check Q5 specifically - what would they improve
q5_primary = []  # Q5 is primarily about reliability
q5_secondary = []  # Q5 mentions reliability but also other things
q5_elsewhere = []  # reliability mentioned in other Qs but not Q5

for r in reliability_respondents:
    q5 = r.get("q5", "") or ""
    other_qs = " ".join(r.get(f"q{i}", "") or "" for i in range(1, 5))

    q5_has_reliability = bool(reliability_pattern.search(q5))
    other_has_reliability = bool(reliability_pattern.search(other_qs))

    if q5_has_reliability:
        # Check if Q5 is MOSTLY about reliability (reliability terms outnumber others)
        rel_matches = len(reliability_pattern.findall(q5))
        q5_words = len(q5.split())
        # If Q5 is short and focused on reliability, or reliability dominates
        q5_sentences = [s.strip() for s in re.split(r'[.!?]+', q5) if s.strip()]
        rel_sentences = [s for s in q5_sentences if reliability_pattern.search(s)]

        if len(rel_sentences) / max(len(q5_sentences), 1) > 0.5:
            q5_primary.append(r)
        else:
            q5_secondary.append(r)
    else:
        q5_elsewhere.append(r)

print(f"Reliability is DOMINANT theme in Q5: {len(q5_primary)} ({len(q5_primary)/len(reliability_respondents)*100:.1f}%)")
print(f"Reliability mentioned in Q5 alongside other issues: {len(q5_secondary)} ({len(q5_secondary)/len(reliability_respondents)*100:.1f}%)")
print(f"Reliability mentioned in other Qs but NOT in Q5: {len(q5_elsewhere)} ({len(q5_elsewhere)/len(reliability_respondents)*100:.1f}%)")

print(f"\nExamples where reliability DOMINATES Q5:")
for r in q5_primary[:5]:
    print(f"  [{r['employee_id']}] Q5: \"{(r.get('q5','') or '')[:200]}...\"")

print(f"\nExamples where reliability is in other Qs but NOT Q5:")
for r in q5_elsewhere[:5]:
    q5 = (r.get('q5','') or '')[:150]
    # Find which Q has the reliability mention
    for qi in range(1, 5):
        qtxt = r.get(f"q{qi}", "") or ""
        if reliability_pattern.search(qtxt):
            print(f"  [{r['employee_id']}] Reliability in Q{qi}, but Q5: \"{q5}...\"")
            break

# === NORTH WING DEEP DIVE ===
print("\n" + "=" * 70)
print("NORTH WING DEEP DIVE")
print("=" * 70)

north_wing = [r for r in data if r.get("building_wing") == "North Wing"]
print(f"Total North Wing respondents: {len(north_wing)}")
print(f"All at site: {Counter(r['site'] for r in north_wing)}")
print(f"Positions: {Counter(r['position'] for r in north_wing)}")
print(f"Reliability complainers: {sum(1 for r in north_wing if reliability_pattern.search(get_all_text(r)))}")

nw_rel = [r for r in north_wing if reliability_pattern.search(get_all_text(r))]
nw_non = [r for r in north_wing if not reliability_pattern.search(get_all_text(r))]

print(f"\nNorth Wing reliability complainers by position:")
for pos, count in Counter(r['position'] for r in nw_rel).most_common():
    print(f"  {pos}: {count}")

print(f"\nNorth Wing reliability complaint quotes:")
for r in nw_rel[:6]:
    text = get_all_text(r)
    matches = reliability_pattern.findall(text)
    print(f"\n  [{r['employee_id']}] {r['position']} | {r.get('room_type','?')}")
    print(f"  Terms: {matches}")
    for qi in range(1, 6):
        qtxt = r.get(f"q{qi}", "") or ""
        if reliability_pattern.search(qtxt):
            print(f"  Q{qi}: \"{qtxt[:250]}{'...' if len(qtxt)>250 else ''}\"")

# Compare Hillcrest North Wing vs Hillcrest non-North-Wing
print("\n" + "=" * 70)
print("HILLCREST: NORTH WING vs REST OF SCHOOL")
print("=" * 70)
hillcrest = [r for r in data if r["site"] == "Hillcrest Elementary"]
hc_nw = [r for r in hillcrest if r.get("building_wing") == "North Wing"]
hc_other = [r for r in hillcrest if r.get("building_wing") != "North Wing"]

hc_nw_rel = sum(1 for r in hc_nw if reliability_pattern.search(get_all_text(r)))
hc_oth_rel = sum(1 for r in hc_other if reliability_pattern.search(get_all_text(r)))

print(f"North Wing: {hc_nw_rel}/{len(hc_nw)} = {hc_nw_rel/len(hc_nw)*100:.1f}% report reliability issues")
print(f"Rest of Hillcrest: {hc_oth_rel}/{len(hc_other)} = {hc_oth_rel/len(hc_other)*100:.1f}% report reliability issues")

# What terms are North Wing using vs others?
nw_terms = []
oth_terms = []
for r in hc_nw:
    text = get_all_text(r)
    nw_terms.extend(reliability_pattern.findall(text))
for r in hc_other:
    text = get_all_text(r)
    oth_terms.extend(reliability_pattern.findall(text))

print(f"\nNorth Wing top terms: {Counter(t.lower() for t in nw_terms).most_common(8)}")
print(f"Rest of Hillcrest top terms: {Counter(t.lower() for t in oth_terms).most_common(8)}")

# Tenure comparison within North Wing
from statistics import mean, median
print(f"\nNorth Wing demographics:")
print(f"  Mean age: {mean(r['age'] for r in hc_nw):.1f}")
print(f"  Mean yrs at district: {mean(r['years_at_district'] for r in hc_nw):.1f}")
print(f"  Transfers: {sum(1 for r in hc_nw if r.get('is_transfer'))}/{len(hc_nw)}")
print(f"  Room types: {Counter(r.get('room_type','?') for r in hc_nw)}")
