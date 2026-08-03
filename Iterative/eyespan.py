#!/usr/bin/env python3
"""eyespan -- recover the 208 classes' spans by inverting their shipped rows
against the corpus, with a bit-level round-trip gate (FR201 keystone).

Each class block decomposes into pairs: cross-message rows carry {b_m1,+1},
{b_m2,-1} and a shared rhs = (p2-p1) mod 83; same-message rows carry no base
columns. A pair's ordered cells give the aligned glyph sequences (A_i, D_i),
contiguous under per_msg_prog_rows -- locate both substrings in the corpus
with the required offset relation, demand a unique joint placement, then
re-emit rows from the recovered span and require the multiset to equal the
shipped block exactly."""
import sys, os, json
from collections import defaultdict, Counter
sys.path.insert(0, ".")
from make_mandatory import parse_problem, N

XD = "XD-MBYG04K-URS3LF"
CORPUS = os.path.join("..","Eyes-main","noita_eye_core","corpus.json")

def load_corpus():
    c = json.load(open(CORPUS)); return c["message_labels"], c["ciphertexts"]

def decompose(block):
    """class block -> list of pair dicts {m1,m2,dp,cells:[(A,D),...]} in row order.
    Rows of one pair are consecutive in the block (emitters yield per pair)."""
    pairs = []
    cur = None
    for row, rhs in block:
        bases = sorted(c for c in row if c >= N)
        gl = {c: v for c, v in row.items() if c < N}
        # identify A (coeff -1 = 82) and D (coeff +1)
        Ds = [c for c, v in gl.items() if v == 1]
        As = [c for c, v in gl.items() if v == N-1]
        if len(Ds) == 1 and len(As) == 1:
            A, D = As[0], Ds[0]
        elif not gl:                     # A == D cancelled: same glyph both sides
            A = D = None
        else:                            # coefficient 2 impossible here; skip-flag
            A = D = ("?",)
        if bases:
            b1 = [c for c in bases if row[c] == 1][0] - N
            b2 = [c for c in bases if row[c] == N-1][0] - N
            key = (b1, b2, rhs)
        else:
            key = (None, None, rhs)
        if cur is None or cur["key"] != key:
            cur = {"key": key, "cells": []}; pairs.append(cur)
        cur["cells"].append((A, D))
    return pairs

def locate(pairs, cts):
    """place each pair in the corpus; return spans or raise reasons."""
    out = []
    for pr in pairs:
        b1, b2, dp = pr["key"]; L = len(pr["cells"])
        seqA = [a for a, d in pr["cells"]]
        seqD = [d for a, d in pr["cells"]]
        if any(a is None or isinstance(a, tuple) for a in seqA+seqD):
            out.append({"err": "ambiguous-cells", "key": pr["key"], "L": L}); continue
        cand = []
        msgs1 = [b1] if b1 is not None else range(9)
        for m1 in msgs1:
            row1 = cts[m1]
            for p1 in range(len(row1)-L+1):
                if list(row1[p1:p1+L]) != seqA: continue
                m2s = [b2] if b2 is not None else ([m1] if b1 is None else range(9))
                for m2 in m2s:
                    row2 = cts[m2]
                    for p2 in range(len(row2)-L+1):
                        if (p2-p1) % N != dp: continue
                        if list(row2[p2:p2+L]) != seqD: continue
                        if m1 == m2 and p1 == p2: continue
                        cand.append((m1,p1,m2,p2,L))
        # dedupe symmetric duplicates for same-message
        cand = sorted(set(cand))
        out.append({"cand": cand, "key": pr["key"], "L": L})
    return out

def reemit(m1,p1,m2,p2,L,cts):
    rows = []
    for i in range(L):
        A = int(cts[m1][p1+i]); D = int(cts[m2][p2+i])
        row = {}
        row[D] = (row.get(D,0)+1) % N; row[A] = (row.get(A,0)+N-1) % N
        if m1 != m2:
            row[N+m2] = (row.get(N+m2,0)+N-1) % N; row[N+m1] = (row.get(N+m1,0)+1) % N
        rows.append((tuple(sorted((c,v) for c,v in row.items() if v)), (p2-p1)%N))
    return rows

def canon(block):
    return Counter((tuple(sorted((c,v) for c,v in row.items() if v)), rhs)
                   for row, rhs in block)

def main():
    labels, cts = load_corpus()
    seeds0, classes = parse_problem("maxset_problem.txt")
    stats = Counter(); spans = {}; problems = []
    for ci, block in enumerate(classes):
        prs = decompose(block)
        loc = locate(prs, cts)
        cls_spans = []; ok = True
        for r in loc:
            if "err" in r: stats["ambig"] += 1; ok = False; problems.append((ci, r)); continue
            if len(r["cand"]) == 1:
                cls_spans.append(r["cand"][0]); stats["unique"] += 1
            elif len(r["cand"]) == 0:
                stats["none"] += 1; ok = False; problems.append((ci, r))
            else:
                # multiple placements: acceptable iff all re-emit identically
                em = {tuple(sorted(reemit(*c, cts))) for c in r["cand"]}
                if len(em) == 1:
                    cls_spans.append(r["cand"][0]); stats["multi-equiv"] += 1
                else:
                    stats["multi-diff"] += 1; ok = False; problems.append((ci, r))
        if ok:
            # round-trip gate: re-emitted multiset == shipped block multiset
            re_rows = []
            for c in cls_spans: re_rows += [ (r, rh) for r, rh in reemit(*c, cts) ]
            if Counter(re_rows) == canon(block):
                spans[ci] = cls_spans; stats["class-ok"] += 1
            else:
                stats["roundtrip-fail"] += 1; problems.append((ci, "roundtrip"))
    print(f"pairs: unique {stats['unique']}  multi-equiv {stats['multi-equiv']}  "
          f"none {stats['none']}  multi-diff {stats['multi-diff']}  ambig {stats['ambig']}")
    print(f"classes fully recovered with round-trip PASS: {stats['class-ok']} / {len(classes)}")
    if stats['roundtrip-fail']: print(f"round-trip failures: {stats['roundtrip-fail']}")
    json.dump({str(k): v for k, v in spans.items()}, open("spans_208.json","w"))
    if problems:
        print("first problems:", problems[:4])

if __name__ == "__main__":
    main()
