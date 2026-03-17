#!/usr/bin/env python3
"""Qualitative analysis of Q3 (communication about the installation) responses.
Identifies communication failure themes by site and position, finds representative
quotes, and checks for positive communication experiences."""

import json
import re
from collections import defaultdict, Counter

# Load data
with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print(f"Sites: {sorted(set(r['site'] for r in data))}")
print(f"Positions: {sorted(set(r['position'] for r in data))}")
print()

# ── Theme definitions ──
negative_themes = {
    "blindsided": r"\bblindside[d]?\b",
    "no_input": r"\bno input\b|\bnot (asked|consulted|included|involved)\b|\bwithout (our|my|any|staff) input\b|\bnever asked\b|\bnever consulted\b",
    "found_out_from_others": r"\bfound out from\b|\bheard (it |about it )?from (a |another )?(teacher|colleague|coworker|custodian|parent|student|secretary)\b",
    "last_to_know": r"\blast to (know|hear|find out|learn)\b|\blast (ones?|people|group) to\b",
    "top_down": r"\btop[- ]?down\b|\bdictated\b|\bhanded down\b|\bfrom (the )?above\b|\bno say\b|\bno voice\b",
    "no_notice": r"\bno (advance |prior )?notice\b|\bno warning\b|\bno heads[- ]?up\b|\bshort notice\b|\bwithout (any )?notice\b|\bwithout warning\b",
    "surprised": r"\bsurprise[d]?\b|\bcaught (me |us )?off guard\b|\bdidn.t (even )?know\b|\bhad no idea\b",
    "after_the_fact": r"\bafter the fact\b|\bafter (it was |the )?decision\b|\balready decided\b|\bfait accompli\b|\bdone deal\b",
    "timeline_shifting": r"\btimeline (kept )?(shift|chang|mov)\w*\b|\bkept (changing|shifting|moving)\b|\bno clear timeline\b|\bvague timeline\b",
    "lack_of_transparency": r"\btransparenc\w*\b|\bnot transparent\b|\bkept in the dark\b|\bmushroom\b|\bleft out\b|\bout of the loop\b",
}

positive_themes = {
    "well_informed": r"\bwell[- ]?informed\b|\bkept (us |me )?(well |fully )?(informed|updated|in the loop)\b",
    "good_communication": r"\bgood communi\w+\b|\bgreat communi\w+\b|\bclear communi\w+\b|\beffective communi\w+\b|\bexcellent communi\w+\b",
    "appreciated_updates": r"\bappreciat\w+ (the )?(update|communi|info|notice|heads[- ]?up|email)\w*\b|\bthankful\b|\bgrateful\b",
    "advance_notice": r"\badvance notice\b|\bearly notice\b|\bplenty of (notice|warning|time|info)\b|\bgave us time\b|\bample (notice|warning|time)\b",
    "felt_included": r"\bfelt included\b|\bfelt (like )?(we |I )?(were |was )?(part of|included|consulted|heard|listened to)\b|\basked (for )?(our|my) (input|opinion|feedback|thought)\b",
    "transparent_process": r"\btransparent\b.*\b(process|communi|approach)\b|\bopen (and |about |communi)\b",
}

# ── Count themes ──
def find_themes(text, theme_dict):
    found = []
    for name, pattern in theme_dict.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(name)
    return found

# Per-record analysis
for r in data:
    r["neg_themes"] = find_themes(r["q3"], negative_themes)
    r["pos_themes"] = find_themes(r["q3"], positive_themes)
    r["neg_count"] = len(r["neg_themes"])
    r["pos_count"] = len(r["pos_themes"])

# ════════════════════════════════════════════════
# 1. OVERALL THEME FREQUENCY
# ════════════════════════════════════════════════
print("=" * 70)
print("OVERALL NEGATIVE COMMUNICATION THEME FREQUENCY")
print("=" * 70)
neg_totals = Counter()
for r in data:
    for t in r["neg_themes"]:
        neg_totals[t] += 1

for theme, count in neg_totals.most_common():
    print(f"  {theme:30s}  {count:4d}  ({count/len(data)*100:.1f}%)")

