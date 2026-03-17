#!/usr/bin/env python3
"""
Demographic Equity Analysis: Gender & Race/Ethnicity Patterns in Satisfaction
Hypothesis: There may be gender and/or race/ethnicity patterns in satisfaction
that indicate equity concerns in installation, training, or communication.
"""

import json
import re
from collections import defaultdict
from itertools import product

DATA_PATH = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA_PATH) as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# --- Sentiment scoring via keyword matching ---
POS_WORDS = {"improved", "better", "great", "smooth", "easy", "helpful", "clear",
             "excellent", "reliable", "intuitive", "appreciate", "pleased", "well",
             "good", "positive", "effective", "efficient", "comfortable"}
NEG_WORDS = {"frustrated", "disrupted", "poor", "problem", "issue", "difficult",
             "rushed", "confused", "worse", "terrible", "complaint", "glitch",
             "garbled", "blindsided", "overwhelming", "struggled", "broken",
             "bad", "annoying", "disappointing", "inadequate", "chaotic", "ignored"}

def score_text(text):
    """Return (pos_count, neg_count, net_score) for a text string."""
    if not text:
        return 0, 0, 0
    words = set(re.findall(r'[a-z]+', text.lower()))
    pos = len(words & POS_WORDS)
    neg = len(words & NEG_WORDS)
    return pos, neg, pos - neg

def score_record(rec, questions=None):
    """Score across specified questions (default: all q1-q5)."""
    if questions is None:
        questions = ["q1", "q2", "q3", "q4", "q5"]
    total_pos, total_neg = 0, 0
    for q in questions:
        p, n, _ = score_text(rec.get(q, ""))
        total_pos += p
        total_neg += n
    return total_pos, total_neg, total_pos - total_neg

# Score every record
for rec in data:
    p, n, net = score_record(rec)
    rec["_pos"] = p
    rec["_neg"] = n
    rec["_net"] = net
    # Also per-question scores
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        _, _, qnet = score_record(rec, [q])
        rec[f"_{q}_net"] = qnet

# --- Helper functions ---
def group_stats(records, score_key="_net"):
    """Return n, mean, stdev for a list of records on given score key."""
    vals = [r[score_key] for r in records]
    n = len(vals)
    if n == 0:
        return 0, 0.0, 0.0
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n if n > 1 else 0
    return n, mean, var ** 0.5

def print_group_table(grouped, score_key="_net", label="Group"):
    """Print a formatted table of group statistics."""
    rows = []
    for name, recs in sorted(grouped.items()):
        n, mean, sd = group_stats(recs, score_key)
        rows.append((name, n, mean, sd))

    # Header
    print(f"\n  {'':2}{label:<30} {'N':>5}  {'Mean':>7}  {'StdDev':>7}")
    print(f"  {'':2}{'-'*30} {'-----':>5}  {'-------':>7}  {'-------':>7}")
    for name, n, mean, sd in rows:
        flag = " ***" if n < 15 else (" **" if n < 30 else "")
        print(f"  {'':2}{str(name):<30} {n:>5}  {mean:>+7.2f}  {sd:>7.2f}{flag}")
    return rows

def group_by(records, field):
    grouped = defaultdict(list)
    for r in records:
        grouped[r[field]].append(r)
    return grouped

# ============================================================
# 1. OVERALL DEMOGRAPHIC DISTRIBUTIONS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: DEMOGRAPHIC DISTRIBUTIONS")
print("=" * 70)

for field in ["gender", "race_ethnicity"]:
    g = group_by(data, field)
    print(f"\n  {field}:")
    for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
        print(f"    {k}: {len(v)}")

# ============================================================
# 2. SENTIMENT BY GENDER
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: OVERALL SENTIMENT BY GENDER")
print("=" * 70)

by_gender = group_by(data, "gender")
print_group_table(by_gender, label="Gender")

# ============================================================
# 3. SENTIMENT BY RACE/ETHNICITY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: OVERALL SENTIMENT BY RACE/ETHNICITY")
print("=" * 70)

by_race = group_by(data, "race_ethnicity")
print_group_table(by_race, label="Race/Ethnicity")

