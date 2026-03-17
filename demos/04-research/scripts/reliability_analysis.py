#!/usr/bin/env python3
"""Analyze intermittent reliability complaints in survey data."""

import json
import re
from collections import Counter, defaultdict
from statistics import mean, median

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

print(f"Total respondents: {len(data)}\n")

# --- 1. Find reliability complainers ---
RELIABILITY_TERMS = [
    r"cuts?\s*out", r"sometimes", r"inconsistent", r"intermittent",
    r"unreliable", r"glitch(?:es|y|ing)?", r"static", r"drop(?:s|ped|ping)?",
    r"lag(?:s|gy|ging)?", r"delay(?:s|ed)?", r"some\s*days", r"hit\s*or\s*miss",
    r"in\s*and\s*out", r"spotty", r"flicker", r"cut\s*out", r"cuts\s*out",
    r"went\s*dead", r"goes\s*dead", r"goes\s*silent", r"went\s*silent",
    r"crackl(?:e|es|ing)", r"buzz(?:es|ing)?", r"feedback",
]

reliability_pattern = re.compile("|".join(RELIABILITY_TERMS), re.IGNORECASE)

# Secondary complaint patterns (communication/training/process issues)
COMM_TERMS = [
    r"communicat(?:ion|ed|ing)", r"told\s*(?:us|me)", r"inform(?:ed|ation)?",
    r"blindsided", r"no\s*notice", r"didn.t\s*know", r"never\s*(?:told|heard|informed)",
    r"lack\s*of\s*(?:communication|information|notice)",
]
TRAINING_TERMS = [
    r"train(?:ing|ed)?", r"learn(?:ed|ing)?", r"workshop", r"hands.on",
    r"demo(?:nstration)?", r"confus(?:ed|ing)", r"don.t\s*(?:understand|know\s*how)",
    r"figure\s*(?:it\s*)?out",
]
PROCESS_TERMS = [
    r"rushed", r"disrupt(?:ion|ed|ive)?", r"timeline", r"schedule",
    r"install(?:ation|ed)?.*(?:mess|chaos|problem)", r"consult(?:ed)?",
    r"input", r"voice", r"asked\s*(?:us|me)",
]

comm_pattern = re.compile("|".join(COMM_TERMS), re.IGNORECASE)
training_pattern = re.compile("|".join(TRAINING_TERMS), re.IGNORECASE)
process_pattern = re.compile("|".join(PROCESS_TERMS), re.IGNORECASE)

def get_all_text(r):
    return " ".join(r.get(f"q{i}", "") or "" for i in range(1, 6))

reliability_respondents = []
non_reliability = []

for r in data:
    text = get_all_text(r)
    if reliability_pattern.search(text):
        # Find which terms matched
        matches = reliability_pattern.findall(text)
        r["_reliability_matches"] = matches
        r["_all_text"] = text
        # Check for other complaint types
        r["_has_comm"] = bool(comm_pattern.search(text))
        r["_has_training"] = bool(training_pattern.search(text))
        r["_has_process"] = bool(process_pattern.search(text))
        r["_other_complaints"] = r["_has_comm"] or r["_has_training"] or r["_has_process"]
        reliability_respondents.append(r)
    else:
        non_reliability.append(r)

print("=" * 70)
print("1. RELIABILITY COMPLAINT PREVALENCE")
print("=" * 70)
n_rel = len(reliability_respondents)
print(f"Respondents mentioning reliability issues: {n_rel} / {len(data)} ({n_rel/len(data)*100:.1f}%)")

# Most common matched terms
all_matches = []
for r in reliability_respondents:
    all_matches.extend([m.lower() for m in r["_reliability_matches"]])
term_counts = Counter(all_matches)
print(f"\nMost common reliability terms:")
for term, count in term_counts.most_common(15):
    print(f"  '{term}': {count}")

# --- 2. Breakdown by site ---
print("\n" + "=" * 70)
print("2. BREAKDOWN BY SITE")
print("=" * 70)
site_total = Counter(r["site"] for r in data)
site_rel = Counter(r["site"] for r in reliability_respondents)

print(f"{'Site':<30} {'Reliability':>12} {'Total':>8} {'Rate':>8}")
print("-" * 60)
for site in sorted(site_total.keys()):
    rel = site_rel.get(site, 0)
    tot = site_total[site]
    print(f"{site:<30} {rel:>12} {tot:>8} {rel/tot*100:>7.1f}%")

# --- 3. Breakdown by building_wing and room_type ---
print("\n" + "=" * 70)
print("3. BREAKDOWN BY BUILDING_WING")
print("=" * 70)
wing_total = Counter(r.get("building_wing") or "None/null" for r in data)
wing_rel = Counter(r.get("building_wing") or "None/null" for r in reliability_respondents)

