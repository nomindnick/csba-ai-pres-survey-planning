#!/usr/bin/env python3
"""Analyze transfer status x site interactions and 'better' origin transfer complaints."""

import json
import re
from collections import Counter, defaultdict

# Load data
with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json") as f:
    data = json.load(f)

# --- Sentiment scoring ---
POS_WORDS = {"great","excellent","improved","better","smooth","helpful","good","easy","appreciate","intuitive","clear"}
NEG_WORDS = {"frustrated","terrible","poor","difficult","disruption","problem","issue","confusing","rushed","broken","fail","worse","struggle","complaint","disappointed"}

def sentiment_score(record):
    text = " ".join(record.get(f"q{i}","") or "" for i in range(1,6)).lower()
    words = re.findall(r'\b\w+\b', text)
    pos = sum(1 for w in words if w in POS_WORDS)
    neg = sum(1 for w in words if w in NEG_WORDS)
    return pos - neg

def sentiment_label(score):
    if score > 0: return "positive"
    if score < 0: return "negative"
    return "neutral"

for r in data:
    r["_sent_score"] = sentiment_score(r)
    r["_sent_label"] = sentiment_label(r["_sent_score"])

# ============================================================
# 1. Cross-tab: is_transfer x site with sentiment counts/means
# ============================================================
print("=" * 80)
print("1. CROSS-TAB: is_transfer x site -- sentiment counts and means")
print("=" * 80)

sites = sorted(set(r["site"] for r in data))
transfer_vals = [True, False]

for site in sites:
    print(f"\n--- {site} ---")
    for tv in transfer_vals:
        subset = [r for r in data if r["site"] == site and r["is_transfer"] == tv]
        n = len(subset)
        if n == 0:
            print(f"  Transfer={tv}: n=0")
            continue
        scores = [r["_sent_score"] for r in subset]
        mean_s = sum(scores) / n
        labels = Counter(r["_sent_label"] for r in subset)
        print(f"  Transfer={tv}: n={n}  mean_sent={mean_s:+.2f}  "
              f"pos={labels['positive']}  neu={labels['neutral']}  neg={labels['negative']}")

# Summary table
print("\n\nSummary: mean sentiment by transfer status x site")
print(f"{'Site':<30} {'Non-xfer mean':>13} {'n':>4}  {'Xfer mean':>10} {'n':>4}  {'Delta':>7}")
for site in sites:
    non = [r["_sent_score"] for r in data if r["site"] == site and not r["is_transfer"]]
    xfr = [r["_sent_score"] for r in data if r["site"] == site and r["is_transfer"]]
    nm = sum(non)/len(non) if non else 0
    xm = sum(xfr)/len(xfr) if xfr else 0
    delta = xm - nm
    print(f"{site:<30} {nm:>+13.2f} {len(non):>4}  {xm:>+10.2f} {len(xfr):>4}  {delta:>+7.2f}")

# ============================================================
# 2. Cross-tab: origin_district_system_quality x site (transfers only)
# ============================================================
print("\n" + "=" * 80)
print("2. CROSS-TAB: origin_district_system_quality x site (transfers only)")
print("=" * 80)

transfers = [r for r in data if r["is_transfer"]]
origins = sorted(set(r["origin_district_system_quality"] for r in transfers if r["origin_district_system_quality"]))

print(f"\n{'Site':<30}", end="")
for o in origins:
    print(f" {o:>8}", end="")
print(f" {'Total':>6}")

for site in sites:
    sub = [r for r in transfers if r["site"] == site]
    print(f"{site:<30}", end="")
    for o in origins:
        ct = sum(1 for r in sub if r["origin_district_system_quality"] == o)
        print(f" {ct:>8}", end="")
    print(f" {len(sub):>6}")

# Also show mean sentiment by origin quality x site
print("\nMean sentiment by origin_quality x site (transfers only):")
print(f"{'Site':<30}", end="")
for o in origins:
    print(f" {o:>10}", end="")
print()
for site in sites:
    print(f"{site:<30}", end="")
    for o in origins:
        sub = [r for r in transfers if r["site"] == site and r["origin_district_system_quality"] == o]
        if sub:
            m = sum(r["_sent_score"] for r in sub) / len(sub)
            print(f" {m:>+8.2f}({len(sub)})", end="")
        else:
            print(f" {'---':>10}", end="")
    print()

# ============================================================
# 3. Are "better" origin transfers concentrated at any site?
# ============================================================
print("\n" + "=" * 80)
print("3. 'Better' origin transfers by site")
print("=" * 80)

better = [r for r in transfers if r["origin_district_system_quality"] == "better"]
print(f"\nTotal 'better' origin transfers: {len(better)}")
site_counts = Counter(r["site"] for r in better)
for site in sites:
    ct = site_counts.get(site, 0)
    total_at_site = sum(1 for r in data if r["site"] == site)
    xfer_at_site = sum(1 for r in transfers if r["site"] == site)
    print(f"  {site:<30} better={ct:>3}  (of {xfer_at_site} transfers, {total_at_site} total staff)")

# Mean sentiment for better-origin by site
print("\nMean sentiment of 'better' origin transfers by site:")
for site in sites:
    sub = [r for r in better if r["site"] == site]
    if sub:
        m = sum(r["_sent_score"] for r in sub) / len(sub)
        print(f"  {site:<30} mean={m:>+.2f}  n={len(sub)}")

# ============================================================
# 4. What do "better" origin transfers complain about?
# ============================================================
print("\n" + "=" * 80)
print("4. 'Better' origin transfer complaint analysis")
print("=" * 80)

