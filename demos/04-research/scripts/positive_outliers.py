#!/usr/bin/env python3
"""
Positive Outlier Analysis
Find and analyze the most positive respondents within the most negative subgroups:
1. North Wing staff
2. Food Service 20+ years tenure
3. Counselors/Specialists
"""

import json
import re
from collections import Counter

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

# --- Simple sentiment scoring ---
# We'll use a keyword-based approach: count positive and negative signal words
# across all 5 questions, then compute a net sentiment score.

POSITIVE_WORDS = [
    'great', 'excellent', 'love', 'fantastic', 'wonderful', 'impressed',
    'smooth', 'smoother', 'easy', 'easier', 'intuitive', 'improved',
    'improvement', 'better', 'helpful', 'appreciate', 'appreciated',
    'pleased', 'positive', 'glad', 'happy', 'comfortable', 'confident',
    'seamless', 'well-organized', 'well organized', 'clear', 'effective',
    'efficient', 'enjoy', 'good experience', 'works well', 'no issues',
    'no problems', 'straightforward', 'user-friendly', 'user friendly',
    'welcome', 'upgrade', 'benefit', 'valuable', 'supportive', 'thorough',
    'responsive', 'proactive', 'thoughtful', 'adequate', 'reasonable',
    'solid', 'reliable', 'professional', 'organized', 'timely',
]

NEGATIVE_WORDS = [
    'frustrat', 'disrupt', 'confus', 'overwhelm', 'difficult', 'struggle',
    'poor', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'angry',
    'disappoint', 'inadequate', 'insufficient', 'fail', 'broken', 'glitch',
    'malfunction', 'unreliable', 'inconsistent', 'chaotic', 'stressful',
    'anxiety', 'anxious', 'concern', 'worried', 'fear', 'rushed',
    'blindsided', 'ignored', 'dismiss', 'disrespect', 'undermine',
    'neglect', 'lack', 'problem', 'issue', 'complaint', 'worse',
    'interrupt', 'intrusive', 'invasion', 'uncomfortable', 'unacceptable',
    'unprofessional', 'disorganized', 'poorly', 'mess', 'nightmare',
    'ridiculous', 'absurd', 'waste', 'pointless', 'unnecessary',
    'not consulted', 'no input', 'no say', 'cut out', 'left out',
]

def sentiment_score(record):
    """Return (positive_count, negative_count, net_score) across all q1-q5."""
    text = ' '.join([
        record.get('q1') or '',
        record.get('q2') or '',
        record.get('q3') or '',
        record.get('q4') or '',
        record.get('q5') or '',
    ]).lower()

    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    return pos, neg, pos - neg

def print_respondent(r, rank=None):
    """Print full details for a respondent."""
    pos, neg, net = sentiment_score(r)
    prefix = f"  [{rank}] " if rank else "  "
    print(f"{prefix}{r['employee_id']} — {r['name']}")
    print(f"      Site: {r['site']} | Position: {r['position']} | Age: {r['age']}")
    print(f"      Tenure: {r['years_at_district']}yr district ({r['years_at_district_band']}), "
          f"{r['years_in_profession']}yr profession ({r['years_in_profession_band']})")
    print(f"      Transfer: {r['is_transfer']} | Origin system quality: {r['origin_district_system_quality']}")
    print(f"      Wing: {r['building_wing']} | Room: {r['room_type']}")
    print(f"      Sentiment: +{pos} / -{neg} = net {net}")
    print()
    for q in ['q1', 'q2', 'q3', 'q4', 'q5']:
        print(f"      {q.upper()}: {r.get(q) or '(no response)'}")
        print()

def group_sentiment_summary(group, label):
    """Print summary stats for a group."""
    scores = [sentiment_score(r) for r in group]
    nets = [s[2] for s in scores]
    avg = sum(nets) / len(nets) if nets else 0
    print(f"  Group '{label}': n={len(group)}, avg net sentiment={avg:.2f}, "
          f"range=[{min(nets)}, {max(nets)}]")

# ============================================================
# 1. NORTH WING ANALYSIS
# ============================================================
print("=" * 80)
print("1. NORTH WING — POSITIVE OUTLIERS")
print("=" * 80)

north_wing = [r for r in data if r.get('building_wing') == 'North Wing']
print(f"\n  Total North Wing respondents: {len(north_wing)}")
group_sentiment_summary(north_wing, "North Wing")

