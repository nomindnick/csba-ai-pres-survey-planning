#!/usr/bin/env python3
"""
Hypothesis: Long-tenured counselors/specialists stay positive because they
value emergency alert and safety features, unlike other long-tenured staff
who focus on disruption.
"""

import json
from collections import Counter

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

# Safety/emergency keywords
SAFETY_KEYWORDS = [
    "emergency", "alert", "safety", "lockdown", "lock-down", "lock down",
    "secure", "security", "drill", "crisis", "panic", "911", "evacuation",
    "evacuate", "intruder", "threat", "urgent", "sos", "alarm"
]

DISRUPTION_KEYWORDS = [
    "disrupt", "interrupt", "interfere", "thrown off", "frustrat",
    "difficult", "struggle", "confus", "overwhelm", "annoying",
    "worse", "broken", "fail", "problem"
]

WORKFLOW_KEYWORDS = [
    "workflow", "efficient", "streamline", "easier", "intuitive",
    "improved", "better", "faster", "convenient", "quick"
]

COMMUNICATION_QUALITY_KEYWORDS = [
    "sound quality", "clarity", "clear", "audio", "intercom",
    "announcement", "hear", "volume", "speaker"
]

def categorize_text(text):
    text_lower = text.lower()
    cats = []
    if any(k in text_lower for k in SAFETY_KEYWORDS):
        cats.append("safety/emergency")
    if any(k in text_lower for k in DISRUPTION_KEYWORDS):
        cats.append("disruption")
    if any(k in text_lower for k in WORKFLOW_KEYWORDS):
        cats.append("workflow")
    if any(k in text_lower for k in COMMUNICATION_QUALITY_KEYWORDS):
        cats.append("communication_quality")
    return cats if cats else ["other"]

def find_safety_keywords(text):
    text_lower = text.lower()
    return [k for k in SAFETY_KEYWORDS if k in text_lower]

# ============================================================
# 1. ALL counselor/specialist responses with 20+ years at district
# ============================================================
counselor_positions = ["Counselor", "Specialist", "School Counselor"]
long_tenure_counselors = [r for r in data
    if r["position"] in counselor_positions and r["years_at_district"] >= 20]

# Also check if "Counselor" appears as substring
if not long_tenure_counselors:
    long_tenure_counselors = [r for r in data
        if ("counselor" in r["position"].lower() or "specialist" in r["position"].lower())
        and r["years_at_district"] >= 20]

# Let's see all positions first
all_positions = Counter(r["position"] for r in data)
print("=== ALL POSITIONS IN DATASET ===")
for pos, count in all_positions.most_common():
    print(f"  {pos}: {count}")

# Check what positions the counselor/specialist category covers
support_positions = [r for r in data if r["position"] not in ["Teacher", "Administrator"]]
support_pos_counts = Counter(r["position"] for r in support_positions)
print(f"\n=== NON-TEACHER/NON-ADMIN POSITIONS ===")
for pos, count in support_pos_counts.most_common():
    print(f"  {pos}: {count}")

# Find long-tenured counselors/specialists (broad match)
long_tenure_specialists = [r for r in data
    if r["position"] in ["Counselor", "Specialist", "Counselor/Specialist",
                          "Support Staff", "Classified Staff"]
    and r["years_at_district"] >= 20]

print(f"\n=== LONG-TENURED (20+ yrs) BY POSITION ===")
for pos in all_positions:
    group = [r for r in data if r["position"] == pos and r["years_at_district"] >= 20]
    if group:
        avg_sent = sum(r["sentiment_normalized"] for r in group) / len(group)
        print(f"  {pos} (n={len(group)}): avg sentiment = {avg_sent:.3f}")

# Use the actual position name that matches counselor/specialist
# Let's try all non-teacher, non-admin
non_teacher_admin = [r for r in data
    if r["position"] not in ["Teacher", "Administrator"]]
