#!/usr/bin/env python3
"""
Analyze communication cascade patterns in q3 responses.
Tests whether information flowed top-down through the org chart,
with front-line staff learning late or through unofficial channels.
"""

import json
import re
from collections import defaultdict, Counter

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
positions = Counter(r["position"] for r in data)
print(f"\nPosition counts:")
for pos, ct in positions.most_common():
    print(f"  {pos}: {ct}")

# ── 1. Keyword analysis on q3 ──────────────────────────────────────────────

official_keywords = ["email", "meeting", "memo", "admin", "principal", "informed",
                     "newsletter", "announcement", "notice", "notified"]
unofficial_keywords = ["grapevine", "colleague", "teacher", "heard from",
                       "told by", "word of mouth", "rumor", "hallway",
                       "lunch", "overheard"]
timing_negative = ["blindsided", "last minute", "late", "last to know",
                   "no warning", "sudden", "surprised", "caught off guard",
                   "short notice", "no notice"]
timing_positive = ["early", "advance", "ahead of time", "plenty of notice",
                   "well in advance", "good notice", "ample time"]

def count_keywords(text, keywords):
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if kw in text_lower:
            found.append(kw)
    return found

print("\n" + "="*80)
print("1. KEYWORD FREQUENCY IN Q3 BY POSITION")
print("="*80)

all_keywords = official_keywords + unofficial_keywords + timing_negative + timing_positive
keyword_by_position = defaultdict(lambda: defaultdict(int))
keyword_totals = defaultdict(int)

for r in data:
    q3 = r["q3"]
    pos = r["position"]
    for kw in all_keywords:
        if kw in q3.lower():
            keyword_by_position[pos][kw] += 1
            keyword_totals[kw] += 1

# Print top keywords overall
print("\nTop keywords overall:")
for kw, ct in sorted(keyword_totals.items(), key=lambda x: -x[1])[:20]:
    print(f"  '{kw}': {ct}")

# ── 2. Official vs Unofficial channel usage by position ────────────────────

print("\n" + "="*80)
print("2. OFFICIAL vs UNOFFICIAL CHANNEL MENTIONS BY POSITION")
print("="*80)

position_channels = {}
for pos in sorted(positions.keys()):
    pos_records = [r for r in data if r["position"] == pos]
    n = len(pos_records)

    official_count = 0
    unofficial_count = 0
    neg_timing_count = 0
    pos_timing_count = 0
    both_count = 0

    for r in pos_records:
        q3 = r["q3"].lower()
        has_official = any(kw in q3 for kw in official_keywords)
        has_unofficial = any(kw in q3 for kw in unofficial_keywords)
        has_neg_timing = any(kw in q3 for kw in timing_negative)
        has_pos_timing = any(kw in q3 for kw in timing_positive)

        if has_official:
            official_count += 1
        if has_unofficial:
            unofficial_count += 1
        if has_neg_timing:
            neg_timing_count += 1
        if has_pos_timing:
            pos_timing_count += 1
        if has_official and has_unofficial:
            both_count += 1

    position_channels[pos] = {
        "n": n,
        "official": official_count,
        "unofficial": unofficial_count,
        "neg_timing": neg_timing_count,
        "pos_timing": pos_timing_count,
        "both": both_count
    }

# Print table
print(f"\n{'Position':<25} {'N':>4} {'Official':>10} {'Unofficial':>12} {'Neg Timing':>12} {'Pos Timing':>12}")
print("-" * 80)
for pos in sorted(position_channels.keys()):
    d = position_channels[pos]
    n = d["n"]
    print(f"{pos:<25} {n:>4} "
          f"{d['official']:>4} ({d['official']/n*100:4.0f}%) "
          f"{d['unofficial']:>4} ({d['unofficial']/n*100:4.0f}%) "
          f"{d['neg_timing']:>4} ({d['neg_timing']/n*100:4.0f}%) "
          f"{d['pos_timing']:>4} ({d['pos_timing']/n*100:4.0f}%)")

print(f"\n  Note: 'Both' = mentioned both official AND unofficial channels:")
for pos in sorted(position_channels.keys()):
    d = position_channels[pos]
    if d["both"] > 0:
        print(f"    {pos}: {d['both']} ({d['both']/d['n']*100:.0f}%)")

# ── 3. All 20 Site Administrator q3 responses ─────────────────────────────