# Sort by sentiment score descending
north_wing_scored = sorted(north_wing, key=lambda r: sentiment_score(r)[2], reverse=True)

# Show the distribution
print("\n  Sentiment distribution (net score):")
net_scores = [sentiment_score(r)[2] for r in north_wing]
for score in sorted(set(net_scores), reverse=True):
    count = net_scores.count(score)
    print(f"    Net {score:+d}: {count} respondents")

print("\n  --- TOP 5 MOST POSITIVE NORTH WING RESPONDENTS ---\n")
for i, r in enumerate(north_wing_scored[:5], 1):
    print_respondent(r, rank=i)
    print("  " + "-" * 70)

# Also show the most negative for comparison
print("\n  --- MOST NEGATIVE NORTH WING RESPONDENTS (bottom 3, for comparison) ---\n")
for i, r in enumerate(north_wing_scored[-3:], 1):
    print_respondent(r, rank=f"neg-{i}")
    print("  " + "-" * 70)

# ============================================================
# 2. FOOD SERVICE 20+ YEARS
# ============================================================
print("\n" + "=" * 80)
print("2. FOOD SERVICE WITH 20+ YEARS TENURE — POSITIVE OUTLIERS")
print("=" * 80)

food_service = [r for r in data if r.get('position') == 'Food Service']
food_service_20plus = [r for r in food_service
                       if r['years_in_profession'] >= 20 or r['years_at_district'] >= 20]
# Also try just years_in_profession >= 20
food_service_prof20 = [r for r in food_service if r['years_in_profession'] >= 20]

print(f"\n  Total Food Service: {len(food_service)}")
print(f"  Food Service with 20+ years in profession: {len(food_service_prof20)}")
print(f"  Food Service with 20+ years at district OR profession: {len(food_service_20plus)}")

# Let's look at ALL food service sorted by tenure
food_service_scored = sorted(food_service, key=lambda r: sentiment_score(r)[2], reverse=True)

print("\n  All Food Service respondents by sentiment:")
for r in food_service_scored:
    pos, neg, net = sentiment_score(r)
    print(f"    {r['employee_id']} {r['name']:25s} | district:{r['years_at_district']:2d}yr "
          f"profession:{r['years_in_profession']:2d}yr | net={net:+d}")

# Show long-tenured food service
long_tenure_fs = [r for r in food_service if r['years_at_district'] >= 20 or r['years_in_profession'] >= 20]
long_tenure_fs_scored = sorted(long_tenure_fs, key=lambda r: sentiment_score(r)[2], reverse=True)

print(f"\n  --- LONG-TENURED FOOD SERVICE (20+ yr district or profession): n={len(long_tenure_fs)} ---\n")
for i, r in enumerate(long_tenure_fs_scored, 1):
    print_respondent(r, rank=i)
    print("  " + "-" * 70)

# If no clearly positive ones, also show the LEAST negative
if long_tenure_fs:
    best_net = sentiment_score(long_tenure_fs_scored[0])[2]
    if best_net <= 0:
        print("  NOTE: No clearly positive long-tenured food service staff found.")
        print("  Showing ALL for context.\n")

# ============================================================
# 3. COUNSELORS/SPECIALISTS
# ============================================================
print("\n" + "=" * 80)
print("3. COUNSELORS/SPECIALISTS — POSITIVE OUTLIERS")
print("=" * 80)

counselors = [r for r in data if r.get('position') == 'Counselor/Specialist']
print(f"\n  Total Counselors/Specialists: {len(counselors)}")
group_sentiment_summary(counselors, "Counselor/Specialist")

counselors_scored = sorted(counselors, key=lambda r: sentiment_score(r)[2], reverse=True)

# Sentiment distribution
print("\n  Sentiment distribution (net score):")
c_nets = [sentiment_score(r)[2] for r in counselors]
for score in sorted(set(c_nets), reverse=True):
    count = c_nets.count(score)
    print(f"    Net {score:+d}: {count} respondents")