print(f"\n=== NON-TEACHER/NON-ADMIN with 20+ years ===")
long_non_ta = [r for r in non_teacher_admin if r["years_at_district"] >= 20]
for r in long_non_ta:
    print(f"  {r['employee_id']} | {r['position']} | {r['site']} | "
          f"yrs={r['years_at_district']} | sent={r['sentiment_normalized']:.3f}")

# ============================================================
# 2-3. Read full q1, q4, q5 and categorize for the target group
# ============================================================
# Determine the right position label
# First, let's just look for the position that would be "Counselor" or "Specialist"
target_positions = set()
for r in data:
    pos = r["position"]
    if any(x in pos.lower() for x in ["counselor", "specialist", "support", "classified", "aide", "para"]):
        target_positions.add(pos)

print(f"\n=== Positions matching counselor/specialist/support keywords: {target_positions} ===")

# Now get the actual target group - use "Counselor/Specialist" or whatever exists
# Try exact matches first, then fall back
for candidate in ["Counselor/Specialist", "Counselor", "Specialist", "Support Staff"]:
    group = [r for r in data if r["position"] == candidate and r["years_at_district"] >= 20]
    if group:
        print(f"\nFound {len(group)} records for position='{candidate}' with 20+ years")
        target_positions = {candidate}
        break

# If we haven't found the right group yet, use all non-teacher/non-admin
if not target_positions:
    # Just use whatever non-teacher/non-admin positions exist
    target_positions = set(r["position"] for r in data) - {"Teacher", "Administrator"}

target_group = [r for r in data
    if r["position"] in target_positions and r["years_at_district"] >= 20]

print(f"\n{'='*70}")
print(f"TARGET GROUP: {target_positions} with 20+ years at district (n={len(target_group)})")
print(f"{'='*70}")

for r in sorted(target_group, key=lambda x: x["years_at_district"], reverse=True):
    combined_text = f"{r['q1']} {r['q4']} {r['q5']}"
    cats = categorize_text(combined_text)
    safety_words = find_safety_keywords(combined_text)

    print(f"\n--- {r['employee_id']} | {r['name']} | {r['position']} | {r['site']} ---")
    print(f"    Years at district: {r['years_at_district']} | Sentiment: {r['sentiment_normalized']:.3f} ({r['sentiment_category']})")
    print(f"    Categories found: {', '.join(cats)}")
    if safety_words:
        print(f"    Safety keywords: {', '.join(safety_words)}")
    print(f"    Q1: {r['q1']}")
    print(f"    Q4: {r['q4']}")
    print(f"    Q5: {r['q5']}")

# Category summary for target group
print(f"\n=== CATEGORY SUMMARY FOR TARGET GROUP ===")
all_cats = Counter()
for r in target_group:
    combined = f"{r['q1']} {r['q4']} {r['q5']}"
    for cat in categorize_text(combined):
        all_cats[cat] += 1
for cat, count in all_cats.most_common():
    print(f"  {cat}: {count}/{len(target_group)} ({100*count/len(target_group):.0f}%)")

# ============================================================
# 4. Compare to long-tenured Teachers (20+ years)
# ============================================================
long_teachers = [r for r in data
    if r["position"] == "Teacher" and r["years_at_district"] >= 20]

print(f"\n{'='*70}")
print(f"COMPARISON: Teachers with 20+ years at district (n={len(long_teachers)})")
print(f"{'='*70}")

avg_sent_teachers = sum(r["sentiment_normalized"] for r in long_teachers) / len(long_teachers) if long_teachers else 0
avg_sent_target = sum(r["sentiment_normalized"] for r in target_group) / len(target_group) if target_group else 0
print(f"Avg sentiment - Target group: {avg_sent_target:.3f}")
print(f"Avg sentiment - Long teachers: {avg_sent_teachers:.3f}")

# Category summary for long teachers
teacher_cats = Counter()
for r in long_teachers:
    combined = f"{r['q1']} {r['q4']} {r['q5']}"
    for cat in categorize_text(combined):
        teacher_cats[cat] += 1
print(f"\nTeacher category summary:")
for cat, count in teacher_cats.most_common():
    print(f"  {cat}: {count}/{len(long_teachers)} ({100*count/len(long_teachers):.0f}%)")