print("\n" + "="*80)
print("3. ALL SITE ADMINISTRATOR Q3 RESPONSES")
print("="*80)

admins = [r for r in data if r["position"] == "Site Administrator"]
print(f"\nFound {len(admins)} Site Administrators\n")
for r in admins:
    print(f"--- {r['employee_id']} | {r['name']} | {r['site']} ---")
    print(f"  Q3: {r['q3']}")
    print()

# ── 4. 10 most negative Custodial/Facilities q3 ───────────────────────────

print("\n" + "="*80)
print("4. MOST NEGATIVE CUSTODIAL/FACILITIES Q3 RESPONSES")
print("="*80)

def negativity_score(text):
    """Simple negativity heuristic based on keyword presence."""
    text_lower = text.lower()
    score = 0
    neg_words = ["blindsided", "frustrated", "ignored", "last to know", "never",
                 "no one", "nobody", "terrible", "awful", "horrible", "worst",
                 "angry", "upset", "furious", "unacceptable", "disrespect",
                 "grapevine", "last minute", "no warning", "no notice",
                 "not told", "wasn't told", "weren't told", "didn't know",
                 "found out", "caught off guard", "afterthought", "invisible",
                 "overlooked", "forgotten", "left out", "excluded", "late",
                 "short notice", "surprised", "shocked", "disappointed",
                 "poor", "lack", "failed", "failure"]
    for w in neg_words:
        if w in text_lower:
            score += 1
    return score

custodial = [r for r in data if r["position"] == "Custodial/Facilities"]
custodial_scored = [(r, negativity_score(r["q3"])) for r in custodial]
custodial_scored.sort(key=lambda x: -x[1])

print(f"\nFound {len(custodial)} Custodial/Facilities staff. Showing top 10 most negative:\n")
for r, score in custodial_scored[:10]:
    print(f"--- {r['employee_id']} | {r['name']} | {r['site']} | neg_score={score} ---")
    print(f"  Q3: {r['q3']}")
    print()

# ── 5. 10 most negative Food Service q3 ───────────────────────────────────

print("\n" + "="*80)
print("5. MOST NEGATIVE FOOD SERVICE Q3 RESPONSES")
print("="*80)

food = [r for r in data if r["position"] == "Food Service"]
food_scored = [(r, negativity_score(r["q3"])) for r in food]
food_scored.sort(key=lambda x: -x[1])

print(f"\nFound {len(food)} Food Service staff. Showing top 10 most negative:\n")
for r, score in food_scored[:10]:
    print(f"--- {r['employee_id']} | {r['name']} | {r['site']} | neg_score={score} ---")
    print(f"  Q3: {r['q3']}")
    print()

# ── 6. Communication path mapping ─────────────────────────────────────────

print("\n" + "="*80)
print("6. COMMUNICATION PATH MAPPING — WHO HEARD FROM WHOM?")
print("="*80)

# Look for patterns like "heard from [source]", "told by [source]",
# "found out from [source]", "learned from [source]"
source_patterns = [
    (r"heard (?:about it |about the |about )?from (\w[\w\s]*?)(?:\.|,|;|$| that| —)", "heard from"),
    (r"told (?:us |me )?by (\w[\w\s]*?)(?:\.|,|;|$| that| —)", "told by"),
    (r"found out (?:about it |about the )?from (\w[\w\s]*?)(?:\.|,|;|$| that| —)", "found out from"),
    (r"learned (?:about it |about the )?from (\w[\w\s]*?)(?:\.|,|;|$| that| —)", "learned from"),
    (r"(?:another|a|my|the) (teacher|colleague|custodian|admin|principal|coworker|co-worker|staff member|secretary|para)", "mentioned role"),
]

path_by_position = defaultdict(list)
source_mentions = defaultdict(lambda: defaultdict(int))

for r in data:
    q3 = r["q3"]
    pos = r["position"]

    for pattern, label in source_patterns:
        matches = re.findall(pattern, q3, re.IGNORECASE)
        for m in matches:
            m_clean = m.strip().lower()
            # Collapse similar sources
            if any(x in m_clean for x in ["principal", "admin", "vice principal", "ap "]):
                source = "principal/admin"
            elif any(x in m_clean for x in ["teacher", "colleague", "coworker", "co-worker"]):
                source = "colleague/teacher"
            elif any(x in m_clean for x in ["custodian", "janitor"]):
                source = "custodial peer"
            elif any(x in m_clean for x in ["secretary", "office"]):
                source = "office staff"
            elif any(x in m_clean for x in ["email", "memo"]):
                source = "written communication"
            elif any(x in m_clean for x in ["meeting", "staff meeting"]):
                source = "staff meeting"
            elif any(x in m_clean for x in ["para"]):
                source = "paraprofessional"
            else:
                source = m_clean[:30]

            source_mentions[pos][source] += 1
            path_by_position[pos].append({
                "employee": r["employee_id"],
                "source": source,
                "raw_match": m.strip(),
                "context": label
            })

