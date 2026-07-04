#!/usr/bin/env python3
"""
isoscan -- Isomorph-constrained language scanner for the Noita Eye Messages.

Takes the 13 isomorph patterns catalogued in the community "Isomorph Structure
of the Eye Messages" chart and scans natural-language corpora (English,
Finnish, Livvi-Karelian) for text windows consistent with each pattern under
several distinct cipher-model hypotheses.

Why multiple modes: under autokey/progressive ciphers, ciphertext isomorph
patterns generally do NOT transfer to the plaintext directly (see Pyry's
Alberti-autokey demonstration on the wiki: identical plaintexts produced
ciphertext isomorphs whose pattern the plaintext itself does not have).
What DOES hold, per model, is a constraint on a *derived stream* of the
plaintext. Each mode builds that stream and pattern-matches it:

  direct    s[i] = p[i]                      (fixed alphabet over the window:
                                              repeats in ct <=> repeats in pt)
  delta:D   s[i] = (p[i] - p[i-D]) mod M     (progressive key / Delta-isomorph
                                              view; running-key difference)
  sigma:D   s[i] = (p[i] + p[i-D]) mod M     (Vigenere plaintext-autokey, lag D:
                                              c=p+k, k=p shifted by D)
  psum      s[i] = (p[0]+...+p[i]) mod M     (Alberti autokey where the ring
                                              advances by the previous plaintext
                                              value: ct repeats <=> zero-sum
                                              plaintext intervals)
  bigram:D  s[i] = (p[i-D], p[i]) as a pair  (alphabet-agnostic autokey: any
                                              injective cipher of the lagged
                                              pair; strictly stronger than
                                              sigma/delta)

Matching semantics:
  eq        positions sharing a pattern letter must be EQUAL in the stream
            (the defensible core constraint; always applied)
  distinct  additionally, different pattern letters must be UNEQUAL
  strict    additionally, '.' positions must be window-unique (the window's
            full repeat pattern equals the given pattern exactly)

For letter-level plaintext in direct mode, strict is essentially unsatisfiable
at window lengths >= ~20 (English text rarely has so few internal repeats);
for derived streams over larger effective alphabets it becomes plausible.

Usage examples:
  ./isoscan.py --selftest
  ./isoscan.py --validate-eyes path/to/noita_eye_data_trigrams.csv
  ./isoscan.py --corpus english=english.txt --corpus finnish=kalevala.txt \
               --modes direct,delta:1,sigma:1,psum,bigram:1 --top 8
"""

import argparse
import csv
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

try:
    import numpy as np
except ImportError:
    sys.exit("isoscan requires numpy: pip install numpy --break-system-packages")

# --------------------------------------------------------------------------
# Pattern catalogue, transcribed from the community isomorph chart legend.
# Fields: name, pattern, declared internal repeats, declared occurrences,
#         declared length, declared score (log2 prob of arising randomly).
# Notation: same letter = repeated symbol; '.' = symbol unique in window.
# "Internal repeats" is sum over repeat classes of (occurrences - 1).
# --------------------------------------------------------------------------
PATTERNS = [
    ("#1",  "A.....BCD.ED.BE.CA",                5, 4, 18, 28.0),
    ("#C0", "A.....BCD.ED.BE.CAF....F",          6, 2, 24, 17.5),
    ("#C1", "A.....BCD.ED.BE.CA..F....F",        6, 2, 26, 17.5),
    ("#2-", "A...A......B.....C...C..B",         3, 4, 25, 12.8),
    ("#2",  "AB...C...C......D.A...E...EB.D",    5, 3, 30, 20.9),
    ("#2+", "ABC..D...D......E.A...F...FB.EC.F", 7, 2, 33, 21.4),
    ("#S",  "A..BAC........B..DE.F....E.DF.C",   6, 2, 31, 17.5),
    ("#F",  "AB......A.C.D.BD.CB",               5, 3, 19, 20.8),
    ("#M",  "A.B.CB.AC",                         3, 6,  9, 19.5),
    ("#M-", "A.B..B.A",                          2, 7,  8,  9.7),
    ("#3",  "AB.C....B.AC",                      3, 3, 12,  9.1),
    ("#3+", "AB.C....B.AC..B",                   4, 2, 15,  9.7),
    ("#4",  "A..B.B.......A",                    2, 3, 14,  3.5),
]

MASTER_ALPHABET = "abcdefghijklmnopqrstuvwxyz" + "äöåčšžü"


# --------------------------------------------------------------------------
# Pattern machinery
# --------------------------------------------------------------------------
def parse_pattern(pat):
    """Return (length, classes) where classes = {letter: [positions]}."""
    classes = defaultdict(list)
    for i, ch in enumerate(pat):
        if ch != ".":
            classes[ch].append(i)
    return len(pat), dict(classes)


