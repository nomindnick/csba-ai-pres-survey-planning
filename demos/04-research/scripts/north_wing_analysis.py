#!/usr/bin/env python3
"""Analyze North Wing building_wing subgroup vs rest of their site."""

import json
from collections import Counter

DATA_PATH = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA_PATH) as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# ── 1. Segment by building_wing ──────────────────────────────────────────────
wing_values = Counter(r.get("building_wing") for r in data)
print("\n=== building_wing distribution ===")
for k, v in wing_values.most_common():
    print(f"  {k!r}: {v}")

north_wing = [r for r in data if r.get("building_wing") == "North Wing"]
non_north = [r for r in data if r.get("building_wing") != "North Wing"]

print(f"\nNorth Wing count: {len(north_wing)}")

# ── 2. Profile North Wing ────────────────────────────────────────────────────
print("\n=== North Wing Profile ===")
print("Sites:", Counter(r["site"] for r in north_wing).most_common())
print("Positions:", Counter(r["position"] for r in north_wing).most_common())
print("Gender:", Counter(r["gender"] for r in north_wing).most_common())
print("Race/Ethnicity:", Counter(r["race_ethnicity"] for r in north_wing).most_common())
print("Age range:", min(r["age"] for r in north_wing), "-", max(r["age"] for r in north_wing))
print("Avg age:", round(sum(r["age"] for r in north_wing) / len(north_wing), 1))
print("Tenure bands:", Counter(r["years_at_district_band"] for r in north_wing).most_common())
print("Room types:", Counter(r["room_type"] for r in north_wing).most_common())
print("is_transfer:", Counter(r["is_transfer"] for r in north_wing).most_common())

# ── 3. Keyword-based sentiment scoring ───────────────────────────────────────
POSITIVE_WORDS = {
    "great", "excellent", "good", "well", "smooth", "easy", "helpful", "improved",
    "better", "love", "appreciate", "pleased", "satisfied", "fantastic", "wonderful",
    "impressed", "intuitive", "efficient", "effective", "positive", "clear", "clearer",
    "happy", "glad", "nice", "enjoy", "comfortable", "confident", "seamless",
    "responsive", "reliable", "upgrade", "benefit", "thankful", "grateful"
}
NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "awful", "frustrating", "frustrated", "difficult",
    "confusing", "confused", "broken", "fail", "failed", "failure", "worse",
    "worst", "problem", "problems", "issue", "issues", "disruption", "disruptive",
    "disrupted", "annoying", "annoyed", "disappointed", "disappointing", "rushed",
    "inadequate", "insufficient", "unreliable", "glitch", "glitches", "malfunction",
    "delay", "delays", "delayed", "noise", "noisy", "loud", "overwhelmed",
    "stressful", "stress", "struggle", "struggling", "complaint", "broken",
    "nightmare", "mess", "chaos", "chaotic", "horrible", "useless", "waste",
    "ignored", "neglected", "blindsided", "cut out", "inconsistent"
}

def sentiment_score(text):
    """Return (positive_count, negative_count, net_score) for a text."""
    if not text:
        return 0, 0, 0
    words = text.lower().split()
    # Also check bigrams for phrases like "cut out"
    tokens = set(words)
    for i in range(len(words) - 1):
        tokens.add(words[i] + " " + words[i+1])
    pos = sum(1 for w in tokens if w in POSITIVE_WORDS)
    neg = sum(1 for w in tokens if w in NEGATIVE_WORDS)
    return pos, neg, pos - neg

def score_all_questions(records):
    """Return per-question and overall sentiment stats."""
    questions = ["q1", "q2", "q3", "q4", "q5"]
    results = {}
    for q in questions:
        scores = [sentiment_score(r[q]) for r in records]
        pos_total = sum(s[0] for s in scores)
        neg_total = sum(s[1] for s in scores)
        net_scores = [s[2] for s in scores]
        avg_net = sum(net_scores) / len(net_scores) if net_scores else 0
        pct_negative = sum(1 for s in net_scores if s < 0) / len(net_scores) * 100 if net_scores else 0
        results[q] = {
            "avg_net": round(avg_net, 2),
            "pct_negative": round(pct_negative, 1),
            "pos_total": pos_total,
            "neg_total": neg_total,
            "n": len(records)
        }
    # Overall across all questions
    all_nets = []
    for r in records:
        nets = [sentiment_score(r[q])[2] for q in questions]
        all_nets.append(sum(nets) / len(nets))
    results["overall"] = {
        "avg_net": round(sum(all_nets) / len(all_nets), 2) if all_nets else 0,
        "pct_negative_avg": round(sum(1 for n in all_nets if n < 0) / len(all_nets) * 100, 1) if all_nets else 0,
        "n": len(records)
    }
    return results

