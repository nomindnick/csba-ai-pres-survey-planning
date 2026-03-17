#!/usr/bin/env python3
"""Tenure × Site sentiment cross-tabulation analysis."""

import json
import re
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    records = json.load(f)

# --- Keyword sentiment scoring ---
POS = re.compile(
    r"\b(?:great|excellent|improved|better|smooth|helpful|good|easy|appreciate|intuitive|clear)\b",
    re.IGNORECASE,
)
NEG = re.compile(
    r"\b(?:frustrated|terrible|poor|difficult|disruption|problem|issue|confusing|rushed|broken|fail|worse|struggle|complaint|disappointed)\b",
    re.IGNORECASE,
)

def sentiment(record):
    text = " ".join(record.get(f"q{i}", "") or "" for i in range(1, 6))
    pos = len(POS.findall(text))
    neg = len(NEG.findall(text))
    total = pos + neg
    return (pos - neg) / total if total else 0.0

for r in records:
    r["sentiment"] = sentiment(r)

# --- Helper: compute group stats ---
def group_stats(rows):
    if not rows:
        return {"n": 0, "mean": None}
    vals = [r["sentiment"] for r in rows]
    return {"n": len(vals), "mean": round(sum(vals) / len(vals), 3)}

# --- Build lookups ---
sites = sorted(set(r["site"] for r in records))
district_bands = ["0-3", "4-10", "11-20", "20+"]
profession_bands = ["0-5", "6-15", "16-25", "25+"]

# Fix: discover actual band labels from data
# Order bands logically, not alphabetically
DISTRICT_ORDER = ["0-3", "4-10", "11-20", "20+"]
PROFESSION_ORDER = ["0-5", "6-15", "16-25", "25+"]
district_bands_actual = [b for b in DISTRICT_ORDER if b in set(r["years_at_district_band"] for r in records)]
profession_bands_actual = [b for b in PROFESSION_ORDER if b in set(r["years_in_profession_band"] for r in records)]

print("=== District-tenure bands found:", district_bands_actual)
print("=== Profession-tenure bands found:", profession_bands_actual)
print()

# --- Cross-tab: site × years_at_district_band ---
print("=" * 80)
print("CROSS-TAB: Site × Years-at-District Band (mean sentiment, N)")
print("=" * 80)

# Header
bands = district_bands_actual
header = f"{'Site':<30}" + "".join(f"{'  ' + b:>16}" for b in bands) + f"{'  ALL':>16}"
print(header)
print("-" * len(header))

site_band_data = {}  # (site, band) -> stats
for site in sites:
    parts = []
    for band in bands:
        rows = [r for r in records if r["site"] == site and r["years_at_district_band"] == band]
        s = group_stats(rows)
        site_band_data[(site, band)] = s
        parts.append(f"{s['mean']:+.3f} (n={s['n']:>3})" if s["n"] else "  --- (n=  0)")
    all_rows = [r for r in records if r["site"] == site]
    sa = group_stats(all_rows)
    parts.append(f"{sa['mean']:+.3f} (n={sa['n']:>3})")
    print(f"{site:<30}" + "".join(f"{p:>16}" for p in parts))

# Overall row
parts = []
for band in bands:
    rows = [r for r in records if r["years_at_district_band"] == band]
    s = group_stats(rows)
    parts.append(f"{s['mean']:+.3f} (n={s['n']:>3})")
all_s = group_stats(records)
parts.append(f"{all_s['mean']:+.3f} (n={all_s['n']:>3})")
print("-" * len(header))
print(f"{'ALL SITES':<30}" + "".join(f"{p:>16}" for p in parts))

# --- Cross-tab: site × years_in_profession_band ---
print()
print("=" * 80)
print("CROSS-TAB: Site × Years-in-Profession Band (mean sentiment, N)")
print("=" * 80)

pbands = profession_bands_actual
header2 = f"{'Site':<30}" + "".join(f"{'  ' + b:>16}" for b in pbands) + f"{'  ALL':>16}"
print(header2)
print("-" * len(header2))