print()
print("OVERALL POSITIVE COMMUNICATION THEME FREQUENCY")
print("-" * 50)
pos_totals = Counter()
for r in data:
    for t in r["pos_themes"]:
        pos_totals[t] += 1

for theme, count in pos_totals.most_common():
    print(f"  {theme:30s}  {count:4d}  ({count/len(data)*100:.1f}%)")

has_neg = sum(1 for r in data if r["neg_count"] > 0)
has_pos = sum(1 for r in data if r["pos_count"] > 0)
has_neither = sum(1 for r in data if r["neg_count"] == 0 and r["pos_count"] == 0)
print(f"\nRecords with >= 1 negative theme: {has_neg} ({has_neg/len(data)*100:.1f}%)")
print(f"Records with >= 1 positive theme: {has_pos} ({has_pos/len(data)*100:.1f}%)")
print(f"Records with no detected themes:  {has_neither} ({has_neither/len(data)*100:.1f}%)")

# ════════════════════════════════════════════════
# 2. THEMES BY SITE
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("NEGATIVE THEME FREQUENCY BY SITE")
print("=" * 70)

sites = sorted(set(r["site"] for r in data))
for site in sites:
    site_records = [r for r in data if r["site"] == site]
    n = len(site_records)
    neg_at_site = Counter()
    for r in site_records:
        for t in r["neg_themes"]:
            neg_at_site[t] += 1
    has_any_neg = sum(1 for r in site_records if r["neg_count"] > 0)
    has_any_pos = sum(1 for r in site_records if r["pos_count"] > 0)
    print(f"\n  {site} (n={n}) — {has_any_neg} with neg themes ({has_any_neg/n*100:.0f}%), {has_any_pos} with pos themes ({has_any_pos/n*100:.0f}%)")
    for theme, count in neg_at_site.most_common():
        print(f"    {theme:28s}  {count:3d}  ({count/n*100:.1f}%)")

# ════════════════════════════════════════════════
# 3. THEMES BY POSITION
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("NEGATIVE THEME FREQUENCY BY POSITION")
print("=" * 70)

positions = sorted(set(r["position"] for r in data))
for pos in positions:
    pos_records = [r for r in data if r["position"] == pos]
    n = len(pos_records)
    neg_at_pos = Counter()
    for r in pos_records:
        for t in r["neg_themes"]:
            neg_at_pos[t] += 1
    has_any_neg = sum(1 for r in pos_records if r["neg_count"] > 0)
    has_any_pos = sum(1 for r in pos_records if r["pos_count"] > 0)
    print(f"\n  {pos} (n={n}) — {has_any_neg} with neg themes ({has_any_neg/n*100:.0f}%), {has_any_pos} with pos themes ({has_any_pos/n*100:.0f}%)")
    for theme, count in neg_at_pos.most_common():
        print(f"    {theme:28s}  {count:3d}  ({count/n*100:.1f}%)")

# ════════════════════════════════════════════════
# 4. CROSS-TAB: SITE x POSITION — % with any negative theme
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CROSS-TAB: % OF GROUP WITH ANY NEGATIVE COMMUNICATION THEME")
print("=" * 70)

header = f"{'':30s}" + "".join(f"{s:>22s}" for s in sites)
print(header)
for pos in positions:
    row = f"{pos:30s}"
    for site in sites:
        group = [r for r in data if r["site"] == site and r["position"] == pos]
        n = len(group)
        if n == 0:
            row += f"{'—':>22s}"
        else:
            neg_n = sum(1 for r in group if r["neg_count"] > 0)
            row += f"{neg_n}/{n} ({neg_n/n*100:.0f}%){' ':>6s}"
    print(row)

# ════════════════════════════════════════════════
# 5. REPRESENTATIVE NEGATIVE QUOTES BY SITE (top 5 per site, most themes)
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("REPRESENTATIVE NEGATIVE Q3 QUOTES BY SITE (strongest complaints)")
print("=" * 70)