print("\n  --- TOP 5 MOST POSITIVE COUNSELORS/SPECIALISTS ---\n")
for i, r in enumerate(counselors_scored[:5], 1):
    print_respondent(r, rank=i)
    # Check for intercom/session mentions
    full_text = ' '.join([(r.get(f'q{i}') or '') for i in range(1, 6)]).lower()
    mentions_intercom = any(w in full_text for w in ['intercom', 'announcement', 'interrupt', 'session', 'counseling', 'meeting', 'privacy', 'confidential'])
    print(f"      >>> Mentions intercom/session/privacy issues: {mentions_intercom}")
    # Show which keywords matched
    matched = [w for w in ['intercom', 'announcement', 'interrupt', 'session', 'counseling', 'meeting', 'privacy', 'confidential', 'intrusive'] if w in full_text]
    print(f"      >>> Matched keywords: {matched}")
    print("  " + "-" * 70)

# Show the most negative counselors for comparison
print("\n  --- MOST NEGATIVE COUNSELORS (bottom 3, for comparison) ---\n")
for i, r in enumerate(counselors_scored[-3:], 1):
    print_respondent(r, rank=f"neg-{i}")
    full_text = ' '.join([(r.get(f'q{j}') or '') for j in range(1, 6)]).lower()
    matched = [w for w in ['intercom', 'announcement', 'interrupt', 'session', 'counseling', 'meeting', 'privacy', 'confidential', 'intrusive'] if w in full_text]
    print(f"      >>> Matched keywords: {matched}")
    print("  " + "-" * 70)

# ============================================================
# 4. CROSS-CUTTING ANALYSIS: WHAT DISTINGUISHES POSITIVE OUTLIERS?
# ============================================================
print("\n" + "=" * 80)
print("4. CROSS-CUTTING: WHAT DO POSITIVE OUTLIERS HAVE IN COMMON?")
print("=" * 80)

# Collect all positive outliers
pos_outliers = north_wing_scored[:5] + long_tenure_fs_scored[:3] + counselors_scored[:5]
# Remove duplicates by employee_id
seen = set()
unique_outliers = []
for r in pos_outliers:
    if r['employee_id'] not in seen:
        seen.add(r['employee_id'])
        unique_outliers.append(r)

print(f"\n  Total unique positive outliers collected: {len(unique_outliers)}")

# Transfer status
transfers = sum(1 for r in unique_outliers if r['is_transfer'])
print(f"\n  Transfer status: {transfers}/{len(unique_outliers)} are transfers")

# Origin district system quality
origin_quals = [r['origin_district_system_quality'] for r in unique_outliers if r['origin_district_system_quality']]
if origin_quals:
    print(f"  Origin system quality among transfers: {Counter(origin_quals)}")

# Age distribution
ages = [r['age'] for r in unique_outliers]
print(f"  Age range: {min(ages)}-{max(ages)}, mean={sum(ages)/len(ages):.1f}")

# Tenure
tenures = [r['years_at_district'] for r in unique_outliers]
print(f"  District tenure range: {min(tenures)}-{max(tenures)}, mean={sum(tenures)/len(tenures):.1f}")

# Room type
rooms = Counter(r['room_type'] for r in unique_outliers)
print(f"  Room types: {dict(rooms)}")

# Sites
sites = Counter(r['site'] for r in unique_outliers)
print(f"  Sites: {dict(sites)}")

# Look at language patterns - what do positive outliers talk about?
print("\n  --- LANGUAGE PATTERNS IN POSITIVE OUTLIERS ---")
all_pos_text = ' '.join([
    ' '.join([(r.get(f'q{i}') or '') for i in range(1, 6)])
    for r in unique_outliers
]).lower()

# Common themes in positive responses
themes = {
    'training_positive': ['training was helpful', 'training was good', 'training was great', 'well-trained', 'training.*thorough'],
    'communication_positive': ['well communicated', 'good communication', 'kept us informed', 'transparent', 'clear communication'],
    'adaptation': ['adapted', 'adjust', 'got used to', 'learning curve', 'figured out'],
    'comparison_to_old': ['better than', 'improvement over', 'upgrade from', 'old system'],
    'specific_features': ['sound quality', 'interface', 'intercom', 'announcement', 'scheduling'],
    'consulted': ['asked', 'input', 'consulted', 'involved', 'voice'],
}

for theme, keywords in themes.items():
    matches = sum(1 for kw in keywords if kw in all_pos_text)
    print(f"  {theme}: {matches}/{len(keywords)} keywords found")

print("\n\nDone.")
