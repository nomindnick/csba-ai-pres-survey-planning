#!/usr/bin/env python3
"""
Hypothesis: The tenure-sentiment relationship differs for transfers vs non-transfers.
Specifically, long-tenured non-transfers are the most negative group, while transfers
maintain positive sentiment regardless of tenure.
"""

import json
import sys
from collections import defaultdict

# Load data
with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print()

# ============================================================
# 1. Cross-tabulate tenure band x transfer status
# ============================================================
print("=" * 70)
print("1. TENURE BAND x TRANSFER STATUS: Mean Sentiment & N")
print("=" * 70)

# Collect by (tenure_band, is_transfer)
cells = defaultdict(list)
for r in data:
    key = (r["years_at_district_band"], r["is_transfer"])
    cells[key].append(r["sentiment_normalized"])

# Get unique bands in order
band_order = ["0-3", "4-10", "11-20", "21+"]
existing_bands = sorted(set(r["years_at_district_band"] for r in data),
                        key=lambda b: band_order.index(b) if b in band_order else 99)

print(f"\n{'Tenure Band':<15} {'Non-Transfer':>20} {'Transfer':>20}")
print(f"{'':.<15} {'Mean (n)':>20} {'Mean (n)':>20}")
print("-" * 55)

for band in existing_bands:
    for is_t in [False, True]:
        vals = cells.get((band, is_t), [])
        if vals:
            mean = sum(vals) / len(vals)
            cells[(band, is_t, "mean")] = mean
            cells[(band, is_t, "n")] = len(vals)

    nt_vals = cells.get((band, False), [])
    t_vals = cells.get((band, True), [])
    nt_str = f"{sum(nt_vals)/len(nt_vals):+.3f} (n={len(nt_vals)})" if nt_vals else "--- (n=0)"
    t_str = f"{sum(t_vals)/len(t_vals):+.3f} (n={len(t_vals)})" if t_vals else "--- (n=0)"
    print(f"{band:<15} {nt_str:>20} {t_str:>20}")

# Overall by transfer status
print("-" * 55)
for is_t, label in [(False, "Non-Transfer"), (True, "Transfer")]:
    vals = [r["sentiment_normalized"] for r in data if r["is_transfer"] == is_t]
    print(f"{'Overall':<15} ", end="")
    if is_t:
        print(f"{'':>20} {sum(vals)/len(vals):+.3f} (n={len(vals)})")
    else:
        print(f"{sum(vals)/len(vals):+.3f} (n={len(vals)})")

# Overall sentiment by transfer
print("\n--- Overall Transfer vs Non-Transfer ---")
for is_t in [False, True]:
    vals = [r["sentiment_normalized"] for r in data if r["is_transfer"] == is_t]
    label = "Transfer" if is_t else "Non-Transfer"
    print(f"  {label}: mean={sum(vals)/len(vals):+.3f}, n={len(vals)}")

# ============================================================
# 2. Among transfers: origin_district_system_quality x tenure
# ============================================================
print("\n" + "=" * 70)
print("2. TRANSFERS ONLY: Origin System Quality x Tenure Band")
print("=" * 70)

transfers = [r for r in data if r["is_transfer"]]
print(f"\nTotal transfers: {len(transfers)}")

# What values does origin_district_system_quality take?
odsq_vals = set(r["origin_district_system_quality"] for r in transfers)
print(f"Origin system quality values: {sorted(v for v in odsq_vals if v is not None)}")

odsq_cells = defaultdict(list)
for r in transfers:
    odsq = r.get("origin_district_system_quality")
    if odsq is None:
        odsq = "Unknown"
    odsq_cells[(r["years_at_district_band"], odsq)].append(r["sentiment_normalized"])

odsq_labels = sorted(set(r.get("origin_district_system_quality", "Unknown") or "Unknown" for r in transfers))
header = f"{'Tenure Band':<15}" + "".join(f"{q:>20}" for q in odsq_labels)
print(f"\n{header}")
print("-" * (15 + 20 * len(odsq_labels)))

for band in existing_bands:
    row = f"{band:<15}"
    for q in odsq_labels:
        vals = odsq_cells.get((band, q), [])
        if vals:
            row += f"{sum(vals)/len(vals):+.3f} (n={len(vals):>2})     "
        else:
            row += f"{'--- (n= 0)':>20}"
    print(row)

# ============================================================
# 3. Transfer positivity boost by tenure band
# ============================================================
print("\n" + "=" * 70)
print("3. TRANSFER POSITIVITY BOOST BY TENURE BAND")
print("=" * 70)

print(f"\n{'Tenure Band':<15} {'Non-Xfer Mean':>15} {'Xfer Mean':>15} {'Boost':>10} {'Xfer n':>8} {'Non-Xfer n':>12}")
print("-" * 75)

