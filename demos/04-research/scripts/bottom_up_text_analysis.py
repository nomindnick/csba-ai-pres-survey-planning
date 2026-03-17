#!/usr/bin/env python3
"""Bottom-up text analysis: bigrams, trigrams, keyword hunting, sentiment-differential phrases."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────────
DATA = Path(__file__).resolve().parent.parent / "data" / "survey_full_dataset.json"
with open(DATA) as f:
    records = json.load(f)

print(f"Loaded {len(records)} records\n")

# ── Stopwords (English common words) ──────────────────────────────────────
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because
been before being below between both but by can't cannot could couldn't did
didn't do does doesn't doing don't down during each few for from further get got
had hadn't has hasn't have haven't having he he'd he'll he's her here here's
hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't
it it's its itself let's me more most mustn't my myself no nor not of off on
once only or other ought our ours ourselves out over own same shan't she she'd
she'll she's should shouldn't so some such than that that's the their theirs
them themselves then there there's these they they'd they'll they're they've
this those through to too under until up upon very was wasn't we we'd we'll
we're we've were weren't what what's when when's where where's which while who
who's whom why why's will with won't would wouldn't you you'd you'll you're
you've your yours yourself yourselves also just really like think feel felt
still even much one two three would've could've should've been don't didn't
wasn't weren't i've i'm i'd i'll it's that's there's here's who's what's
""".split())

# Add more domain-generic stopwords
STOPWORDS.update("""
know make made going go went come came way things thing something anything
everything nothing lot lots bit quite pretty well good great bad new old
""".split())

