#!/usr/bin/env python3
"""Investigate Riverside Elementary sentiment polarization."""

import json
import re
from collections import Counter
from statistics import mean, stdev

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

# --- 1. Filter to Riverside ---
riverside = [r for r in data if r["site"] == "Riverside Elementary"]
print(f"=== RIVERSIDE ELEMENTARY: n={len(riverside)} ===\n")

# --- 2. Keyword sentiment scoring ---
POS_WORDS = ["great","excellent","improved","better","smooth","helpful","good",
             "easy","appreciate","intuitive","clear","love","wonderful"]
NEG_WORDS = ["frustrated","terrible","poor","difficult","disruption","problem",
             "issue","confusing","rushed","broken","fail","worse","struggle",
             "complaint","disappointed","nightmare","awful"]

def sentiment_score(record):
    text = " ".join((record[f"q{i}"] or "") for i in range(1,6)).lower()
    pos = sum(len(re.findall(r'\b' + w + r'\w*\b', text)) for w in POS_WORDS)
    neg = sum(len(re.findall(r'\b' + w + r'\w*\b', text)) for w in NEG_WORDS)
    return pos - neg

for r in riverside:
    r["_sent"] = sentiment_score(r)

scores = [r["_sent"] for r in riverside]
print(f"Sentiment scores — mean: {mean(scores):.2f}, stdev: {stdev(scores):.2f}, "
      f"min: {min(scores)}, max: {max(scores)}")

# --- 3. Top quartile vs bottom quartile ---
sorted_rs = sorted(riverside, key=lambda r: r["_sent"])
q_size = len(riverside) // 4
bottom_q = sorted_rs[:q_size]
top_q = sorted_rs[-q_size:]

print(f"\nBottom quartile: n={len(bottom_q)}, score range [{bottom_q[0]['_sent']}, {bottom_q[-1]['_sent']}]")
print(f"Top quartile:    n={len(top_q)}, score range [{top_q[0]['_sent']}, {top_q[-1]['_sent']}]")

# --- 4. Demographic comparisons ---
def demo_breakdown(group, label):
    print(f"\n--- {label} (n={len(group)}) ---")
    for field in ["position", "years_at_district_band", "is_transfer",
                   "room_type", "building_wing", "gender", "race_ethnicity"]:
        counts = Counter(r[field] for r in group)
        total = len(group)
        dist = ", ".join(f"{k}: {v} ({v/total*100:.0f}%)" for k, v in counts.most_common())
        print(f"  {field}: {dist}")

demo_breakdown(bottom_q, "BOTTOM QUARTILE (most negative)")
demo_breakdown(top_q, "TOP QUARTILE (most positive)")

# Side-by-side comparison for key fields
print("\n=== KEY DEMOGRAPHIC COMPARISONS ===")
for field in ["position", "is_transfer", "years_at_district_band", "room_type", "building_wing"]:
    bc = Counter(r[field] for r in bottom_q)
    tc = Counter(r[field] for r in top_q)
    all_vals = sorted(set(list(bc.keys()) + list(tc.keys())), key=str)
    print(f"\n  {field}:")
    print(f"    {'Value':<30} {'Bottom%':>8} {'Top%':>8} {'Diff':>8}")
    for v in all_vals:
        bp = bc.get(v, 0) / len(bottom_q) * 100
        tp = tc.get(v, 0) / len(top_q) * 100
        print(f"    {str(v):<30} {bp:>7.1f}% {tp:>7.1f}% {tp-bp:>+7.1f}%")

# --- 5. Read extreme responses ---
print("\n\n=== MOST NEGATIVE RIVERSIDE RESPONDENTS (bottom 4) ===")
for r in sorted_rs[:4]:
    print(f"\n>> {r['employee_id']} | {r['name']} | {r['position']} | "
          f"tenure={r['years_at_district']}y | transfer={r['is_transfer']} | "
          f"wing={r['building_wing']} | room={r['room_type']} | "
          f"score={r['_sent']}")
    for qi in range(1, 6):
        print(f"   Q{qi}: {(r[f'q{qi}'] or 'N/A')[:200]}")

print("\n\n=== MOST POSITIVE RIVERSIDE RESPONDENTS (top 4) ===")
for r in sorted_rs[-4:]:
    print(f"\n>> {r['employee_id']} | {r['name']} | {r['position']} | "
          f"tenure={r['years_at_district']}y | transfer={r['is_transfer']} | "
          f"wing={r['building_wing']} | room={r['room_type']} | "
          f"score={r['_sent']}")
    for qi in range(1, 6):
        print(f"   Q{qi}: {(r[f'q{qi}'] or 'N/A')[:200]}")

# --- 6. Transfer vs non-transfer at Riverside ---
transfers = [r for r in riverside if r["is_transfer"]]
non_transfers = [r for r in riverside if not r["is_transfer"]]

print(f"\n\n=== TRANSFER vs NON-TRANSFER AT RIVERSIDE ===")
print(f"Transfers:     n={len(transfers)}, mean sentiment={mean([r['_sent'] for r in transfers]):.2f}, "
      f"stdev={stdev([r['_sent'] for r in transfers]):.2f}" if len(transfers) > 1 else f"Transfers: n={len(transfers)}")
print(f"Non-transfers: n={len(non_transfers)}, mean sentiment={mean([r['_sent'] for r in non_transfers]):.2f}, "
      f"stdev={stdev([r['_sent'] for r in non_transfers]):.2f}")

# Transfer origin system quality
print(f"\nTransfer origin_district_system_quality distribution:")
oq = Counter(r["origin_district_system_quality"] for r in transfers)
for k, v in oq.most_common():
    sub = [r for r in transfers if r["origin_district_system_quality"] == k]
    ms = mean([r["_sent"] for r in sub]) if sub else 0
    print(f"  {k}: n={v}, mean_sentiment={ms:.2f}")

# Transfer sentiment by whether origin was good/poor
print(f"\nTransfer sentiment breakdown by origin quality:")
for quality in sorted(set(r["origin_district_system_quality"] for r in transfers if r["origin_district_system_quality"])):
    sub = [r for r in transfers if r["origin_district_system_quality"] == quality]
    if len(sub) > 1:
        print(f"  origin='{quality}': n={len(sub)}, mean={mean([r['_sent'] for r in sub]):.2f}, stdev={stdev([r['_sent'] for r in sub]):.2f}")
    else:
        print(f"  origin='{quality}': n={len(sub)}, score={sub[0]['_sent']}")

# Bonus: within-wing analysis
print(f"\n=== SENTIMENT BY BUILDING WING (Riverside only) ===")
wings = Counter(r["building_wing"] for r in riverside)
for wing, cnt in wings.most_common():
    sub = [r for r in riverside if r["building_wing"] == wing]
    ms = mean([r["_sent"] for r in sub])
    sd = stdev([r["_sent"] for r in sub]) if len(sub) > 1 else 0
    print(f"  {str(wing):<15} n={cnt:>3}, mean={ms:>+6.2f}, stdev={sd:.2f}")

# Bonus: room_type analysis
print(f"\n=== SENTIMENT BY ROOM TYPE (Riverside only) ===")
rooms = Counter(r["room_type"] for r in riverside)
for room, cnt in rooms.most_common():
    sub = [r for r in riverside if r["room_type"] == room]
    ms = mean([r["_sent"] for r in sub])
    sd = stdev([r["_sent"] for r in sub]) if len(sub) > 1 else 0
    print(f"  {str(room):<20} n={cnt:>3}, mean={ms:>+6.2f}, stdev={sd:.2f}")
