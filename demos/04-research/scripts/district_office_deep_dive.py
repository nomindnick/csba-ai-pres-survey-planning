#!/usr/bin/env python3
"""Deep dive into District Office staff (n=12): the positive-but-critical-on-q5 contradiction."""

import json
import re
from collections import Counter

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json") as f:
    data = json.load(f)

# ── 1. Extract all District Office staff ──────────────────────────────
do_staff = [r for r in data if r["position"] == "District Office Staff"]
print(f"District Office staff count: {len(do_staff)}\n")

# ── 2. Demographics / tenure / position breakdown ─────────────────────
print("=" * 70)
print("DEMOGRAPHICS & TENURE")
print("=" * 70)

positions = Counter(r["position"] for r in do_staff)
print(f"\nPositions: {dict(positions)}")

tenures = sorted([r["years_at_district"] for r in do_staff])
print(f"Years at district: {tenures}")
print(f"  Mean: {sum(tenures)/len(tenures):.1f}  |  Range: {min(tenures)}-{max(tenures)}")

tenure_bands = Counter(r["years_at_district_band"] for r in do_staff)
print(f"  Bands: {dict(tenure_bands)}")

prof_years = sorted([r["years_in_profession"] for r in do_staff])
print(f"Years in profession: {prof_years}")
print(f"  Mean: {sum(prof_years)/len(prof_years):.1f}")

ages = sorted([r["age"] for r in do_staff])
print(f"Ages: {ages}")
print(f"  Mean: {sum(ages)/len(ages):.1f}")

transfers = Counter(r["is_transfer"] for r in do_staff)
print(f"Transfer status: {dict(transfers)}")

origin_quality = [r["origin_district_system_quality"] for r in do_staff if r["origin_district_system_quality"]]
if origin_quality:
    print(f"Origin system quality (transfers): {origin_quality}")

sites = Counter(r["site"] for r in do_staff)
print(f"Site distribution: {dict(sites)}")

genders = Counter(r["gender"] for r in do_staff)
print(f"Gender: {dict(genders)}")

races = Counter(r["race_ethnicity"] for r in do_staff)
print(f"Race/ethnicity: {dict(races)}")

wings = Counter(r["building_wing"] for r in do_staff)
print(f"Building wing: {dict(wings)}")

room_types = Counter(r["room_type"] for r in do_staff)
print(f"Room type: {dict(room_types)}")

# ── 3. Print ALL responses for every DO staff member ──────────────────
print("\n" + "=" * 70)
print("ALL DISTRICT OFFICE RESPONSES (FULL TEXT)")
print("=" * 70)

for i, r in enumerate(do_staff, 1):
    print(f"\n{'─' * 70}")
    print(f"[{i}] {r['employee_id']} — {r['name']}")
    print(f"    Position: {r['position']}  |  Age: {r['age']}  |  Tenure: {r['years_at_district']}y district / {r['years_in_profession']}y profession")
    print(f"    Transfer: {r['is_transfer']}  |  Wing: {r['building_wing']}  |  Room: {r['room_type']}")
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        print(f"  {q.upper()}: {r[q]}")

# ── 4. Thematic analysis of q5 (what would you change?) ──────────────
print("\n" + "=" * 70)
print("Q5 THEMATIC ANALYSIS — WHAT DISTRICT OFFICE STAFF WOULD CHANGE")
print("=" * 70)

# Keywords that signal district-wide / administrative perspective
admin_keywords = {
    "budget": 0, "cost": 0, "vendor": 0, "contract": 0, "procurement": 0,
    "timeline": 0, "schedule": 0, "deadline": 0,
    "district-wide": 0, "district wide": 0, "all sites": 0, "every site": 0, "across": 0,
    "rollout": 0, "implementation": 0, "planning": 0, "phase": 0,
    "coordination": 0, "coordinate": 0, "stakeholder": 0,
    "oversight": 0, "accountability": 0, "governance": 0,
    "standardiz": 0, "consistency": 0, "uniform": 0,
    "pilot": 0, "testing": 0,
    "training": 0, "support": 0, "help desk": 0,
    "communication": 0, "transparency": 0, "inform": 0,
    "feedback": 0, "input": 0, "voice": 0,
    "staff": 0, "morale": 0, "buy-in": 0,
}

# Front-line keywords (classroom/school level)
frontline_keywords = {
    "glitch": 0, "bug": 0, "crash": 0, "freeze": 0,
    "intercom": 0, "bell": 0, "PA": 0, "announcement": 0,
    "classroom": 0, "my room": 0, "my class": 0,
    "volume": 0, "sound": 0, "noise": 0, "static": 0,
    "button": 0, "interface": 0, "screen": 0,
}

print("\nQ5 responses with keyword flags:")
for r in do_staff:
    q5 = r["q5"].lower()
    print(f"\n  [{r['employee_id']}] {r['name']} ({r['position']}):")
    print(f"    \"{r['q5']}\"")

    admin_hits = [kw for kw in admin_keywords if kw in q5]
    front_hits = [kw for kw in frontline_keywords if kw in q5]
    if admin_hits:
        print(f"    >> Admin/district-level keywords: {admin_hits}")
    if front_hits:
        print(f"    >> Front-line/technical keywords: {front_hits}")

    for kw in admin_hits:
        admin_keywords[kw] += 1
    for kw in front_hits:
        frontline_keywords[kw] += 1

