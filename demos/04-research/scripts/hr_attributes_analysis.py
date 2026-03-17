"""
Hypothesis: Transfer employees and those with specific HR attributes
(building_wing, room_type, origin_district_system_quality) show different
sentiment patterns.
"""

import json
import statistics
import random

random.seed(42)

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

def group_stats(records, label="Group"):
    if not records:
        return {"label": label, "n": 0}
    vals = [r["sentiment_normalized"] for r in records]
    return {
        "label": label,
        "n": len(records),
        "mean": round(statistics.mean(vals), 3),
        "median": round(statistics.median(vals), 3),
        "stdev": round(statistics.stdev(vals), 3) if len(vals) > 1 else 0,
        "pct_negative": round(sum(1 for r in records if r["sentiment_category"] == "negative") / len(records) * 100, 1),
        "pct_positive": round(sum(1 for r in records if r["sentiment_category"] == "positive") / len(records) * 100, 1),
    }

def print_stats(s):
    print(f"  {s['label']}: n={s['n']}, mean={s['mean']}, median={s['median']}, "
          f"stdev={s['stdev']}, %neg={s['pct_negative']}%, %pos={s['pct_positive']}%")

def print_quotes(records, label, n=3, sort_key="sentiment_normalized", ascending=True):
    """Print representative quotes from a subgroup, sorted by sentiment."""
    sorted_recs = sorted(records, key=lambda r: r[sort_key], reverse=not ascending)
    sample = sorted_recs[:n]
    print(f"\n  --- Representative quotes from {label} (most {'negative' if ascending else 'positive'} first) ---")
    for r in sample:
        # Pick the most sentiment-laden response (q1 or q5 typically)
        quote = r["q1"] if len(r["q1"]) > len(r["q5"]) else r["q5"]
        # Truncate to ~200 chars
        if len(quote) > 250:
            quote = quote[:247] + "..."
        print(f"  [{r['employee_id']}, {r['position']}, {r['site']}, sent={r['sentiment_normalized']}]")
        print(f"    \"{quote}\"")

# ============================================================
# 1. Transfers vs Non-Transfers
# ============================================================
print("=" * 70)
print("1. TRANSFERS vs NON-TRANSFERS")
print("=" * 70)

transfers = [r for r in data if r["is_transfer"]]
non_transfers = [r for r in data if not r["is_transfer"]]

t_stats = group_stats(transfers, "Transfers")
nt_stats = group_stats(non_transfers, "Non-Transfers")
print_stats(t_stats)
print_stats(nt_stats)
diff = round(t_stats["mean"] - nt_stats["mean"], 3)
print(f"  Difference (transfer - non-transfer): {diff}")

# Sentiment category breakdown
print("\n  Sentiment category breakdown:")
for label, group in [("Transfers", transfers), ("Non-Transfers", non_transfers)]:
    cats = {}
    for r in group:
        cats[r["sentiment_category"]] = cats.get(r["sentiment_category"], 0) + 1
    total = len(group)
    print(f"  {label}: " + ", ".join(f"{k}={v} ({round(v/total*100,1)}%)" for k, v in sorted(cats.items())))

# ============================================================
# 2. Among Transfers: by origin_district_system_quality
# ============================================================
print("\n" + "=" * 70)
print("2. TRANSFERS BY ORIGIN DISTRICT SYSTEM QUALITY")
print("=" * 70)

origin_groups = {}
for r in transfers:
    key = r["origin_district_system_quality"] or "null"
    origin_groups.setdefault(key, []).append(r)

for key in sorted(origin_groups.keys()):
    s = group_stats(origin_groups[key], f"origin={key}")
    print_stats(s)

# Most interesting: those from worse systems vs better systems
if "worse" in origin_groups and "better" in origin_groups:
    worse_mean = statistics.mean([r["sentiment_normalized"] for r in origin_groups["worse"]])
    better_mean = statistics.mean([r["sentiment_normalized"] for r in origin_groups["better"]])
    print(f"\n  Gap (worse_origin - better_origin): {round(worse_mean - better_mean, 3)}")

# Quotes from each origin quality group
for key in ["worse", "better", "comparable"]:
    if key in origin_groups:
        print_quotes(origin_groups[key], f"origin={key} transfers", n=2, ascending=(key == "better"))

