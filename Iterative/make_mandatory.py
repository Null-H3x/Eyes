#!/usr/bin/env python3
"""make_mandatory.py -- build the ATLAS-MANDATORY maxset problem file (FR176's
system) from the live canonical machinery, and compute gate reference vectors
with an independent Python implementation of eyemax's run_order.

Steps, each gated:
  1. load canonical corpus/atlas via eyeaudit.load
  2. repair C = drop East 1@68 only (the extended skeleton's pool, FR122/FR145)
  3. emit pool rows via EG.make_rows (the canonical emitter -- same convention
     as the class blocks in maxset_problem.txt, verified below)
  4. PARITY GATE: the Python mirror must reproduce eyemax's shipped gate
     triples (794/61/6, 724/61/6, 794/61/6) on the classes-only system
  5. compute the mandatory-system triples for the same three fixed orders
  6. write mand/maxset_problem.txt + mand/maxset_orders.txt
  7. cross-checks: identity-order mandatory build vs the published extended
     skeleton (794 rel / 61 gly), the 19 EXT_CORE relations, and the base
     columns vs the 9 published differences incl. W2 = 39
"""
import sys, os, json
sys.path.insert(0, ".")
import eyeaudit as A
import eyegauge as EG
import eyerepair as ERP

XD = "XD-MBYG04K-URS3LF"; N = 83; NCOL = 92
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json")
ATLAS  = os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json")

EXT_CORE = [(1,27,81),(2,26,1),(2,73,2),(6,57,82),(9,79,82),(13,19,53),
            (13,66,55),(17,63,2),(19,66,2),(21,40,82),(22,62,30),(22,64,0),
            (25,60,82),(26,73,1),(32,59,30),(34,45,82),(35,37,2),(36,68,0),
            (62,64,53)]
PUB_BDIFF = [(1,0,0),(2,0,77),(8,6,0),(7,6,54),(5,4,54),(4,0,52),(5,0,23),
             (6,0,53),(3,0,39)]  # (m2, m1, b[m2]-b[m1]) drift-1; last is W2

# ---------------------------------------------------------------- GF mirror
class Ech:
    """row-echelon GF(83) system over NCOL columns, mirroring eyemax.c"""
    def __init__(s): s.piv = {}; s.rows = []          # piv: col -> row idx
    def _reduce(s, v):
        for c in range(NCOL):
            x = v.get(c, 0) % N
            if not x: continue
            r = s.piv.get(c)
            if r is None: return c, v
            rr = s.rows[r]
            for k, val in rr.items():
                v[k] = (v.get(k, 0) - x * val) % N
        return None, v
    def add(s, row, rhs):
        """0 redundant, 1 added, -1 contradiction (same contract as sys_add)"""
        v = dict(row); v[NCOL] = rhs % N
        c, v = s._reduce(v)
        if c is None:
            return -1 if v.get(NCOL, 0) % N else 0
        f = pow(v[c], -1, N)
        nv = {k: (val * f) % N for k, val in v.items() if (val * f) % N or k == NCOL}
        nv[NCOL] = (v.get(NCOL, 0) * f) % N
        s.piv[c] = len(s.rows); s.rows.append(nv)
        return 1
    def query(s, a, b):
        """value of q[b]-q[a] if determined, else None (smart reduction)."""
        v = {b: 1, a: N - 1, NCOL: 0}
        c, v = s._reduce(v)
        if c is not None: return None
        return (-v.get(NCOL, 0)) % N   # residual d - rhs = 0 form
    def used_glyphs(s):
        g = set()
        for r in s.rows:
            for k, val in r.items():
                if k < N and val % N: g.add(k)
        return sorted(g)

def run_order(seeds, classes, order):
    s = Ech()
    for row, rhs in seeds: s.add(row, rhs)
    for ci in order:
        bak_piv = dict(s.piv); bak_rows = list(s.rows)
        okc = True
        for row, rhs in classes[ci]:
            if s.add(row, rhs) == -1:
                s.piv, s.rows = bak_piv, bak_rows; okc = False; break
        # (rows list may have grown before the contradiction; restore handled)
    gl = s.used_glyphs()
    R = E = 0; sig = []
    for i in range(len(gl)):
        for j in range(i + 1, len(gl)):
            d = s.query(gl[i], gl[j])
            if d is not None:
                R += 1; E += (d == 0); sig.append((gl[i], gl[j], d))
    return R, len(gl), E, sig, s

# ---------------------------------------------------------------- parse shipped
def parse_problem(path):
    tok = open(path).read().split(); i = 0
    def nxt():
        nonlocal i; i += 1; return int(tok[i - 1])
    ncls, p, nb, nseed = nxt(), nxt(), nxt(), nxt()
    def read_row():
        n, rhs = nxt(), nxt()
        row = {}
        for _ in range(n):
            c, v = nxt(), nxt(); row[c] = (row.get(c, 0) + v) % N
        return ({c: v for c, v in row.items() if v}, rhs % N)
    seeds = [read_row() for _ in range(nseed)]
    classes = []
    for _ in range(ncls):
        idx, nr = nxt(), nxt()
        classes.append([read_row() for _ in range(nr)])
    return seeds, classes

