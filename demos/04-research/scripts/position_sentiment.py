"""Hypothesis: Sentiment varies significantly by position type."""
import json
import statistics
from collections import defaultdict

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

# ── 1. Mean sentiment, category distribution, and N per position ──────────

positions = defaultdict(list)
for r in data:
    positions[r["position"]].append(r)

print("=" * 80)
print("POSITION-LEVEL SENTIMENT SUMMARY")
print("=" * 80)

summaries = {}
for pos in sorted(positions, key=lambda p: statistics.mean(r["sentiment_normalized"] for r in positions[p])):
    records = positions[pos]
    scores = [r["sentiment_normalized"] for r in records]
    cats = defaultdict(int)
    for r in records:
        cats[r["sentiment_category"]] += 1
    mean_s = statistics.mean(scores)
    median_s = statistics.median(scores)
    sd_s = statistics.stdev(scores) if len(scores) > 1 else 0
    summaries[pos] = {"mean": mean_s, "median": median_s, "sd": sd_s, "n": len(scores), "cats": dict(cats)}
    cat_str = "  ".join(f"{c}: {cats[c]} ({cats[c]/len(scores)*100:.0f}%)" for c in ["positive", "neutral", "negative"])
    print(f"\n{pos}  (n={len(scores)})")
    print(f"  Mean sentiment_normalized: {mean_s:+.3f}   Median: {median_s:+.3f}   SD: {sd_s:.3f}")
    print(f"  Categories: {cat_str}")

# Overall baseline
all_scores = [r["sentiment_normalized"] for r in data]
print(f"\nOverall baseline  (n={len(data)})")
print(f"  Mean: {statistics.mean(all_scores):+.3f}   Median: {statistics.median(all_scores):+.3f}")

# ── 2. Representative quotes for most negative and most positive positions ─

sorted_positions = sorted(summaries, key=lambda p: summaries[p]["mean"])
most_negative = sorted_positions[0]
most_positive = sorted_positions[-1]

def print_quotes(pos_name, records, n=3):
    """Print n quotes from the middle of the sentiment distribution for representativeness."""
    sorted_recs = sorted(records, key=lambda r: r["sentiment_normalized"])
    # Pick from 25th, 50th, 75th percentile-ish
    indices = [len(sorted_recs)//4, len(sorted_recs)//2, 3*len(sorted_recs)//4]
    if len(sorted_recs) < 4:
        indices = list(range(min(n, len(sorted_recs))))
    print(f"\n--- Representative quotes: {pos_name} (mean={summaries[pos_name]['mean']:+.3f}) ---")
    for idx in indices[:n]:
        r = sorted_recs[idx]
        print(f"\n  [{r['employee_id']}, {r['site']}, sentiment={r['sentiment_normalized']:+.3f}]")
        print(f"  Q1: {r['q1'][:200]}...")
        print(f"  Q5: {r['q5'][:200]}...")

print("\n" + "=" * 80)
print("REPRESENTATIVE QUOTES")
print("=" * 80)
print_quotes(most_negative, positions[most_negative])
print_quotes(most_positive, positions[most_positive])

# ── 3. Position sentiment WITHIN each site ────────────────────────────────

print("\n" + "=" * 80)
print("POSITION SENTIMENT WITHIN EACH SITE")
print("=" * 80)

sites = sorted(set(r["site"] for r in data))
# Build site × position matrix
for site in sites:
    print(f"\n{site}:")
    site_recs = [r for r in data if r["site"] == site]
    site_positions = defaultdict(list)
    for r in site_recs:
        site_positions[r["position"]].append(r["sentiment_normalized"])
    for pos in sorted(site_positions, key=lambda p: statistics.mean(site_positions[p])):
        scores = site_positions[pos]
        m = statistics.mean(scores)
        print(f"  {pos:25s}  n={len(scores):3d}  mean={m:+.3f}")

# ── 4. Check consistency: does the position ranking hold across sites? ────

print("\n" + "=" * 80)
print("POSITION RANK CONSISTENCY ACROSS SITES")
print("=" * 80)

# For each site, rank positions by mean sentiment
position_ranks = defaultdict(list)
for site in sites:
    site_recs = [r for r in data if r["site"] == site]
    site_positions = defaultdict(list)
    for r in site_recs:
        site_positions[r["position"]].append(r["sentiment_normalized"])
    ranked = sorted(site_positions, key=lambda p: statistics.mean(site_positions[p]))
    for rank, pos in enumerate(ranked):
        position_ranks[pos].append((site, rank + 1, len(site_positions[pos]), statistics.mean(site_positions[pos])))

for pos in sorted(position_ranks, key=lambda p: summaries[p]["mean"]):
    entries = position_ranks[pos]
    print(f"\n{pos} (overall mean={summaries[pos]['mean']:+.3f}):")
    for site, rank, n, m in entries:
        print(f"  {site:30s} rank={rank}  n={n:3d}  mean={m:+.3f}")
