#!/usr/bin/env python3
"""reduce_fast.py -- validated reduction, ~10-20x faster than reduce_validated,
with progress to stderr and cross-machine signature verification.

Same validation semantics: every block's row count is checked against its
R-line's declared count; mismatched blocks are quarantined (corrupt), the
trailing block of a possibly-live file is held out, neither is ever counted.

Speed: runs are deduplicated by the raw bytes of their signature blocks --
valid because eyemax emits rows in a deterministic order per reading -- and
only the first occurrence of each distinct block is parsed. The dominant
reading is then re-parsed, canonically sorted, and hashed; for the MANDATORY
file this hash must equal the certified sandbox value below (FR196: the same
794-relation object, bit-for-bit, across implementations and machines).

Usage:
    python3 reduce_fast.py mand/m_all.txt ctrl_all.txt
    python3 reduce_fast.py <any_eyemax_output> [more...]
"""
import sys, hashlib

CERT_SHA = "7e9ab7231a6eb285795c9ca484329b209c1e95ff15fb317b8055a170761fecdf"
CERT_REL = 794

def reduce(path):
    counts = {}; first = {}; order = []
    cur_lines = []; declared = None; have = False
    bad = 0; trailing = 0
    n_seen = 0
    def commit(final):
        nonlocal bad, trailing, n_seen
        if not have: return
        if len(cur_lines) != declared:
            if final: trailing += 1
            else: bad += 1
            return
        h = hash(tuple(cur_lines))
        if h not in counts:
            counts[h] = 0; first[h] = list(cur_lines); order.append(len(counts))
        else:
            order.append(len(counts))
        counts[h] += 1; n_seen += 1
        if n_seen % 50000 == 0:
            print(f"  ...{n_seen:,} runs, {len(counts)} distinct", file=sys.stderr)
    with open(path, "rb") as f:
        for raw in f:
            if raw.startswith(b"R "):
                commit(final=False)
                p = raw.split()
                declared = int(p[4]); cur_lines = []; have = True
            elif have:
                cur_lines.append(raw)
    commit(final=True)
    n = sum(counts.values()); k = len(counts)
    freq = sorted(counts.values(), reverse=True)
    s1 = sum(1 for v in freq if v == 1); s2 = sum(1 for v in freq if v == 2)
    chao1 = (k + (s1 * (s1 - 1)) / (2 * (s2 + 1))) if k else 0.0
    step = max(1, len(order) // 12) if order else 1
    # canonical hash of the dominant reading
    dom_h = max(counts, key=counts.get) if counts else None
    canon_sha, dom_rel = None, 0
    if dom_h is not None:
        rows = sorted(tuple(int(x) for x in ln.split()) for ln in first[dom_h])
        dom_rel = len(rows)
        canon = ";".join(f"{a},{b},{d}" for a, b, d in rows).encode()
        canon_sha = hashlib.sha256(canon).hexdigest()
    return dict(runs=n, distinct=k, chao1=chao1, freq=freq[:10],
                curve=order[::step][:13], bad=bad, trailing=trailing,
                dom_rel=dom_rel, canon_sha=canon_sha)

def main(paths):
    for path in paths:
        name = "MANDATORY" if "m_all" in path or "m_pool" in path else \
               "CONTROL" if "ctrl" in path else path
        print(f"reducing {path} ...", file=sys.stderr)
        try:
            r = reduce(path)
        except FileNotFoundError:
            print(f"{name}: (absent: {path})"); continue
        print(f"{name}: runs {r['runs']:,}  distinct {r['distinct']}  "
              f"Chao1 {r['chao1']:.1f}  corrupt {r['bad']}  "
              f"trailing-heldout {r['trailing']}")
        print(f"  curve {r['curve']}")
        print(f"  freq  {r['freq']}")
        if r['runs']:
            print(f"  95% miss bound on an unseen reading: p < {3.0/r['runs']:.2e} per run")
        print(f"  dominant reading: {r['dom_rel']} relations, canonical sha256 "
              f"{r['canon_sha'][:16]}...")
        if name == "MANDATORY":
            ok = (r['canon_sha'] == CERT_SHA and r['dom_rel'] == CERT_REL
                  and r['distinct'] == 1)
            print(f"  [{'PASS' if ok else 'FAIL'}] matches the certified object "
                  f"(794 relations, sandbox sha {CERT_SHA[:16]}...) "
                  f"and distinct == 1")
        if name == "CONTROL":
            print(f"  reference: FR162 exhaustive answer is 68 distinct")

if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else ["mand/m_all.txt", "ctrl_all.txt"])
