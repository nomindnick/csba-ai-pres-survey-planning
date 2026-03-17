#!/usr/bin/env python3
"""Per-question keyword sentiment analysis across demographic subgroups."""

import json
import re
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

POSITIVE = ["great", "excellent", "improved", "better", "smooth", "helpful",
            "good", "easy", "appreciate", "intuitive", "clear", "love",
            "wonderful"]
NEGATIVE = ["frustrated", "terrible", "poor", "difficult", "disruption",
            "problem", "issue", "confusing", "rushed", "broken", "fail",
            "worse", "struggle", "complaint", "disappointed", "nightmare",
            "awful"]

QUESTIONS = ["q1", "q2", "q3", "q4", "q5"]
Q_LABELS = {
    "q1": "Overall Experience",
    "q2": "Training",
    "q3": "Communication",
    "q4": "System Functionality",
    "q5": "What to Change",
}

def score(text):
    """Return (positive_count, negative_count, net) for a text string."""
    if not text:
        return (0, 0, 0)
    words = re.findall(r"[a-z]+", text.lower())
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    return (pos, neg, pos - neg)

with open(DATA) as f:
    data = json.load(f)

print(f"Total records: {len(data)}\n")

# ─── 1. Overall average sentiment per question ────────────────────────
print("=" * 80)
print("1. AVERAGE SENTIMENT PER QUESTION (all 500 respondents)")
print("=" * 80)
print(f"{'Question':<25} {'Avg Pos':>8} {'Avg Neg':>8} {'Avg Net':>8} {'% with any neg kw':>18}")
print("-" * 70)
for q in QUESTIONS:
    scores = [score(r[q]) for r in data]
    avg_pos = sum(s[0] for s in scores) / len(scores)
    avg_neg = sum(s[1] for s in scores) / len(scores)
    avg_net = sum(s[2] for s in scores) / len(scores)
    pct_neg = sum(1 for s in scores if s[1] > 0) / len(scores) * 100
    print(f"{Q_LABELS[q]:<25} {avg_pos:>8.2f} {avg_neg:>8.2f} {avg_net:>8.2f} {pct_neg:>17.1f}%")

# ─── Helper: group-level table ────────────────────────────────────────
def print_group_table(title, group_field, questions=QUESTIONS):
    """Print a per-question sentiment table grouped by group_field."""
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    # Gather groups
    groups = sorted(set(r[group_field] for r in data))

    for q in questions:
        print(f"\n  {Q_LABELS[q]} ({q})")
        print(f"  {'Group':<35} {'N':>5} {'Avg Pos':>8} {'Avg Neg':>8} {'Net':>8}")
        print(f"  {'-'*66}")
        group_nets = {}
        for g in groups:
            subset = [r for r in data if r[group_field] == g]
            scores_list = [score(r[q]) for r in subset]
            n = len(scores_list)
            if n == 0:
                continue
            avg_pos = sum(s[0] for s in scores_list) / n
            avg_neg = sum(s[1] for s in scores_list) / n
            avg_net = sum(s[2] for s in scores_list) / n
            group_nets[g] = avg_net
            print(f"  {str(g):<35} {n:>5} {avg_pos:>8.2f} {avg_neg:>8.2f} {avg_net:>+8.2f}")
        # Range
        if group_nets:
            vals = list(group_nets.values())
            spread = max(vals) - min(vals)
            best = max(group_nets, key=group_nets.get)
            worst = min(group_nets, key=group_nets.get)
            print(f"  --> Spread: {spread:.2f}  (most positive: {best}, most negative: {worst})")

    return groups

# ─── 2. Per-question sentiment by site ────────────────────────────────
print_group_table("2. PER-QUESTION SENTIMENT BY SITE", "site")

# ─── 3. Per-question sentiment by position ────────────────────────────
print_group_table("3. PER-QUESTION SENTIMENT BY POSITION", "position")

# ─── 4. Per-question sentiment by tenure band ────────────────────────
print_group_table("4. PER-QUESTION SENTIMENT BY TENURE BAND (years_at_district_band)", "years_at_district_band")

# ─── 5. Which question shows MOST variation by subgroup? ──────────────
print()
print("=" * 80)
print("5. VARIATION ANALYSIS — Which question has highest spread across subgroups?")
print("=" * 80)

def compute_spread(group_field, q):
    groups = set(r[group_field] for r in data)
    nets = []
    for g in groups:
        subset = [r for r in data if r[group_field] == g]
        scores_list = [score(r[q]) for r in subset]
        n = len(scores_list)
        if n < 5:
            continue
        avg_net = sum(s[2] for s in scores_list) / n
        nets.append(avg_net)
    if len(nets) < 2:
        return 0
    return max(nets) - min(nets)

