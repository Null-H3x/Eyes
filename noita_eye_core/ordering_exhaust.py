"""Residual ordering exhaust — Phase 2 after refrain_sweep survivors.

When pin_structure leaves few free ordering slots, exhaustively permute residual
O assignments (CPU multiprocessing) or fall back to parallel hill-climb restarts.

Input: pinned x-map from pin_structure + crib-anchored O seed (order_solve logic).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import ngram_solve as ng
import order_solve as os_
import refrain as rf


@dataclass
class ExhaustResult:
    consistent: bool
    free_slots: int
    method: str
    score: float
    z: float
    word_coverage: float
    symbols_pinned: int
    ordering: List[str] = field(default_factory=list)
    plaintext: Dict[int, str] = field(default_factory=dict)


def _free_ordering_slots(messages, crib, inst, x, N) -> Tuple[List[int], List[int], set]:
    """Return (free value slots, anchored rv list, anchored set)."""
    m0, p0 = inst[0]
    rv = [(x[int(messages[m0][p0 + i])] - (p0 + i)) % N for i in range(len(crib))]
    anchored = {rr % N for rr in rv}
    free = [v for v in range(N) if v not in anchored]
    return free, rv, anchored


def _score_ordering(O, messages, vals, fixed_bases, model, aidx, N):
    Oi = [aidx[ch] for ch in O]

    def msg_shifts(seq, mi):
        present = [v for v in seq if v is not None]
        if mi in fixed_bases:
            return fixed_bases[mi], present
        best, bsh = -1e9, 0
        for sh in range(N):
            s = model.score_idx([Oi[(v - sh) % N] for v in present])
            if s > best:
                best, bsh = s, sh
        return bsh, present

    total = 0.0
    cnt = 0
    for mi, seq in enumerate(vals):
        present = [v for v in seq if v is not None]
        if len(present) < 3:
            continue
        sh, _ = msg_shifts(seq, mi)
        idxs = [Oi[(v - sh) % N] for v in present]
        total += model.score_idx(idxs) * len(present)
        cnt += len(present)
    return total / max(1, cnt)


def _build_seed_O(crib, rv, alphabet, N):
    seed_O = [None] * N
    for i, ch in enumerate(crib):
        seed_O[rv[i] % N] = ch
    pool = [ch for ch in alphabet if ch not in set(crib)] + list(alphabet)
    pi = 0
    for v in range(N):
        if seed_O[v] is None:
            seed_O[v] = pool[pi % len(pool)]
            pi += 1
    return seed_O


def exhaust_ordering(
    messages,
    crib: str,
    offset: int,
    N: int,
    *,
    alphabet=None,
    model=None,
    region=None,
    exhaust_if_free: int = 12,
    max_perms: int = 500_000,
    hillclimb_restarts: int = 20,
    n_null: int = 30,
    seed: int = 0,
) -> ExhaustResult:
    """Exhaust residual O permutations when free_slots <= exhaust_if_free."""
    import numpy as np

    if alphabet is None:
        alphabet = rf.DEFAULT_ALPHABET
    if model is None:
        model = ng.TrigramModel(alphabet, ng._ENGLISH)
    if region is None:
        region = rf.DEFAULT_INSTANCES

    inst = [(m, p + offset) for (m, p) in region]
    x, contra, fixed_bases = os_.pin_structure(messages, crib, inst, N)
    if contra is not None:
        return ExhaustResult(False, N, "rejected", 0, 0, 0, len(x))

    vals = os_._decrypt_values(messages, x, N)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    free, rv, _ = _free_ordering_slots(messages, crib, inst, x, N)
    seed_O = _build_seed_O(crib, rv, alphabet, N)

    n_perms = math.factorial(len(free)) if len(free) <= 15 else max_perms + 1
    use_exhaust = len(free) <= exhaust_if_free and n_perms <= max_perms

    if not use_exhaust:
        r = os_.solve(
            messages, crib, offset, N,
            alphabet=alphabet, model=model, region=region,
            restarts=hillclimb_restarts, iters=2500, n_null=n_null, seed=seed,
        )
        bestO = _build_seed_O(crib, rv, alphabet, N)
        if r.consistent:
            m0, p0 = inst[0]
            rv2 = [(x[int(messages[m0][p0 + i])] - (p0 + i)) % N
                   for i in range(len(crib))]
            for i, ch in enumerate(crib):
                bestO[rv2[i] % N] = ch
        return ExhaustResult(
            r.consistent, len(free), "hillclimb",
            r.score, r.z, r.word_coverage, r.symbols_pinned,
            ordering=bestO, plaintext=r.plaintext,
        )

    free_chars = [seed_O[v] for v in free]
    best_score = -1e18
    best_O = list(seed_O)
    n_try = 0
    for perm in itertools.permutations(free_chars):
        O = list(seed_O)
        for v, ch in zip(free, perm):
            O[v] = ch
        sc = _score_ordering(O, messages, vals, fixed_bases, model, aidx, N)
        if sc > best_score:
            best_score = sc
            best_O = list(O)
        n_try += 1
        if n_try >= max_perms:
            break

    rng = np.random.default_rng(seed)
    nulls = []
    Oi = [aidx[ch] for ch in best_O]
    for _ in range(n_null):
        sc = 0.0
        cnt = 0
        for seq in vals:
            present = [Oi[v] for v in seq if v is not None]
            if len(present) >= 3:
                sh = list(present)
                rng.shuffle(sh)
                sc += model.score_idx(sh) * len(sh)
                cnt += len(sh)
        nulls.append(sc / max(1, cnt))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    z = (best_score - nm) / (nsd + 1e-9)

    plaintext = {}
    all_text = []
    for mi, seq in enumerate(vals):
        sh = fixed_bases.get(mi, 0)
        txt = os_._render(seq, best_O, sh, N)
        plaintext[mi] = txt
        all_text.append(txt)
    wcov = os_._word_coverage(" ".join(all_text))

    return ExhaustResult(
        True, len(free), "exhaustive",
        best_score, z, wcov, len(x),
        ordering=best_O, plaintext=plaintext,
    )


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    crib = "trueknowledgeofthegodsabo"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=4)]
    T = 110
    msgs = []
    pos0 = 0
    for m in range(4):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]
        pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps: ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    r = exhaust_ordering(
        msgs, crib, 0, N, region=insts,
        exhaust_if_free=12, max_perms=5000,
        hillclimb_restarts=2, n_null=10,
    )
    out.append(("exhaust on plant: consistent", r.consistent))
    out.append(("exhaust on plant: z>=6", r.z >= 6))
    out.append(("exhaust reports method", r.method in ("exhaustive", "hillclimb")))
    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} ordering_exhaust checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
