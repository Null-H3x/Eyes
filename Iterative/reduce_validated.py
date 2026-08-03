#!/usr/bin/env python3
"""reduce2 -- validated reduction: every signature block must match its R-line's
declared row count; the trailing block of a live file is held out; mismatched
blocks are reported, never counted."""
import sys
from collections import Counter

def reduce(path):
    sigs = Counter(); order = []
    cur = None; rows = []; declared = None
    bad = 0; heldout = 0
    def commit(final):
        nonlocal bad, heldout
        if cur is None: return
        if len(rows) != declared:
            if final: heldout += 1
            else: bad += 1
            return
        sigs[tuple(sorted(rows))] += 1; order.append(len(sigs))
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p: continue
            if p[0] == 'R':
                commit(final=False)
                cur = int(p[1]); declared = int(p[4]); rows = []
            else:
                if len(p) == 3: rows.append((int(p[0]), int(p[1]), int(p[2])))
                else: rows.append(None)  # malformed line -> block will mismatch
    commit(final=True)
    n = sum(sigs.values()); k = len(sigs)
    freq = sorted(sigs.values(), reverse=True)
    s1 = sum(1 for v in freq if v == 1); s2 = sum(1 for v in freq if v == 2)
    chao1 = k + (s1*(s1-1))/(2*(s2+1)) if k else 0
    step = max(1, len(order)//12) if order else 1
    return dict(runs=n, distinct=k, chao1=chao1, freq=freq[:10],
                curve=order[::step][:13], bad=bad, heldout=heldout, sigs=sigs)

if __name__ == "__main__":
    for name, path in (("MANDATORY","mand/m_all.txt"),("CONTROL","ctrl_all.txt")):
        try: r = reduce(path)
        except FileNotFoundError: print(f"{name}: (absent)"); continue
        print(f"{name}: runs {r['runs']:,}  distinct {r['distinct']}  "
              f"Chao1 {r['chao1']:.1f}  corrupt {r['bad']}  trailing-heldout {r['heldout']}")
        print(f"  curve {r['curve']}\n  freq  {r['freq']}")
        if name == "MANDATORY" and r['runs']:
            print(f"  95% miss bound: p < {3.0/r['runs']:.2e} per run")
        if r['distinct'] > 1:
            top = r['sigs'].most_common()
            main_sig = set(top[0][0])
            for s, c in top[1:4]:
                inter = len(main_sig & set(s))
                print(f"  rival (freq {c}): {len(s)} rows, overlap with dominant "
                      f"{inter}/{len(main_sig)}")
