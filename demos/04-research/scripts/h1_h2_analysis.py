#!/usr/bin/env python3
"""
Investigate two hypotheses:
  H1: Large/Specialized rooms have different experiences than Standard rooms.
  H2: Interaction between tenure band and position group (teaching vs non-teaching) on sentiment.
"""

import json, re, textwrap
from collections import defaultdict, Counter

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    records = json.load(f)

print(f"Total records: {len(records)}\n")

# ── Sentiment scoring ──────────────────────────────────────────────────────
POS_WORDS = r'\b(?:improved|better|great|smooth|easy|helpful|clear|excellent|reliable|intuitive)\b'
NEG_WORDS = r'\b(?:frustrated|disrupted|poor|problem|issue|difficult|rushed|confused|worse|terrible|complaint|glitch|cut\s+out|garbled|hard\s+to\s+hear)\b'

def sentiment_score(record):
    """Return (pos_count, neg_count, net) across q1-q5."""
    text = " ".join(record.get(f"q{i}", "") or "" for i in range(1, 6)).lower()
    pos = len(re.findall(POS_WORDS, text))
    neg = len(re.findall(NEG_WORDS, text))
    return pos, neg, pos - neg

for r in records:
    r["_pos"], r["_neg"], r["_net"] = sentiment_score(r)

# ── Helper functions ───────────────────────────────────────────────────────
def stats(group, label=""):
    nets = [r["_net"] for r in group]
    n = len(nets)
    if n == 0:
        return {"label": label, "n": 0}
    mean = sum(nets) / n
    pos_pct = sum(1 for x in nets if x > 0) / n * 100
    neg_pct = sum(1 for x in nets if x < 0) / n * 100
    neu_pct = sum(1 for x in nets if x == 0) / n * 100
    return {
        "label": label, "n": n,
        "mean_net": round(mean, 2),
        "pos_pct": round(pos_pct, 1),
        "neg_pct": round(neg_pct, 1),
        "neu_pct": round(neu_pct, 1),
    }

def print_stats(s):
    print(f"  {s['label']:40s}  n={s['n']:>4d}  mean_net={s.get('mean_net','N/A'):>6}  "
          f"pos={s.get('pos_pct','N/A'):>5}%  neg={s.get('neg_pct','N/A'):>5}%  neu={s.get('neu_pct','N/A'):>5}%")

def pull_quotes(group, sort_key="_net", n_neg=3, n_pos=2):
    """Return representative negative and positive quotes."""
    sorted_g = sorted(group, key=lambda r: r[sort_key])
    quotes = []
    for r in sorted_g[:n_neg]:
        text = " | ".join((r.get(f"q{i}","") or "")[:120] for i in range(1,6) if r.get(f"q{i}"))
        quotes.append(f"  [{r['employee_id']} | {r['position']} | {r['site']} | net={r['_net']}]\n    {text[:300]}...")
    for r in sorted_g[-n_pos:]:
        text = " | ".join((r.get(f"q{i}","") or "")[:120] for i in range(1,6) if r.get(f"q{i}"))
        quotes.append(f"  [{r['employee_id']} | {r['position']} | {r['site']} | net={r['_net']}]\n    {text[:300]}...")
    return quotes

# ═══════════════════════════════════════════════════════════════════════════
# H1: LARGE/SPECIALIZED vs STANDARD ROOMS
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 80)
print("H1: LARGE/SPECIALIZED ROOMS vs STANDARD ROOMS")
print("=" * 80)

large = [r for r in records if r.get("room_type") == "Large/Specialized"]
standard = [r for r in records if r.get("room_type") == "Standard"]
null_room = [r for r in records if not r.get("room_type")]

print(f"\nRoom type distribution:")
print(f"  Standard:          {len(standard)}")
print(f"  Large/Specialized: {len(large)}")
print(f"  Null/missing:      {len(null_room)}")

