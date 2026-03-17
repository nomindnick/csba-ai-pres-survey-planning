#!/usr/bin/env python3
"""
Tenure Deep Dive: Is negativity about tenure itself, or about
(a) change fatigue, (b) attachment to old system, (c) not being consulted?
"""
import json
import re
from collections import Counter

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json") as f:
    data = json.load(f)

print(f"Total respondents: {len(data)}\n")

# --- Helper: combine all q1-q5 text for a respondent ---
def all_text(r):
    return " ".join(r.get(f"q{i}", "") or "" for i in range(1, 6)).lower()

# --- Helper: simple sentiment heuristic ---
POSITIVE_WORDS = ["great", "excellent", "love", "wonderful", "impressed", "smooth",
                  "improved", "better", "pleased", "happy", "appreciate", "good upgrade",
                  "works well", "positive", "excited", "welcome change"]
NEGATIVE_WORDS = ["frustrated", "disappointed", "terrible", "awful", "worse", "hate",
                  "unacceptable", "waste", "angry", "furious", "nightmare", "horrible",
                  "broken", "fail", "never work", "useless"]

def sentiment_score(text):
    t = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    return pos - neg

# ============================================================
# 1) For ALL 500, search for key phrases
# ============================================================
print("=" * 70)
print("1) KEYWORD PREVALENCE ACROSS ALL 500 RESPONDENTS")
print("=" * 70)

# Group into thematic clusters
CHANGE_FATIGUE = ["again", "another", "always", "every time", "same thing", "here we go",
                  "tired of", "yet another", "how many times", "keeps happening"]
OLD_SYSTEM_REF = ["old system", "previous system", "used to", "before the",
                  "what we had", "the way it was", "worked fine", "wasn't broken",
                  "old one", "previous one"]
CONSULTATION = ["not consulted", "never asked", "wasn't asked", "weren't asked",
                "no input", "no say", "didn't ask", "without asking",
                "not included", "wasn't included", "weren't included",
                "no one asked", "nobody asked", "not involved", "weren't consulted",
                "wasn't consulted", "didn't consult", "without consulting"]
# Broader consultation catches
CONSULTATION_BROAD = CONSULTATION + ["should have asked", "wish they had asked",
                                      "could have asked", "would have liked input",
                                      "voice", "opinion wasn't", "blindsided",
                                      "sprung on", "told not asked", "top-down",
                                      "decided for us", "no voice"]

def has_any(text, phrases):
    t = text.lower()
    return any(p in t for p in phrases)

bands = {"0-3": [], "4-10": [], "11-20": [], "20+": []}
for r in data:
    yrs = r["years_at_district"]
    if yrs <= 3:
        bands["0-3"].append(r)
    elif yrs <= 10:
        bands["4-10"].append(r)
    elif yrs <= 20:
        bands["11-20"].append(r)
    else:
        bands["20+"].append(r)

print(f"\nTenure band sizes: { {k: len(v) for k, v in bands.items()} }\n")

for label, phrases, desc in [
    ("Change fatigue", CHANGE_FATIGUE, "('again','another','always','every time','same thing', etc.)"),
    ("Old system ref", OLD_SYSTEM_REF, "('old system','used to','before','what we had', etc.)"),
    ("Not consulted (strict)", CONSULTATION, "('not consulted','never asked','no input', etc.)"),
    ("Not consulted (broad)", CONSULTATION_BROAD, "(includes 'blindsided','sprung on','top-down', etc.)"),
]:
    print(f"\n--- {label} {desc} ---")
    for band_name in ["0-3", "4-10", "11-20", "20+"]:
        group = bands[band_name]
        count = sum(1 for r in group if has_any(all_text(r), phrases))
        pct = count / len(group) * 100 if group else 0
        print(f"  {band_name:>5} years: {count:3d}/{len(group):3d} = {pct:5.1f}%")

# ============================================================
# 2) 20+ year veterans: % mentioning old system FAVORABLY
# ============================================================
print("\n" + "=" * 70)
print("2) 20+ YEAR VETERANS: OLD SYSTEM MENTIONED FAVORABLY")
print("=" * 70)

FAVORABLE_OLD = ["worked fine", "wasn't broken", "better than", "miss the old",
                 "preferred the old", "old system worked", "old one was",
                 "used to work", "what we had worked", "perfectly fine",
                 "nothing wrong with", "didn't need"]

veterans = bands["20+"]
fav_old_count = 0
fav_old_examples = []
for r in veterans:
    t = all_text(r)
    if has_any(t, FAVORABLE_OLD):
        fav_old_count += 1
        fav_old_examples.append(r)

pct = fav_old_count / len(veterans) * 100 if veterans else 0
print(f"\n20+ year staff mentioning old system favorably: {fav_old_count}/{len(veterans)} = {pct:.1f}%")
if fav_old_examples:
    print("\nExample quotes:")
    for r in fav_old_examples[:5]:
        t = all_text(r)
        # Find the sentence with the favorable mention
        for phrase in FAVORABLE_OLD:
            if phrase in t:
                # Extract surrounding context
                idx = t.index(phrase)
                start = max(0, t.rfind(".", 0, idx) + 1)
                end = t.find(".", idx) + 1 if t.find(".", idx) != -1 else len(t)
                snippet = t[start:end].strip()
                print(f"  - [{r['employee_id']}] {r['position']}, {r['years_at_district']}yr: \"{snippet}\"")
                break

