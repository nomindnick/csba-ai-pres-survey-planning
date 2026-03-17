#!/usr/bin/env python3
"""
Hypothesis: The extreme negativity of males at Valley High (-0.154) is explained
by their concentration in custodial/facilities roles and other operational
positions, not by gender itself.
"""

import json
import pandas as pd
from collections import Counter

pd.set_option('display.max_colwidth', 120)
pd.set_option('display.width', 140)
pd.set_option('display.max_rows', 100)

with open('/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_scored.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)
vh = df[df['site'] == 'Valley High School']

print("=" * 80)
print("1. GENDER x POSITION CROSS-TABULATION AT VALLEY HIGH")
print("=" * 80)

ct = pd.crosstab(vh['position'], vh['gender'], margins=True)
print(ct)
print()

# Percentage within gender
ct_pct = pd.crosstab(vh['position'], vh['gender'], normalize='columns').round(3) * 100
print("Percentage within each gender:")
print(ct_pct)
print()

print("=" * 80)
print("2. MALE vs FEMALE SENTIMENT WITHIN EACH POSITION AT VALLEY HIGH")
print("=" * 80)

for pos in sorted(vh['position'].unique()):
    subset = vh[vh['position'] == pos]
    by_gender = subset.groupby('gender')['sentiment_normalized'].agg(['mean', 'count', 'std']).round(3)
    print(f"\n--- {pos} ---")
    print(by_gender)

# Overall controlled comparison
print("\n\n--- SUMMARY: Position-controlled gender comparison ---")
position_gender = vh.groupby(['position', 'gender'])['sentiment_normalized'].agg(['mean', 'count']).round(3)
print(position_gender)

# Weighted average of within-position gender gaps
print("\n\n--- WEIGHTED GENDER GAP (controlling for position) ---")
gaps = []
for pos in vh['position'].unique():
    subset = vh[vh['position'] == pos]
    males = subset[subset['gender'] == 'Male']['sentiment_normalized']
    females = subset[subset['gender'] == 'Female']['sentiment_normalized']
    if len(males) > 0 and len(females) > 0:
        gap = males.mean() - females.mean()
        weight = len(subset)
        gaps.append({'position': pos, 'male_mean': males.mean(), 'female_mean': females.mean(),
                     'gap': gap, 'n_male': len(males), 'n_female': len(females), 'n_total': weight})

gaps_df = pd.DataFrame(gaps).round(3)
print(gaps_df.to_string(index=False))
total_weight = gaps_df['n_total'].sum()
weighted_gap = (gaps_df['gap'] * gaps_df['n_total']).sum() / total_weight
print(f"\nWeighted average gender gap (M - F), controlling for position: {weighted_gap:.3f}")

# Raw gap for comparison
raw_m = vh[vh['gender'] == 'Male']['sentiment_normalized'].mean()
raw_f = vh[vh['gender'] == 'Female']['sentiment_normalized'].mean()
print(f"Raw gender gap (M - F), not controlling: {raw_m - raw_f:.3f}")
print(f"  Male mean: {raw_m:.3f} (n={len(vh[vh['gender']=='Male'])})")
print(f"  Female mean: {raw_f:.3f} (n={len(vh[vh['gender']=='Female'])})")

print("\n" + "=" * 80)
print("3. MALE vs FEMALE SENTIMENT AMONG TEACHERS AT VALLEY HIGH")
print("=" * 80)

teachers = vh[vh['position'] == 'Teacher']
for g in ['Male', 'Female']:
    subset = teachers[teachers['gender'] == g]
    print(f"\n{g} Teachers at Valley High:")
    print(f"  n = {len(subset)}")
    print(f"  Mean sentiment: {subset['sentiment_normalized'].mean():.3f}")
    print(f"  Median sentiment: {subset['sentiment_normalized'].median():.3f}")
    print(f"  Std: {subset['sentiment_normalized'].std():.3f}")
    print(f"  Category distribution:")
    print(f"    {subset['sentiment_category'].value_counts().to_dict()}")

print("\n" + "=" * 80)
print("4. MALE TENURE DISTRIBUTION AT VALLEY HIGH vs OTHER SITES")
print("=" * 80)

males = df[df['gender'] == 'Male']
print("\nMale tenure (years_at_district) by site:")
for site in sorted(df['site'].unique()):
    site_males = males[males['site'] == site]
    print(f"  {site}: mean={site_males['years_at_district'].mean():.1f}, "
          f"median={site_males['years_at_district'].median():.0f}, n={len(site_males)}")

print("\nMale tenure BAND distribution at Valley High:")
vh_males = vh[vh['gender'] == 'Male']
print(vh_males['years_at_district_band'].value_counts().sort_index())

print("\nMale tenure BAND distribution at all other sites combined:")
other_males = males[males['site'] != 'Valley High School']
print(other_males['years_at_district_band'].value_counts().sort_index())

# Also check: is the male negativity at VH driven by long-tenured males?
print("\n\nValley High males by tenure band - sentiment:")
for band in sorted(vh_males['years_at_district_band'].unique()):
    subset = vh_males[vh_males['years_at_district_band'] == band]
    print(f"  {band}: mean_sentiment={subset['sentiment_normalized'].mean():.3f}, n={len(subset)}")

print("\n" + "=" * 80)
print("5. REPRESENTATIVE QUOTES FROM NEGATIVE VALLEY HIGH MALE TEACHERS")
print("=" * 80)

neg_vh_male_teachers = vh[(vh['gender'] == 'Male') &
                          (vh['position'] == 'Teacher') &
                          (vh['sentiment_normalized'] < 0)].sort_values('sentiment_normalized')

print(f"\nTotal negative male teachers at Valley High: {len(neg_vh_male_teachers)}")
print(f"Showing up to 5 most negative:\n")

for i, (_, row) in enumerate(neg_vh_male_teachers.head(5).iterrows()):
    print(f"--- Respondent {i+1}: {row['employee_id']} | sentiment={row['sentiment_normalized']:.3f} | "
          f"tenure={row['years_at_district']}yr | age={row['age']} ---")
    print(f"  Q1 (experience): {row['q1'][:300]}")
    print(f"  Q3 (communication): {row['q3'][:300]}")
    if row.get('is_transfer'):
        print(f"  [TRANSFER from system rated: {row['origin_district_system_quality']}]")
    print()

# Bonus: what are negative male teachers complaining about that female teachers aren't?
print("=" * 80)
print("BONUS: NEGATIVE FEMALE TEACHERS AT VALLEY HIGH FOR COMPARISON")
print("=" * 80)

neg_vh_female_teachers = vh[(vh['gender'] == 'Female') &
                            (vh['position'] == 'Teacher') &
                            (vh['sentiment_normalized'] < 0)].sort_values('sentiment_normalized')

print(f"\nTotal negative female teachers at Valley High: {len(neg_vh_female_teachers)}")
print(f"Showing up to 3 most negative:\n")

for i, (_, row) in enumerate(neg_vh_female_teachers.head(3).iterrows()):
    print(f"--- Respondent {i+1}: {row['employee_id']} | sentiment={row['sentiment_normalized']:.3f} | "
          f"tenure={row['years_at_district']}yr | age={row['age']} ---")
    print(f"  Q1 (experience): {row['q1'][:300]}")
    print(f"  Q3 (communication): {row['q3'][:300]}")
    print()

# Final summary
print("=" * 80)
print("STRUCTURED FINDING")
print("=" * 80)
print(f"""
HYPOTHESIS: The extreme negativity of males at Valley High (-0.154) is explained
by their concentration in custodial/facilities roles, not by gender itself.

RESULT: See analysis above. Key question — does the gender gap persist or
disappear when we control for position?

Raw gender gap at Valley High (M - F): {raw_m - raw_f:.3f}
Position-controlled weighted gender gap: {weighted_gap:.3f}

If the controlled gap is near zero, the hypothesis is SUPPORTED (position explains it).
If the controlled gap remains large, the hypothesis is REFUTED (gender effect persists
even within the same positions).
""")
