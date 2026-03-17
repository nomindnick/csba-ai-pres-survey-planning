#!/usr/bin/env python3
"""Keyword-based sentiment analysis of survey responses by site."""

import json
import statistics
from collections import defaultdict

# Load data
with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json") as f:
    data = json.load(f)

# Define keyword lists
POSITIVE = {"great", "excellent", "improved", "better", "smooth", "helpful",
            "good", "easy", "appreciate", "intuitive", "clear", "pleased",
            "effective", "comfortable", "well", "nice", "love", "fantastic",
            "wonderful", "positive", "seamless", "convenient"}
NEGATIVE = {"frustrated", "terrible", "poor", "difficult", "disruption",
            "problem", "issue", "confusing", "rushed", "broken", "fail",
            "worse", "struggle", "disruptive", "frustrating", "overwhelmed",
            "chaotic", "inadequate", "unreliable", "annoying", "complaint",
            "disappointing", "horrible", "awful", "nightmare", "stressed"}

QUESTIONS = ["q1", "q2", "q3", "q4", "q5"]


def score_text(text: str) -> dict:
    """Return positive count, negative count, and net score for a text."""
    words = text.lower().split()
    # Also catch word variants by checking if any keyword is a substring of a word
    pos = sum(1 for w in words for kw in POSITIVE if kw in w)
    neg = sum(1 for w in words for kw in NEGATIVE if kw in w)
    return {"positive": pos, "negative": neg, "net": pos - neg}


# Score every record
for record in data:
    total_pos = 0
    total_neg = 0
    for q in QUESTIONS:
        text = record.get(q, "") or ""
        s = score_text(text)
        total_pos += s["positive"]
        total_neg += s["negative"]
    record["sentiment_pos"] = total_pos
    record["sentiment_neg"] = total_neg
    record["sentiment_net"] = total_pos - total_neg


# Aggregate by site
site_scores = defaultdict(list)
for record in data:
    site_scores[record["site"]].append(record["sentiment_net"])

print("=" * 70)
print("SENTIMENT ANALYSIS BY SITE")
print("=" * 70)

site_stats = {}
for site in sorted(site_scores.keys()):
    scores = site_scores[site]
    n = len(scores)
    mean = statistics.mean(scores)
    med = statistics.median(scores)
    stdev = statistics.stdev(scores) if n > 1 else 0
    mn, mx = min(scores), max(scores)
    site_stats[site] = {"n": n, "mean": mean, "median": med, "stdev": stdev,
                        "min": mn, "max": mx}
    print(f"\n{site} (n={n})")
    print(f"  Mean sentiment:   {mean:+.2f}")
    print(f"  Median sentiment: {med:+.1f}")
    print(f"  Std dev:          {stdev:.2f}")
    print(f"  Range:            [{mn}, {mx}]")

    # Distribution buckets
    very_neg = sum(1 for s in scores if s <= -3)
    neg = sum(1 for s in scores if -3 < s < 0)
    neutral = sum(1 for s in scores if s == 0)
    pos = sum(1 for s in scores if 0 < s < 3)
    very_pos = sum(1 for s in scores if s >= 3)
    print(f"  Distribution: very_neg(<=-3)={very_neg}  neg=({neg})  "
          f"neutral={neutral}  pos={pos}  very_pos(>=3)={very_pos}")

# Find most positive and most negative sites
ranked = sorted(site_stats.items(), key=lambda x: x[1]["mean"])
most_negative_site = ranked[0][0]
most_positive_site = ranked[-1][0]

print("\n" + "=" * 70)
print(f"MOST NEGATIVE SITE: {most_negative_site} "
      f"(mean={ranked[0][1]['mean']:+.2f}, n={ranked[0][1]['n']})")
print("=" * 70)

# Get representative responses from most negative site
neg_records = [r for r in data if r["site"] == most_negative_site]
neg_records.sort(key=lambda r: r["sentiment_net"])
print("\n--- Most negative individual responses ---")
for r in neg_records[:3]:
    print(f"\n  Employee: {r['employee_id']} | Position: {r['position']} | "
          f"Score: {r['sentiment_net']:+d}")
    for q in QUESTIONS:
        text = r.get(q, "")
        if text:
            print(f"    {q}: {text[:200]}{'...' if len(text) > 200 else ''}")

print("\n" + "=" * 70)
print(f"MOST POSITIVE SITE: {most_positive_site} "
      f"(mean={ranked[-1][1]['mean']:+.2f}, n={ranked[-1][1]['n']})")
print("=" * 70)

pos_records = [r for r in data if r["site"] == most_positive_site]
pos_records.sort(key=lambda r: r["sentiment_net"], reverse=True)
print("\n--- Most positive individual responses ---")
for r in pos_records[:3]:
    print(f"\n  Employee: {r['employee_id']} | Position: {r['position']} | "
          f"Score: {r['sentiment_net']:+d}")
    for q in QUESTIONS:
        text = r.get(q, "")
        if text:
            print(f"    {q}: {text[:200]}{'...' if len(text) > 200 else ''}")

# Overall summary
print("\n" + "=" * 70)
print("SITE RANKING (by mean sentiment, ascending)")
print("=" * 70)
for site, stats in ranked:
    bar_len = int((stats["mean"] + 10) * 2)  # rough visual
    bar = "#" * max(bar_len, 1)
    print(f"  {site:<30s} mean={stats['mean']:+.2f}  (n={stats['n']})  {bar}")
