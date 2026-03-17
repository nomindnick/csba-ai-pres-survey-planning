"""Per-question sentiment analysis by site and position."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sentiment import score_text

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'survey_scored.json')) as f:
    data = json.load(f)

QUESTIONS = ['q1', 'q2', 'q3', 'q4', 'q5']
Q_LABELS = {
    'q1': 'Q1: Overall experience',
    'q2': 'Q2: Training quality',
    'q3': 'Q3: Communication',
    'q4': 'Q4: System functionality',
    'q5': 'Q5: Open feedback',
}

# --- Score each question individually for every record ---
for r in data:
    for q in QUESTIONS:
        p, n, net = score_text(r[q])
        total = p + n
        r[f'{q}_net'] = net
        r[f'{q}_norm'] = round(net / total, 3) if total > 0 else 0.0

# --- 1. Mean per-question sentiment by site ---
sites = sorted(set(r['site'] for r in data))

print("=" * 90)
print("QUESTION × SITE SENTIMENT (normalized -1 to +1)")
print("=" * 90)

# Header
header = f"{'Site':<28}"
for q in QUESTIONS:
    header += f"  {q:>7}"
header += f"  {'Overall':>8}  {'N':>4}"
print(header)
print("-" * 90)

site_q_means = {}
for site in sites:
    subset = [r for r in data if r['site'] == site]
    n = len(subset)
    row = f"{site:<28}"
    site_q_means[site] = {}
    for q in QUESTIONS:
        mean = sum(r[f'{q}_norm'] for r in subset) / n
        site_q_means[site][q] = mean
        row += f"  {mean:>+7.3f}"
    overall = sum(r['sentiment_normalized'] for r in subset) / n
    site_q_means[site]['overall'] = overall
    row += f"  {overall:>+8.3f}  {n:>4}"
    print(row)

# --- 2. Biggest site gaps per question ---
print("\n" + "=" * 90)
print("SITE GAPS: Highest vs. Lowest site per question")
print("=" * 90)

for q in QUESTIONS:
    scores = {s: site_q_means[s][q] for s in sites}
    best_site = max(scores, key=scores.get)
    worst_site = min(scores, key=scores.get)
    gap = scores[best_site] - scores[worst_site]
    print(f"  {Q_LABELS[q]:<30}  Best: {best_site:<25} ({scores[best_site]:+.3f})  "
          f"Worst: {worst_site:<25} ({scores[worst_site]:+.3f})  Gap: {gap:.3f}")

# --- 3. Per-question sentiment for Food Service and Custodial ---
print("\n" + "=" * 90)
print("QUESTION × POSITION for Food Service & Custodial")
print("=" * 90)

focus_positions = ['Food Service', 'Custodial']
all_positions = sorted(set(r['position'] for r in data))

header2 = f"{'Position':<22}"
for q in QUESTIONS:
    header2 += f"  {q:>7}"
header2 += f"  {'Overall':>8}  {'N':>4}"
print(header2)
print("-" * 90)

pos_q_means = {}
for pos in all_positions:
    subset = [r for r in data if r['position'] == pos]
    n = len(subset)
    pos_q_means[pos] = {}
    row = f"{pos:<22}"
    for q in QUESTIONS:
        mean = sum(r[f'{q}_norm'] for r in subset) / n
        pos_q_means[pos][q] = mean
        row += f"  {mean:>+7.3f}"
    overall = sum(r['sentiment_normalized'] for r in subset) / n
    pos_q_means[pos]['overall'] = overall
    row += f"  {overall:>+8.3f}  {n:>4}"
    if pos in focus_positions:
        print(f"  >>> {row}")
    else:
        print(f"      {row}")

# --- 4. Check for REVERSED patterns ---
print("\n" + "=" * 90)
print("REVERSED PATTERN CHECK")
print("Positions/sites negative overall but positive on specific questions (or vice versa)")
print("=" * 90)

# Check positions
print("\nBy Position:")
for pos in all_positions:
    overall = pos_q_means[pos]['overall']
    for q in QUESTIONS:
        qmean = pos_q_means[pos][q]
        if (overall < -0.05 and qmean > 0.05) or (overall > 0.05 and qmean < -0.05):
            n = len([r for r in data if r['position'] == pos])
            print(f"  ** {pos} (n={n}): Overall={overall:+.3f} but {Q_LABELS[q]}={qmean:+.3f}")

print("\nBy Site:")
for site in sites:
    overall = site_q_means[site]['overall']
    for q in QUESTIONS:
        qmean = site_q_means[site][q]
        if (overall < -0.05 and qmean > 0.05) or (overall > 0.05 and qmean < -0.05):
            n = len([r for r in data if r['site'] == site])
            print(f"  ** {site} (n={n}): Overall={overall:+.3f} but {Q_LABELS[q]}={qmean:+.3f}")

# --- 5. Valley High deep dive: per-question by position ---
print("\n" + "=" * 90)
print("VALLEY HIGH: Per-question sentiment by position")
print("=" * 90)

vh = [r for r in data if r['site'] == 'Valley High School']
vh_positions = sorted(set(r['position'] for r in vh))

header3 = f"{'Position':<22}"
for q in QUESTIONS:
    header3 += f"  {q:>7}"
header3 += f"  {'Overall':>8}  {'N':>4}"
print(header3)
print("-" * 90)

for pos in vh_positions:
    subset = [r for r in vh if r['position'] == pos]
    n = len(subset)
    row = f"{pos:<22}"
    for q in QUESTIONS:
        mean = sum(r[f'{q}_norm'] for r in subset) / n
        row += f"  {mean:>+7.3f}"
    overall = sum(r['sentiment_normalized'] for r in subset) / n
    row += f"  {overall:>+8.3f}  {n:>4}"
    print(row)

# --- 6. Cross-site position comparison for Food Service ---
print("\n" + "=" * 90)
print("FOOD SERVICE: Per-question sentiment by site")
print("=" * 90)
fs = [r for r in data if r['position'] == 'Food Service']
fs_sites = sorted(set(r['site'] for r in fs))
header4 = f"{'Site':<28}"
for q in QUESTIONS:
    header4 += f"  {q:>7}"
header4 += f"  {'Overall':>8}  {'N':>4}"
print(header4)
print("-" * 90)
for site in fs_sites:
    subset = [r for r in fs if r['site'] == site]
    n = len(subset)
    row = f"{site:<28}"
    for q in QUESTIONS:
        mean = sum(r[f'{q}_norm'] for r in subset) / n
        row += f"  {mean:>+7.3f}"
    overall = sum(r['sentiment_normalized'] for r in subset) / n
    row += f"  {overall:>+8.3f}  {n:>4}"
    print(row)