print(f"{'Wing':<25} {'Reliability':>12} {'Total':>8} {'Rate':>8}")
print("-" * 55)
for wing in sorted(wing_total.keys()):
    rel = wing_rel.get(wing, 0)
    tot = wing_total[wing]
    print(f"{wing:<25} {rel:>12} {tot:>8} {rel/tot*100:>7.1f}%")

print("\n" + "=" * 70)
print("4. BREAKDOWN BY ROOM_TYPE")
print("=" * 70)
room_total = Counter(r.get("room_type") or "None/null" for r in data)
room_rel = Counter(r.get("room_type") or "None/null" for r in reliability_respondents)

print(f"{'Room Type':<25} {'Reliability':>12} {'Total':>8} {'Rate':>8}")
print("-" * 55)
for room in sorted(room_total.keys()):
    rel = room_rel.get(room, 0)
    tot = room_total[room]
    print(f"{room:<25} {rel:>12} {tot:>8} {rel/tot*100:>7.1f}%")

# --- 4. Cross-tab: site x wing ---
print("\n" + "=" * 70)
print("5. CROSS-TAB: SITE x BUILDING_WING (reliability rate)")
print("=" * 70)
site_wing_total = defaultdict(int)
site_wing_rel = defaultdict(int)
for r in data:
    key = (r["site"], r.get("building_wing") or "None/null")
    site_wing_total[key] += 1
for r in reliability_respondents:
    key = (r["site"], r.get("building_wing") or "None/null")
    site_wing_rel[key] += 1

wings = sorted(set(r.get("building_wing") or "None/null" for r in data))
sites = sorted(set(r["site"] for r in data))

print(f"{'Site':<30}", end="")
for w in wings:
    print(f" {w:>12}", end="")
print()
print("-" * (30 + 13 * len(wings)))
for site in sites:
    print(f"{site:<30}", end="")
    for w in wings:
        key = (site, w)
        tot = site_wing_total.get(key, 0)
        rel = site_wing_rel.get(key, 0)
        if tot > 0:
            print(f" {rel}/{tot}={rel/tot*100:.0f}%".rjust(12), end="")
        else:
            print(f"{'---':>12}", end="")
    print()

# --- 5. Primary vs secondary complaint ---
print("\n" + "=" * 70)
print("6. PRIMARY vs SECONDARY COMPLAINT")
print("=" * 70)
primary = [r for r in reliability_respondents if not r["_other_complaints"]]
secondary = [r for r in reliability_respondents if r["_other_complaints"]]
print(f"Reliability as PRIMARY complaint (no other major issue types): {len(primary)} ({len(primary)/n_rel*100:.1f}%)")
print(f"Reliability as SECONDARY complaint (alongside comm/training/process): {len(secondary)} ({len(secondary)/n_rel*100:.1f}%)")

print(f"\nAmong those with secondary complaints:")
print(f"  Also mention communication issues: {sum(1 for r in secondary if r['_has_comm'])} ({sum(1 for r in secondary if r['_has_comm'])/len(secondary)*100:.1f}%)")
print(f"  Also mention training issues: {sum(1 for r in secondary if r['_has_training'])} ({sum(1 for r in secondary if r['_has_training'])/len(secondary)*100:.1f}%)")
print(f"  Also mention process issues: {sum(1 for r in secondary if r['_has_process'])} ({sum(1 for r in secondary if r['_has_process'])/len(secondary)*100:.1f}%)")

# --- 6. Representative quotes ---
print("\n" + "=" * 70)
print("7. REPRESENTATIVE RELIABILITY QUOTES (10 examples)")
print("=" * 70)

# Pick diverse examples: mix of primary/secondary, different sites
import random
random.seed(42)

# Get a mix: some primary, some secondary, different sites
quote_pool_primary = sorted(primary, key=lambda r: len(r["_reliability_matches"]), reverse=True)
quote_pool_secondary = sorted(secondary, key=lambda r: len(r["_reliability_matches"]), reverse=True)

selected = []
sites_seen = set()

# Get top primary from different sites
for r in quote_pool_primary:
    if r["site"] not in sites_seen or len(selected) < 3:
        selected.append(("PRIMARY", r))
        sites_seen.add(r["site"])
    if len(selected) >= 4:
        break

# Get top secondary from different sites
for r in quote_pool_secondary:
    if r["site"] not in sites_seen or len(selected) < 7:
        selected.append(("SECONDARY", r))
        sites_seen.add(r["site"])
    if len(selected) >= 10:
        break