# ============================================================
# 3. Building Wing analysis
# ============================================================
print("\n" + "=" * 70)
print("3. SENTIMENT BY BUILDING WING")
print("=" * 70)

wing_groups = {}
for r in data:
    key = r["building_wing"] if r["building_wing"] else "null/Main"
    wing_groups.setdefault(key, []).append(r)

for key in sorted(wing_groups.keys()):
    s = group_stats(wing_groups[key], f"wing={key}")
    print_stats(s)

# North Wing specifically
if "North Wing" in wing_groups:
    nw = wing_groups["North Wing"]
    rest = [r for r in data if r["building_wing"] != "North Wing"]
    nw_s = group_stats(nw, "North Wing")
    rest_s = group_stats(rest, "All Others")
    print(f"\n  North Wing vs All Others gap: {round(nw_s['mean'] - rest_s['mean'], 3)}")
    print_quotes(nw, "North Wing", n=3, ascending=True)

# ============================================================
# 4. Room Type analysis
# ============================================================
print("\n" + "=" * 70)
print("4. SENTIMENT BY ROOM TYPE")
print("=" * 70)

room_groups = {}
for r in data:
    key = r["room_type"] if r["room_type"] else "null"
    room_groups.setdefault(key, []).append(r)

for key in sorted(room_groups.keys()):
    s = group_stats(room_groups[key], f"room={key}")
    print_stats(s)

# Large/Specialized vs Standard
if "Large/Specialized" in room_groups and "Standard" in room_groups:
    lg = room_groups["Large/Specialized"]
    std = room_groups["Standard"]
    lg_s = group_stats(lg, "Large/Specialized")
    std_s = group_stats(std, "Standard")
    print(f"\n  Large/Specialized vs Standard gap: {round(lg_s['mean'] - std_s['mean'], 3)}")
    print_quotes(lg, "Large/Specialized rooms", n=3, ascending=True)

# ============================================================
# 5. Interaction: Transfer x Building Wing
# ============================================================
print("\n" + "=" * 70)
print("5. INTERACTION: TRANSFER STATUS x BUILDING WING")
print("=" * 70)

for is_t, t_label in [(True, "Transfer"), (False, "Non-Transfer")]:
    for wing in sorted(wing_groups.keys()):
        sub = [r for r in data if r["is_transfer"] == is_t and (r["building_wing"] or "null/Main") == wing]
        if sub:
            s = group_stats(sub, f"{t_label} + {wing}")
            print_stats(s)

# ============================================================
# 6. Interaction: Transfer x Room Type
# ============================================================
print("\n" + "=" * 70)
print("6. INTERACTION: TRANSFER STATUS x ROOM TYPE")
print("=" * 70)

for is_t, t_label in [(True, "Transfer"), (False, "Non-Transfer")]:
    for room in sorted(room_groups.keys()):
        sub = [r for r in data if r["is_transfer"] == is_t and (r["room_type"] or "null") == room]
        if sub:
            s = group_stats(sub, f"{t_label} + {room}")
            print_stats(s)

# ============================================================
# 7. Origin quality x site (do transfers from worse systems
#    fare better at specific sites?)
# ============================================================
print("\n" + "=" * 70)
print("7. TRANSFERS FROM 'WORSE' ORIGIN: BY SITE")
print("=" * 70)

if "worse" in origin_groups:
    site_groups = {}
    for r in origin_groups["worse"]:
        site_groups.setdefault(r["site"], []).append(r)
    for site in sorted(site_groups.keys()):
        s = group_stats(site_groups[site], f"worse_origin @ {site}")
        print_stats(s)

# ============================================================
# 8. North Wing: deeper look by site and position
# ============================================================
print("\n" + "=" * 70)
print("8. NORTH WING: BY SITE AND POSITION")
print("=" * 70)

if "North Wing" in wing_groups:
    nw = wing_groups["North Wing"]
    # By site
    nw_sites = {}
    for r in nw:
        nw_sites.setdefault(r["site"], []).append(r)
    for site in sorted(nw_sites.keys()):
        s = group_stats(nw_sites[site], f"NorthWing @ {site}")
        print_stats(s)
    # By position
    nw_pos = {}
    for r in nw:
        nw_pos.setdefault(r["position"], []).append(r)
    for pos in sorted(nw_pos.keys()):
        s = group_stats(nw_pos[pos], f"NorthWing + {pos}")
        print_stats(s)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
