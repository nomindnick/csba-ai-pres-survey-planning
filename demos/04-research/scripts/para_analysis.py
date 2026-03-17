#!/usr/bin/env python3
"""Deep investigation of Paraprofessional/Aide survey responses."""

import json
import re
from collections import Counter, defaultdict

DATA = "/home/nick/Projects/csba-ai-pres-survey-planning/demos/04-research/data/survey_full_dataset.json"

with open(DATA) as f:
    data = json.load(f)

POSITIVE = ["great", "excellent", "improved", "better", "smooth", "helpful",
            "good", "easy", "appreciate", "intuitive", "clear"]
NEGATIVE = ["frustrated", "terrible", "poor", "difficult", "disruption",
            "problem", "issue", "confusing", "rushed", "broken", "fail",
            "worse", "struggle", "complaint", "disappointed"]

def keyword_score(text):
    """Return (pos_count, neg_count, net) for a text string."""
    if not text:
        return 0, 0, 0
    t = text.lower()
    pos = sum(1 for w in POSITIVE if re.search(r'\b' + w + r'\w*\b', t))
    neg = sum(1 for w in NEGATIVE if re.search(r'\b' + w + r'\w*\b', t))
    return pos, neg, pos - neg

def person_sentiment(record):
    """Aggregate sentiment across q1-q5."""
    total_pos, total_neg = 0, 0
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        p, n, _ = keyword_score(record[q])
        total_pos += p
        total_neg += n
    return total_pos, total_neg, total_pos - total_neg

# ── 1. Filter to paras ──────────────────────────────────────────────
paras = [r for r in data if r["position"] == "Paraprofessional/Aide"]
teachers = [r for r in data if r["position"] == "Teacher"]
print(f"{'='*70}")
print(f"PARAPROFESSIONAL/AIDE DEEP DIVE  (n={len(paras)})")
print(f"{'='*70}\n")

# ── 2. Overall keyword sentiment ────────────────────────────────────
print("── OVERALL KEYWORD SENTIMENT ──")
para_scores = [(r, *person_sentiment(r)) for r in paras]
teacher_scores = [(r, *person_sentiment(r)) for r in teachers]

para_nets = [s[3] for s in para_scores]
teacher_nets = [s[3] for s in teacher_scores]

def stats(vals):
    n = len(vals)
    mean = sum(vals) / n
    pos_pct = sum(1 for v in vals if v > 0) / n * 100
    neg_pct = sum(1 for v in vals if v < 0) / n * 100
    neutral_pct = sum(1 for v in vals if v == 0) / n * 100
    return mean, pos_pct, neg_pct, neutral_pct

pm, pp, pn, pneu = stats(para_nets)
tm, tp, tn, tneu = stats(teacher_nets)

print(f"  Paras    (n={len(paras):3d}):  mean net={pm:+.2f}  pos={pp:.0f}%  neg={pn:.0f}%  neutral={pneu:.0f}%")
print(f"  Teachers (n={len(teachers):3d}):  mean net={tm:+.2f}  pos={tp:.0f}%  neg={tn:.0f}%  neutral={tneu:.0f}%")
print()

# ── 3. Breakdown by site ────────────────────────────────────────────
print("── PARAS BY SITE ──")
sites = sorted(set(r["site"] for r in paras))
for site in sites:
    group = [s for s in para_scores if s[0]["site"] == site]
    nets = [s[3] for s in group]
    m, pp2, pn2, _ = stats(nets) if nets else (0, 0, 0, 0)
    print(f"  {site:35s}  n={len(group):2d}  mean net={m:+.2f}  pos={pp2:.0f}%  neg={pn2:.0f}%")
print()

# ── 3b. Breakdown by tenure band ────────────────────────────────────
print("── PARAS BY TENURE BAND (years_at_district_band) ──")
bands = sorted(set(r["years_at_district_band"] for r in paras),
               key=lambda b: int(b.split("-")[0]) if "-" in b else int(b.rstrip("+")))
for band in bands:
    group = [s for s in para_scores if s[0]["years_at_district_band"] == band]
    nets = [s[3] for s in group]
    m, pp2, pn2, _ = stats(nets)
    print(f"  {band:12s}  n={len(group):2d}  mean net={m:+.2f}  pos={pp2:.0f}%  neg={pn2:.0f}%")
print()

