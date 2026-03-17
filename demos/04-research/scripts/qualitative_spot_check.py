"""
Qualitative spot-check: randomly sample 30 responses (10 per site),
stratified by position type with a mix of tenure bands. Seed=42.
"""

import json
import random
from collections import defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json"

with open(DATA) as f:
    data = json.load(f)

random.seed(42)

# Group by site
by_site = defaultdict(list)
for r in data:
    by_site[r["site"]].append(r)

sites = sorted(by_site.keys())
print(f"Sites: {sites}")
print(f"Total records: {len(data)}")
for s in sites:
    print(f"  {s}: {len(by_site[s])} records")
print()

# For each site, stratify by position type and sample 10
# ensuring a mix of tenure bands
sampled = []
for site in sites:
    records = by_site[site]
    # Group by position
    by_pos = defaultdict(list)
    for r in records:
        by_pos[r["position"]].append(r)

    positions = sorted(by_pos.keys())
    print(f"\n{site} position breakdown:")
    for p in positions:
        print(f"  {p}: {len(by_pos[p])}")

    # Proportional sampling by position, at least 1 per position if possible
    n_target = 10
    # Calculate proportional allocation
    total = len(records)
    allocation = {}
    for p in positions:
        allocation[p] = max(1, round(len(by_pos[p]) / total * n_target))

    # Adjust to exactly 10
    while sum(allocation.values()) > n_target:
        # Remove from largest allocation
        biggest = max(allocation, key=allocation.get)
        allocation[biggest] -= 1
    while sum(allocation.values()) < n_target:
        biggest = max(positions, key=lambda p: len(by_pos[p]))
        allocation[biggest] += 1

    print(f"  Sampling allocation: {dict(allocation)}")

    site_sample = []
    for p, n in allocation.items():
        pool = by_pos[p]
        # Sort by tenure band to ensure we get a mix
        random.shuffle(pool)
        # Try to pick from different tenure bands
        by_tenure = defaultdict(list)
        for r in pool:
            by_tenure[r["years_at_district_band"]].append(r)

        picked = []
        # Round-robin through tenure bands
        bands = list(by_tenure.keys())
        random.shuffle(bands)
        idx = 0
        while len(picked) < n and any(by_tenure.values()):
            band = bands[idx % len(bands)]
            if by_tenure[band]:
                picked.append(by_tenure[band].pop())
            idx += 1
            if idx > len(bands) * 10:
                break

        site_sample.extend(picked)

    sampled.extend(site_sample)

print(f"\n{'='*100}")
print(f"SAMPLED {len(sampled)} RECORDS")
print(f"{'='*100}")

# Print demographics summary
print("\nDemographic summary of sample:")
print(f"  Sites: {dict((s, sum(1 for r in sampled if r['site']==s)) for s in sites)}")
positions_sampled = defaultdict(int)
tenure_sampled = defaultdict(int)
transfer_sampled = defaultdict(int)
for r in sampled:
    positions_sampled[r["position"]] += 1
    tenure_sampled[r["years_at_district_band"]] += 1
    transfer_sampled[r["is_transfer"]] += 1
print(f"  Positions: {dict(positions_sampled)}")
print(f"  Tenure bands: {dict(tenure_sampled)}")
print(f"  Transfers: {dict(transfer_sampled)}")

# Now print each record in full
for i, r in enumerate(sampled, 1):
    print(f"\n{'='*100}")
    print(f"RECORD {i}/{len(sampled)}: {r['employee_id']} — {r['name']}")
    print(f"{'='*100}")
    print(f"  Site: {r['site']}  |  Position: {r['position']}  |  Age: {r['age']}  |  Gender: {r['gender']}")
    print(f"  Race/Ethnicity: {r['race_ethnicity']}")
    print(f"  Years at district: {r['years_at_district']} ({r['years_at_district_band']})  |  Years in profession: {r['years_in_profession']} ({r['years_in_profession_band']})")
    print(f"  Transfer: {r['is_transfer']}  |  Origin system quality: {r['origin_district_system_quality']}")
    print(f"  Building wing: {r['building_wing']}  |  Room type: {r['room_type']}")
    print(f"  Sentiment: {r['sentiment_category']} (net={r['sentiment_net']}, normalized={r['sentiment_normalized']})")
    print()
    for q_num in range(1, 6):
        q_key = f"q{q_num}"
        print(f"  Q{q_num}: {r[q_key]}")
        print()