# ============================================================
# 3) 20+ year veterans: % mentioning not consulted/asked/included
# ============================================================
print("\n" + "=" * 70)
print("3) 20+ YEAR VETERANS: NOT CONSULTED / NOT ASKED / NOT INCLUDED")
print("=" * 70)

consult_count = 0
consult_examples = []
for r in veterans:
    t = all_text(r)
    if has_any(t, CONSULTATION_BROAD):
        consult_count += 1
        consult_examples.append(r)

pct = consult_count / len(veterans) * 100 if veterans else 0
print(f"\n20+ year staff feeling not consulted (broad): {consult_count}/{len(veterans)} = {pct:.1f}%")

# Compare to other bands
for band_name in ["0-3", "4-10", "11-20"]:
    group = bands[band_name]
    c = sum(1 for r in group if has_any(all_text(r), CONSULTATION_BROAD))
    p = c / len(group) * 100 if group else 0
    print(f"  (comparison) {band_name:>5} years: {c}/{len(group)} = {p:.1f}%")

if consult_examples:
    print("\nExample quotes from 20+ year staff:")
    for r in consult_examples[:5]:
        t = all_text(r)
        for phrase in CONSULTATION_BROAD:
            if phrase in t:
                idx = t.index(phrase)
                start = max(0, t.rfind(".", 0, idx) + 1)
                end = t.find(".", idx) + 1 if t.find(".", idx) != -1 else len(t)
                snippet = t[start:end].strip()
                print(f"  - [{r['employee_id']}] {r['position']}, {r['years_at_district']}yr: \"{snippet}\"")
                break

# ============================================================
# 4) 0-3 year staff: do ANY mention old system or previous changes?
# ============================================================
print("\n" + "=" * 70)
print("4) 0-3 YEAR STAFF: MENTIONS OF OLD SYSTEM OR PREVIOUS CHANGES")
print("=" * 70)

newbies = bands["0-3"]
PREV_CHANGE_WORDS = OLD_SYSTEM_REF + CHANGE_FATIGUE + ["previous", "last time", "before this"]

new_mentioning = []
for r in newbies:
    t = all_text(r)
    if has_any(t, PREV_CHANGE_WORDS):
        new_mentioning.append(r)

pct = len(new_mentioning) / len(newbies) * 100 if newbies else 0
print(f"\n0-3 year staff mentioning old system/previous changes: {len(new_mentioning)}/{len(newbies)} = {pct:.1f}%")
if new_mentioning:
    print("\nExamples:")
    for r in new_mentioning[:5]:
        t = all_text(r)
        for phrase in PREV_CHANGE_WORDS:
            if phrase in t:
                idx = t.index(phrase)
                start = max(0, t.rfind(".", 0, idx) + 1)
                end = t.find(".", idx) + 1 if t.find(".", idx) != -1 else len(t)
                snippet = t[start:end].strip()
                print(f"  - [{r['employee_id']}] {r['position']}, {r['years_at_district']}yr: \"{snippet}\"")
                break
else:
    print("  None found — new staff have no reference point for the old system.")

# ============================================================
# 5) Positive 20+ year veterans — what makes them different?
# ============================================================
print("\n" + "=" * 70)
print("5) POSITIVE 20+ YEAR VETERANS — WHO ARE THEY?")
print("=" * 70)

# Score all veterans
vet_scored = []
for r in veterans:
    t = all_text(r)
    score = sentiment_score(t)
    vet_scored.append((score, r))

vet_scored.sort(key=lambda x: -x[0])  # most positive first

# Find positive ones (score > 0)
positive_vets = [(s, r) for s, r in vet_scored if s > 0]
neutral_vets = [(s, r) for s, r in vet_scored if s == 0]
negative_vets = [(s, r) for s, r in vet_scored if s < 0]

print(f"\n20+ year veterans sentiment breakdown:")
print(f"  Positive: {len(positive_vets)}/{len(veterans)} ({len(positive_vets)/len(veterans)*100:.1f}%)")
print(f"  Neutral:  {len(neutral_vets)}/{len(veterans)} ({len(neutral_vets)/len(veterans)*100:.1f}%)")
print(f"  Negative: {len(negative_vets)}/{len(veterans)} ({len(negative_vets)/len(veterans)*100:.1f}%)")

print(f"\nTop 5 most positive 20+ year veterans:")
for score, r in positive_vets[:5]:
    print(f"\n  [{r['employee_id']}] {r['name']}")
    print(f"  Position: {r['position']}, Site: {r['site']}")
    print(f"  District tenure: {r['years_at_district']}yr, Profession: {r['years_in_profession']}yr")
    print(f"  Transfer: {r['is_transfer']}, Wing: {r.get('building_wing')}, Room: {r.get('room_type')}")
    print(f"  Sentiment score: {score}")
    # Print their most telling responses
    for q in ["q1", "q5"]:
        resp = r.get(q, "")
        if resp:
            print(f"  {q}: \"{resp[:200]}{'...' if len(resp) > 200 else ''}\"")

