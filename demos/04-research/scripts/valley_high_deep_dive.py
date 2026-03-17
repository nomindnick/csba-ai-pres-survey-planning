"""
Hypothesis: Valley High's lower sentiment is broad-based across most staff,
not just driven by custodial/admin outliers.
"""
import json
import statistics

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

# ── 1. Valley High: mean sentiment by every position type ──────────────
print("=" * 70)
print("1. VALLEY HIGH — MEAN SENTIMENT BY POSITION")
print("=" * 70)

vh = [r for r in data if r["site"] == "Valley High"]
if not vh:
    sites = sorted(set(r["site"] for r in data))
    print(f"No 'Valley High' found. Sites: {sites}")
    vh = [r for r in data if "valley" in r["site"].lower() or "high" in r["site"].lower()]
    if vh:
        site_name = vh[0]["site"]
        print(f"Using '{site_name}' instead")
    else:
        print("No matching site found!")
        exit()
else:
    site_name = "Valley High"

vh = [r for r in data if r["site"] == site_name]

positions_vh = {}
for r in vh:
    pos = r["position"]
    positions_vh.setdefault(pos, []).append(r["sentiment_normalized"])

print(f"\n{'Position':<30} {'n':>5} {'Mean':>8} {'StdDev':>8} {'Min':>8} {'Max':>8}")
print("-" * 70)
for pos in sorted(positions_vh, key=lambda p: statistics.mean(positions_vh[p])):
    vals = positions_vh[pos]
    mean = statistics.mean(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0
    print(f"{pos:<30} {len(vals):>5} {mean:>8.3f} {sd:>8.3f} {min(vals):>8.3f} {max(vals):>8.3f}")

# ── 2. Compare each VH position to same position at other sites ────────
print("\n" + "=" * 70)
print("2. VALLEY HIGH vs. OTHER SITES — BY POSITION")
print("=" * 70)

other = [r for r in data if r["site"] != site_name]
positions_other = {}
for r in other:
    pos = r["position"]
    positions_other.setdefault(pos, []).append(r["sentiment_normalized"])

site_pos = {}
for r in data:
    key = (r["site"], r["position"])
    site_pos.setdefault(key, []).append(r["sentiment_normalized"])

all_positions = sorted(set(list(positions_vh.keys()) + list(positions_other.keys())))
sites = sorted(set(r["site"] for r in data))

print(f"\n{'Position':<25}", end="")
for s in sites:
    print(f" {s[:15]:>17}", end="")
print()
print("-" * (25 + 17 * len(sites)))

for pos in all_positions:
    print(f"{pos:<25}", end="")
    for s in sites:
        vals = site_pos.get((s, pos), [])
        if vals:
            mean = statistics.mean(vals)
            print(f"  {mean:>6.3f} (n={len(vals):<3})", end="")
        else:
            print(f"  {'---':>15}", end="")
    print()

print(f"\n{'Position':<25} {'VH Mean':>8} {'Others Mean':>12} {'Gap':>8} {'VH n':>6} {'Others n':>8}")
print("-" * 70)
for pos in all_positions:
    vh_vals = positions_vh.get(pos, [])
    ot_vals = positions_other.get(pos, [])
    if vh_vals and ot_vals:
        vh_m = statistics.mean(vh_vals)
        ot_m = statistics.mean(ot_vals)
        gap = vh_m - ot_m
        print(f"{pos:<25} {vh_m:>8.3f} {ot_m:>12.3f} {gap:>+8.3f} {len(vh_vals):>6} {len(ot_vals):>8}")

# ── 3. VH sentiment excluding custodial and admin ──────────────────────
print("\n" + "=" * 70)
print("3. VALLEY HIGH SENTIMENT — WITH vs. WITHOUT CUSTODIAL & ADMIN")
print("=" * 70)

vh_all_vals = [r["sentiment_normalized"] for r in vh]
print(f"\nAll VH positions: {sorted(set(r['position'] for r in vh))}")
print(f"\nAll VH (n={len(vh_all_vals)}):  mean = {statistics.mean(vh_all_vals):.3f}")

exclude_positions = set()
for pos in set(r["position"] for r in vh):
    pl = pos.lower()
    if any(x in pl for x in ["custod", "admin", "office", "clerical", "secretary"]):
        exclude_positions.add(pos)

print(f"Excluding positions: {exclude_positions}")
vh_excl = [r["sentiment_normalized"] for r in vh if r["position"] not in exclude_positions]
print(f"VH excl. custodial/admin (n={len(vh_excl)}): mean = {statistics.mean(vh_excl):.3f}")

other_all = [r["sentiment_normalized"] for r in other]
other_excl = [r["sentiment_normalized"] for r in other if r["position"] not in exclude_positions]
print(f"\nOther sites all (n={len(other_all)}): mean = {statistics.mean(other_all):.3f}")
print(f"Other sites excl. (n={len(other_excl)}): mean = {statistics.mean(other_excl):.3f}")

vh_gap_all = statistics.mean(vh_all_vals) - statistics.mean(other_all)
vh_gap_excl = statistics.mean(vh_excl) - statistics.mean(other_excl)
print(f"\nGap (VH - Others), all staff:        {vh_gap_all:+.3f}")
print(f"Gap (VH - Others), excl. cust/admin: {vh_gap_excl:+.3f}")

# ── 4. Building wing and room type at Valley High ─────────────────────
print("\n" + "=" * 70)
print("4. VALLEY HIGH — BUILDING WING & ROOM TYPE")
print("=" * 70)

wing_counts = {}
for r in vh:
    w = r.get("building_wing") or "null"
    wing_counts.setdefault(w, []).append(r["sentiment_normalized"])

print(f"\n{'Building Wing':<25} {'n':>5} {'Mean Sent':>10}")
print("-" * 42)
for w in sorted(wing_counts, key=lambda x: statistics.mean(wing_counts[x])):
    vals = wing_counts[w]
    print(f"{w:<25} {len(vals):>5} {statistics.mean(vals):>10.3f}")

room_counts = {}
for r in vh:
    rt = r.get("room_type") or "null"
    room_counts.setdefault(rt, []).append(r["sentiment_normalized"])

print(f"\n{'Room Type':<25} {'n':>5} {'Mean Sent':>10}")
print("-" * 42)
for rt in sorted(room_counts, key=lambda x: statistics.mean(room_counts[x])):
    vals = room_counts[rt]
    print(f"{rt:<25} {len(vals):>5} {statistics.mean(vals):>10.3f}")

print(f"\nRoom type breakdown by site:")
print(f"{'Room Type':<20}", end="")
for s in sites:
    print(f" {s[:15]:>17}", end="")
print()
print("-" * (20 + 17 * len(sites)))

all_room_types = sorted(set(r.get("room_type") or "null" for r in data))
for rt in all_room_types:
    print(f"{rt:<20}", end="")
    for s in sites:
        site_rt = [r["sentiment_normalized"] for r in data if r["site"] == s and (r.get("room_type") or "null") == rt]
        if site_rt:
            print(f"  {statistics.mean(site_rt):>6.3f} (n={len(site_rt):<3})", end="")
        else:
            print(f"  {'---':>15}", end="")
    print()

# ── 5. Representative negative quotes from VH teachers ────────────────
print("\n" + "=" * 70)
print("5. REPRESENTATIVE NEGATIVE QUOTES — VALLEY HIGH TEACHERS")
print("=" * 70)

vh_teachers = [r for r in vh if r["position"] == "Teacher"]
vh_teachers_sorted = sorted(vh_teachers, key=lambda r: r["sentiment_normalized"])

print(f"\nTotal VH teachers: {len(vh_teachers)}")
print(f"VH teacher mean sentiment: {statistics.mean([t['sentiment_normalized'] for t in vh_teachers]):.3f}")

for i, r in enumerate(vh_teachers_sorted[:5]):
    print(f"\n--- Teacher {i+1}: {r['name']} | sentiment={r['sentiment_normalized']:.3f} | "
          f"tenure={r['years_at_district']}yr | age={r['age']} | wing={r.get('building_wing')} | room={r.get('room_type')} ---")
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        text = r.get(q, "")
        if text and len(text) > 20:
            preview = text[:300] + ("..." if len(text) > 300 else "")
            print(f"  {q}: {preview}")

# ── Summary ────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

district_mean = statistics.mean(r["sentiment_normalized"] for r in data)
below_count = sum(1 for pos in positions_vh
                  if statistics.mean(positions_vh[pos]) < district_mean)
print(f"\nDistrict-wide mean sentiment: {district_mean:.3f}")
print(f"Valley High positions below district average: {below_count}/{len(positions_vh)}")
print(f"Valley High overall mean: {statistics.mean(vh_all_vals):.3f}")