def eq_pairs(classes):
    """Chained equality pairs sufficient to enforce all class equalities."""
    pairs = []
    for pos in classes.values():
        for a, b in zip(pos, pos[1:]):
            pairs.append((a, b))
    return pairs


def n_constraints(classes):
    return sum(len(p) - 1 for p in classes.values())


def canonical_pattern(seq):
    """Canonical repeat pattern of a sequence: letters in order of first
    appearance for symbols occurring >=2 times, '.' otherwise."""
    counts = Counter(seq)
    out, mapping, nxt = [], {}, 0
    for x in seq:
        if counts[x] < 2:
            out.append(".")
        else:
            if x not in mapping:
                mapping[x] = chr(ord("A") + nxt)
                nxt += 1
            out.append(mapping[x])
    return "".join(out)


def selftest():
    ok = True
    for name, pat, reps, occ, ln, score in PATTERNS:
        L, classes = parse_pattern(pat)
        C = n_constraints(classes)
        good = (L == ln) and (C == reps)
        print(f"  {name:4s} len {L:2d} (declared {ln:2d})  "
              f"constraints {C} (declared {reps})  "
              f"classes {len(classes)}  {'OK' if good else 'MISMATCH'}")
        ok &= good
    print("selftest:", "PASS" if ok else "FAIL")
    return ok


# --------------------------------------------------------------------------
# Eye-message validation: find strict instances of each pattern in the
# canonical trigram data and compare counts against the chart legend.
# --------------------------------------------------------------------------
def load_eye_csv(path):
    msgs = {}
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f):
            if not row or row[0].startswith("#"):
                continue
            name = row[1].strip()
            vals = [int(x) for x in row[2:] if x.strip() != ""]
            msgs[name] = vals
    return msgs


def validate_eyes(path):
    msgs = load_eye_csv(path)
    total = sum(len(v) for v in msgs.values())
    print(f"loaded {len(msgs)} messages, {total} trigrams total")
    # shared-prefix sanity check
    names = list(msgs)
    print("\npairwise common prefixes >= 3:")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = msgs[names[i]], msgs[names[j]]
            k = 0
            while k < min(len(a), len(b)) and a[k] == b[k]:
                k += 1
            if k >= 3:
                print(f"  {names[i]:8s} ~ {names[j]:8s}: {k}")
    print("\nstrict pattern instances in ciphertext "
          "(window repeat pattern == legend pattern exactly):")
    for name, pat, reps, occ, ln, score in PATTERNS:
        L, _ = parse_pattern(pat)
        hits = []
        for mname, vals in msgs.items():
            for s in range(len(vals) - L + 1):
                if canonical_pattern(vals[s:s + L]) == pat:
                    hits.append((mname, s))
        flag = "==" if len(hits) == occ else "!="
        locs = ", ".join(f"{m}@{s}" for m, s in hits)
        print(f"  {name:4s} found {len(hits)} {flag} legend {occ}   [{locs}]")


# --------------------------------------------------------------------------
# Corpus loading and stream derivation
# --------------------------------------------------------------------------
def read_text(path):
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    # trim Gutenberg boilerplate if present
    m = re.search(r"\*\*\* ?START.*?\*\*\*", text)
    if m:
        text = text[m.end():]
    m = re.search(r"\*\*\* ?END", text)
    if m:
        text = text[:m.start()]
    # strip XML/HTML tags if any
    if "<" in text[:2000]:
        text = re.sub(r"<[^>]+>", " ", text)
    return text


def normalize(text, keep_space=False):
    text = unicodedata.normalize("NFC", text.lower())
    idx = {c: i for i, c in enumerate(MASTER_ALPHABET)}
    out = []
    prev_space = True
    for ch in text:
        if ch in idx:
            out.append(idx[ch])
            prev_space = False
        elif keep_space and not prev_space:
            out.append(len(MASTER_ALPHABET))  # space symbol
            prev_space = True
    return np.array(out, dtype=np.int64)


def derive_stream(x, mode, M):
    """Return (stream s, text_offset) where s[k] corresponds to text index
    k + text_offset."""
    if mode == "direct":
        return x, 0
    if mode == "psum":
        return np.cumsum(x) % M, 0
    kind, _, arg = mode.partition(":")
    D = int(arg) if arg else 1
    if kind == "delta":
        return (x[D:] - x[:-D]) % M, D
    if kind == "sigma":
        return (x[D:] + x[:-D]) % M, D
    if kind == "bigram":
        K = int(x.max()) + 1
        return x[D:] * K + x[:-D], D
    raise ValueError(f"unknown mode {mode}")