print("\n\nKeyword frequency across DO q5 responses:")
print("  Admin/district-level terms:")
for kw, count in sorted(admin_keywords.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"    {kw}: {count}")

print("  Front-line/technical terms:")
for kw, count in sorted(frontline_keywords.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"    {kw}: {count}")

# ── 5. Compare q5 themes: DO vs all other staff ──────────────────────
print("\n" + "=" * 70)
print("Q5 COMPARISON: DISTRICT OFFICE vs. ALL OTHER STAFF")
print("=" * 70)

non_do = [r for r in data if r["position"] != "District Office Staff"]
print(f"\nDistrict Office n={len(do_staff)}  |  All others n={len(non_do)}")

# Broader theme categories
themes = {
    "communication/transparency": ["communicat", "transparen", "inform", "told", "notice", "aware", "heads up", "heads-up"],
    "training": ["train", "workshop", "learn", "tutorial", "instruction"],
    "timeline/planning": ["timeline", "rush", "hurr", "plan", "phase", "rollout", "roll out", "schedule", "deadline", "slow"],
    "technical issues": ["glitch", "bug", "crash", "freeze", "error", "malfunction", "broken", "fail", "cut out", "static", "unreliable"],
    "vendor/contract": ["vendor", "contract", "compan", "supplier", "procure"],
    "budget/cost": ["budget", "cost", "money", "expensive", "fund", "price", "spend"],
    "staff input/buy-in": ["input", "voice", "feedback", "ask", "consult", "involve", "buy-in", "opinion", "listen"],
    "support/help": ["support", "help desk", "help", "assist", "technician", "IT"],
    "consistency/standardization": ["consisten", "standardiz", "uniform", "same", "every site", "all sites", "district-wide"],
    "leadership/oversight": ["leadership", "oversight", "accountab", "principal", "admin"],
    "workload/disruption": ["disrupt", "workload", "burden", "overwhelm", "busy", "time", "extra work"],
    "sound/volume": ["volume", "sound", "noise", "loud", "quiet", "hear"],
}

def theme_pct(responses, theme_words):
    count = 0
    for r in responses:
        text = (r["q5"] or "").lower()
        if any(w in text for w in theme_words):
            count += 1
    return count, count / len(responses) * 100 if responses else 0

print(f"\n{'Theme':<35} {'DO (n=12)':<18} {'Others (n={})'.format(len(non_do)):<18} {'Diff':>8}")
print("─" * 80)
for theme_name, words in themes.items():
    do_n, do_pct = theme_pct(do_staff, words)
    other_n, other_pct = theme_pct(non_do, words)
    diff = do_pct - other_pct
    marker = " ◄◄" if abs(diff) > 15 else " ◄" if abs(diff) > 8 else ""
    print(f"  {theme_name:<33} {do_n:>2} ({do_pct:5.1f}%)     {other_n:>3} ({other_pct:5.1f}%)  {diff:>+6.1f}%{marker}")

# ── 6. Q1-Q4 sentiment context ───────────────────────────────────────
print("\n" + "=" * 70)
print("Q1-Q4 THEMES FOR DISTRICT OFFICE (what they're POSITIVE about)")
print("=" * 70)

for q in ["q1", "q2", "q3", "q4"]:
    print(f"\n  {q.upper()} responses:")
    for r in do_staff:
        text = r[q] or "(no response)"
        print(f"    [{r['employee_id']}] {text[:120]}{'...' if len(text) > 120 else ''}")

# ── 7. Position-specific breakdown within DO ──────────────────────────
print("\n" + "=" * 70)
print("POSITION BREAKDOWN WITHIN DISTRICT OFFICE")
print("=" * 70)

for pos, count in positions.items():
    pos_staff = [r for r in do_staff if r["position"] == pos]
    print(f"\n  {pos} (n={count}):")
    for r in pos_staff:
        print(f"    {r['employee_id']} {r['name']} — tenure {r['years_at_district']}y")
        print(f"      Q5: {r['q5'][:200]}")

# ── 8. What DO mentions that others rarely do ─────────────────────────
print("\n" + "=" * 70)
print("DISTINCTIVE LANGUAGE: Words/phrases more common in DO q5 vs others")
print("=" * 70)

# Build word frequency for DO vs others in q5
def word_freq(responses, field="q5"):
    words = Counter()
    for r in responses:
        text = re.sub(r'[^\w\s]', '', (r[field] or "").lower())
        for w in text.split():
            if len(w) > 3:  # skip short words
                words[w] += 1
    # Normalize to per-response rate
    total = len(responses)
    return {w: c/total for w, c in words.items()}

do_freq = word_freq(do_staff)
other_freq = word_freq(non_do)

print("\nWords significantly more frequent in DO q5 responses:")
print(f"  {'Word':<20} {'DO rate':<12} {'Others rate':<12} {'Ratio':>8}")
print("  " + "─" * 55)
ratios = []
for w, rate in do_freq.items():
    other_rate = other_freq.get(w, 0.001)
    ratio = rate / other_rate
    if rate >= 0.15:  # appears in at least ~2 of 12 responses
        ratios.append((w, rate, other_freq.get(w, 0), ratio))

for w, dr, or_, ratio in sorted(ratios, key=lambda x: -x[3])[:25]:
    print(f"  {w:<20} {dr:<12.3f} {or_:<12.3f} {ratio:>7.1f}x")

print("\n\nDone.")
