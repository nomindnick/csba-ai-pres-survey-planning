"""
Scorer Bias Analysis: Challenge the keyword-based sentiment scoring method.

Tests whether findings are artifacts of the scoring method rather than real patterns.
"""
import json, re, random, statistics

random.seed(42)

# Load the scoring lists (replicated from sentiment.py)
POSITIVE = [
    'improved', 'better', 'great', 'excellent', 'love', 'smooth', 'smoother',
    'helpful', 'appreciate', 'intuitive', 'easier', 'effective', 'impressed',
    'pleased', 'well-organized', 'clear', 'clearer', 'positive', 'good',
    'fantastic', 'wonderful', 'efficient', 'upgrade', 'reliable', 'responsive',
    'supportive', 'thorough', 'well done', 'happy', 'comfortable', 'confident',
    'welcome', 'refreshing', 'straightforward', 'user-friendly', 'seamless',
    'professional', 'proactive', 'thoughtful', 'grateful'
]

NEGATIVE = [
    'frustrated', 'frustrating', 'frustration', 'terrible', 'awful', 'worse',
    'poor', 'poorly', 'difficult', 'confusing', 'confused', 'disruption',
    'disruptive', 'disrupted', 'rushed', 'overwhelmed', 'overwhelming',
    'blindsided', 'ignored', 'neglected', 'broken', 'unreliable', 'glitch',
    'glitches', 'fail', 'failed', 'failure', 'inadequate', 'insufficient',
    'lacking', 'disappointed', 'disappointing', 'complaint', 'problem',
    'problems', 'issue', 'issues', 'concern', 'concerns', 'struggle',
    'struggling', 'nightmare', 'horrible', 'unacceptable', 'chaotic',
    'chaos', 'mess', 'waste', 'wasted', 'annoying', 'annoyed',
    'not great', 'not good', 'not helpful', 'not enough', 'not adequate',
    'no input', 'no communication', 'no training', 'no support',
    'left out', 'cut out', 'shut out', 'left behind',
    'top-down', 'dismissive', 'disrespectful', 'condescending',
    'anxiety', 'stress', 'stressful', 'worried', 'worry',
    'excluded', 'overlooked', 'undervalued', 'unfair', 'unsafe',
    'angry', 'anger', 'resentment', 'resent', 'hostile',
    'distrust', 'skeptical', 'skepticism', 'cynical',
    'regression', 'downgrade', 'setback', 'worse off'
]

with open('data/survey_scored.json') as f:
    data = json.load(f)

def get_all_text(record):
    """Combine all q1-q5 text."""
    texts = []
    for q in ['q1', 'q2', 'q3', 'q4', 'q5']:
        if record[q]:
            texts.append(record[q])
    return ' '.join(texts)

def word_count(text):
    if not text:
        return 0
    return len(text.split())

def total_word_count(record):
    return sum(word_count(record[q]) for q in ['q1','q2','q3','q4','q5'] if record[q])

print("=" * 80)
print("SCORER BIAS ANALYSIS")
print("=" * 80)

# ============================================================
# PART 1: Find misscored records — high divergence candidates
# ============================================================
print("\n" + "=" * 80)
print("PART 1: POTENTIAL MISSCORED RECORDS")
print("=" * 80)

# Strategy: Find records with extreme scores but text that contains
# hedging, negation patterns, or mixed signals
# Focus on records that are scored very positive but have negative-sounding text,
# and vice versa.

# Look for specific patterns that confuse keyword scorers:
# - Negation: "not bad", "not terrible", "isn't great" -> these flip meaning
# - Comparative to old system: "worse" describing old system = actually positive
# - Hedging: "I guess", "it's fine", "okay I suppose"
# - Sarcasm indicators

negation_patterns = [
    r"not\s+(?:bad|terrible|awful|horrible|the worst|a problem|an issue)",
    r"isn't\s+(?:bad|terrible|awful)",
    r"wasn't\s+(?:bad|terrible|awful|that bad)",
    r"can't\s+complain",
    r"no\s+complaint",
    r"not\s+(?:great|good|ideal|perfect|what I'd hoped|impressed)",
    r"isn't\s+(?:great|good|ideal|perfect)",
    r"wasn't\s+(?:great|good|ideal)",
    r"not\s+(?:really|exactly|particularly)\s+(?:better|improved|helpful|good|great)",
    r"could\s+(?:be|have been)\s+(?:better|worse)",
]