for band in existing_bands:
    nt_vals = cells.get((band, False), [])
    t_vals = cells.get((band, True), [])
    if nt_vals and t_vals:
        nt_mean = sum(nt_vals) / len(nt_vals)
        t_mean = sum(t_vals) / len(t_vals)
        boost = t_mean - nt_mean
        print(f"{band:<15} {nt_mean:>+15.3f} {t_mean:>+15.3f} {boost:>+10.3f} {len(t_vals):>8} {len(nt_vals):>12}")
    elif nt_vals:
        nt_mean = sum(nt_vals) / len(nt_vals)
        print(f"{band:<15} {nt_mean:>+15.3f} {'N/A':>15} {'N/A':>10} {0:>8} {len(nt_vals):>12}")
    elif t_vals:
        t_mean = sum(t_vals) / len(t_vals)
        print(f"{band:<15} {'N/A':>15} {t_mean:>+15.3f} {'N/A':>10} {len(t_vals):>8} {0:>12}")

# ============================================================
# 4. Sentiment category distribution by transfer x tenure
# ============================================================
print("\n" + "=" * 70)
print("4. SENTIMENT CATEGORY DISTRIBUTION: Transfer x Tenure")
print("=" * 70)

for band in existing_bands:
    for is_t, label in [(False, "Non-Transfer"), (True, "Transfer")]:
        group = [r for r in data if r["years_at_district_band"] == band and r["is_transfer"] == is_t]
        if not group:
            continue
        cats = defaultdict(int)
        for r in group:
            cats[r["sentiment_category"]] += 1
        total = len(group)
        dist = ", ".join(f"{c}: {n} ({100*n/total:.0f}%)" for c, n in sorted(cats.items()))
        print(f"  {band} / {label} (n={total}): {dist}")

# ============================================================
# 5. Quotes from long-tenured transfers
# ============================================================
print("\n" + "=" * 70)
print("5. QUOTES FROM LONG-TENURED TRANSFERS (11+ years at district)")
print("=" * 70)

long_tenure_transfers = [r for r in data if r["is_transfer"] and r["years_at_district"] >= 11]
print(f"\nFound {len(long_tenure_transfers)} transfers with 11+ years at district")

if not long_tenure_transfers:
    # Expand to 7+
    long_tenure_transfers = [r for r in data if r["is_transfer"] and r["years_at_district"] >= 7]
    print(f"Expanding to 7+ years: found {len(long_tenure_transfers)}")

if not long_tenure_transfers:
    # Just show longest-tenured transfers
    transfers_sorted = sorted(transfers, key=lambda r: r["years_at_district"], reverse=True)
    long_tenure_transfers = transfers_sorted[:5]
    print(f"Showing top 5 longest-tenured transfers instead:")

for r in long_tenure_transfers[:8]:
    print(f"\n--- {r['name']} ({r['position']}, {r['site']}) ---")
    print(f"    Years at district: {r['years_at_district']}, Years in profession: {r['years_in_profession']}")
    print(f"    Transfer: {r['is_transfer']}, Origin quality: {r['origin_district_system_quality']}")
    print(f"    Sentiment: {r['sentiment_normalized']:+.3f} ({r['sentiment_category']})")
    print(f"    Q1: {r['q1'][:200]}...")
    print(f"    Q5: {r['q5'][:200]}...")

# ============================================================
# 6. Also show quotes from long-tenured NON-transfers for comparison
# ============================================================
print("\n" + "=" * 70)
print("6. COMPARISON: QUOTES FROM MOST NEGATIVE LONG-TENURED NON-TRANSFERS")
print("=" * 70)

long_nt = [r for r in data if not r["is_transfer"] and r["years_at_district"] >= 11]
long_nt_sorted = sorted(long_nt, key=lambda r: r["sentiment_normalized"])

for r in long_nt_sorted[:5]:
    print(f"\n--- {r['name']} ({r['position']}, {r['site']}) ---")
    print(f"    Years at district: {r['years_at_district']}, Years in profession: {r['years_in_profession']}")
    print(f"    Sentiment: {r['sentiment_normalized']:+.3f} ({r['sentiment_category']})")
    print(f"    Q1: {r['q1'][:200]}...")
    print(f"    Q5: {r['q5'][:200]}...")

# ============================================================
# 7. Statistical summary
# ============================================================
print("\n" + "=" * 70)
print("7. STATISTICAL SUMMARY")
print("=" * 70)

# Compute correlation between tenure and sentiment separately for transfers/non-transfers
for is_t, label in [(False, "Non-Transfer"), (True, "Transfer")]:
    group = [r for r in data if r["is_transfer"] == is_t]
    x = [r["years_at_district"] for r in group]
    y = [r["sentiment_normalized"] for r in group]
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
    std_x = (sum((xi - mean_x)**2 for xi in x) / n) ** 0.5
    std_y = (sum((yi - mean_y)**2 for yi in y) / n) ** 0.5
    if std_x > 0 and std_y > 0:
        corr = cov / (std_x * std_y)
    else:
        corr = 0
    print(f"\n{label} (n={n}):")
    print(f"  Tenure-sentiment correlation (Pearson r): {corr:+.3f}")
    print(f"  Mean sentiment: {mean_y:+.3f}")
    print(f"  Mean tenure: {mean_x:.1f} years")