# ── 4. Compare North Wing vs rest of SAME SITE ──────────────────────────────
print("\n=== Sentiment: North Wing vs Same-Site Non-North-Wing ===")

# Get sites that have North Wing employees
nw_sites = set(r["site"] for r in north_wing)
print(f"North Wing sites: {nw_sites}")

# Same-site comparison group (excluding North Wing)
same_site_rest = [r for r in data if r["site"] in nw_sites and r.get("building_wing") != "North Wing"]
other_sites = [r for r in data if r["site"] not in nw_sites]

nw_sent = score_all_questions(north_wing)
same_site_sent = score_all_questions(same_site_rest)

print(f"\n{'Question':<12} {'NW avg_net':>10} {'NW %neg':>8} {'Site-rest avg_net':>17} {'Site-rest %neg':>14} {'NW n':>5} {'Rest n':>7}")
print("-" * 80)
for q in ["q1", "q2", "q3", "q4", "q5", "overall"]:
    nw_key = q if q != "overall" else "overall"
    sr_key = q if q != "overall" else "overall"
    nw_avg = nw_sent[nw_key]["avg_net"]
    nw_neg = nw_sent[nw_key].get("pct_negative", nw_sent[nw_key].get("pct_negative_avg", 0))
    sr_avg = same_site_sent[sr_key]["avg_net"]
    sr_neg = same_site_sent[sr_key].get("pct_negative", same_site_sent[sr_key].get("pct_negative_avg", 0))
    nw_n = nw_sent[nw_key]["n"]
    sr_n = same_site_sent[sr_key]["n"]
    print(f"{q:<12} {nw_avg:>10.2f} {nw_neg:>7.1f}% {sr_avg:>17.2f} {sr_neg:>13.1f}% {nw_n:>5} {sr_n:>7}")

# Per-site breakdown for North Wing sites
for site in sorted(nw_sites):
    nw_at_site = [r for r in north_wing if r["site"] == site]
    rest_at_site = [r for r in same_site_rest if r["site"] == site]
    if not nw_at_site or not rest_at_site:
        continue
    nw_s = score_all_questions(nw_at_site)
    rest_s = score_all_questions(rest_at_site)
    print(f"\n  --- {site} ---")
    print(f"  North Wing (n={len(nw_at_site)}): overall avg_net = {nw_s['overall']['avg_net']:.2f}, %neg = {nw_s['overall']['pct_negative_avg']:.1f}%")
    print(f"  Rest of site (n={len(rest_at_site)}): overall avg_net = {rest_s['overall']['avg_net']:.2f}, %neg = {rest_s['overall']['pct_negative_avg']:.1f}%")

# ── 5. Theme analysis in North Wing responses ────────────────────────────────
INFRASTRUCTURE_KEYWORDS = [
    "noise", "noisy", "loud", "sound", "echo", "wall", "walls", "ceiling",
    "wiring", "wire", "cable", "cables", "duct", "vent", "ventilation",
    "construction", "dust", "debris", "drill", "drilling", "hammer",
    "plumbing", "pipe", "pipes", "asbestos", "mold", "leak", "leaking",
    "temperature", "heat", "heating", "cold", "hvac", "air conditioning",
    "electrical", "outlet", "power", "outage", "building", "wing",
    "hallway", "corridor", "classroom", "room", "space", "physical",
    "infrastructure", "structural", "renovation", "remodel"
]
DELAY_KEYWORDS = [
    "delay", "delayed", "late", "behind schedule", "took longer", "slow",
    "waited", "waiting", "overdue", "timeline", "schedule", "reschedule",
    "rescheduled", "postpone", "postponed", "pushed back", "setback",
    "weeks", "months", "still waiting", "not finished", "incomplete",
    "unfinished", "ongoing"
]
EQUIPMENT_KEYWORDS = [
    "equipment", "speaker", "speakers", "microphone", "mic", "intercom",
    "monitor", "screen", "camera", "hardware", "device", "unit", "panel",
    "router", "switch", "server", "phone", "handset", "receiver",
    "malfunction", "broken", "glitch", "glitches", "static", "feedback",
    "cut out", "cutting out", "drop", "dropping", "intermittent",
    "unreliable", "defective", "faulty"
]