def tokenize(text):
    """Lowercase, remove punctuation, split into words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    tokens = text.split()
    return [t.strip("'-") for t in tokens if t.strip("'-")]

def ngrams(tokens, n):
    """Generate n-grams from token list."""
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def filtered_ngrams(tokens, n):
    """Generate n-grams, skipping those that are all stopwords."""
    result = []
    for i in range(len(tokens) - n + 1):
        gram = tokens[i:i+n]
        # At least one non-stopword
        if any(w not in STOPWORDS for w in gram):
            result.append(" ".join(gram))
    return result

# ── Simple keyword sentiment scoring ──────────────────────────────────────
POS_WORDS = set("good great excellent wonderful amazing fantastic helpful clear smooth easy improved better best love appreciate grateful positive professional efficient effective intuitive convenient reliable consistent".split())
NEG_WORDS = set("bad terrible awful poor frustrating difficult confusing broken disrupted rushed chaotic inadequate insufficient ignored dismissed lacking worst nightmare horrible struggle struggling failed failure disruptive problematic unreliable inconsistent".split())

def sentiment_score(text):
    tokens = set(tokenize(text))
    pos = len(tokens & POS_WORDS)
    neg = len(tokens & NEG_WORDS)
    return pos - neg

# ── Compute per-record sentiment across all questions ─────────────────────
for r in records:
    all_text = " ".join(r.get(f"q{i}", "") or "" for i in range(1, 6))
    r["_sentiment"] = sentiment_score(all_text)
    r["_all_text"] = all_text

sentiments = sorted(records, key=lambda r: r["_sentiment"])
n = len(sentiments)
cutoff_neg = n // 5  # bottom 20%
cutoff_pos = n - n // 5  # top 20%

neg_records = sentiments[:cutoff_neg]
pos_records = sentiments[cutoff_pos:]
print(f"Negative group (bottom 20%): {len(neg_records)} records, sentiment range [{neg_records[0]['_sentiment']}, {neg_records[-1]['_sentiment']}]")
print(f"Positive group (top 20%): {len(pos_records)} records, sentiment range [{pos_records[0]['_sentiment']}, {pos_records[-1]['_sentiment']}]")
print()

# ══════════════════════════════════════════════════════════════════════════
# PART 1: Top bigrams and trigrams per question
# ══════════════════════════════════════════════════════════════════════════
print("=" * 80)
print("PART 1: MOST COMMON BIGRAMS AND TRIGRAMS PER QUESTION")
print("=" * 80)

for q in ["q1", "q2", "q3", "q4", "q5"]:
    bigram_counts = Counter()
    trigram_counts = Counter()
    for r in records:
        text = r.get(q, "") or ""
        tokens = tokenize(text)
        bigram_counts.update(filtered_ngrams(tokens, 2))
        trigram_counts.update(filtered_ngrams(tokens, 3))

    print(f"\n── {q.upper()} ──")
    print(f"  Top 15 bigrams:")
    for phrase, count in bigram_counts.most_common(15):
        print(f"    {count:4d}  {phrase}")
    print(f"  Top 15 trigrams:")
    for phrase, count in trigram_counts.most_common(15):
        print(f"    {count:4d}  {phrase}")

# ══════════════════════════════════════════════════════════════════════════
# PART 2: Phrases distinctive to negative vs positive responses
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 2: PHRASES DISTINCTIVE TO NEGATIVE vs POSITIVE RESPONSES")
print("=" * 80)

for n_gram_size, label in [(2, "BIGRAMS"), (3, "TRIGRAMS")]:
    neg_counts = Counter()
    pos_counts = Counter()

    for r in neg_records:
        tokens = tokenize(r["_all_text"])
        neg_counts.update(filtered_ngrams(tokens, n_gram_size))

    for r in pos_records:
        tokens = tokenize(r["_all_text"])
        pos_counts.update(filtered_ngrams(tokens, n_gram_size))

    # Normalize to rate per record
    neg_n = len(neg_records)
    pos_n = len(pos_records)

    all_phrases = set(neg_counts.keys()) | set(pos_counts.keys())

    # Compute ratio: (neg_rate + smoothing) / (pos_rate + smoothing)
    MIN_COUNT = 5  # must appear at least 5 times total
    ratios = []
    for phrase in all_phrases:
        nc = neg_counts[phrase]
        pc = pos_counts[phrase]
        if nc + pc < MIN_COUNT:
            continue
        neg_rate = nc / neg_n
        pos_rate = pc / pos_n
        ratio = (neg_rate + 0.01) / (pos_rate + 0.01)
        ratios.append((phrase, ratio, nc, pc))

    ratios.sort(key=lambda x: x[1], reverse=True)

    print(f"\n── {label}: Most distinctive to NEGATIVE responses ──")
    for phrase, ratio, nc, pc in ratios[:20]:
        print(f"    {ratio:5.1f}x  neg={nc:3d} pos={pc:3d}  \"{phrase}\"")

    print(f"\n── {label}: Most distinctive to POSITIVE responses ──")
    ratios.sort(key=lambda x: x[1])
    for phrase, ratio, nc, pc in ratios[:20]:
        inv = 1/ratio if ratio > 0 else 999
        print(f"    {inv:5.1f}x  neg={nc:3d} pos={pc:3d}  \"{phrase}\"")

# ══════════════════════════════════════════════════════════════════════════
# PART 3: Targeted keyword search
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 3: TARGETED KEYWORD SEARCH")
print("=" * 80)

TARGET_TERMS = [
    "safety", "emergency", "lockdown", "fire", "drill", "pa system", "pa ",
    "intercom", "bell", "schedule", "vendor", "contractor", "construction",
    "noise", "dust", "asbestos", "wifi", "wi-fi", "network", "phone", "app",
    "principal", "admin", "union", "board", "parent", "student",
    "classroom", "office", "gym", "cafeteria", "library", "hallway",
    "summer", "winter", "weekend", "after hours", "overtime",
    "old system", "previous system", "new system",
    "budget", "cost", "money", "waste",
    "morale", "stress", "anxiety", "overwhelm", "burnout",
    "equity", "fair", "unfair", "favor",
    "trust", "respect", "listen", "voice", "input", "feedback",
    "promise", "told", "assured", "supposed to",
    "delay", "late", "behind schedule", "timeline",
    "broken", "malfunction", "glitch", "bug", "crash",
    "zone", "wing", "building", "portable", "trailer",
    "transfer", "transferred", "previous district",
    "seniority", "tenure", "veteran", "newer",
    "age", "older", "younger", "generation",
    "race", "gender", "discrimination", "bias",
]

# For each term, count occurrences in neg vs pos vs all
print(f"\n{'Term':<25s} {'All':>5s} {'Neg':>5s} {'Pos':>5s} {'Neg%':>6s} {'Pos%':>6s} {'Ratio':>7s}")
print("-" * 65)

term_results = []
for term in TARGET_TERMS:
    all_count = sum(1 for r in records if term in r["_all_text"].lower())
    neg_count = sum(1 for r in records[:cutoff_neg] if term in sentiments[records.index(r) if r in records else 0]["_all_text"].lower())
    # Simpler: just use the pre-computed groups
    neg_count = sum(1 for r in neg_records if term in r["_all_text"].lower())
    pos_count = sum(1 for r in pos_records if term in r["_all_text"].lower())

    if all_count == 0:
        continue

    neg_pct = neg_count / len(neg_records) * 100
    pos_pct = pos_count / len(pos_records) * 100

    if pos_pct > 0:
        ratio = neg_pct / pos_pct
    elif neg_pct > 0:
        ratio = 99.9
    else:
        ratio = 1.0

    term_results.append((term, all_count, neg_count, pos_count, neg_pct, pos_pct, ratio))

# Sort by ratio descending
term_results.sort(key=lambda x: x[6], reverse=True)

for term, ac, nc, pc, npct, ppct, ratio in term_results:
    flag = " ***" if ratio > 2.0 and ac >= 10 else (" **" if ratio > 1.5 and ac >= 10 else "")
    print(f"{term:<25s} {ac:5d} {nc:5d} {pc:5d} {npct:5.1f}% {ppct:5.1f}% {ratio:6.1f}x{flag}")

# ══════════════════════════════════════════════════════════════════════════
# PART 4: Discovery — what words appear that we haven't looked for?
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 4: HIGH-FREQUENCY WORDS BY QUESTION (potential unseen themes)")
print("=" * 80)

for q in ["q1", "q2", "q3", "q4", "q5"]:
    word_counts = Counter()
    for r in records:
        text = r.get(q, "") or ""
        tokens = tokenize(text)
        for t in tokens:
            if t not in STOPWORDS and len(t) > 2:
                word_counts[t] += 1

    print(f"\n── {q.upper()} — Top 30 words ──")
    for word, count in word_counts.most_common(30):
        print(f"    {count:4d}  {word}")

# ══════════════════════════════════════════════════════════════════════════
# PART 5: Phrases unique to negative responses (appear in neg, rare in pos)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 5: PHRASES APPEARING ALMOST EXCLUSIVELY IN NEGATIVE RESPONSES")
print("=" * 80)

for n_gram_size, label in [(2, "BIGRAMS"), (3, "TRIGRAMS")]:
    neg_counts = Counter()
    pos_counts = Counter()
    mid_counts = Counter()

    mid_records = sentiments[cutoff_neg:cutoff_pos]

    for r in neg_records:
        tokens = tokenize(r["_all_text"])
        neg_counts.update(set(filtered_ngrams(tokens, n_gram_size)))  # unique per record

    for r in pos_records:
        tokens = tokenize(r["_all_text"])
        pos_counts.update(set(filtered_ngrams(tokens, n_gram_size)))

    for r in mid_records:
        tokens = tokenize(r["_all_text"])
        mid_counts.update(set(filtered_ngrams(tokens, n_gram_size)))

    # Find phrases in 5+ negative records but 0-1 positive records
    print(f"\n── {label}: In 5+ negative records, 0-1 positive records ──")
    exclusive = []
    for phrase in neg_counts:
        nc = neg_counts[phrase]
        pc = pos_counts[phrase]
        mc = mid_counts[phrase]
        if nc >= 5 and pc <= 1:
            exclusive.append((phrase, nc, mc, pc))

    exclusive.sort(key=lambda x: x[1], reverse=True)
    for phrase, nc, mc, pc in exclusive[:25]:
        print(f"    neg={nc:3d} mid={mc:3d} pos={pc:3d}  \"{phrase}\"")

# ══════════════════════════════════════════════════════════════════════════
# PART 6: Site-specific and role-specific language
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 6: DISTINCTIVE LANGUAGE BY SITE")
print("=" * 80)

sites = set(r["site"] for r in records)
all_bigrams = Counter()
site_bigrams = defaultdict(Counter)

for r in records:
    tokens = tokenize(r["_all_text"])
    bg = set(filtered_ngrams(tokens, 2))
    all_bigrams.update(bg)
    site_bigrams[r["site"]].update(bg)

for site in sorted(sites):
    site_n = sum(1 for r in records if r["site"] == site)
    print(f"\n── {site} (n={site_n}) — Most distinctive bigrams ──")

    ratios = []
    for phrase in site_bigrams[site]:
        sc = site_bigrams[site][phrase]
        total = all_bigrams[phrase]
        if sc < 5:
            continue
        expected = total * site_n / len(records)
        if expected > 0:
            ratio = sc / expected
            ratios.append((phrase, sc, total, ratio))

    ratios.sort(key=lambda x: x[3], reverse=True)
    for phrase, sc, tc, ratio in ratios[:10]:
        print(f"    {ratio:5.1f}x  site={sc:3d} all={tc:3d}  \"{phrase}\"")

# ══════════════════════════════════════════════════════════════════════════
# PART 7: Room type and building wing language
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("PART 7: DISTINCTIVE LANGUAGE BY ROOM TYPE AND BUILDING WING")
print("=" * 80)

for field, field_label in [("room_type", "ROOM TYPE"), ("building_wing", "BUILDING WING")]:
    groups = defaultdict(list)
    for r in records:
        val = r.get(field)
        if val:
            groups[val].append(r)

    all_bg = Counter()
    group_bg = defaultdict(Counter)

    for val, recs in groups.items():
        for r in recs:
            tokens = tokenize(r["_all_text"])
            bg = set(filtered_ngrams(tokens, 2))
            all_bg.update(bg)
            group_bg[val].update(bg)

    for val in sorted(groups.keys()):
        grp_n = len(groups[val])
        if grp_n < 5:
            continue
        print(f"\n── {field_label}: {val} (n={grp_n}) — Most distinctive bigrams ──")

        ratios = []
        for phrase in group_bg[val]:
            gc = group_bg[val][phrase]
            total = all_bg[phrase]
            if gc < 3:
                continue
            expected = total * grp_n / sum(len(v) for v in groups.values())
            if expected > 0:
                ratio = gc / expected
                ratios.append((phrase, gc, total, ratio))

        ratios.sort(key=lambda x: x[3], reverse=True)
        for phrase, gc, tc, ratio in ratios[:10]:
            print(f"    {ratio:5.1f}x  grp={gc:3d} all={tc:3d}  \"{phrase}\"")

print("\n\nDone.")