tech_keywords = ["audio", "speaker", "microphone", "static", "feedback", "wiring",
                 "intercom", "glitch", "cut out", "buzzing", "volume", "sound",
                 "north wing", "hardware", "software", "crash", "lag", "delay",
                 "connection", "network", "wi-fi", "wifi", "dropped"]
regression_keywords = ["old district", "previous district", "former district",
                       "old system", "previous system", "used to", "where i came from",
                       "at my last", "my old school", "compared to", "downgrade",
                       "step back", "step backward", "worse than", "better at",
                       "better where", "other district", "last district"]

for r in better:
    text = " ".join(r.get(f"q{i}","") or "" for i in range(1,6)).lower()
    r["_has_tech"] = any(kw in text for kw in tech_keywords)
    r["_has_regression"] = any(kw in text for kw in regression_keywords)

tech_ct = sum(1 for r in better if r["_has_tech"])
regr_ct = sum(1 for r in better if r["_has_regression"])
both_ct = sum(1 for r in better if r["_has_tech"] and r["_has_regression"])
neither = sum(1 for r in better if not r["_has_tech"] and not r["_has_regression"])

print(f"\nAmong {len(better)} 'better' origin transfers:")
print(f"  Technical complaint mentions:    {tech_ct}")
print(f"  Regression/comparison mentions:  {regr_ct}")
print(f"  Both:                            {both_ct}")
print(f"  Neither:                         {neither}")

# By site
print("\nBy site:")
for site in sites:
    sub = [r for r in better if r["site"] == site]
    if not sub:
        continue
    tc = sum(1 for r in sub if r["_has_tech"])
    rc = sum(1 for r in sub if r["_has_regression"])
    print(f"  {site:<30} n={len(sub):>2}  tech={tc}  regression={rc}")

# ============================================================
# 5. Read q1 and q4 from all "better" origin transfers
# ============================================================
print("\n" + "=" * 80)
print("5. Q1 and Q4 from all 'better' origin transfers")
print("=" * 80)

for r in sorted(better, key=lambda x: (x["site"], x["employee_id"])):
    print(f"\n--- {r['employee_id']} | {r['site']} | {r['position']} | sent={r['_sent_score']:+d} ---")
    print(f"  Q1: {r['q1']}")
    print(f"  Q4: {r['q4']}")

# ============================================================
# 6. Categorize complaints
# ============================================================
print("\n" + "=" * 80)
print("6. Complaint categorization for 'better' origin transfers")
print("=" * 80)

cat_system = ["glitch", "audio", "speaker", "sound", "intercom", "static", "cut out",
              "broken", "fail", "crash", "lag", "delay", "volume", "buzzing",
              "hardware", "software", "wiring", "connection", "dropped", "unreliable",
              "malfunction", "defect", "quality"]
cat_training = ["training", "workshop", "session", "learn", "hands-on", "demo",
                "instruction", "tutorial", "guide", "manual", "onboard"]
cat_communication = ["communicat", "informed", "told", "notice", "email", "meeting",
                     "announce", "timeline", "schedule", "transparency", "blindsided",
                     "surprised", "consult", "input", "voice"]
cat_comparison = ["old district", "previous district", "former district", "old system",
                  "previous system", "used to", "where i came from", "at my last",
                  "my old school", "compared to", "downgrade", "step back",
                  "worse than", "better at", "other district", "last district",
                  "old school", "previous school"]

categories = {
    "system_quality": cat_system,
    "training": cat_training,
    "communication": cat_communication,
    "comparison_to_old": cat_comparison
}

cat_counts = defaultdict(int)
cat_examples = defaultdict(list)

for r in better:
    text = " ".join(r.get(f"q{i}","") or "" for i in range(1,6)).lower()
    for cat_name, keywords in categories.items():
        if any(kw in text for kw in keywords):
            cat_counts[cat_name] += 1
            if len(cat_examples[cat_name]) < 3:
                for kw in keywords:
                    idx = text.find(kw)
                    if idx >= 0:
                        start = max(0, idx - 60)
                        end = min(len(text), idx + 60)
                        snippet = text[start:end]
                        cat_examples[cat_name].append((r["employee_id"], r["site"], snippet))
                        break

print(f"\nCategory counts among {len(better)} 'better' origin transfers:")
for cat_name in categories:
    pct = cat_counts[cat_name] / len(better) * 100 if better else 0
    print(f"  {cat_name:<20} {cat_counts[cat_name]:>3} ({pct:.0f}%)")

print("\nRepresentative snippets per category:")
for cat_name in categories:
    print(f"\n  [{cat_name}]")
    for eid, site, snip in cat_examples[cat_name]:
        print(f"    {eid} ({site}): ...{snip}...")

# ============================================================
# BONUS: Negative "better" transfers vs negative non-transfers
# ============================================================
print("\n" + "=" * 80)
print("BONUS: Negative 'better' transfers vs negative non-transfers")
print("=" * 80)

neg_better = [r for r in better if r["_sent_score"] < 0]
non_transfers = [r for r in data if not r["is_transfer"]]
neg_non = [r for r in non_transfers if r["_sent_score"] < 0]

print(f"\nNegative 'better' transfers: {len(neg_better)} of {len(better)} ({len(neg_better)/len(better)*100:.0f}%)")
print(f"Negative non-transfers: {len(neg_non)} of {len(non_transfers)} "
      f"({len(neg_non)/len(non_transfers)*100:.0f}%)")

for label, group in [("neg_better_transfers", neg_better), ("neg_non_transfers", neg_non[:50])]:
    comp_ct = 0
    for r in group:
        text = " ".join(r.get(f"q{i}","") or "" for i in range(1,6)).lower()
        if any(kw in text for kw in cat_comparison):
            comp_ct += 1
    print(f"  {label}: {comp_ct}/{len(group)} use comparison/regression language")