# Also check if there are any truly positive ones — read full text
if not positive_vets:
    print("\n  No clearly positive 20+ year veterans found by keyword heuristic.")
    print("  Looking at least-negative instead:")
    for score, r in vet_scored[:5]:
        print(f"\n  [{r['employee_id']}] {r['name']} (score={score})")
        print(f"  Position: {r['position']}, Site: {r['site']}")
        print(f"  District tenure: {r['years_at_district']}yr")
        print(f"  q1: \"{r.get('q1', '')[:200]}\"")

# ============================================================
# 6) Among positive veterans, what % are site administrators?
# ============================================================
print("\n" + "=" * 70)
print("6) POSITIVE VETERANS: POSITION BREAKDOWN")
print("=" * 70)

if positive_vets:
    pos_counter = Counter(r["position"] for _, r in positive_vets)
    print(f"\nPositive 20+ year veterans by position (n={len(positive_vets)}):")
    for pos, count in pos_counter.most_common():
        pct = count / len(positive_vets) * 100
        print(f"  {pos}: {count} ({pct:.1f}%)")

    # Compare to overall veteran position distribution
    all_vet_pos = Counter(r["position"] for r in veterans)
    print(f"\nAll 20+ year veterans by position (n={len(veterans)}):")
    for pos, count in all_vet_pos.most_common():
        pct = count / len(veterans) * 100
        print(f"  {pos}: {count} ({pct:.1f}%)")

    admin_positive = sum(1 for _, r in positive_vets if "admin" in r["position"].lower() or "principal" in r["position"].lower())
    print(f"\n% of positive veterans who are administrators: {admin_positive}/{len(positive_vets)} = {admin_positive/len(positive_vets)*100:.1f}%")
else:
    # Use least-negative
    least_neg = vet_scored[:10]
    pos_counter = Counter(r["position"] for _, r in least_neg)
    print(f"\nLeast-negative 20+ year veterans by position (n={len(least_neg)}):")
    for pos, count in pos_counter.most_common():
        pct = count / len(least_neg) * 100
        print(f"  {pos}: {count} ({pct:.1f}%)")

# ============================================================
# SYNTHESIS: Which explanation wins?
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS: DISTINGUISHING THE THREE EXPLANATIONS")
print("=" * 70)

# Calculate change fatigue prevalence by band
print("\n--- Change Fatigue Signal ---")
for band_name in ["0-3", "4-10", "11-20", "20+"]:
    group = bands[band_name]
    c = sum(1 for r in group if has_any(all_text(r), CHANGE_FATIGUE))
    p = c / len(group) * 100 if group else 0
    print(f"  {band_name:>5}: {c}/{len(group)} = {p:.1f}%")

print("\n--- Old System Attachment Signal ---")
for band_name in ["0-3", "4-10", "11-20", "20+"]:
    group = bands[band_name]
    c = sum(1 for r in group if has_any(all_text(r), OLD_SYSTEM_REF))
    p = c / len(group) * 100 if group else 0
    print(f"  {band_name:>5}: {c}/{len(group)} = {p:.1f}%")

print("\n--- Not Consulted Signal ---")
for band_name in ["0-3", "4-10", "11-20", "20+"]:
    group = bands[band_name]
    c = sum(1 for r in group if has_any(all_text(r), CONSULTATION_BROAD))
    p = c / len(group) * 100 if group else 0
    print(f"  {band_name:>5}: {c}/{len(group)} = {p:.1f}%")

# Key test: among 20+ veterans, do the three signals overlap or are they distinct?
print("\n--- Overlap Analysis Among 20+ Year Veterans ---")
vet_fatigue = set(r["employee_id"] for r in veterans if has_any(all_text(r), CHANGE_FATIGUE))
vet_old_sys = set(r["employee_id"] for r in veterans if has_any(all_text(r), OLD_SYSTEM_REF))
vet_consult = set(r["employee_id"] for r in veterans if has_any(all_text(r), CONSULTATION_BROAD))

print(f"  Change fatigue only: {len(vet_fatigue - vet_old_sys - vet_consult)}")
print(f"  Old system only:     {len(vet_old_sys - vet_fatigue - vet_consult)}")
print(f"  Not consulted only:  {len(vet_consult - vet_fatigue - vet_old_sys)}")
print(f"  All three:           {len(vet_fatigue & vet_old_sys & vet_consult)}")
print(f"  Fatigue + old sys:   {len((vet_fatigue & vet_old_sys) - vet_consult)}")
print(f"  Fatigue + consult:   {len((vet_fatigue & vet_consult) - vet_old_sys)}")
print(f"  Old sys + consult:   {len((vet_old_sys & vet_consult) - vet_fatigue)}")
print(f"  None of the three:   {len(set(r['employee_id'] for r in veterans) - vet_fatigue - vet_old_sys - vet_consult)}")