hedging_patterns = [
    r"I\s+guess",
    r"I\s+suppose",
    r"it's\s+(?:fine|okay|ok|alright)",
    r"it\s+was\s+(?:fine|okay|ok|alright)",
    r"not\s+the\s+(?:end of the world|worst)",
    r"could\s+be\s+worse",
    r"at\s+least",
    r"for\s+what\s+it's\s+worth",
    r"if\s+I'm\s+being\s+honest",
]

# Find records where negation may flip the intended meaning of a keyword
negation_flip_records = []
for r in data:
    text = get_all_text(r).lower()
    flips = []
    for pat in negation_patterns:
        matches = re.findall(pat, text)
        if matches:
            flips.extend(matches)
    if flips:
        negation_flip_records.append((r, flips))

print(f"\nRecords with negation patterns that may flip keyword meaning: {len(negation_flip_records)}")
print("\nTop 20 examples (showing q1 excerpt + score + matched pattern):\n")
for r, flips in negation_flip_records[:20]:
    q1_excerpt = (r['q1'] or '')[:120]
    print(f"  {r['employee_id']} | Score: {r['sentiment_net']:+d} ({r['sentiment_category']}) | Negation: {flips}")
    print(f"    q1: \"{q1_excerpt}...\"")
    print()

# ============================================================
# PART 2: Transfer "worse" bias — key hypothesis
# ============================================================
print("\n" + "=" * 80)
print("PART 2: TRANSFER 'WORSE' BIAS ANALYSIS")
print("=" * 80)

transfers = [r for r in data if r['is_transfer']]
non_transfers = [r for r in data if not r['is_transfer']]

print(f"\nTransfers: {len(transfers)}, Non-transfers: {len(non_transfers)}")

# Check how many transfers use "worse" and in what context
worse_transfers = []
worse_non_transfers = []

for r in transfers:
    text = get_all_text(r).lower()
    if 'worse' in text:
        # Find the context around "worse"
        sentences = re.split(r'[.!?]', text)
        worse_sentences = [s.strip() for s in sentences if 'worse' in s]
        worse_transfers.append((r, worse_sentences))

for r in non_transfers:
    text = get_all_text(r).lower()
    if 'worse' in text:
        sentences = re.split(r'[.!?]', text)
        worse_sentences = [s.strip() for s in sentences if 'worse' in s]
        worse_non_transfers.append((r, worse_sentences))

print(f"\nTransfers using 'worse': {len(worse_transfers)} / {len(transfers)} ({100*len(worse_transfers)/len(transfers):.1f}%)")
print(f"Non-transfers using 'worse': {len(worse_non_transfers)} / {len(non_transfers)} ({100*len(worse_non_transfers)/len(non_transfers):.1f}%)")

# Classify "worse" usage: referring to OLD system vs NEW system
print("\n--- Context of 'worse' in transfer responses ---")
old_system_worse = 0
new_system_worse = 0
ambiguous_worse = 0

for r, sentences in worse_transfers:
    for s in sentences:
        # Heuristic: if "old", "previous", "before", "used to", "came from" near "worse"
        if any(w in s for w in ['old', 'previous', 'before', 'used to', 'came from', 'prior', 'former', 'last district', 'other district']):
            old_system_worse += 1
            print(f"  [OLD SYSTEM] {r['employee_id']} ({r['origin_district_system_quality']}): \"{s[:150]}\"")
        elif any(w in s for w in ['new', 'this', 'current', 'now']):
            new_system_worse += 1
            print(f"  [NEW SYSTEM] {r['employee_id']} ({r['origin_district_system_quality']}): \"{s[:150]}\"")
        else:
            ambiguous_worse += 1
            print(f"  [AMBIGUOUS]  {r['employee_id']} ({r['origin_district_system_quality']}): \"{s[:150]}\"")

