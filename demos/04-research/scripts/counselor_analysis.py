#!/usr/bin/env python3
"""Deep-dive analysis of Counselor/Specialist negativity in survey data."""

import json
from collections import Counter, defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

POSITIVE = {"great", "excellent", "improved", "better", "smooth", "helpful",
            "good", "easy", "appreciate", "intuitive", "clear"}
NEGATIVE = {"frustrated", "terrible", "poor", "difficult", "disruption",
            "problem", "issue", "confusing", "rushed", "broken", "fail",
            "worse", "struggle", "complaint", "disappointed"}

QUESTIONS = ["q1", "q2", "q3", "q4", "q5"]


def score_text(text):
    """Return (pos_count, neg_count, net_score) for a text."""
    if not text:
        return 0, 0, 0
    words = text.lower().split()
    # Also catch word variants by checking if any keyword is a substring of each word
    pos = sum(1 for w in words for kw in POSITIVE if kw in w)
    neg = sum(1 for w in words for kw in NEGATIVE if kw in w)
    return pos, neg, pos - neg


def score_record(rec, questions=None):
    """Score all questions (or a subset) for a record."""
    qs = questions or QUESTIONS
    total_pos, total_neg = 0, 0
    for q in qs:
        p, n, _ = score_text(rec[q])
        total_pos += p
        total_neg += n
    return total_pos, total_neg, total_pos - total_neg


# ── 1. Overall position comparison ──────────────────────────────────────
print("=" * 70)
print("1. OVERALL SENTIMENT BY POSITION")
print("=" * 70)

position_stats = defaultdict(lambda: {"n": 0, "pos": 0, "neg": 0, "net": 0})
for rec in data:
    pos, neg, net = score_record(rec)
    p = rec["position"]
    position_stats[p]["n"] += 1
    position_stats[p]["pos"] += pos
    position_stats[p]["neg"] += neg
    position_stats[p]["net"] += net

for pos_name in sorted(position_stats, key=lambda x: position_stats[x]["net"] / position_stats[x]["n"]):
    s = position_stats[pos_name]
    avg_net = s["net"] / s["n"]
    avg_pos = s["pos"] / s["n"]
    avg_neg = s["neg"] / s["n"]
    print(f"  {pos_name:30s}  n={s['n']:3d}  avg_pos={avg_pos:.2f}  avg_neg={avg_neg:.2f}  avg_net={avg_net:+.2f}")

# ── 2. Counselor/Specialist breakdown by site ────────────────────────────
counselors = [r for r in data if r["position"] == "Counselor/Specialist"]
others = [r for r in data if r["position"] != "Counselor/Specialist"]

print(f"\n{'=' * 70}")
print(f"2. COUNSELOR/SPECIALIST BY SITE (n={len(counselors)})")
print("=" * 70)

site_stats = defaultdict(lambda: {"n": 0, "nets": []})
for rec in counselors:
    _, _, net = score_record(rec)
    site_stats[rec["site"]]["n"] += 1
    site_stats[rec["site"]]["nets"].append(net)

for site in sorted(site_stats, key=lambda x: sum(site_stats[x]["nets"]) / len(site_stats[x]["nets"])):
    s = site_stats[site]
    avg = sum(s["nets"]) / len(s["nets"])
    print(f"  {site:35s}  n={s['n']:2d}  avg_net={avg:+.2f}")

# ── 3. Counselor/Specialist breakdown by tenure band ─────────────────────
print(f"\n{'=' * 70}")
print("3. COUNSELOR/SPECIALIST BY TENURE BAND (years_at_district_band)")
print("=" * 70)

tenure_stats = defaultdict(lambda: {"n": 0, "nets": []})
for rec in counselors:
    _, _, net = score_record(rec)
    tenure_stats[rec["years_at_district_band"]]["n"] += 1
    tenure_stats[rec["years_at_district_band"]]["nets"].append(net)

band_order = ["0-3", "4-10", "11-20", "21+"]
for band in band_order:
    if band in tenure_stats:
        s = tenure_stats[band]
        avg = sum(s["nets"]) / len(s["nets"])
        print(f"  {band:10s}  n={s['n']:2d}  avg_net={avg:+.2f}")

# ── 4. Counselor/Specialist breakdown by is_transfer ─────────────────────
print(f"\n{'=' * 70}")
print("4. COUNSELOR/SPECIALIST BY TRANSFER STATUS")
print("=" * 70)

transfer_stats = defaultdict(lambda: {"n": 0, "nets": []})
for rec in counselors:
    _, _, net = score_record(rec)
    transfer_stats[rec["is_transfer"]]["n"] += 1
    transfer_stats[rec["is_transfer"]]["nets"].append(net)

for tf in [False, True]:
    s = transfer_stats[tf]
    avg = sum(s["nets"]) / len(s["nets"])
    label = "Transfer" if tf else "Non-transfer"
    print(f"  {label:15s}  n={s['n']:2d}  avg_net={avg:+.2f}")

# ── 5. Q2 (training) and Q3 (communication) — counselors vs. others ─────
print(f"\n{'=' * 70}")
print("5. Q2 (TRAINING) AND Q3 (COMMUNICATION): COUNSELORS vs. OTHERS")
print("=" * 70)