# ── Profile the Large/Specialized group ────────────────────────────────────
print(f"\n--- Profile of Large/Specialized rooms (n={len(large)}) ---")

print("\n  By site:")
site_counts = Counter(r["site"] for r in large)
for site, cnt in site_counts.most_common():
    print(f"    {site:35s} {cnt:>3d}")

print("\n  By position:")
pos_counts = Counter(r["position"] for r in large)
for pos, cnt in pos_counts.most_common():
    print(f"    {pos:35s} {cnt:>3d}")

print("\n  By building_wing:")
wing_counts = Counter(r.get("building_wing") or "null" for r in large)
for w, cnt in wing_counts.most_common():
    print(f"    {w:35s} {cnt:>3d}")

print("\n  Tenure distribution:")
tenure_counts = Counter(r["years_at_district_band"] for r in large)
for t, cnt in sorted(tenure_counts.items()):
    print(f"    {t:35s} {cnt:>3d}")

print("\n  Gender:")
for g, cnt in Counter(r["gender"] for r in large).most_common():
    print(f"    {g:35s} {cnt:>3d}")

print("\n  Race/Ethnicity:")
for g, cnt in Counter(r["race_ethnicity"] for r in large).most_common():
    print(f"    {g:35s} {cnt:>3d}")

# ── Overall sentiment comparison ───────────────────────────────────────────
print(f"\n--- Sentiment: Large/Specialized vs Standard (overall) ---")
print_stats(stats(large, "Large/Specialized"))
print_stats(stats(standard, "Standard"))

# ── Control for site ──────────────────────────────────────────────────────
print(f"\n--- Sentiment by room_type, controlling for site ---")
sites = sorted(set(r["site"] for r in records))
for site in sites:
    lg = [r for r in large if r["site"] == site]
    st = [r for r in standard if r["site"] == site]
    if len(lg) == 0:
        continue
    print(f"\n  {site}:")
    print_stats(stats(lg, f"  Large/Spec"))
    print_stats(stats(st, f"  Standard"))
    diff = (stats(lg)["mean_net"] - stats(st)["mean_net"]) if len(st) > 0 else None
    if diff is not None:
        print(f"    --> Difference (Large - Standard): {diff:+.2f}")

# ── Quotes from Large/Specialized ──────────────────────────────────────────
print(f"\n--- Representative quotes from Large/Specialized rooms ---")
for q in pull_quotes(large, n_neg=3, n_pos=2):
    print(q)

# ═══════════════════════════════════════════════════════════════════════════
# H2: TENURE x POSITION INTERACTION
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("H2: TENURE BAND x POSITION GROUP INTERACTION ON SENTIMENT")
print("=" * 80)

TEACHING = {"Teacher"}
NON_TEACHING_LABELS = {"Administrative Assistant", "Custodian", "IT Staff",
                       "Office Staff", "Counselor", "Nurse", "Librarian",
                       "Cafeteria Staff", "Security", "Paraprofessional",
                       "Bus Driver", "Maintenance"}

# Classify positions
for r in records:
    r["_pos_group"] = "Teaching" if r["position"] in TEACHING else "Non-Teaching"

pos_groups = sorted(set(r["_pos_group"] for r in records))
tenure_bands = ["0-3", "4-10", "11-20", "20+"]

print("\n--- Mean net sentiment: Tenure Band x Position Group ---")
print(f"  {'Tenure Band':>12s}", end="")
for pg in pos_groups:
    print(f"  {'n':>4s} {'mean':>6s}", end="")
print(f"  {'diff':>7s}")

for tb in tenure_bands:
    print(f"  {tb:>12s}", end="")
    group_stats = {}
    for pg in pos_groups:
        grp = [r for r in records if r["years_at_district_band"] == tb and r["_pos_group"] == pg]
        s = stats(grp, pg)
        group_stats[pg] = s
        print(f"  {s['n']:>4d} {s.get('mean_net', 'N/A'):>6}", end="")
    if all(pg in group_stats and group_stats[pg]["n"] > 0 for pg in pos_groups):
        diff = group_stats["Non-Teaching"]["mean_net"] - group_stats["Teaching"]["mean_net"]
        print(f"  {diff:>+7.2f}", end="")
    print()

