#!/usr/bin/env python3
"""
Broken Promises / Expectation Gap Analysis
-------------------------------------------
Analyzes survey responses for language indicating unmet expectations:
"told", "supposed to", "promised", "expected", "we were", "said it would", "they said"

Breaks down by site, position, and distinguishes communication gaps from broken promises.
Compares sentiment of "told" language users vs non-users.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Load data
data_path = Path("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json")
with open(data_path) as f:
    records = json.load(f)

print(f"Total records: {len(records)}")
print("=" * 80)

# ─── 1. FIND ALL RESPONDENTS WITH EXPECTATION-GAP LANGUAGE ────────────────────

# Patterns to search for (case-insensitive)
patterns = {
    "told": r"\btold\b",
    "supposed to": r"\bsupposed\s+to\b",
    "promised": r"\bpromis\w+\b",
    "expected": r"\bexpect\w+\b",
    "we were": r"\bwe\s+were\b",
    "said it would": r"\bsaid\s+it\s+would\b",
    "they said": r"\bthey\s+said\b",
}

questions = ["q1", "q2", "q3", "q4", "q5"]

def get_all_text(record):
    return " ".join(record.get(q, "") or "" for q in questions)

def find_pattern_matches(text):
    """Return dict of pattern_name -> list of match contexts"""
    matches = {}
    for name, pat in patterns.items():
        found = list(re.finditer(pat, text, re.IGNORECASE))
        if found:
            contexts = []
            for m in found:
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippet = text[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                contexts.append(snippet)
            matches[name] = contexts
    return matches

# Find all respondents with any match
flagged = []
for r in records:
    text = get_all_text(r)
    matches = find_pattern_matches(text)
    if matches:
        flagged.append({
            "record": r,
            "matches": matches,
            "text": text,
            "pattern_count": sum(len(v) for v in matches.values()),
            "patterns_used": set(matches.keys()),
        })

print(f"\n1. RESPONDENTS WITH EXPECTATION-GAP LANGUAGE")
print(f"   Flagged: {len(flagged)} / {len(records)} ({100*len(flagged)/len(records):.1f}%)")
print(f"\n   Pattern frequency across all flagged respondents:")

pattern_counts = Counter()
for f_item in flagged:
    for pat_name in f_item["patterns_used"]:
        pattern_counts[pat_name] += 1

for pat, count in pattern_counts.most_common():
    print(f"     {pat:20s}: {count:3d} respondents ({100*count/len(records):.1f}% of all)")

# ─── 2. READ 10-15 QUOTES SHOWING EXPECTATION GAP ────────────────────────────

print("\n" + "=" * 80)
print("\n2. REPRESENTATIVE QUOTES — EXPECTATION GAP")
print("   (What were they told vs what happened?)\n")

# Sort by number of pattern matches to find the most "loaded" responses
flagged_sorted = sorted(flagged, key=lambda x: x["pattern_count"], reverse=True)

# Collect individual quotes from q1-q5 that contain the patterns
all_quotes = []
for f_item in flagged:
    r = f_item["record"]
    for q in questions:
        text = r.get(q, "") or ""
        # Check if this specific answer has any pattern
        has_match = False
        for pat in patterns.values():
            if re.search(pat, text, re.IGNORECASE):
                has_match = True
                break
        if has_match and len(text) > 40:  # Skip very short responses
            all_quotes.append({
                "employee_id": r["employee_id"],
                "site": r["site"],
                "position": r["position"],
                "question": q,
                "text": text,
                "years_at_district": r["years_at_district"],
            })

# Pick diverse quotes (different sites, positions, patterns)
shown_sites = Counter()
shown_positions = Counter()
selected_quotes = []

# First pass: prioritize quotes with strongest expectation gap language
# (multiple patterns or "supposed to" / "promised" / "said it would")
priority_patterns = [r"\bsupposed\s+to\b", r"\bpromis\w+\b", r"\bsaid\s+it\s+would\b", r"\bthey\s+said\b"]

def priority_score(quote):
    score = 0
    for p in priority_patterns:
        if re.search(p, quote["text"], re.IGNORECASE):
            score += 2
    if re.search(r"\btold\b", quote["text"], re.IGNORECASE):
        score += 1
    return score

all_quotes.sort(key=lambda q: priority_score(q), reverse=True)

for q in all_quotes:
    if len(selected_quotes) >= 15:
        break
    # Ensure diversity
    if shown_sites[q["site"]] >= 4:
        continue
    selected_quotes.append(q)
    shown_sites[q["site"]] += 1
    shown_positions[q["position"]] += 1

for i, q in enumerate(selected_quotes, 1):
    print(f"  [{i}] {q['employee_id']} | {q['site']} | {q['position']} | {q['years_at_district']}yr | {q['question']}")
    # Truncate long quotes for readability
    text = q["text"]
    if len(text) > 300:
        text = text[:300] + "..."
    print(f"      \"{text}\"")
    print()

# ─── 3. BREAKDOWN BY SITE AND POSITION ───────────────────────────────────────

print("=" * 80)
print("\n3. BREAKDOWN BY SITE AND POSITION\n")

# By site
site_flagged = Counter()
site_total = Counter()
for r in records:
    site_total[r["site"]] += 1
for f_item in flagged:
    site_flagged[f_item["record"]["site"]] += 1

print("   BY SITE:")
print(f"   {'Site':35s} {'Flagged':>8s} {'Total':>6s} {'Rate':>7s}")
print(f"   {'-'*35} {'-'*8} {'-'*6} {'-'*7}")
for site in sorted(site_total.keys()):
    n_flag = site_flagged.get(site, 0)
    n_total = site_total[site]
    rate = 100 * n_flag / n_total if n_total > 0 else 0
    marker = " <<<" if rate > 50 else ""
    print(f"   {site:35s} {n_flag:8d} {n_total:6d} {rate:6.1f}%{marker}")

# By position
pos_flagged = Counter()
pos_total = Counter()
for r in records:
    pos_total[r["position"]] += 1
for f_item in flagged:
    pos_flagged[f_item["record"]["position"]] += 1

print(f"\n   BY POSITION:")
print(f"   {'Position':35s} {'Flagged':>8s} {'Total':>6s} {'Rate':>7s}")
print(f"   {'-'*35} {'-'*8} {'-'*6} {'-'*7}")
for pos in sorted(pos_total.keys()):
    n_flag = pos_flagged.get(pos, 0)
    n_total = pos_total[pos]
    rate = 100 * n_flag / n_total if n_total > 0 else 0
    print(f"   {pos:35s} {n_flag:8d} {n_total:6d} {rate:6.1f}%")

# Cross-tab: site x position (top combinations)
print(f"\n   TOP SITE x POSITION COMBINATIONS (by rate, min 3 respondents):")
cross = defaultdict(lambda: {"flagged": 0, "total": 0})
for r in records:
    key = (r["site"], r["position"])
    cross[key]["total"] += 1
for f_item in flagged:
    r = f_item["record"]
    key = (r["site"], r["position"])
    cross[key]["flagged"] += 1

cross_rates = []
for (site, pos), counts in cross.items():
    if counts["total"] >= 3:
        rate = 100 * counts["flagged"] / counts["total"]
        cross_rates.append((site, pos, counts["flagged"], counts["total"], rate))

cross_rates.sort(key=lambda x: x[4], reverse=True)
print(f"   {'Site':30s} {'Position':20s} {'Flag':>5s} {'Tot':>5s} {'Rate':>7s}")
print(f"   {'-'*30} {'-'*20} {'-'*5} {'-'*5} {'-'*7}")
for site, pos, nf, nt, rate in cross_rates[:15]:
    print(f"   {site:30s} {pos:20s} {nf:5d} {nt:5d} {rate:6.1f}%")

# ─── 4. COMMUNICATION vs BROKEN PROMISES ─────────────────────────────────────

print("\n" + "=" * 80)
print("\n4. COMMUNICATION GAPS vs BROKEN PROMISES\n")

# Classification approach:
# "Communication gap" = language about being informed/not informed of the change
#   Indicators: "told about", "told us about", "weren't told", "didn't tell",
#               "informed", "communicated", "heard about", "found out"
# "Broken promise" = language about system not meeting stated expectations
#   Indicators: "told it would", "supposed to", "promised", "said it would",
#               "was going to", "they said", "told us it", "told it was"

comm_patterns = [
    r"\btold\s+(us\s+)?about\b",
    r"\bweren'?t\s+told\b",
    r"\bnot\s+told\b",
    r"\bdidn'?t\s+tell\b",
    r"\bnever\s+told\b",
    r"\bfound\s+out\b",
    r"\bheard\s+about\b",
    r"\binformed\b",
    r"\bno\s+(one|body)\s+(told|informed|said)\b",
]

promise_patterns = [
    r"\btold\s+(us\s+)?(it|the|this)\s+(would|was|could|should)\b",
    r"\bsupposed\s+to\b",
    r"\bpromis\w+\b",
    r"\bsaid\s+it\s+would\b",
    r"\bthey\s+said\b",
    r"\bwas\s+going\s+to\b",
    r"\btold\s+(us\s+)?(it|things?)\s+(were|would)\b",
    r"\bexpected\s+(it|the|this|things?)\s+to\b",
    r"\bwhat\s+we\s+were\s+told\b",
]

comm_respondents = set()
promise_respondents = set()
both_respondents = set()

comm_quotes = []
promise_quotes = []

for f_item in flagged:
    r = f_item["record"]
    text = f_item["text"]
    eid = r["employee_id"]

    is_comm = any(re.search(p, text, re.IGNORECASE) for p in comm_patterns)
    is_promise = any(re.search(p, text, re.IGNORECASE) for p in promise_patterns)

    if is_comm:
        comm_respondents.add(eid)
    if is_promise:
        promise_respondents.add(eid)
    if is_comm and is_promise:
        both_respondents.add(eid)

    # Collect quotes for each category
    for q in questions:
        qt = r.get(q, "") or ""
        if is_comm and any(re.search(p, qt, re.IGNORECASE) for p in comm_patterns):
            comm_quotes.append({"eid": eid, "site": r["site"], "pos": r["position"], "q": q, "text": qt})
        if is_promise and any(re.search(p, qt, re.IGNORECASE) for p in promise_patterns):
            promise_quotes.append({"eid": eid, "site": r["site"], "pos": r["position"], "q": q, "text": qt})

only_comm = comm_respondents - promise_respondents
only_promise = promise_respondents - comm_respondents

print(f"   Communication gap only:  {len(only_comm):3d} respondents")
print(f"   Broken promise only:     {len(only_promise):3d} respondents")
print(f"   Both:                    {len(both_respondents):3d} respondents")
print(f"   Neither (other patterns):{len(flagged) - len(comm_respondents | promise_respondents):3d} respondents")
print(f"   Total flagged:           {len(flagged):3d} respondents")

# Site breakdown for each category
print(f"\n   COMMUNICATION GAP — by site:")
comm_by_site = Counter()
for f_item in flagged:
    if f_item["record"]["employee_id"] in comm_respondents:
        comm_by_site[f_item["record"]["site"]] += 1
for site in sorted(site_total.keys()):
    n = comm_by_site.get(site, 0)
    t = site_total[site]
    print(f"     {site:35s} {n:3d}/{t:3d} ({100*n/t:.1f}%)")

print(f"\n   BROKEN PROMISE — by site:")
prom_by_site = Counter()
for f_item in flagged:
    if f_item["record"]["employee_id"] in promise_respondents:
        prom_by_site[f_item["record"]["site"]] += 1
for site in sorted(site_total.keys()):
    n = prom_by_site.get(site, 0)
    t = site_total[site]
    print(f"     {site:35s} {n:3d}/{t:3d} ({100*n/t:.1f}%)")

print(f"\n   SAMPLE COMMUNICATION GAP QUOTES:")
for i, q in enumerate(comm_quotes[:5], 1):
    text = q["text"][:250] + "..." if len(q["text"]) > 250 else q["text"]
    print(f"     [{i}] {q['eid']} ({q['site']}, {q['pos']}) — {q['q']}")
    print(f"         \"{text}\"\n")

print(f"   SAMPLE BROKEN PROMISE QUOTES:")
for i, q in enumerate(promise_quotes[:5], 1):
    text = q["text"][:250] + "..." if len(q["text"]) > 250 else q["text"]
    print(f"     [{i}] {q['eid']} ({q['site']}, {q['pos']}) — {q['q']}")
    print(f"         \"{text}\"\n")

# ─── 5. SENTIMENT COMPARISON: "TOLD" LANGUAGE vs NOT ─────────────────────────

print("=" * 80)
print("\n5. SENTIMENT COMPARISON: EXPECTATION-GAP LANGUAGE vs NO SUCH LANGUAGE\n")

# Simple sentiment proxy: count negative and positive indicator words
negative_words = [
    r"\bfrustrat\w+\b", r"\bdisappoint\w+\b", r"\bconfus\w+\b", r"\boverwhelm\w+\b",
    r"\bdifficult\b", r"\bpoorly\b", r"\bterrible\b", r"\bawful\b", r"\bworse\b",
    r"\bfail\w*\b", r"\bstruggl\w+\b", r"\bignor\w+\b", r"\bdisrupt\w+\b",
    r"\brunning\s+into\b", r"\bproblem\w*\b", r"\bissue\w*\b", r"\bglitch\w*\b",
    r"\bunacceptable\b", r"\brushed\b", r"\bpoorly\b", r"\black\s+of\b",
    r"\bnot\s+(great|good|helpful|adequate|sufficient)\b", r"\binadequate\b",
    r"\bwaste\b", r"\bstress\w*\b", r"\bburden\w*\b",
]

positive_words = [
    r"\bgreat\b", r"\bexcellent\b", r"\bimprov\w+\b", r"\bhelpful\b",
    r"\bsmooth\w*\b", r"\beas\w+\b", r"\bbetter\b", r"\befficient\b",
    r"\bappreciat\w+\b", r"\bpleas\w+\b", r"\bsatisf\w+\b", r"\bgood\b",
    r"\beffective\b", r"\bclear\w*\b", r"\bwell\b", r"\bpositive\b",
    r"\bintuit\w+\b", r"\bseamless\b", r"\bwonderful\b",
]

def sentiment_score(text):
    """Simple sentiment: positive count - negative count"""
    neg = sum(1 for p in negative_words if re.search(p, text, re.IGNORECASE))
    pos = sum(1 for p in positive_words if re.search(p, text, re.IGNORECASE))
    return pos - neg, pos, neg

flagged_ids = set(f_item["record"]["employee_id"] for f_item in flagged)

flagged_scores = []
unflagged_scores = []

for r in records:
    text = get_all_text(r)
    score, pos, neg = sentiment_score(text)
    entry = {"score": score, "pos": pos, "neg": neg, "site": r["site"], "position": r["position"]}
    if r["employee_id"] in flagged_ids:
        flagged_scores.append(entry)
    else:
        unflagged_scores.append(entry)

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

flag_avg = avg([s["score"] for s in flagged_scores])
unflag_avg = avg([s["score"] for s in unflagged_scores])
flag_neg_avg = avg([s["neg"] for s in flagged_scores])
unflag_neg_avg = avg([s["neg"] for s in unflagged_scores])
flag_pos_avg = avg([s["pos"] for s in flagged_scores])
unflag_pos_avg = avg([s["pos"] for s in unflagged_scores])

print(f"   {'Metric':35s} {'With gap lang':>14s} {'Without':>14s} {'Delta':>10s}")
print(f"   {'-'*35} {'-'*14} {'-'*14} {'-'*10}")
print(f"   {'N respondents':35s} {len(flagged_scores):14d} {len(unflagged_scores):14d}")
print(f"   {'Avg sentiment score (pos-neg)':35s} {flag_avg:14.2f} {unflag_avg:14.2f} {flag_avg - unflag_avg:10.2f}")
print(f"   {'Avg negative word count':35s} {flag_neg_avg:14.2f} {unflag_neg_avg:14.2f} {flag_neg_avg - unflag_neg_avg:10.2f}")
print(f"   {'Avg positive word count':35s} {flag_pos_avg:14.2f} {unflag_pos_avg:14.2f} {flag_pos_avg - unflag_pos_avg:10.2f}")

# Sentiment by category (communication gap vs broken promise)
print(f"\n   SENTIMENT BY SUBCATEGORY:")
promise_scores = [s for s, f in zip(flagged_scores, flagged) if f["record"]["employee_id"] in promise_respondents]
comm_only_scores = [s for s, f in zip(flagged_scores, flagged) if f["record"]["employee_id"] in only_comm]
both_scores = [s for s, f in zip(flagged_scores, flagged) if f["record"]["employee_id"] in both_respondents]

categories = [
    ("Broken promise (any)", promise_scores),
    ("Communication gap only", comm_only_scores),
    ("Both comm + promise", both_scores),
    ("No expectation-gap language", unflagged_scores),
]

print(f"   {'Category':35s} {'N':>5s} {'Avg sent':>10s} {'Avg neg':>10s} {'Avg pos':>10s}")
print(f"   {'-'*35} {'-'*5} {'-'*10} {'-'*10} {'-'*10}")
for cat_name, scores in categories:
    if scores:
        print(f"   {cat_name:35s} {len(scores):5d} {avg([s['score'] for s in scores]):10.2f} {avg([s['neg'] for s in scores]):10.2f} {avg([s['pos'] for s in scores]):10.2f}")

# Breakdown: within flagged group, by site
print(f"\n   SENTIMENT OF FLAGGED RESPONDENTS — by site:")
print(f"   {'Site':35s} {'N flag':>7s} {'Avg sent':>10s} {'Avg neg':>10s}")
print(f"   {'-'*35} {'-'*7} {'-'*10} {'-'*10}")

site_flag_scores = defaultdict(list)
for s, f in zip(flagged_scores, flagged):
    site_flag_scores[f["record"]["site"]].append(s)

for site in sorted(site_total.keys()):
    scores = site_flag_scores.get(site, [])
    if scores:
        print(f"   {site:35s} {len(scores):7d} {avg([s['score'] for s in scores]):10.2f} {avg([s['neg'] for s in scores]):10.2f}")

# ─── 6. ADDITIONAL: TENURE & TRANSFER PATTERNS ───────────────────────────────

print("\n" + "=" * 80)
print("\n6. ADDITIONAL DIMENSIONS: TENURE, TRANSFERS, DEMOGRAPHICS\n")

# Tenure band breakdown
print("   BY YEARS AT DISTRICT:")
tenure_flagged = Counter()
tenure_total = Counter()
for r in records:
    tenure_total[r["years_at_district_band"]] += 1
for f in flagged:
    tenure_flagged[f["record"]["years_at_district_band"]] += 1

bands_order = ["0-3", "4-10", "11-20", "21-30", "31+"]
for band in bands_order:
    if band in tenure_total:
        nf = tenure_flagged.get(band, 0)
        nt = tenure_total[band]
        print(f"     {band:10s}: {nf:3d}/{nt:3d} ({100*nf/nt:.1f}%)")

# Transfer status
print(f"\n   BY TRANSFER STATUS:")
for is_transfer in [True, False]:
    total = sum(1 for r in records if r["is_transfer"] == is_transfer)
    flag_n = sum(1 for f in flagged if f["record"]["is_transfer"] == is_transfer)
    label = "Transfer" if is_transfer else "Non-transfer"
    print(f"     {label:15s}: {flag_n:3d}/{total:3d} ({100*flag_n/total:.1f}%)")

# Broken promise specifically among transfers
promise_transfer = sum(1 for f in flagged if f["record"]["employee_id"] in promise_respondents and f["record"]["is_transfer"])
transfer_total = sum(1 for r in records if r["is_transfer"])
promise_nontransfer = sum(1 for f in flagged if f["record"]["employee_id"] in promise_respondents and not f["record"]["is_transfer"])
nontransfer_total = sum(1 for r in records if not r["is_transfer"])
print(f"\n   BROKEN PROMISE language specifically:")
print(f"     Transfers:     {promise_transfer:3d}/{transfer_total:3d} ({100*promise_transfer/transfer_total:.1f}%)")
print(f"     Non-transfers: {promise_nontransfer:3d}/{nontransfer_total:3d} ({100*promise_nontransfer/nontransfer_total:.1f}%)")

print("\n" + "=" * 80)
print("\nDONE.")
