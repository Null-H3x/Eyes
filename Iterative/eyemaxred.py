#!/usr/bin/env python3
"""eyemaxred -- reduce eyemax output to distinct readings and the exact
invariant core. Prints the discovery curve so saturation is visible."""
import sys
from collections import Counter

def main(path):
    import os
    if not os.path.exists(path):
        print(f"XD-MBYG04K-URS3LF: '{path}' not found.")
        print()
        print("This file is produced by run_maxset.sh. If it is missing, the")
        print("harness did not complete. Check in order:")
        print("  1. run WITHOUT sudo:   bash run_maxset.sh 1000000 32")
        print("  2. all four files in ONE directory:")
        print("       run_maxset.sh  eyemax.c  maxset_problem.txt  maxset_orders.txt")
        print("  3. if the gate failed, eyemax printed FAIL lines -- send those")
        raise SystemExit(2)
    if os.path.getsize(path) == 0:
        print(f"XD-MBYG04K-URS3LF: '{path}' is empty -- no run reached the")
        print("700-relation floor. Send the eyemax stderr output.")
        raise SystemExit(2)
    sigs = Counter(); best = 0; cur = None; rows = []; order = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p: continue
            if p[0] == 'R':
                if cur is not None and rows:
                    sigs[tuple(sorted(rows))] += 1; order.append(len(sigs))
                rows = []; cur = int(p[1]); best = max(best, cur)
            else:
                rows.append((int(p[0]), int(p[1]), int(p[2])))
    if cur is not None and rows:
        sigs[tuple(sorted(rows))] += 1; order.append(len(sigs))
    print(f"runs recorded     : {sum(sigs.values()):,}")
    print(f"DISTINCT readings : {len(sigs):,}")
    print(f"max relations     : {best}")
    freq = sorted(sigs.values(), reverse=True)
    print(f"frequency profile : {freq[:15]}{' ...' if len(freq) > 15 else ''}")
    singles = sum(1 for v in freq if v == 1)
    doubles = sum(1 for v in freq if v == 2)
    print(f"Chao1 estimate    : {len(sigs) + (singles*(singles-1))/(2*(doubles+1)):.0f}")
    if order:
        step = max(1, len(order)//12)
        print(f"discovery curve   : {order[::step]}")
    keys = list(sigs); common = set(keys[0])
    for k in keys[1:]:
        common &= set(k)
        if not common: break
    print(f"\nEXACT INVARIANT CORE : {len(common)} relations")
    for a, b, d in sorted(common):
        print(f"   q[{a}] - q[{b}] = {d}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "maxset_out.txt")