# ── Percentage negative by tenure x position ──────────────────────────────
print("\n--- Pct negative sentiment: Tenure Band x Position Group ---")
print(f"  {'Tenure Band':>12s}", end="")
for pg in pos_groups:
    print(f"  {'n':>4s} {'%neg':>6s}", end="")
print(f"  {'diff':>7s}")

for tb in tenure_bands:
    print(f"  {tb:>12s}", end="")
    group_stats = {}
    for pg in pos_groups:
        grp = [r for r in records if r["years_at_district_band"] == tb and r["_pos_group"] == pg]
        s = stats(grp, pg)
        group_stats[pg] = s
        print(f"  {s['n']:>4d} {s.get('neg_pct', 'N/A'):>5}%", end="")
    if all(pg in group_stats and group_stats[pg]["n"] > 0 for pg in pos_groups):
        diff = group_stats["Non-Teaching"]["neg_pct"] - group_stats["Teaching"]["neg_pct"]
        print(f"  {diff:>+6.1f}%", end="")
    print()

# ── Detailed position breakdown for veterans (21+) ───────────────────────
print("\n--- Veteran (20+ years) breakdown by specific position ---")
veterans = [r for r in records if r["years_at_district_band"] == "20+"]
vet_positions = Counter(r["position"] for r in veterans)
print(f"  Total veterans: {len(veterans)}")
for pos, cnt in vet_positions.most_common():
    grp = [r for r in veterans if r["position"] == pos]
    s = stats(grp, pos)
    print_stats(s)

# ── Also check 11-20 band (larger sample) ────────────────────────────────
print("\n--- Senior (11-20 years) breakdown by specific position ---")
seniors = [r for r in records if r["years_at_district_band"] == "11-20"]
sen_positions = Counter(r["position"] for r in seniors)
print(f"  Total 11-20 year staff: {len(seniors)}")
for pos, cnt in sen_positions.most_common():
    grp = [r for r in seniors if r["position"] == pos]
    s = stats(grp, pos)
    print_stats(s)

# ── Non-teaching veteran quotes ───────────────────────────────────────────
print("\n--- Representative quotes: Veteran Non-Teaching staff ---")
vet_nonteach = [r for r in records if r["years_at_district_band"] in ("21+", "11-20") and r["_pos_group"] == "Non-Teaching"]
print(f"  (Pool: {len(vet_nonteach)} records with 11+ years, non-teaching)")
for q in pull_quotes(vet_nonteach, n_neg=4, n_pos=2):
    print(q)

# ── Compare new hires teaching vs non-teaching ───────────────────────────
print("\n--- New hires (0-3 years) by position group ---")
new_hires = [r for r in records if r["years_at_district_band"] == "0-3"]
for pg in pos_groups:
    grp = [r for r in new_hires if r["_pos_group"] == pg]
    print_stats(stats(grp, f"  {pg} (0-3 yrs)"))

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SUMMARY OF FINDINGS")
print("=" * 80)

lg_s = stats(large, "Large/Specialized")
st_s = stats(standard, "Standard")
print(f"""
H1 — Large/Specialized Rooms:
  - {lg_s['n']} Large/Specialized vs {st_s['n']} Standard rooms
  - Mean net sentiment: Large/Spec = {lg_s['mean_net']}, Standard = {st_s['mean_net']}
  - Pct negative: Large/Spec = {lg_s['neg_pct']}%, Standard = {st_s['neg_pct']}%
  - Difference = {lg_s['mean_net'] - st_s['mean_net']:+.2f} net sentiment points

H2 — Tenure x Position Interaction:
  See tables above for full cross-tabulation.
  Key question: Does the gap between Teaching and Non-Teaching sentiment
  widen for more tenured staff?
""")