def kappa(s):
    """Empirical index of coincidence of a stream (probability two random
    positions agree)."""
    _, counts = np.unique(s, return_counts=True)
    n = s.size
    return float((counts * (counts - 1)).sum()) / (n * (n - 1)) if n > 1 else 0.0


# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------
def scan_pattern(s, pat):
    """Vectorized equality-class matching. Returns stream-window start
    indices satisfying all equality constraints."""
    L, classes = parse_pattern(pat)
    V = s.size - L + 1
    if V <= 0:
        return np.empty(0, dtype=np.int64), classes, L
    mask = np.ones(V, dtype=bool)
    for a, b in eq_pairs(classes):
        mask &= s[a:a + V] == s[b:b + V]
        if not mask.any():
            break
    return np.flatnonzero(mask), classes, L


def filter_distinct(s, starts, classes):
    reps = [pos[0] for pos in classes.values()]
    keep = []
    for p in starts:
        vals = [s[p + r] for r in reps]
        if len(set(vals)) == len(vals):
            keep.append(p)
    return np.array(keep, dtype=np.int64)


def filter_strict(s, starts, pat):
    L = len(pat)
    keep = [p for p in starts
            if canonical_pattern(s[p:p + L].tolist()) == pat]
    return np.array(keep, dtype=np.int64)


def window_text(letters_idx, start, length, keep_space):
    tbl = MASTER_ALPHABET + (" " if keep_space else "")
    return "".join(tbl[i] for i in letters_idx[start:start + length])


def run_scan(corpora, modes, mod_override, keep_space, top_n, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    report = open(os.path.join(out_dir, "isoscan_report.txt"), "w",
                  encoding="utf-8")
    tsv = open(os.path.join(out_dir, "isoscan_hits.tsv"), "w",
               encoding="utf-8")
    tsv.write("corpus\tmode\tpattern\tconstraints\tkappa\twindows\texpected"
              "\tobserved_eq\tobs_distinct\tobs_strict\tratio\ttop_matches\n")

    def emit(line=""):
        print(line)
        report.write(line + "\n")

    for cname, path in corpora.items():
        x = normalize(read_text(path), keep_space=keep_space)
        M = mod_override or (26 if x.max() < 26 else int(x.max()) + 1)
        emit(f"\n=== corpus {cname}: {x.size} letters, alphabet mod {M} ===")
        for mode in modes:
            s, off = derive_stream(x, mode, M)
            kap = kappa(s)
            for name, pat, reps, occ, ln, score in PATTERNS:
                starts, classes, L = scan_pattern(s, pat)
                V = max(s.size - L + 1, 0)
                C = n_constraints(classes)
                expected = V * (kap ** C)
                d = filter_distinct(s, starts, classes)
                st = filter_strict(s, d, pat) if d.size else d
                ratio = (starts.size / expected) if expected > 0 else float("inf")
                # collect crib strings (original text spanning the lag context)
                span = off + L
                cnt = Counter(window_text(x, p, span, keep_space)
                              for p in starts[:200000])
                tops = cnt.most_common(top_n)
                top_str = "; ".join(f"{t}×{c}" for t, c in tops)
                emit(f"[{mode:9s}] {name:4s} C={C} κ={kap:.4f} "
                     f"exp={expected:9.1f} obs={starts.size:7d} "
                     f"(distinct {d.size}, strict {st.size}) "
                     f"ratio={ratio:6.2f}")
                if tops:
                    emit(f"           top: {top_str}")
                tsv.write(f"{cname}\t{mode}\t{name}\t{C}\t{kap:.5f}\t{V}\t"
                          f"{expected:.1f}\t{starts.size}\t{d.size}\t"
                          f"{st.size}\t{ratio:.3f}\t{top_str}\n")
    report.close()
    tsv.close()


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--validate-eyes", metavar="CSV")
    ap.add_argument("--corpus", action="append", default=[],
                    metavar="NAME=PATH")
    ap.add_argument("--modes", default="direct,delta:1,delta:2,sigma:1,psum,bigram:1")
    ap.add_argument("--mod", type=int, default=0,
                    help="override alphabet modulus for delta/sigma/psum")
    ap.add_argument("--keep-space", action="store_true",
                    help="retain word boundaries as a symbol")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if args.validate_eyes:
        validate_eyes(args.validate_eyes)
        return
    if not args.corpus:
        ap.error("provide at least one --corpus NAME=PATH (or --selftest)")
    corpora = dict(c.split("=", 1) for c in args.corpus)
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    run_scan(corpora, modes, args.mod, args.keep_space, args.top, args.out)


if __name__ == "__main__":
    main()