# ── 4. Q2 (training) comparison: paras vs teachers ──────────────────
print("── Q2 (TRAINING) SENTIMENT: PARAS vs TEACHERS ──")
def q_sentiment(records, q):
    scores = [keyword_score(r[q]) for r in records]
    nets = [s[2] for s in scores]
    m = sum(nets) / len(nets)
    neg_pct = sum(1 for n in nets if n < 0) / len(nets) * 100
    pos_pct = sum(1 for n in nets if n > 0) / len(nets) * 100
    return m, pos_pct, neg_pct

for q in ["q2", "q3"]:
    pm2, pp2, pn2 = q_sentiment(paras, q)
    tm2, tp2, tn2 = q_sentiment(teachers, q)
    print(f"  {q.upper()}:")
    print(f"    Paras    (n={len(paras)}):  mean net={pm2:+.2f}  pos={pp2:.0f}%  neg={pn2:.0f}%")
    print(f"    Teachers (n={len(teachers)}):  mean net={tm2:+.2f}  pos={tp2:.0f}%  neg={tn2:.0f}%")
print()

# Q2 by site for paras vs teachers
print("── Q2 (TRAINING) BY SITE: PARAS vs TEACHERS ──")
all_sites = sorted(set(r["site"] for r in data))
for site in all_sites:
    sp = [r for r in paras if r["site"] == site]
    st = [r for r in teachers if r["site"] == site]
    if sp:
        pm2, _, pn2 = q_sentiment(sp, "q2")
        tm2, _, tn2 = q_sentiment(st, "q2") if st else (0, 0, 0)
        print(f"  {site:35s}  Para n={len(sp):2d} net={pm2:+.2f} neg={pn2:.0f}%  |  Teacher n={len(st):2d} net={tm2:+.2f} neg={tn2:.0f}%")
print()

# ── 5. Read q2 and q3 from 5 most negative paras ────────────────────
print("── 5 MOST NEGATIVE PARAS: Q2 (training) & Q3 (communication) ──")
para_scores_sorted = sorted(para_scores, key=lambda s: s[3])
for rank, (r, pos, neg, net) in enumerate(para_scores_sorted[:5], 1):
    print(f"\n  #{rank}: {r['employee_id']} — {r['name']} | {r['site']} | tenure={r['years_at_district']}yr | net={net:+d} (pos={pos}, neg={neg})")
    print(f"    Q2 (training): {r['q2'][:300]}")
    print(f"    Q3 (communication): {r['q3'][:300]}")
print()

# ── 6. Role-specific complaint analysis ─────────────────────────────
print("── ROLE-SPECIFIC LANGUAGE: PARAS vs TEACHERS ──")
# Look for words/phrases more common in para responses vs teacher responses
def get_all_text(records):
    return " ".join(r[q] for r in records for q in ["q1","q2","q3","q4","q5"] if r[q]).lower()

para_text = get_all_text(paras)
teacher_text = get_all_text(teachers)

# Role-specific terms to check
role_terms = [
    "left out", "forgotten", "afterthought", "not included", "wasn't invited",
    "wasn't told", "no one told", "last to know", "didn't get", "excluded",
    "classroom aide", "aide", "para", "support staff", "not a priority",
    "different training", "separate", "wasn't trained", "no training",
    "teachers got", "teachers received", "teachers were", "only teachers",
    "not my job", "above my pay", "expected to", "supposed to",
    "don't have access", "no access", "can't use", "not allowed",
    "shared space", "no room", "no desk", "no computer",
    "between", "middle", "caught", "go-between",
    "ignored", "overlooked", "invisible", "second class", "second-class"
]

print(f"  {'Term':30s} {'Para freq':>12s} {'Teacher freq':>12s} {'Para rate':>10s} {'Teacher rate':>10s}")
print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*10} {'-'*10}")
for term in role_terms:
    pc = len(re.findall(r'\b' + re.escape(term) + r'\b', para_text))
    tc = len(re.findall(r'\b' + re.escape(term) + r'\b', teacher_text))
    pr = pc / len(paras) * 100
    tr = tc / len(teachers) * 100
    if pc > 0 or tc > 0:
        flag = " <<<" if pr > tr * 1.5 and pc >= 2 else ""
        print(f"  {term:30s} {pc:12d} {tc:12d} {pr:9.1f}% {tr:9.1f}%{flag}")
print()

# Also do a broader scan: any bigrams more common in para text
from collections import Counter
def get_bigrams(text):
    words = re.findall(r'[a-z]+', text)
    return [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]

para_bigrams = Counter(get_bigrams(para_text))
teacher_bigrams = Counter(get_bigrams(teacher_text))