print(f"\n{'Question':<25} {'By Site':>10} {'By Position':>12} {'By Tenure':>12} {'Max Spread':>12}")
print("-" * 72)
max_spread_q = None
max_spread_val = 0
for q in QUESTIONS:
    s_site = compute_spread("site", q)
    s_pos = compute_spread("position", q)
    s_ten = compute_spread("years_at_district_band", q)
    mx = max(s_site, s_pos, s_ten)
    if mx > max_spread_val:
        max_spread_val = mx
        max_spread_q = q
    print(f"{Q_LABELS[q]:<25} {s_site:>10.2f} {s_pos:>12.2f} {s_ten:>12.2f} {mx:>12.2f}")

print(f"\n--> MOST VARIABLE QUESTION: {Q_LABELS[max_spread_q]} ({max_spread_q}) with max spread {max_spread_val:.2f}")

# ─── 6. Cross-question pattern divergence ─────────────────────────────
print()
print("=" * 80)
print("6. DIVERGENT PATTERN DETECTION — Questions that break the overall trend")
print("=" * 80)
print("\nFor each subgroup, which question deviates most from that group's average?")

def analyze_divergence(group_field, label):
    print(f"\n  By {label}:")
    print(f"  {'Group':<30} {'Avg Net':>8} {'Outlier Q':>12} {'Q Net':>8} {'Delta':>8}")
    print(f"  {'-'*68}")
    groups = sorted(set(r[group_field] for r in data))
    for g in groups:
        subset = [r for r in data if r[group_field] == g]
        if len(subset) < 5:
            continue
        q_nets = {}
        for q in QUESTIONS:
            scores_list = [score(r[q]) for r in subset]
            q_nets[q] = sum(s[2] for s in scores_list) / len(scores_list)
        overall = sum(q_nets.values()) / len(q_nets)
        # find biggest deviation
        worst_q = max(QUESTIONS, key=lambda q: abs(q_nets[q] - overall))
        delta = q_nets[worst_q] - overall
        print(f"  {str(g):<30} {overall:>+8.2f} {Q_LABELS[worst_q]:>12} {q_nets[worst_q]:>+8.2f} {delta:>+8.2f}")

analyze_divergence("site", "Site")
analyze_divergence("position", "Position")
analyze_divergence("years_at_district_band", "Tenure Band")

# ─── 7. Heatmap-style summary: net sentiment by site x question ──────
print()
print("=" * 80)
print("7. HEATMAP: Net sentiment by SITE x QUESTION")
print("=" * 80)
sites = sorted(set(r["site"] for r in data))
print(f"\n{'Site':<30}", end="")
for q in QUESTIONS:
    print(f" {q:>8}", end="")
print(f" {'Mean':>8}")
print("-" * (30 + 9 * 6))
for site in sites:
    subset = [r for r in data if r["site"] == site]
    print(f"{site:<30}", end="")
    row_vals = []
    for q in QUESTIONS:
        scores_list = [score(r[q]) for r in subset]
        net = sum(s[2] for s in scores_list) / len(scores_list)
        row_vals.append(net)
        print(f" {net:>+8.2f}", end="")
    print(f" {sum(row_vals)/len(row_vals):>+8.2f}")

# ─── 8. Heatmap: net sentiment by POSITION x QUESTION ────────────────
print()
print("=" * 80)
print("8. HEATMAP: Net sentiment by POSITION x QUESTION")
print("=" * 80)
positions = sorted(set(r["position"] for r in data))
print(f"\n{'Position':<30}", end="")
for q in QUESTIONS:
    print(f" {q:>8}", end="")
print(f" {'Mean':>8}")
print("-" * (30 + 9 * 6))
for pos in positions:
    subset = [r for r in data if r["position"] == pos]
    print(f"{pos:<30}", end="")
    row_vals = []
    for q in QUESTIONS:
        scores_list = [score(r[q]) for r in subset]
        net = sum(s[2] for s in scores_list) / len(scores_list)
        row_vals.append(net)
        print(f" {net:>+8.2f}", end="")
    print(f" {sum(row_vals)/len(row_vals):>+8.2f}")

# ─── 9. Heatmap: net sentiment by TENURE x QUESTION ──────────────────
print()
print("=" * 80)
print("9. HEATMAP: Net sentiment by TENURE BAND x QUESTION")
print("=" * 80)
tenure_order = ["0-3", "4-10", "11-20", "20+"]
tenures = [t for t in tenure_order if t in set(r["years_at_district_band"] for r in data)]
print(f"\n{'Tenure Band':<30}", end="")
for q in QUESTIONS:
    print(f" {q:>8}", end="")
print(f" {'Mean':>8}")
print("-" * (30 + 9 * 6))
for ten in tenures:
    subset = [r for r in data if r["years_at_district_band"] == ten]
    print(f"{ten:<30}", end="")
    row_vals = []
    for q in QUESTIONS:
        scores_list = [score(r[q]) for r in subset]
        net = sum(s[2] for s in scores_list) / len(scores_list)
        row_vals.append(net)
        print(f" {net:>+8.2f}", end="")
    print(f" {sum(row_vals)/len(row_vals):>+8.2f}")

print("\n\nDone.")