# ============================================================
# 4. Q2 (TRAINING) AND Q3 (COMMUNICATION) BY DEMOGRAPHICS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: TRAINING (Q2) AND COMMUNICATION (Q3) BY DEMOGRAPHICS")
print("=" * 70)

for q, qlabel in [("_q2_net", "Q2 — Training"), ("_q3_net", "Q3 — Communication")]:
    print(f"\n--- {qlabel} by Gender ---")
    print_group_table(by_gender, score_key=q, label="Gender")
    print(f"\n--- {qlabel} by Race/Ethnicity ---")
    print_group_table(by_race, score_key=q, label="Race/Ethnicity")

# ============================================================
# 5. INTERACTIONS: GENDER × SITE
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: INTERACTIONS — GENDER × SITE")
print("=" * 70)

by_site = group_by(data, "site")
for site_name in sorted(by_site.keys()):
    site_recs = by_site[site_name]
    site_gender = group_by(site_recs, "gender")
    print(f"\n  --- {site_name} ---")
    print_group_table(site_gender, label="Gender")

# ============================================================
# 6. INTERACTIONS: RACE × SITE
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: INTERACTIONS — RACE/ETHNICITY × SITE")
print("=" * 70)

for site_name in sorted(by_site.keys()):
    site_recs = by_site[site_name]
    site_race = group_by(site_recs, "race_ethnicity")
    print(f"\n  --- {site_name} ---")
    print_group_table(site_race, label="Race/Ethnicity")

# ============================================================
# 7. INTERACTIONS: RACE × POSITION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: INTERACTIONS — RACE/ETHNICITY × POSITION")
print("=" * 70)

by_position = group_by(data, "position")
for pos_name in sorted(by_position.keys()):
    pos_recs = by_position[pos_name]
    pos_race = group_by(pos_recs, "race_ethnicity")
    print(f"\n  --- {pos_name} ---")
    print_group_table(pos_race, label="Race/Ethnicity")

# ============================================================
# 8. CONTROLLING FOR POSITION: IS RACE EFFECT REALLY POSITION?
# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: RACE DIFFERENCES WITHIN EACH POSITION (CONTROLLING FOR POSITION)")
print("=" * 70)

# For each position, compute race group means. Then compute a position-adjusted
# overall mean for each race group (weighted average of within-position means).
race_groups = sorted(by_race.keys())
position_groups = sorted(by_position.keys())

print("\n  Position-adjusted sentiment by race/ethnicity:")
print("  (Weighted average of within-position means, weighting by race group size in each position)\n")

# Collect within-position means
race_adjusted = defaultdict(list)  # race -> list of (weight, mean)
for pos in position_groups:
    pos_recs = by_position[pos]
    pos_race = group_by(pos_recs, "race_ethnicity")
    for race in race_groups:
        recs = pos_race.get(race, [])
        if len(recs) >= 3:  # only include cells with enough data
            n, mean, _ = group_stats(recs)
            race_adjusted[race].append((n, mean))

print(f"  {'Race/Ethnicity':<30} {'Raw Mean':>9}  {'Adj Mean':>9}  {'N (raw)':>7}")
print(f"  {'-'*30} {'-'*9}  {'-'*9}  {'-'*7}")
for race in race_groups:
    n_raw, raw_mean, _ = group_stats(by_race[race])
    pairs = race_adjusted[race]
    if pairs:
        total_w = sum(w for w, _ in pairs)
        adj_mean = sum(w * m for w, m in pairs) / total_w if total_w else 0
        print(f"  {race:<30} {raw_mean:>+9.2f}  {adj_mean:>+9.2f}  {n_raw:>7}")
    else:
        print(f"  {race:<30} {raw_mean:>+9.2f}  {'N/A':>9}  {n_raw:>7}")

# ============================================================
# 9. FIND STANDOUT GROUPS & PULL REPRESENTATIVE QUOTES
# ============================================================
print("\n" + "=" * 70)
print("SECTION 9: STANDOUT GROUPS & REPRESENTATIVE QUOTES")
print("=" * 70)

# Identify groups with notably high or low sentiment
overall_n, overall_mean, overall_sd = group_stats(data)
print(f"\n  Overall: N={overall_n}, Mean={overall_mean:+.2f}, SD={overall_sd:.2f}")