# Normalize by group size
print("  TOP BIGRAMS OVERREPRESENTED IN PARA RESPONSES (vs teachers):")
para_rate = {bg: c / len(paras) for bg, c in para_bigrams.items() if c >= 3}
teacher_rate = {bg: c / len(teachers) for bg, c in teacher_bigrams.items()}

overrep = []
for bg, pr in para_rate.items():
    tr = teacher_rate.get(bg, 0.001)
    ratio = pr / tr
    if ratio > 1.5 and para_bigrams[bg] >= 3:
        overrep.append((bg, para_bigrams[bg], teacher_bigrams.get(bg, 0), ratio))

overrep.sort(key=lambda x: -x[3])
for bg, pc, tc, ratio in overrep[:20]:
    print(f"    '{bg}': para={pc} ({pc/len(paras)*100:.1f}%), teacher={tc} ({tc/len(teachers)*100:.1f}%), ratio={ratio:.1f}x")
print()

# ── 7. Site-level comparison for paras ───────────────────────────────
print("── PARA SENTIMENT BY SITE (detailed) ──")
for site in sites:
    group = [s for s in para_scores if s[0]["site"] == site]
    if not group:
        continue
    nets = [s[3] for s in group]
    m = sum(nets) / len(nets)

    # Also compute per-question
    site_paras = [s[0] for s in group]
    print(f"\n  {site} (n={len(group)})  overall mean net={m:+.2f}")
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        qm, qp, qn = q_sentiment(site_paras, q)
        print(f"    {q.upper()}: mean net={qm:+.2f}  pos={qp:.0f}%  neg={qn:.0f}%")

    # Tenure breakdown within site
    site_bands = sorted(set(r["years_at_district_band"] for r in site_paras),
                        key=lambda b: int(b.split("-")[0]) if "-" in b else int(b.rstrip("+")))
    for band in site_bands:
        bg = [s for s in group if s[0]["years_at_district_band"] == band]
        bn = [s[3] for s in bg]
        bm = sum(bn) / len(bn)
        print(f"    tenure {band}: n={len(bg)}, net={bm:+.2f}")

print()

# ── Outlier site check ───────────────────────────────────────────────
print("── SITE OUTLIER CHECK ──")
site_means = {}
for site in sites:
    group = [s for s in para_scores if s[0]["site"] == site]
    nets = [s[3] for s in group]
    site_means[site] = sum(nets) / len(nets)

overall_mean = sum(para_nets) / len(para_nets)
print(f"  Overall para mean: {overall_mean:+.2f}")
for site, m in sorted(site_means.items(), key=lambda x: x[1]):
    n = len([s for s in para_scores if s[0]["site"] == site])
    diff = m - overall_mean
    flag = " *** OUTLIER" if abs(diff) > 1.0 else ""
    print(f"  {site:35s}  n={n:2d}  mean={m:+.2f}  diff from avg={diff:+.2f}{flag}")
print()

# ── Transfer status for paras ────────────────────────────────────────
print("── PARA TRANSFER STATUS ──")
transfers = [s for s in para_scores if s[0]["is_transfer"]]
non_transfers = [s for s in para_scores if not s[0]["is_transfer"]]
if transfers:
    tm_nets = [s[3] for s in transfers]
    nt_nets = [s[3] for s in non_transfers]
    print(f"  Transfers     (n={len(transfers):2d}):  mean net={sum(tm_nets)/len(tm_nets):+.2f}")
    print(f"  Non-transfers (n={len(non_transfers):2d}):  mean net={sum(nt_nets)/len(nt_nets):+.2f}")
else:
    print(f"  No transfers among paras (n={len(paras)})")
print()

# ── Building wing / room type ────────────────────────────────────────
print("── PARA BY ROOM TYPE ──")
room_types = sorted(set(r["room_type"] for r in paras))
for rt in room_types:
    group = [s for s in para_scores if s[0]["room_type"] == rt]
    nets = [s[3] for s in group]
    m = sum(nets) / len(nets)
    print(f"  {rt:20s}  n={len(group):2d}  mean net={m:+.2f}")

print()
print("── PARA BY BUILDING WING ──")
wings = sorted(set(str(r["building_wing"]) for r in paras))
for w in wings:
    group = [s for s in para_scores if str(s[0]["building_wing"]) == w]
    nets = [s[3] for s in group]
    m = sum(nets) / len(nets)
    print(f"  {w:20s}  n={len(group):2d}  mean net={m:+.2f}")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