for q in ["q2", "q3"]:
    c_scores = [score_text(r[q]) for r in counselors]
    o_scores = [score_text(r[q]) for r in others]
    c_avg = sum(s[2] for s in c_scores) / len(c_scores)
    o_avg = sum(s[2] for s in o_scores) / len(o_scores)
    c_neg_rate = sum(1 for s in c_scores if s[2] < 0) / len(c_scores)
    o_neg_rate = sum(1 for s in o_scores if s[2] < 0) / len(o_scores)
    qlabel = "Training" if q == "q2" else "Communication"
    print(f"\n  {q.upper()} ({qlabel}):")
    print(f"    Counselors (n={len(c_scores)}):  avg_net={c_avg:+.2f}  pct_negative={c_neg_rate:.1%}")
    print(f"    Others    (n={len(o_scores)}):  avg_net={o_avg:+.2f}  pct_negative={o_neg_rate:.1%}")

# Also compare per-question across all 5 questions
print(f"\n  Full per-question comparison:")
for q in QUESTIONS:
    c_avg = sum(score_text(r[q])[2] for r in counselors) / len(counselors)
    o_avg = sum(score_text(r[q])[2] for r in others) / len(others)
    gap = c_avg - o_avg
    print(f"    {q}: Counselors={c_avg:+.2f}  Others={o_avg:+.2f}  Gap={gap:+.2f}")

# ── 6. Most negative counselor responses ─────────────────────────────────
print(f"\n{'=' * 70}")
print("6. MOST NEGATIVE COUNSELOR RESPONSES (5-6 records)")
print("=" * 70)

scored_counselors = []
for rec in counselors:
    _, _, net = score_record(rec)
    scored_counselors.append((net, rec))

scored_counselors.sort(key=lambda x: x[0])

for i, (net, rec) in enumerate(scored_counselors[:6]):
    print(f"\n--- #{i+1}: {rec['name']} | {rec['site']} | age={rec['age']} | "
          f"tenure={rec['years_at_district']}yr | transfer={rec['is_transfer']} | "
          f"net_score={net} ---")
    for q in QUESTIONS:
        p, n, s = score_text(rec[q])
        print(f"  {q}: [pos={p} neg={n} net={s}] {rec[q][:200]}")
        if len(rec[q]) > 200:
            print(f"       ...{rec[q][200:]}")

# ── 7. Most positive counselor responses ─────────────────────────────────
print(f"\n{'=' * 70}")
print("7. MOST POSITIVE COUNSELOR RESPONSES (3 records)")
print("=" * 70)

for i, (net, rec) in enumerate(scored_counselors[-3:]):
    print(f"\n--- #{i+1}: {rec['name']} | {rec['site']} | age={rec['age']} | "
          f"tenure={rec['years_at_district']}yr | transfer={rec['is_transfer']} | "
          f"net_score={net} ---")
    for q in QUESTIONS:
        p, n, s = score_text(rec[q])
        print(f"  {q}: [pos={p} neg={n} net={s}] {rec[q][:200]}")
        if len(rec[q]) > 200:
            print(f"       ...{rec[q][200:]}")

# ── 8. Additional breakdowns: origin_district_system_quality, room_type ──
print(f"\n{'=' * 70}")
print("8. COUNSELOR EXTRA FIELDS: origin_district_system_quality, room_type, building_wing")
print("=" * 70)

for field in ["origin_district_system_quality", "room_type", "building_wing"]:
    print(f"\n  {field}:")
    field_stats = defaultdict(lambda: {"n": 0, "nets": []})
    for rec in counselors:
        _, _, net = score_record(rec)
        val = rec.get(field)
        field_stats[val]["n"] += 1
        field_stats[val]["nets"].append(net)
    for val in sorted(field_stats, key=lambda x: str(x)):
        s = field_stats[val]
        avg = sum(s["nets"]) / len(s["nets"])
        print(f"    {str(val):20s}  n={s['n']:2d}  avg_net={avg:+.2f}")

# ── 9. Keyword frequency in counselor negative responses ─────────────────
print(f"\n{'=' * 70}")
print("9. COMMON NEGATIVE KEYWORDS IN COUNSELOR RESPONSES")
print("=" * 70)

neg_keyword_counts = Counter()
for rec in counselors:
    for q in QUESTIONS:
        if not rec[q]:
            continue
        words = rec[q].lower().split()
        for w in words:
            for kw in NEGATIVE:
                if kw in w:
                    neg_keyword_counts[kw] += 1

for kw, count in neg_keyword_counts.most_common(15):
    print(f"  {kw:20s}  {count}")

# Same for others for comparison
print("\n  (Comparison: others, normalized per-person)")
neg_keyword_others = Counter()
for rec in others:
    for q in QUESTIONS:
        if not rec[q]:
            continue
        words = rec[q].lower().split()
        for w in words:
            for kw in NEGATIVE:
                if kw in w:
                    neg_keyword_others[kw] += 1

for kw in [k for k, _ in neg_keyword_counts.most_common(15)]:
    c_rate = neg_keyword_counts[kw] / len(counselors)
    o_rate = neg_keyword_others[kw] / len(others)
    ratio = c_rate / o_rate if o_rate > 0 else float('inf')
    print(f"  {kw:20s}  counselors={c_rate:.2f}/person  others={o_rate:.2f}/person  ratio={ratio:.2f}x")