def count_theme(records, keywords):
    """Count how many records mention at least one keyword across all q's."""
    count = 0
    mentions = []
    for r in records:
        all_text = " ".join(r[f"q{i}"] or "" for i in range(1, 6)).lower()
        found = [kw for kw in keywords if kw in all_text]
        if found:
            count += 1
            mentions.append((r["employee_id"], found))
    return count, mentions

print("\n=== Theme Prevalence: North Wing vs Same-Site Rest ===")
for theme_name, keywords in [("Infrastructure/Physical", INFRASTRUCTURE_KEYWORDS),
                              ("Delays/Timeline", DELAY_KEYWORDS),
                              ("Equipment/Technical", EQUIPMENT_KEYWORDS)]:
    nw_count, nw_mentions = count_theme(north_wing, keywords)
    sr_count, _ = count_theme(same_site_rest, keywords)
    nw_pct = nw_count / len(north_wing) * 100
    sr_pct = sr_count / len(same_site_rest) * 100
    print(f"\n{theme_name}:")
    print(f"  North Wing: {nw_count}/{len(north_wing)} ({nw_pct:.1f}%)")
    print(f"  Same-site rest: {sr_count}/{len(same_site_rest)} ({sr_pct:.1f}%)")
    print(f"  Difference: {nw_pct - sr_pct:+.1f} percentage points")

# ── 6. Representative quotes from North Wing ─────────────────────────────────
print("\n=== Representative North Wing Quotes ===")

# Score each North Wing respondent and pick diverse examples
nw_scored = []
for r in north_wing:
    total_net = sum(sentiment_score(r[f"q{i}"])[2] for i in range(1, 6))
    nw_scored.append((total_net, r))

nw_scored.sort(key=lambda x: x[0])  # most negative first

# Pick 5: 2 most negative, 1 middle, 2 most positive
picks = []
if len(nw_scored) >= 5:
    picks = [nw_scored[0], nw_scored[1], nw_scored[len(nw_scored)//2], nw_scored[-2], nw_scored[-1]]
else:
    picks = nw_scored[:5]

for i, (score, r) in enumerate(picks, 1):
    print(f"\n--- Quote {i} (net sentiment: {score}) ---")
    print(f"Employee: {r['employee_id']} | Site: {r['site']} | Position: {r['position']} | Wing: {r['building_wing']}")
    # Pick the most informative question response (longest with most sentiment words)
    best_q = max(range(1, 6), key=lambda qi: len(r[f"q{qi}"] or ""))
    print(f"[Q{best_q}]: \"{r[f'q{best_q}'][:500]}\"")
    # Also show another question if it's notably different
    second_q = max((qi for qi in range(1, 6) if qi != best_q),
                   key=lambda qi: abs(sentiment_score(r[f"q{qi}"])[2]))
    if abs(sentiment_score(r[f"q{second_q}"])[2]) > 0:
        print(f"[Q{second_q}]: \"{r[f'q{second_q}'][:400]}\"")

# ── 7. Additional: building_wing by other fields ─────────────────────────────
print("\n=== All building_wing values and their sites ===")
for wing_val in wing_values:
    if wing_val is None:
        continue
    wing_records = [r for r in data if r.get("building_wing") == wing_val]
    sites = Counter(r["site"] for r in wing_records)
    print(f"  {wing_val} (n={len(wing_records)}): sites={dict(sites)}")

# ── 8. Compare North Wing to overall dataset ─────────────────────────────────
print("\n=== For reference: Overall dataset sentiment ===")
overall_sent = score_all_questions(data)
print(f"Overall (n={len(data)}): avg_net = {overall_sent['overall']['avg_net']:.2f}, %neg = {overall_sent['overall']['pct_negative_avg']:.1f}%")