# Check each demographic group
standouts = []
for field, grouped in [("gender", by_gender), ("race_ethnicity", by_race)]:
    for name, recs in grouped.items():
        n, mean, sd = group_stats(recs)
        if n >= 5:  # minimum threshold
            diff = mean - overall_mean
            if abs(diff) > 0.3:  # meaningful deviation
                standouts.append((field, name, n, mean, diff, recs))

# Also check cross-tabulations
for site_name, site_recs in by_site.items():
    for field in ["gender", "race_ethnicity"]:
        subgroups = group_by(site_recs, field)
        for name, recs in subgroups.items():
            n, mean, sd = group_stats(recs)
            if n >= 5 and abs(mean - overall_mean) > 0.5:
                standouts.append((f"{field} at {site_name}", name, n, mean, mean - overall_mean, recs))

# Sort by absolute deviation
standouts.sort(key=lambda x: abs(x[4]), reverse=True)

# Print top standouts with quotes
seen = set()
for field, name, n, mean, diff, recs in standouts[:12]:
    key = f"{field}:{name}"
    if key in seen:
        continue
    seen.add(key)

    direction = "MORE POSITIVE" if diff > 0 else "MORE NEGATIVE"
    print(f"\n  >>> {name} ({field}): N={n}, Mean={mean:+.2f} ({direction} than overall by {abs(diff):.2f})")

    # Sort by net score to get most extreme
    sorted_recs = sorted(recs, key=lambda r: r["_net"])

    # Pull quotes from the extreme end matching the direction
    if diff < 0:
        # Most negative quotes
        quote_recs = sorted_recs[:3]
        print(f"      Most negative responses:")
    else:
        # Most positive quotes
        quote_recs = sorted_recs[-3:]
        print(f"      Most positive responses:")

    for qr in quote_recs:
        # Pick the question with the most extreme score
        q_scores = [(q, qr[f"_{q}_net"]) for q in ["q1", "q2", "q3", "q4", "q5"]]
        if diff < 0:
            best_q, _ = min(q_scores, key=lambda x: x[1])
        else:
            best_q, _ = max(q_scores, key=lambda x: x[1])
        quote = qr[best_q]
        if len(quote) > 200:
            quote = quote[:200] + "..."
        print(f"      - [{qr['employee_id']}, {qr['position']}, {qr['site']}] ({best_q}): \"{quote}\"")

# ============================================================
# 10. Q2/Q3 DEMOGRAPHIC STANDOUTS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 10: TRAINING (Q2) & COMMUNICATION (Q3) DEMOGRAPHIC STANDOUTS")
print("=" * 70)

for q, qlabel in [("_q2_net", "Q2-Training"), ("_q3_net", "Q3-Communication")]:
    overall_q_n, overall_q_mean, _ = group_stats(data, q)
    print(f"\n  --- {qlabel}: Overall Mean = {overall_q_mean:+.3f} ---")

    for field, grouped in [("gender", by_gender), ("race_ethnicity", by_race)]:
        for name, recs in sorted(grouped.items()):
            n, mean, sd = group_stats(recs, q)
            diff = mean - overall_q_mean
            flag = " <<<" if abs(diff) > 0.05 and n >= 10 else ""
            print(f"    {name:<30} N={n:>4}, Mean={mean:>+.3f}, Diff={diff:>+.3f}{flag}")

            if abs(diff) > 0.05 and n >= 10:
                # Pull a quote
                sorted_recs = sorted(recs, key=lambda r: r[q])
                if diff < 0:
                    qr = sorted_recs[0]
                else:
                    qr = sorted_recs[-1]
                q_field = q.replace("_net", "").replace("_", "")
                quote = qr.get(q_field, "")
                if len(quote) > 200:
                    quote = quote[:200] + "..."
                print(f"      Example [{qr['employee_id']}]: \"{quote}\"")

# ============================================================
# 11. GENDER × RACE INTERACTION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 11: GENDER × RACE/ETHNICITY INTERACTION")
print("=" * 70)

for gender in sorted(by_gender.keys()):
    g_recs = by_gender[gender]
    g_race = group_by(g_recs, "race_ethnicity")
    print(f"\n  --- {gender} ---")
    print_group_table(g_race, label="Race/Ethnicity")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