for site in sites:
    parts = []
    for band in pbands:
        rows = [r for r in records if r["site"] == site and r["years_in_profession_band"] == band]
        s = group_stats(rows)
        parts.append(f"{s['mean']:+.3f} (n={s['n']:>3})" if s["n"] else "  --- (n=  0)")
    all_rows = [r for r in records if r["site"] == site]
    sa = group_stats(all_rows)
    parts.append(f"{sa['mean']:+.3f} (n={sa['n']:>3})")
    print(f"{site:<30}" + "".join(f"{p:>16}" for p in parts))

parts = []
for band in pbands:
    rows = [r for r in records if r["years_in_profession_band"] == band]
    s = group_stats(rows)
    parts.append(f"{s['mean']:+.3f} (n={s['n']:>3})")
parts.append(f"{all_s['mean']:+.3f} (n={all_s['n']:>3})")
print("-" * len(header2))
print(f"{'ALL SITES':<30}" + "".join(f"{p:>16}" for p in parts))

# --- Steepest tenure decline by site ---
print()
print("=" * 80)
print("TENURE DECLINE BY SITE (newest band vs oldest band, district tenure)")
print("=" * 80)

newest_band = bands[0]   # lowest tenure
oldest_band = bands[-1]  # highest tenure

declines = []
for site in sites:
    new_s = site_band_data.get((site, newest_band), {"n": 0, "mean": None})
    old_s = site_band_data.get((site, oldest_band), {"n": 0, "mean": None})
    if new_s["mean"] is not None and old_s["mean"] is not None:
        drop = new_s["mean"] - old_s["mean"]
        declines.append((site, new_s, old_s, drop))
        print(f"{site:<30}  New ({newest_band}): {new_s['mean']:+.3f} (n={new_s['n']})  "
              f"Veteran ({oldest_band}): {old_s['mean']:+.3f} (n={old_s['n']})  "
              f"Gap: {drop:+.3f}")

declines.sort(key=lambda x: x[3])  # most negative = steepest decline toward veterans
print()
print(f">>> STEEPEST tenure decline: {declines[0][0]} (gap = {declines[0][3]:+.3f})")
print(f">>> FLATTEST/reversed:      {declines[-1][0]} (gap = {declines[-1][3]:+.3f})")

# --- New staff (0-3 district years) by site ---
print()
print("=" * 80)
print("NEW STAFF (0-3 district years) BY SITE")
print("=" * 80)
for site in sites:
    rows = [r for r in records if r["site"] == site and r["years_at_district_band"] == newest_band]
    s = group_stats(rows)
    if s["n"]:
        print(f"{site:<30}  mean={s['mean']:+.3f}  n={s['n']}")

# --- Veteran staff (20+ district years) by site ---
print()
print("=" * 80)
print("VETERAN STAFF (20+ district years) BY SITE — using highest band: " + oldest_band)
print("=" * 80)
for site in sites:
    rows = [r for r in records if r["site"] == site and r["years_at_district_band"] == oldest_band]
    s = group_stats(rows)
    if s["n"]:
        print(f"{site:<30}  mean={s['mean']:+.3f}  n={s['n']}")

# --- Also check: within each site, correlation between raw years and sentiment ---
print()
print("=" * 80)
print("RAW CORRELATION: years_at_district vs sentiment, by site")
print("=" * 80)

def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = sum((x-mx)**2 for x in xs) ** 0.5
    dy = sum((y-my)**2 for y in ys) ** 0.5
    return num / (dx * dy) if dx and dy else None

for site in sites:
    rows = [r for r in records if r["site"] == site]
    xs = [r["years_at_district"] for r in rows]
    ys = [r["sentiment"] for r in rows]
    r_val = pearson(xs, ys)
    if r_val is not None:
        print(f"{site:<30}  r = {r_val:+.3f}  (n={len(rows)})")

print()
print("ALL SITES combined:")
xs = [r["years_at_district"] for r in records]
ys = [r["sentiment"] for r in records]
r_val = pearson(xs, ys)
print(f"  r = {r_val:+.3f}  (n={len(records)})")