for i, (complaint_type, r) in enumerate(selected[:10], 1):
    print(f"\n--- Quote {i} [{complaint_type}] ---")
    print(f"  {r['employee_id']} | {r['site']} | {r['position']} | Wing: {r.get('building_wing', 'N/A')} | Room: {r.get('room_type', 'N/A')}")
    print(f"  Terms matched: {r['_reliability_matches']}")
    # Find the question with the reliability mention
    for qi in range(1, 6):
        qtxt = r.get(f"q{qi}", "") or ""
        if reliability_pattern.search(qtxt):
            # Truncate long quotes
            display = qtxt[:300] + ("..." if len(qtxt) > 300 else "")
            print(f"  Q{qi}: \"{display}\"")

# --- 7. Demographic comparison ---
print("\n" + "=" * 70)
print("8. DEMOGRAPHIC COMPARISON: RELIABILITY COMPLAINERS vs NON-COMPLAINERS")
print("=" * 70)

def safe_mean(vals):
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else 0

rel_ages = [r["age"] for r in reliability_respondents if r.get("age")]
non_ages = [r["age"] for r in non_reliability if r.get("age")]
print(f"\nAge:")
print(f"  Complainers:     mean={safe_mean(rel_ages):.1f}, median={median(rel_ages)}")
print(f"  Non-complainers: mean={safe_mean(non_ages):.1f}, median={median(non_ages)}")

rel_yrs = [r["years_at_district"] for r in reliability_respondents if r.get("years_at_district") is not None]
non_yrs = [r["years_at_district"] for r in non_reliability if r.get("years_at_district") is not None]
print(f"\nYears at District:")
print(f"  Complainers:     mean={safe_mean(rel_yrs):.1f}, median={median(rel_yrs)}")
print(f"  Non-complainers: mean={safe_mean(non_yrs):.1f}, median={median(non_yrs)}")

rel_prof = [r["years_in_profession"] for r in reliability_respondents if r.get("years_in_profession") is not None]
non_prof = [r["years_in_profession"] for r in non_reliability if r.get("years_in_profession") is not None]
print(f"\nYears in Profession:")
print(f"  Complainers:     mean={safe_mean(rel_prof):.1f}, median={median(rel_prof)}")
print(f"  Non-complainers: mean={safe_mean(non_prof):.1f}, median={median(non_prof)}")

print(f"\nPosition:")
pos_rel = Counter(r["position"] for r in reliability_respondents)
pos_non = Counter(r["position"] for r in non_reliability)
pos_all = Counter(r["position"] for r in data)
print(f"  {'Position':<25} {'Complainer':>12} {'Non-comp':>12} {'Rate':>8}")
for pos in sorted(pos_all.keys()):
    rc = pos_rel.get(pos, 0)
    nc = pos_non.get(pos, 0)
    tot = pos_all[pos]
    print(f"  {pos:<25} {rc:>12} {nc:>12} {rc/tot*100:>7.1f}%")

print(f"\nGender:")
gen_rel = Counter(r["gender"] for r in reliability_respondents)
gen_all = Counter(r["gender"] for r in data)
for g in sorted(gen_all.keys()):
    rc = gen_rel.get(g, 0)
    tot = gen_all[g]
    print(f"  {g:<15} {rc}/{tot} = {rc/tot*100:.1f}%")

print(f"\nTransfer status:")
tr_rel = Counter(r.get("is_transfer", False) for r in reliability_respondents)
tr_all = Counter(r.get("is_transfer", False) for r in data)
for t in [True, False]:
    rc = tr_rel.get(t, 0)
    tot = tr_all.get(t, 0)
    label = "Transfer" if t else "Non-transfer"
    if tot > 0:
        print(f"  {label:<15} {rc}/{tot} = {rc/tot*100:.1f}%")

print(f"\nRace/Ethnicity:")
race_rel = Counter(r.get("race_ethnicity", "Unknown") for r in reliability_respondents)
race_all = Counter(r.get("race_ethnicity", "Unknown") for r in data)
print(f"  {'Race/Ethnicity':<30} {'Comp':>6} {'Total':>8} {'Rate':>8}")
for race in sorted(race_all.keys()):
    rc = race_rel.get(race, 0)
    tot = race_all[race]
    print(f"  {race:<30} {rc:>6} {tot:>8} {rc/tot*100:>7.1f}%")

# --- Summary ---
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
- {n_rel} of {len(data)} respondents ({n_rel/len(data)*100:.1f}%) mention reliability/intermittent issues
- {len(primary)} ({len(primary)/n_rel*100:.0f}%) cite reliability as their PRIMARY complaint
- {len(secondary)} ({len(secondary)/n_rel*100:.0f}%) cite it ALONGSIDE other issues (communication, training, process)
- Most common terms: {', '.join(f"'{t}' ({c})" for t,c in term_counts.most_common(5))}
""")