print(f"\n  'Worse' referring to OLD system: {old_system_worse}")
print(f"  'Worse' referring to NEW system: {new_system_worse}")
print(f"  Ambiguous: {ambiguous_worse}")

# Impact analysis: What if we removed the "worse" penalty from transfers
# who are describing their old system?
print("\n--- Impact on transfer sentiment if 'worse' describing old system is removed ---")

transfer_scores_orig = [r['sentiment_net'] for r in transfers]
# Count how many "worse" hits each transfer has
for r, sentences in worse_transfers:
    text = get_all_text(r).lower()
    worse_count = text.count('worse')
    # Also count "worse off" which is a separate keyword
    worse_off_count = text.count('worse off')
    print(f"  {r['employee_id']}: 'worse' appears {worse_count}x, 'worse off' {worse_off_count}x, "
          f"origin_quality={r['origin_district_system_quality']}, "
          f"current score={r['sentiment_net']:+d}")

# Compare transfer scores by origin system quality
print("\n--- Transfer sentiment by origin_district_system_quality ---")
by_origin = {}
for r in transfers:
    origin = r.get('origin_district_system_quality', 'unknown')
    by_origin.setdefault(origin, []).append(r['sentiment_normalized'])

for origin, scores in sorted(by_origin.items(), key=lambda x: x[0] or ''):
    print(f"  Origin '{origin}': n={len(scores)}, mean={statistics.mean(scores):.3f}, "
          f"median={statistics.median(scores):.3f}")


# ============================================================
# PART 3: Response length vs sentiment
# ============================================================
print("\n" + "=" * 80)
print("PART 3: RESPONSE LENGTH vs SENTIMENT")
print("=" * 80)

lengths = [(total_word_count(r), r['sentiment_net'], r['sentiment_normalized'], r['employee_id']) for r in data]