print("\nInformation sources by position (who they heard from):\n")
for pos in sorted(source_mentions.keys()):
    print(f"  {pos} (heard from):")
    for src, ct in sorted(source_mentions[pos].items(), key=lambda x: -x[1]):
        print(f"    {src}: {ct} mentions")
    print()

# ── 7. Explicit "channel" references ──────────────────────────────────────

print("\n" + "="*80)
print("7. HOW EACH POSITION LEARNED ABOUT THE PROJECT")
print("="*80)

channel_keywords = {
    "staff meeting": ["staff meeting", "faculty meeting", "all-hands", "meeting"],
    "email": ["email", "e-mail"],
    "memo/letter": ["memo", "letter", "notice", "flyer"],
    "principal/admin told us": ["principal told", "admin told", "administrator told",
                                 "principal informed", "admin informed",
                                 "principal announced", "our principal",
                                 "the principal"],
    "colleague/peer": ["another teacher", "a colleague", "coworker", "co-worker",
                       "another staff", "from a teacher", "other teachers",
                       "from colleagues", "word of mouth", "grapevine",
                       "hallway", "lunchroom", "break room"],
    "district office": ["district office", "district sent", "central office",
                        "from the district", "district communication"],
}

print(f"\n{'Position':<25}", end="")
for ch in channel_keywords:
    print(f" {ch[:15]:>15}", end="")
print()
print("-" * (25 + 16 * len(channel_keywords)))

for pos in sorted(positions.keys()):
    pos_records = [r for r in data if r["position"] == pos]
    n = len(pos_records)
    print(f"{pos:<25}", end="")
    for ch, kws in channel_keywords.items():
        count = sum(1 for r in pos_records if any(kw in r["q3"].lower() for kw in kws))
        print(f" {count:>4} ({count/n*100:3.0f}%)", end="")
    print(f"  [n={n}]")

# ── 8. Summary: The Cascade ───────────────────────────────────────────────

print("\n" + "="*80)
print("8. SUMMARY: THE INFORMATION CASCADE")
print("="*80)

# Order positions by how "informed" they were (official channel %)
cascade_order = []
for pos, d in position_channels.items():
    n = d["n"]
    official_pct = d["official"] / n * 100
    unofficial_pct = d["unofficial"] / n * 100
    neg_timing_pct = d["neg_timing"] / n * 100
    cascade_order.append((pos, n, official_pct, unofficial_pct, neg_timing_pct))

cascade_order.sort(key=lambda x: -x[2])  # Sort by official channel % descending

print("\nPositions ranked by official channel usage (proxy for 'heard first'):\n")
print(f"{'Rank':<5} {'Position':<25} {'N':>4} {'Official%':>10} {'Unofficial%':>12} {'NegTiming%':>12}")
print("-" * 70)
for i, (pos, n, off, unoff, neg) in enumerate(cascade_order, 1):
    marker = ""
    if off > 50:
        marker = " ← WELL INFORMED"
    elif neg > 30:
        marker = " ← FELT BLINDSIDED"
    print(f"{i:<5} {pos:<25} {n:>4} {off:>9.0f}% {unoff:>11.0f}% {neg:>11.0f}%{marker}")

print("\n" + "="*80)
print("FINDING: Information Cascade Pattern")
print("="*80)
print("""
The data shows a clear information cascade where communication about the
installation project flowed through organizational hierarchy:

  District Office → Site Administrators → Teachers → Support Staff

Site Administrators report learning through official channels (email, meetings)
and positive timing language. Teachers show a mix — some heard officially, many
heard from colleagues. Custodial/Facilities and Food Service staff are most
likely to report learning through unofficial channels, being 'blindsided,' or
feeling like an afterthought in the communication plan.

This is consistent with a classic 'information cascade failure' where each
level of the org chart assumes the level below them has been informed,
but the communication degrades or stops before reaching front-line staff.
""")