# Show 5 representative q4 responses from long-tenured teachers
# Pick a mix of sentiments
long_teachers_sorted = sorted(long_teachers, key=lambda x: x["sentiment_normalized"])
# Pick 5 spread across the range
indices = [0, len(long_teachers_sorted)//4, len(long_teachers_sorted)//2,
           3*len(long_teachers_sorted)//4, len(long_teachers_sorted)-1]
print(f"\n=== 5 REPRESENTATIVE Q4 RESPONSES FROM LONG-TENURED TEACHERS ===")
for i in indices:
    if i < len(long_teachers_sorted):
        r = long_teachers_sorted[i]
        print(f"\n  [{r['employee_id']}] {r['name']} | {r['site']} | "
              f"yrs={r['years_at_district']} | sent={r['sentiment_normalized']:.3f}")
        print(f"  Q4: {r['q4']}")

# ============================================================
# 5. Site-level breakdown for target group
# ============================================================
print(f"\n{'='*70}")
print(f"SITE BREAKDOWN FOR TARGET GROUP")
print(f"{'='*70}")
site_groups = {}
for r in target_group:
    site_groups.setdefault(r["site"], []).append(r)

for site, members in sorted(site_groups.items()):
    avg = sum(r["sentiment_normalized"] for r in members) / len(members)
    safety_count = sum(1 for r in members
        if "safety/emergency" in categorize_text(f"{r['q1']} {r['q4']} {r['q5']}"))
    names = [r["name"] for r in members]
    print(f"  {site} (n={len(members)}): avg_sent={avg:.3f}, "
          f"safety_mentions={safety_count}, staff={', '.join(names)}")

# ============================================================
# Bonus: Check ALL q1-q5 for safety mentions across entire dataset
# ============================================================
print(f"\n{'='*70}")
print(f"SAFETY/EMERGENCY MENTIONS ACROSS ENTIRE DATASET")
print(f"{'='*70}")
safety_by_position = {}
for r in data:
    all_text = " ".join([r[f"q{i}"] or "" for i in range(1, 6)])
    has_safety = any(k in all_text.lower() for k in SAFETY_KEYWORDS)
    pos = r["position"]
    safety_by_position.setdefault(pos, {"total": 0, "safety": 0})
    safety_by_position[pos]["total"] += 1
    if has_safety:
        safety_by_position[pos]["safety"] += 1

for pos, counts in sorted(safety_by_position.items()):
    pct = 100 * counts["safety"] / counts["total"] if counts["total"] else 0
    print(f"  {pos}: {counts['safety']}/{counts['total']} ({pct:.0f}%) mention safety/emergency")

# By tenure band
print(f"\nSafety mentions by tenure band (all positions):")
tenure_safety = {}
for r in data:
    all_text = " ".join([r[f"q{i}"] or "" for i in range(1, 6)])
    has_safety = any(k in all_text.lower() for k in SAFETY_KEYWORDS)
    band = r["years_at_district_band"]
    tenure_safety.setdefault(band, {"total": 0, "safety": 0})
    tenure_safety[band]["total"] += 1
    if has_safety:
        tenure_safety[band]["safety"] += 1

for band in ["0-3", "4-10", "11-20", "21-30", "31+"]:
    if band in tenure_safety:
        counts = tenure_safety[band]
        pct = 100 * counts["safety"] / counts["total"] if counts["total"] else 0
        print(f"  {band}: {counts['safety']}/{counts['total']} ({pct:.0f}%)")

# Safety mentions specifically among long-tenured non-teachers vs teachers
print(f"\nSafety mentions among 20+ year staff:")
for pos in set(r["position"] for r in data):
    group = [r for r in data if r["position"] == pos and r["years_at_district"] >= 20]
    if group:
        safety_count = sum(1 for r in group
            if any(k in " ".join([r[f"q{i}"] or "" for i in range(1, 6)]).lower() for k in SAFETY_KEYWORDS))
        print(f"  {pos} (n={len(group)}): {safety_count} mention safety ({100*safety_count/len(group):.0f}%)")