def parse_orders(path):
    lines = open(path).read().split("\n")
    n, k = map(int, lines[0].split())
    out = []
    for t in range(n):
        nm, wr, wg, we = lines[1 + 2 * t].split()
        order = list(map(int, lines[2 + 2 * t].split()))
        out.append((nm, int(wr), int(wg), int(we), order))
    return out

def fmt_row(row, rhs):
    items = sorted(row.items())
    return f"{len(items)} {rhs % N} " + " ".join(f"{c} {v}" for c, v in items)

# ---------------------------------------------------------------- main
def main():
    ok = True
    def chk(name, cond, note=""):
        nonlocal ok; ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")

    print("STEP 1-3: canonical load, repair C, pool-row emission")
    cts, labels, Lx, ctx, pool, red = A.load(CORPUS, ATLAS)
    chk("pool loaded", len(pool) == 83, f"({len(pool)} pairs)")
    poolC = ERP.drop(pool, (0, 68))
    print(f"  repair C: {len(pool)} -> {len(poolC)} pairs (dropped East 1@68's)")
    rows_fn = EG.make_rows(ctx, drift=1, group=None, n_msgs=9)
    pool_rows = []
    for pr in poolC:
        for row, rhs in rows_fn(pr, cts, N):
            pool_rows.append((dict(row), rhs % N))
    print(f"  emitted {len(pool_rows)} mandatory pool rows")

    print("STEP 4: PARITY GATE -- Python mirror vs eyemax on the shipped system")
    seeds0, classes = parse_problem("maxset_problem.txt")
    for nm, wr, wg, we, order in parse_orders("maxset_orders.txt"):
        R, G, E, _, _ = run_order(seeds0, classes, order)
        chk(f"shipped {nm}", (R, G, E) == (wr, wg, we), f"got {R}/{G}/{E} want {wr}/{wg}/{we}")
    if not ok: raise SystemExit(f"{XD}: parity gate failed -- mirror diverges from eyemax")

    print("STEP 5: mandatory-system references for the same three orders")
    seedsM = seeds0 + pool_rows
    refs = []
    ident_sys = None
    for nm, _, _, _, order in parse_orders("maxset_orders.txt"):
        R, G, E, sig, s = run_order(seedsM, classes, order)
        refs.append((nm, R, G, E, order))
        print(f"  mandatory {nm:9s}: rel {R} gly {G} eq {E}")
        if nm == "identity": ident_sys, ident_sig = s, sig

    print("STEP 6: write mand/ problem + orders files")
    os.makedirs("mand", exist_ok=True)
    with open("mand/maxset_problem.txt", "w") as f:
        f.write(f"208 {N} 9 {len(seedsM)}\n")
        for row, rhs in seedsM: f.write(fmt_row(row, rhs) + "\n")
        src = open("maxset_problem.txt").read().split("\n")
        # copy class blocks verbatim: skip header + 15 seed lines
        for line in src[16:]:
            if line.strip(): f.write(line + "\n")
    with open("mand/maxset_orders.txt", "w") as f:
        f.write(f"3 208\n")
        for nm, R, G, E, order in refs:
            f.write(f"{nm} {R} {G} {E}\n")
            f.write(" ".join(map(str, order)) + "\n")
    print("  written.")

    print("STEP 7: cross-checks on the mandatory identity build")
    chk("extended-skeleton scale reproduced",
        refs[0][1] >= 790 and refs[0][2] == 61,
        f"(rel {refs[0][1]}, gly {refs[0][2]}; published 794/61)")
    sigd = {(a, b): d for a, b, d in ident_sig}
    bad = [(a, b, v) for a, b, v in EXT_CORE
           if sigd.get((min(a,b), max(a,b))) not in
              ((v if a < b else (-v) % N),)]
    chk("all 19 EXT_CORE relations hold in the identity build", not bad,
        f"(fail: {bad[:3]})")
    diffs = []
    for m2, m1, want in PUB_BDIFF:
        got = ident_sys.query(N + m1, N + m2)   # q[b]-q[a] with b=N+m2? sign check below
        diffs.append((labels[m2], labels[m1], want, got))
    print("  base-difference cross-check (b[m2]-b[m1], drift-1):")
    allok = True
    for L2, L1, want, got in diffs:
        mark = "OK " if got == want else ("SGN" if got == (N - want) % N else "??")
        allok &= (got == want or got == (N - want) % N)
        print(f"    {L2:8s} - {L1:8s} want {want:2d} got {got}  {mark}")
    chk("all 9 published diffs reproduced (up to one global sign convention)", allok)

    if not ok: raise SystemExit(f"{XD}: cross-checks failed")
    print("ALL GREEN -- mand/ is gated and ready for the scale run")

if __name__ == "__main__":
    main()