for site in sites:
    site_records = [r for r in data if r["site"] == site and r["neg_count"] > 0]
    site_records.sort(key=lambda r: (-r["neg_count"], r["sentiment_net"]))
    print(f"\n── {site} ──")
    for r in site_records[:5]:
        print(f"  [{r['position']}, {r['years_at_district']}yr, {r['employee_id']}] themes={r['neg_themes']}")
        # Truncate long responses for readability
        q3 = r["q3"]
        if len(q3) > 300:
            q3 = q3[:297] + "..."
        print(f"    \"{q3}\"")
        print()

# ════════════════════════════════════════════════
# 6. WHO REPORTS GOOD COMMUNICATION?
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STAFF WHO REPORT POSITIVE COMMUNICATION EXPERIENCES")
print("=" * 70)

pos_staff = [r for r in data if r["pos_count"] > 0]
print(f"\nTotal with positive communication themes: {len(pos_staff)}")

# Breakdown
print("\nBy site:")
for site in sites:
    group = [r for r in pos_staff if r["site"] == site]
    total = sum(1 for r in data if r["site"] == site)
    print(f"  {site}: {len(group)}/{total} ({len(group)/total*100:.1f}%)")

print("\nBy position:")
for pos in positions:
    group = [r for r in pos_staff if r["position"] == pos]
    total = sum(1 for r in data if r["position"] == pos)
    if total > 0:
        print(f"  {pos}: {len(group)}/{total} ({len(group)/total*100:.1f}%)")

# Also check: purely positive (positive themes, NO negative themes)
pure_pos = [r for r in data if r["pos_count"] > 0 and r["neg_count"] == 0]
print(f"\nPurely positive (positive themes, zero negative): {len(pure_pos)}")
print("\nBy site:")
for site in sites:
    group = [r for r in pure_pos if r["site"] == site]
    total = sum(1 for r in data if r["site"] == site)
    print(f"  {site}: {len(group)}/{total} ({len(group)/total*100:.1f}%)")

print("\nSample positive-communication quotes:")
pure_pos.sort(key=lambda r: -r["pos_count"])
for r in pure_pos[:8]:
    q3 = r["q3"]
    if len(q3) > 300:
        q3 = q3[:297] + "..."
    print(f"  [{r['site']}, {r['position']}, {r['years_at_district']}yr, {r['employee_id']}] themes={r['pos_themes']}")
    print(f"    \"{q3}\"")
    print()

# ════════════════════════════════════════════════
# 7. SPECIAL: Transfers vs non-transfers
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TRANSFER STATUS AND COMMUNICATION THEMES")
print("=" * 70)

for transfer_status in [True, False]:
    group = [r for r in data if r["is_transfer"] == transfer_status]
    n = len(group)
    neg_n = sum(1 for r in group if r["neg_count"] > 0)
    pos_n = sum(1 for r in group if r["pos_count"] > 0)
    label = "Transfers" if transfer_status else "Non-transfers"
    print(f"\n  {label} (n={n}): {neg_n} neg ({neg_n/n*100:.1f}%), {pos_n} pos ({pos_n/n*100:.1f}%)")

# ════════════════════════════════════════════════
# 8. TENURE AND COMMUNICATION COMPLAINTS
# ════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TENURE BANDS AND COMMUNICATION COMPLAINTS")
print("=" * 70)

tenure_bands = ["0-3", "4-10", "11-20", "21+"]
for band in tenure_bands:
    group = [r for r in data if r["years_at_district_band"] == band]
    n = len(group)
    if n == 0:
        continue
    neg_n = sum(1 for r in group if r["neg_count"] > 0)
    pos_n = sum(1 for r in group if r["pos_count"] > 0)
    print(f"  {band:8s} (n={n:3d}): neg={neg_n:3d} ({neg_n/n*100:.1f}%), pos={pos_n:3d} ({pos_n/n*100:.1f}%)")

# Top themes by tenure
print("\n  Top negative themes by tenure band:")
for band in tenure_bands:
    group = [r for r in data if r["years_at_district_band"] == band]
    n = len(group)
    if n == 0:
        continue
    counts = Counter()
    for r in group:
        for t in r["neg_themes"]:
            counts[t] += 1
    top3 = counts.most_common(3)
    top3_str = ", ".join(f"{t}={c}" for t, c in top3)
    print(f"  {band:8s}: {top3_str}")

print("\n\nDone.")
