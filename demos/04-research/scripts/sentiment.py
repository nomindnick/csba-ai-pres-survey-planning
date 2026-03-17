"""Simple keyword-based sentiment scoring for survey responses."""
import json, re

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

def score_text(text):
    """Return (positive_count, negative_count, net_score) for a text."""
    if not text:
        return 0, 0, 0
    text_lower = text.lower()
    words = re.findall(r'\b[\w-]+\b', text_lower)

    pos = sum(1 for w in POSITIVE if w in text_lower)
    neg = sum(1 for w in NEGATIVE if w in text_lower)
    return pos, neg, pos - neg

def score_record(record):
    """Score all 5 questions, return dict with scores."""
    total_pos, total_neg = 0, 0
    for q in ['q1', 'q2', 'q3', 'q4', 'q5']:
        p, n, _ = score_text(record[q])
        total_pos += p
        total_neg += n
    net = total_pos - total_neg
    # Normalize to -1 to 1 scale
    total = total_pos + total_neg
    if total == 0:
        normalized = 0
    else:
        normalized = net / total
    return {
        'positive': total_pos,
        'negative': total_neg,
        'net': net,
        'normalized': round(normalized, 3),
        'category': 'positive' if normalized > 0.15 else ('negative' if normalized < -0.15 else 'neutral')
    }

if __name__ == '__main__':
    with open('data/survey_full_dataset.json') as f:
        data = json.load(f)

    for r in data:
        scores = score_record(r)
        r.update({f'sentiment_{k}': v for k, v in scores.items()})

    with open('data/survey_scored.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Quick summary
    cats = {}
    for r in data:
        c = r['sentiment_category']
        cats[c] = cats.get(c, 0) + 1
    print(f"Sentiment distribution: {cats}")
    print(f"Mean normalized: {sum(r['sentiment_normalized'] for r in data)/len(data):.3f}")
