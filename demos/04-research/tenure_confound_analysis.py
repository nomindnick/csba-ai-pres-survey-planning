"""
Challenge: Is the tenure-sentiment correlation (r=-0.24) driven by
Food Service and Custodial staff who are both long-tenured AND
operationally disrupted? Or is it a robust effect across positions?
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict

with open("/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json") as f:
    data = json.load(f)

# Extract arrays
all_tenure = np.array([r["years_at_district"] for r in data])
all_sentiment = np.array([r["sentiment_normalized"] for r in data])
all_profession = np.array([r["years_in_profession"] for r in data])
all_positions = [r["position"] for r in data]

print("=" * 70)
print("TENURE-SENTIMENT CONFOUND ANALYSIS")
print("=" * 70)

# 1. Baseline: all staff
r_all, p_all = stats.pearsonr(all_tenure, all_sentiment)
print(f"\n1. BASELINE — ALL STAFF (n={len(data)})")
print(f"   r = {r_all:.4f}, p = {p_all:.6f}")

# 2. Excluding Food Service and Custodial
mask_no_ops = np.array([r["position"] not in ("Food Service", "Custodial") for r in data])
r_no_ops, p_no_ops = stats.pearsonr(all_tenure[mask_no_ops], all_sentiment[mask_no_ops])
n_no_ops = mask_no_ops.sum()
print(f"\n2. EXCLUDING Food Service + Custodial (n={n_no_ops})")
print(f"   r = {r_no_ops:.4f}, p = {p_no_ops:.6f}")
pct_change = ((r_no_ops - r_all) / abs(r_all)) * 100
print(f"   Change from baseline: {pct_change:+.1f}%")

# 3. Teachers only
mask_teach = np.array([r["position"] == "Teacher" for r in data])
r_teach, p_teach = stats.pearsonr(all_tenure[mask_teach], all_sentiment[mask_teach])
n_teach = mask_teach.sum()
print(f"\n3. TEACHERS ONLY (n={n_teach})")
print(f"   r = {r_teach:.4f}, p = {p_teach:.6f}")

# 4. By position
print(f"\n4. TENURE-SENTIMENT CORRELATION BY POSITION")
print(f"   {'Position':<25} {'n':>5}  {'r':>8}  {'p':>10}  {'Mean Tenure':>12}  {'Mean Sent':>10}")
print(f"   {'-'*25} {'---':>5}  {'---':>8}  {'---':>10}  {'---':>12}  {'---':>10}")

position_stats = defaultdict(list)
for r in data:
    position_stats[r["position"]].append(r)

pos_results = []
for pos in sorted(position_stats.keys(), key=lambda p: -len(position_stats[p])):
    records = position_stats[pos]
    n = len(records)
    t = np.array([r["years_at_district"] for r in records])
    s = np.array([r["sentiment_normalized"] for r in records])
    mean_t = t.mean()
    mean_s = s.mean()
    if n >= 5:
        r_pos, p_pos = stats.pearsonr(t, s)
        pos_results.append((pos, n, r_pos, p_pos, mean_t, mean_s))
        sig = "*" if p_pos < 0.05 else ""
        print(f"   {pos:<25} {n:>5}  {r_pos:>8.4f}  {p_pos:>10.6f}{sig}  {mean_t:>12.1f}  {mean_s:>10.3f}")
    else:
        pos_results.append((pos, n, None, None, mean_t, mean_s))
        print(f"   {pos:<25} {n:>5}  {'(n<5)':>8}  {'':>10}  {mean_t:>12.1f}  {mean_s:>10.3f}")

# 5. years_in_profession vs years_at_district — partial correlation
print(f"\n5. PROFESSION TENURE vs DISTRICT TENURE — DISENTANGLING")
print(f"   a) Simple correlations:")
r_prof, p_prof = stats.pearsonr(all_profession, all_sentiment)
print(f"      years_in_profession ~ sentiment: r = {r_prof:.4f}, p = {p_prof:.6f}")
print(f"      years_at_district   ~ sentiment: r = {r_all:.4f}, p = {p_all:.6f}")

# Correlation between the two tenure measures
r_tt, _ = stats.pearsonr(all_tenure, all_profession)
print(f"      years_at_district ~ years_in_profession: r = {r_tt:.4f}")

# Partial correlation: sentiment ~ years_in_profession controlling for years_at_district
# Using regression residuals approach
from numpy.polynomial.polynomial import polyfit

# Residualize profession years on district years
slope_pd, intercept_pd = np.polyfit(all_tenure, all_profession, 1)
resid_prof = all_profession - (slope_pd * all_tenure + intercept_pd)

# Residualize sentiment on district years
slope_sd, intercept_sd = np.polyfit(all_tenure, all_sentiment, 1)
resid_sent = all_sentiment - (slope_sd * all_tenure + intercept_sd)

r_partial_prof, p_partial_prof = stats.pearsonr(resid_prof, resid_sent)
print(f"\n   b) Partial correlation: sentiment ~ years_in_profession | years_at_district")
print(f"      r_partial = {r_partial_prof:.4f}, p = {p_partial_prof:.6f}")

# Partial correlation: sentiment ~ years_at_district controlling for years_in_profession
slope_dp, intercept_dp = np.polyfit(all_profession, all_tenure, 1)
resid_dist = all_tenure - (slope_dp * all_profession + intercept_dp)

slope_sp, intercept_sp = np.polyfit(all_profession, all_sentiment, 1)
resid_sent2 = all_sentiment - (slope_sp * all_profession + intercept_sp)

r_partial_dist, p_partial_dist = stats.pearsonr(resid_dist, resid_sent2)
print(f"   c) Partial correlation: sentiment ~ years_at_district | years_in_profession")
print(f"      r_partial = {r_partial_dist:.4f}, p = {p_partial_dist:.6f}")

# 6. Multiple regression
from numpy.linalg import lstsq
X = np.column_stack([np.ones(len(data)), all_tenure, all_profession])
betas, residuals, rank, sv = lstsq(X, all_sentiment, rcond=None)
print(f"\n   d) Multiple regression: sentiment ~ district_years + profession_years")
print(f"      Intercept:          {betas[0]:>8.4f}")
print(f"      years_at_district:  {betas[1]:>8.4f}")
print(f"      years_in_profession:{betas[2]:>8.4f}")

# Calculate R-squared
y_pred = X @ betas
ss_res = np.sum((all_sentiment - y_pred) ** 2)
ss_tot = np.sum((all_sentiment - all_sentiment.mean()) ** 2)
r2 = 1 - ss_res / ss_tot
print(f"      R-squared:          {r2:.4f}")

# 7. Tenure band breakdown — operational vs non-operational
print(f"\n6. TENURE BANDS: OPERATIONAL vs NON-OPERATIONAL ROLES")
print(f"   {'Band':<12} {'Ops n':>6} {'Ops Mean':>9} {'Non-Ops n':>10} {'Non-Ops Mean':>13} {'Gap':>8}")
print(f"   {'-'*12} {'---':>6} {'---':>9} {'---':>10} {'---':>13} {'---':>8}")

ops_roles = {"Food Service", "Custodial"}
bands = ["0-3", "4-10", "11-20", "21+"]
for band in bands:
    ops = [r["sentiment_normalized"] for r in data if r["years_at_district_band"] == band and r["position"] in ops_roles]
    non_ops = [r["sentiment_normalized"] for r in data if r["years_at_district_band"] == band and r["position"] not in ops_roles]
    ops_mean = np.mean(ops) if ops else float('nan')
    non_ops_mean = np.mean(non_ops) if non_ops else float('nan')
    gap = ops_mean - non_ops_mean if ops and non_ops else float('nan')
    print(f"   {band:<12} {len(ops):>6} {ops_mean:>9.3f} {len(non_ops):>10} {non_ops_mean:>13.3f} {gap:>8.3f}")

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
print(f"""
Baseline correlation (all staff):           r = {r_all:.4f}
Excluding Food Service + Custodial:         r = {r_no_ops:.4f} ({pct_change:+.1f}%)
Teachers only:                              r = {r_teach:.4f}

The hypothesis that operational roles DRIVE the tenure effect is:""")

if abs(r_no_ops) < abs(r_all) * 0.5:
    print("  >>> SUPPORTED — removing operational roles substantially weakens the effect")
elif abs(r_no_ops) < abs(r_all) * 0.75:
    print("  >>> PARTIALLY SUPPORTED — operational roles amplify but don't fully explain the effect")
else:
    print("  >>> REFUTED — the tenure effect persists even without operational roles")

print(f"""
Partial correlations suggest:
  - District tenure (controlling for profession): r = {r_partial_dist:.4f}
  - Profession tenure (controlling for district):  r = {r_partial_prof:.4f}
""")
if abs(r_partial_dist) > abs(r_partial_prof):
    print("  >>> District-specific tenure is the stronger predictor — this is about")
    print("      familiarity with THIS system/district, not general career length.")
elif abs(r_partial_prof) > abs(r_partial_dist):
    print("  >>> Profession tenure is the stronger predictor — this is about general")
    print("      career experience/change fatigue, not district-specific attachment.")
else:
    print("  >>> Both contribute roughly equally.")