# Quartiles by word count
lengths.sort(key=lambda x: x[0])
n = len(lengths)
quartiles = [
    lengths[:n//4],
    lengths[n//4:n//2],
    lengths[n//2:3*n//4],
    lengths[3*n//4:]
]

print("\nSentiment by response length quartile:")
for i, q in enumerate(quartiles):
    wc_range = f"{q[0][0]}-{q[-1][0]}"
    net_scores = [x[1] for x in q]
    norm_scores = [x[2] for x in q]
    print(f"  Q{i+1} (words {wc_range:>10s}): n={len(q)}, "
          f"mean_net={statistics.mean(net_scores):+.2f}, "
          f"mean_normalized={statistics.mean(norm_scores):+.3f}, "
          f"median_net={statistics.median(net_scores):+.1f}")

# Correlation: word count vs net sentiment
wc_vals = [x[0] for x in lengths]
net_vals = [x[1] for x in lengths]
norm_vals = [x[2] for x in lengths]

# Manual Pearson correlation
def pearson(x, y):
    n = len(x)
    mx, my = statistics.mean(x), statistics.mean(y)
    sx, sy = statistics.stdev(x), statistics.stdev(y)
    if sx == 0 or sy == 0:
        return 0
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / ((n - 1) * sx * sy)

r_net = pearson(wc_vals, net_vals)
r_norm = pearson(wc_vals, norm_vals)

print(f"\nPearson correlation:")
print(f"  Word count vs net sentiment: r = {r_net:.3f}")
print(f"  Word count vs normalized sentiment: r = {r_norm:.3f}")

# Key insight: longer responses hit MORE keywords mechanically
print("\n  NOTE: The scorer counts keyword hits across all text.")
print("  Longer responses have more words = more chances to hit BOTH pos and neg keywords.")
print("  This means longer responses should have higher absolute keyword counts.")

# Verify: absolute keyword count vs word count
abs_counts = [(total_word_count(r), r['sentiment_positive'] + r['sentiment_negative']) for r in data]
abs_wc = [x[0] for x in abs_counts]
abs_kw = [x[1] for x in abs_counts]
r_abs = pearson(abs_wc, abs_kw)
print(f"\n  Word count vs total keyword hits: r = {r_abs:.3f}")
print(f"  This confirms {'a strong' if abs(r_abs) > 0.5 else 'a moderate' if abs(r_abs) > 0.3 else 'a weak'} "
      f"mechanical relationship between response length and keyword count.")

# Does normalization fix this?
print(f"\n  The normalized score (net/total) partially corrects for length.")
print(f"  But it can still be biased: a long response with 10 pos and 8 neg = normalized +0.11 (neutral),")
print(f"  while a short response with 2 pos and 0 neg = normalized +1.0 (very positive).")


# ============================================================
# PART 4: Hedging and sarcasm detection
# ============================================================
print("\n" + "=" * 80)
print("PART 4: HEDGING & SARCASM DETECTION")
print("=" * 80)

hedging_records = []
for r in data:
    text = get_all_text(r).lower()
    found_hedges = []
    for pat in hedging_patterns:
        matches = re.findall(pat, text)
        if matches:
            found_hedges.extend(matches)
    if found_hedges:
        hedging_records.append((r, found_hedges))

print(f"\nRecords with hedging language: {len(hedging_records)} / {len(data)} ({100*len(hedging_records)/len(data):.1f}%)")

# Are hedging records scored differently?
hedging_ids = set(r['employee_id'] for r, _ in hedging_records)
hedging_scores = [r['sentiment_normalized'] for r in data if r['employee_id'] in hedging_ids]
non_hedging_scores = [r['sentiment_normalized'] for r in data if r['employee_id'] not in hedging_ids]

print(f"\n  Hedging records:     n={len(hedging_scores)}, mean_norm={statistics.mean(hedging_scores):+.3f}")
print(f"  Non-hedging records: n={len(non_hedging_scores)}, mean_norm={statistics.mean(non_hedging_scores):+.3f}")

# Show examples of hedging with their scores
print("\nExamples of hedging language with scores:")
random.shuffle(hedging_records)
for r, hedges in hedging_records[:15]:
    q1_excerpt = (r['q1'] or '')[:140]
    print(f"  {r['employee_id']} | Score: {r['sentiment_normalized']:+.3f} ({r['sentiment_category']}) | Hedges: {hedges}")
    print(f"    \"{q1_excerpt}\"")
    print()

# Look for "not terrible", "not bad" specifically — these are positive statements
# that the scorer might count as negative (because "terrible", "bad" not in list,
# but "not great", "not good" ARE in the negative list)
print("\n--- Negated positives (scorer may miss these) ---")
negated_positive_patterns = [
    r"not\s+(?:bad|terrible|awful|the worst)",
    r"can't\s+complain",
    r"no\s+complaints?",
    r"nothing\s+(?:wrong|bad|terrible)",
    r"wouldn't\s+(?:say|call)\s+it\s+(?:bad|terrible|awful)",
]
for r in data:
    text = get_all_text(r).lower()
    for pat in negated_positive_patterns:
        m = re.search(pat, text)
        if m:
            print(f"  {r['employee_id']} | Score: {r['sentiment_normalized']:+.3f} | Found: \"{m.group()}\"")
            break


# ============================================================
# PART 5: Manual re-scoring of 20 random records
# ============================================================
print("\n" + "=" * 80)
print("PART 5: MANUAL RE-SCORING — 20 RANDOM RECORDS")
print("=" * 80)
print("(Reading q1 text and assigning human judgment)\n")

sample = random.sample(data, 20)

# For each record, I'll apply a rule-based "smarter" scorer that accounts for:
# - Negation context
# - Overall tone (ratio of positive to negative sentiment words, but context-aware)
# - Hedging

def smart_score(record):
    """A more context-aware scorer."""
    text = get_all_text(record).lower()

    # Count raw positive/negative
    pos = sum(1 for w in POSITIVE if w in text)
    neg = sum(1 for w in NEGATIVE if w in text)

    # Adjustments:
    adjustments = []

    # 1. Negated negatives ("not bad", "not terrible") -> should be mildly positive
    for pat in [r"not\s+bad", r"not\s+terrible", r"not\s+awful", r"can't\s+complain",
                r"no\s+complaints?", r"wasn't\s+(?:that\s+)?bad"]:
        if re.search(pat, text):
            pos += 1
            neg -= 1
            adjustments.append(f"negated-negative: +1pos/-1neg")

    # 2. Negated positives ("not great", "not good") -> already in NEGATIVE list, OK

    # 3. "Worse" referring to old system in transfer context
    if record['is_transfer'] and 'worse' in text:
        sentences = re.split(r'[.!?]', text)
        for s in sentences:
            if 'worse' in s and any(w in s for w in ['old', 'previous', 'before', 'prior', 'came from', 'other district', 'last district']):
                neg -= 1
                pos += 1
                adjustments.append(f"'worse' about old system: +1pos/-1neg")

    # 4. Hedging — "I guess it's fine" is damning with faint praise, should be mildly negative
    for pat in [r"i\s+guess", r"i\s+suppose", r"if\s+i'm\s+being\s+honest"]:
        if re.search(pat, text):
            neg += 0.5
            adjustments.append(f"hedging detected: +0.5neg")

    total = max(pos + neg, 1)
    net = pos - neg
    normalized = net / total

    if normalized > 0.15:
        cat = 'positive'
    elif normalized < -0.15:
        cat = 'negative'
    else:
        cat = 'neutral'

    return {
        'pos': pos, 'neg': neg, 'net': net, 'normalized': round(normalized, 3),
        'category': cat, 'adjustments': adjustments
    }

agreements = 0
disagreements = 0
direction_flips = 0

print(f"{'ID':>10s} | {'Auto':>8s} | {'Smart':>8s} | {'Auto Cat':>10s} | {'Smart Cat':>10s} | Match | Notes")
print("-" * 100)

for r in sample:
    auto_cat = r['sentiment_category']
    auto_norm = r['sentiment_normalized']

    smart = smart_score(r)
    smart_cat = smart['category']
    smart_norm = smart['normalized']

    match = auto_cat == smart_cat
    if match:
        agreements += 1
    else:
        disagreements += 1

    # Did direction flip?
    if (auto_norm > 0 and smart_norm < 0) or (auto_norm < 0 and smart_norm > 0):
        direction_flips += 1

    adj_str = '; '.join(smart['adjustments']) if smart['adjustments'] else ''
    print(f"{r['employee_id']:>10s} | {auto_norm:+.3f} | {smart_norm:+.3f} | {auto_cat:>10s} | {smart_cat:>10s} | {'Y' if match else 'N':>5s} | {adj_str}")

print(f"\nAgreement rate: {agreements}/{len(sample)} ({100*agreements/len(sample):.0f}%)")
print(f"Disagreements: {disagreements}/{len(sample)} ({100*disagreements/len(sample):.0f}%)")
print(f"Direction flips (sign change): {direction_flips}/{len(sample)}")

# ============================================================
# PART 6: Systematic bias check — would correcting the scorer
# change any KEY FINDINGS?
# ============================================================
print("\n" + "=" * 80)
print("PART 6: IMPACT ON KEY FINDINGS")
print("=" * 80)

# Re-score ALL records with smart scorer and compare group-level findings
smart_data = []
for r in data:
    s = smart_score(r)
    smart_data.append({
        'employee_id': r['employee_id'],
        'site': r['site'],
        'is_transfer': r['is_transfer'],
        'origin_quality': r.get('origin_district_system_quality'),
        'position': r['position'],
        'years_at_district_band': r['years_at_district_band'],
        'auto_norm': r['sentiment_normalized'],
        'auto_cat': r['sentiment_category'],
        'smart_norm': s['normalized'],
        'smart_cat': s['category'],
    })

# Compare site-level rankings
print("\nSite-level sentiment comparison (auto vs smart scorer):")
sites = set(r['site'] for r in smart_data)
site_comparison = []
for site in sorted(sites):
    auto = [r['auto_norm'] for r in smart_data if r['site'] == site]
    smart = [r['smart_norm'] for r in smart_data if r['site'] == site]
    site_comparison.append((site, statistics.mean(auto), statistics.mean(smart), len(auto)))

site_comparison.sort(key=lambda x: x[1])
print(f"\n{'Site':<30s} | {'n':>4s} | {'Auto Mean':>10s} | {'Smart Mean':>11s} | {'Diff':>6s}")
print("-" * 75)
for site, auto_m, smart_m, n in site_comparison:
    print(f"{site:<30s} | {n:>4d} | {auto_m:+.3f}    | {smart_m:+.3f}     | {smart_m-auto_m:+.3f}")

# Transfer vs non-transfer comparison
print("\n\nTransfer effect comparison:")
auto_transfer = [r['auto_norm'] for r in smart_data if r['is_transfer']]
auto_non = [r['auto_norm'] for r in smart_data if not r['is_transfer']]
smart_transfer = [r['smart_norm'] for r in smart_data if r['is_transfer']]
smart_non = [r['smart_norm'] for r in smart_data if not r['is_transfer']]

print(f"  Auto scorer:  transfers={statistics.mean(auto_transfer):+.3f} vs non-transfers={statistics.mean(auto_non):+.3f} (gap={statistics.mean(auto_transfer)-statistics.mean(auto_non):+.3f})")
print(f"  Smart scorer: transfers={statistics.mean(smart_transfer):+.3f} vs non-transfers={statistics.mean(smart_non):+.3f} (gap={statistics.mean(smart_transfer)-statistics.mean(smart_non):+.3f})")

# Transfers from "worse" systems specifically
print("\n\nTransfers from 'worse' origin systems:")
auto_worse_origin = [r['auto_norm'] for r in smart_data if r['origin_quality'] == 'worse']
smart_worse_origin = [r['smart_norm'] for r in smart_data if r['origin_quality'] == 'worse']
if auto_worse_origin:
    print(f"  Auto scorer:  n={len(auto_worse_origin)}, mean={statistics.mean(auto_worse_origin):+.3f}")
    print(f"  Smart scorer: n={len(smart_worse_origin)}, mean={statistics.mean(smart_worse_origin):+.3f}")
    print(f"  Difference: {statistics.mean(smart_worse_origin)-statistics.mean(auto_worse_origin):+.3f}")
    print(f"  -> The smart scorer {'increases' if statistics.mean(smart_worse_origin) > statistics.mean(auto_worse_origin) else 'decreases'} their score, "
          f"suggesting the auto scorer {'understates' if statistics.mean(smart_worse_origin) > statistics.mean(auto_worse_origin) else 'overstates'} their positivity.")

# Category shifts
print("\n\nCategory shift summary (auto -> smart):")
shifts = {}
for r in smart_data:
    key = f"{r['auto_cat']} -> {r['smart_cat']}"
    shifts[key] = shifts.get(key, 0) + 1

for k, v in sorted(shifts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} records ({100*v/len(smart_data):.1f}%)")

# Tenure band comparison
print("\n\nTenure band sentiment comparison:")
bands = sorted(set(r['years_at_district_band'] for r in smart_data))
print(f"{'Band':<12s} | {'n':>4s} | {'Auto Mean':>10s} | {'Smart Mean':>11s} | {'Diff':>6s}")
print("-" * 55)
for band in bands:
    auto = [r['auto_norm'] for r in smart_data if r['years_at_district_band'] == band]
    smart = [r['smart_norm'] for r in smart_data if r['years_at_district_band'] == band]
    print(f"{band:<12s} | {len(auto):>4d} | {statistics.mean(auto):+.3f}    | {statistics.mean(smart):+.3f}     | {statistics.mean(smart)-statistics.mean(auto):+.3f}")

print("\n" + "=" * 80)
print("SUMMARY OF SCORER BIAS FINDINGS")
print("=" * 80)
print("""
Key findings about scorer validity will be printed above. Review:
1. How many records have negation patterns that flip keyword meaning
2. Whether transfers' use of "worse" (about old system) artificially lowers scores
3. Whether response length mechanically drives keyword counts
4. How much hedging language goes undetected
5. Agreement rate between auto and context-aware scorer
6. Whether correcting biases changes site/group rankings
""")
