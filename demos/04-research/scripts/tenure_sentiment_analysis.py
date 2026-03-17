import json
import re
from collections import defaultdict
import statistics

# Load data
with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json") as f:
    data = json.load(f)

# Keywords
POSITIVE = {"great","excellent","improved","better","smooth","helpful","good","easy","appreciate","intuitive","clear"}
NEGATIVE = {"frustrated","terrible","poor","difficult","disruption","problem","issue","confusing","rushed","broken","fail","worse","struggle","complaint","disappointed"}

def sentiment_score(record):
    """Count positive - negative keyword hits across q1-q5, normalized by total hits."""
    pos = 0
    neg = 0
    for q in ["q1","q2","q3","q4","q5"]:
        text = (record.get(q) or "").lower()
        words = re.findall(r'\b\w+\b', text)
        for w in words:
            if w in POSITIVE:
                pos += 1
            elif w in NEGATIVE:
                neg += 1
    total = pos + neg
    if total == 0:
        return 0.0  # neutral
    return (pos - neg) / total  # range: -1 to +1

# Compute scores
for r in data:
    r["sentiment"] = sentiment_score(r)

scores = [r["sentiment"] for r in data]
print(f"=== OVERALL SENTIMENT ===")
print(f"N = {len(scores)}")
print(f"Mean sentiment: {statistics.mean(scores):.4f}")
print(f"Median: {statistics.median(scores):.4f}")
print(f"Std dev: {statistics.stdev(scores):.4f}")
print(f"Range: [{min(scores):.3f}, {max(scores):.3f}]")

# --- 1. Sentiment by years_at_district_band ---
print(f"\n=== SENTIMENT BY YEARS AT DISTRICT (TENURE BAND) ===")
band_order_district = ["0-3", "4-10", "11-20", "20+"]
groups = defaultdict(list)
for r in data:
    groups[r["years_at_district_band"]].append(r["sentiment"])

print(f"{'Band':<10} {'N':>5} {'Mean':>8} {'Median':>8} {'StdDev':>8}")
print("-" * 44)
for band in band_order_district:
    vals = groups[band]
    if vals:
        m = statistics.mean(vals)
        med = statistics.median(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0
        print(f"{band:<10} {len(vals):>5} {m:>8.4f} {med:>8.4f} {sd:>8.4f}")

# --- 2. Sentiment by years_in_profession_band ---
print(f"\n=== SENTIMENT BY YEARS IN PROFESSION BAND ===")
band_order_prof = ["0-5", "6-15", "16-25", "25+"]
groups2 = defaultdict(list)
for r in data:
    groups2[r["years_in_profession_band"]].append(r["sentiment"])

print(f"{'Band':<10} {'N':>5} {'Mean':>8} {'Median':>8} {'StdDev':>8}")
print("-" * 44)
for band in band_order_prof:
    vals = groups2[band]
    if vals:
        m = statistics.mean(vals)
        med = statistics.median(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0
        print(f"{band:<10} {len(vals):>5} {m:>8.4f} {med:>8.4f} {sd:>8.4f}")

# --- 3. Correlation: age vs sentiment ---
print(f"\n=== AGE-SENTIMENT CORRELATION ===")
ages = [r["age"] for r in data]
sents = [r["sentiment"] for r in data]
n = len(ages)
mean_a = statistics.mean(ages)
mean_s = statistics.mean(sents)
cov = sum((a - mean_a) * (s - mean_s) for a, s in zip(ages, sents)) / (n - 1)
sd_a = statistics.stdev(ages)
sd_s = statistics.stdev(sents)
r_val = cov / (sd_a * sd_s) if sd_a * sd_s > 0 else 0
print(f"Pearson r = {r_val:.4f}")
print(f"N = {n}")
print(f"Mean age = {mean_a:.1f}, Std dev age = {sd_a:.1f}")
print(f"Mean sentiment = {mean_s:.4f}, Std dev sentiment = {sd_s:.4f}")

# Age bins for visualization
print(f"\n  Age bin breakdown:")
age_bins = [(22,30,"22-30"),(31,40,"31-40"),(41,50,"41-50"),(51,60,"51-60"),(61,70,"61-70")]
for lo, hi, label in age_bins:
    vals = [r["sentiment"] for r in data if lo <= r["age"] <= hi]
    if vals:
        print(f"  {label}: N={len(vals):>4}, mean={statistics.mean(vals):>8.4f}")

# --- 4. Sentiment by position ---
print(f"\n=== SENTIMENT BY POSITION ===")
pos_groups = defaultdict(list)
for r in data:
    pos_groups[r["position"]].append(r["sentiment"])

print(f"{'Position':<30} {'N':>5} {'Mean':>8} {'Median':>8} {'StdDev':>8}")
print("-" * 65)
for pos in sorted(pos_groups.keys(), key=lambda p: statistics.mean(pos_groups[p])):
    vals = pos_groups[pos]
    m = statistics.mean(vals)
    med = statistics.median(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0
    print(f"{pos:<30} {len(vals):>5} {m:>8.4f} {med:>8.4f} {sd:>8.4f}")

# --- 5. Cross-tab: tenure band x position ---
print(f"\n=== CROSS-TAB: DISTRICT TENURE BAND x POSITION ===")
cross = defaultdict(list)
for r in data:
    key = (r["years_at_district_band"], r["position"])
    cross[key].append(r["sentiment"])

positions = sorted(pos_groups.keys())
header = f"{'Tenure':<10}" + "".join(f" {p[:12]:>14}" for p in positions)
print(header)
print("-" * len(header))
for band in band_order_district:
    row = f"{band:<10}"
    for pos in positions:
        vals = cross.get((band, pos), [])
        if vals:
            m = statistics.mean(vals)
            row += f" {m:>7.3f}({len(vals):>3})"
        else:
            row += f" {'---':>14}"
    print(row)

# --- Summary statistics ---
print(f"\n=== KEY TAKEAWAYS ===")
# Most/least positive tenure band
best_band = max(band_order_district, key=lambda b: statistics.mean(groups[b]) if groups[b] else -999)
worst_band = min(band_order_district, key=lambda b: statistics.mean(groups[b]) if groups[b] else 999)
print(f"Most positive district tenure band: {best_band} (mean={statistics.mean(groups[best_band]):.4f}, N={len(groups[best_band])})")
print(f"Least positive district tenure band: {worst_band} (mean={statistics.mean(groups[worst_band]):.4f}, N={len(groups[worst_band])})")

best_pos = max(pos_groups.keys(), key=lambda p: statistics.mean(pos_groups[p]))
worst_pos = min(pos_groups.keys(), key=lambda p: statistics.mean(pos_groups[p]))
print(f"Most positive position: {best_pos} (mean={statistics.mean(pos_groups[best_pos]):.4f}, N={len(pos_groups[best_pos])})")
print(f"Least positive position: {worst_pos} (mean={statistics.mean(pos_groups[worst_pos]):.4f}, N={len(pos_groups[worst_pos])})")
print(f"Age-sentiment correlation: r={r_val:.4f} ({'weak' if abs(r_val)<0.2 else 'moderate' if abs(r_val)<0.5 else 'strong'} {'positive' if r_val>0 else 'negative'})")

