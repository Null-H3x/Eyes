"""Cipher fingerprint — does a stack of cut-parameterized transforms reveal
structure?  (The keyless-stack / GAK-xGAK-style hypothesis.)

Complementary to :mod:`cribdrag` (which attacks the keystream/depth model): here
we test the community's *"combination of cipher types, with or without a cut"*
idea — that the ciphertext is a composition of low-parameter, invertible
transforms rather than a keystream.

Bounded by a clean observation
------------------------------
A structure score based on **sequential predictability** (does the next symbol
depend on the previous?) is **invariant under substitution** — relabelling
symbols (add/multiply/affine/Beaufort) preserves bigram structure.  So such a
score can only ever *resolve* the **transposition / sequence** part of a stack;
the substitution part is, by construction, invisible to it.  That is exactly the
corpus's situation (flat unigram = substitution leaves no order trace), and it
shrinks the search from ``N!``-heat-death to a small space of transposition
parameters.  We therefore fingerprint over transposition/sequence transforms and
report substitution as *unresolvable by this signal* (cribdrag / a frequency
anchor is what would pin it).

Honesty
-------
If **no** transform stack restores sequential structure, that is itself
informative: it is evidence *for* a keystream cipher (cribdrag's model) and
*against* the keyless-stack hypothesis.  The selftest proves the machinery
recovers a *planted* transposition; it does not promise the real corpus has one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from langdetect import order_predictability

# ---------------------------------------------------------------------------
# Invertible transforms (sequence / transposition family) + substitutions
# ---------------------------------------------------------------------------


def _columnar_perm(L: int, w: int) -> List[int]:
    return [i for r in range(w) for i in range(r, L, w)]


def columnar(seq: Sequence[int], w: int) -> List[int]:
    perm = _columnar_perm(len(seq), w)
    return [seq[p] for p in perm]


def uncolumnar(seq: Sequence[int], w: int) -> List[int]:
    perm = _columnar_perm(len(seq), w)
    out = [0] * len(seq)
    for k, p in enumerate(perm):
        out[p] = seq[k]
    return out


def _railfence_perm(L: int, r: int) -> List[int]:
    if r < 2:
        return list(range(L))
    rows: List[List[int]] = [[] for _ in range(r)]
    row, step = 0, 1
    for i in range(L):
        rows[row].append(i)
        if row == 0:
            step = 1
        elif row == r - 1:
            step = -1
        row += step
    return [i for row_ in rows for i in row_]


def railfence(seq: Sequence[int], r: int) -> List[int]:
    perm = _railfence_perm(len(seq), r)
    return [seq[p] for p in perm]


def unrailfence(seq: Sequence[int], r: int) -> List[int]:
    perm = _railfence_perm(len(seq), r)
    out = [0] * len(seq)
    for k, p in enumerate(perm):
        out[p] = seq[k]
    return out


def reverse(seq: Sequence[int]) -> List[int]:
    return list(reversed(seq))


def delta(seq: Sequence[int], N: int) -> List[int]:
    return [seq[0]] + [(seq[i] - seq[i - 1]) % N for i in range(1, len(seq))]


def cumsum(seq: Sequence[int], N: int) -> List[int]:
    out = [seq[0]]
    for i in range(1, len(seq)):
        out.append((out[-1] + seq[i]) % N)
    return out


# An op = (name, has_param, param_fn(L)->iterable, apply_fn(seq, param, N))
@dataclass
class Op:
    name: str
    params: Callable[[int], Sequence[int]]
    apply: Callable[[List[int], int, int], List[int]]


def transposition_ops(max_width: int = 16, max_rails: int = 9) -> List[Op]:
    return [
        Op("identity", lambda L: [0], lambda s, p, N: list(s)),
        Op("reverse", lambda L: [0], lambda s, p, N: reverse(s)),
        Op("delta", lambda L: [0], lambda s, p, N: delta(s, N)),
        Op("cumsum", lambda L: [0], lambda s, p, N: cumsum(s, N)),
        Op("uncolumnar",
           lambda L: range(2, min(max_width, max(2, L // 2)) + 1),
           lambda s, p, N: uncolumnar(s, p)),
        Op("columnar",
           lambda L: range(2, min(max_width, max(2, L // 2)) + 1),
           lambda s, p, N: columnar(s, p)),
        Op("unrailfence", lambda L: range(2, min(max_rails, max(2, L // 2)) + 1),
           lambda s, p, N: unrailfence(s, p)),
        Op("railfence", lambda L: range(2, min(max_rails, max(2, L // 2)) + 1),
           lambda s, p, N: railfence(s, p)),
    ]


# ---------------------------------------------------------------------------
# Fingerprint search
# ---------------------------------------------------------------------------

Stack = Tuple[Tuple[str, int], ...]


@dataclass
class FingerprintResult:
    stack: Stack
    score: float                    # mean per-message order predictability (bits)
    z: float                        # vs random-stack decoy null
    detected: bool


def _apply_stack(seq: List[int], stack: Stack, ops: Dict[str, Op], N: int
                 ) -> List[int]:
    out = list(seq)
    for (name, param) in stack:
        out = ops[name].apply(out, param, N)
    return out


def _score(messages: Sequence[Sequence[int]], stack: Stack, ops: Dict[str, Op],
           N: int, body_start: int) -> float:
    vals = []
    for m in messages:
        t = _apply_stack(list(m), stack, ops, N)[body_start:]
        if len(t) >= 10:
            vals.append(order_predictability(t))
    return float(np.mean(vals)) if vals else 0.0


def _enumerate(ops: List[Op], L: int, max_len: int) -> List[Stack]:
    singles: List[Stack] = []
    for op in ops:
        for p in op.params(L):
            singles.append(((op.name, int(p)),))
    stacks = list(singles)
    if max_len >= 2:
        for a in singles:
            for b in singles:
                if a == b:
                    continue
                stacks.append(a + b)
    return stacks


def fingerprint(messages: Sequence[Sequence[int]], N: int, max_len: int = 1,
                body_start: int = 0, max_width: int = 16, max_rails: int = 9,
                n_decoy: int = 60, seed: int = 0, top: int = 15
                ) -> List[FingerprintResult]:
    """Rank transform stacks by restored sequential structure, with a
    random-stack decoy null for the trust gate."""
    op_list = transposition_ops(max_width, max_rails)
    ops = {op.name: op for op in op_list}
    Lmin = min(len(m) for m in messages)
    stacks = _enumerate(op_list, Lmin, max_len)

    scored = [(st, _score(messages, st, ops, N, body_start)) for st in stacks]
    scored.sort(key=lambda x: -x[1])

    # Decoy null: random stacks (same shape distribution) score the noise floor.
    rng = np.random.default_rng(seed)
    decoy = []
    for _ in range(n_decoy):
        st = stacks[rng.integers(0, len(stacks))]
        decoy.append(_score(messages, st, ops, N, body_start))
    mu, sd = float(np.mean(decoy)), float(np.std(decoy, ddof=1) or 1e-9)

    out = []
    for st, sc in scored[:top]:
        z = (sc - mu) / sd
        out.append(FingerprintResult(stack=st, score=sc, z=z,
                                     detected=bool(z > 5 and sc > max(decoy))))
    return out


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _markov(N: int, T: int, rng: np.random.Generator) -> List[int]:
    bi = np.zeros((N, N))
    for a in range(N):
        row = rng.random(N) ** 6
        row[(a + 1) % N] += 8.0
        bi[a] = row / row.sum()
    s = int(rng.integers(0, N))
    out = [s]
    for _ in range(T - 1):
        s = int(rng.choice(N, p=bi[s]))
        out.append(s)
    return out


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(5)

    # Round-trip KATs for the transposition permutations.
    s = list(range(20))
    out.append(("columnar round-trip", uncolumnar(columnar(s, 7), 7) == s))
    out.append(("railfence round-trip", unrailfence(railfence(s, 4), 4) == s))
    out.append(("reverse involution", reverse(reverse(s)) == s))
    out.append(("delta/cumsum inverse",
                cumsum(delta([3, 9, 2, 50, 11], N), N) == [3, 9, 2, 50, 11]))

    # Substitution invariance of the order score (the bounding insight).
    mk = _markov(N, 400, rng)
    add_k = [(x + 17) % N for x in mk]
    out.append(("order score is substitution-invariant",
                abs(order_predictability(mk) - order_predictability(add_k))
                < 1e-9))

    # Plant a columnar(w=7) transposition on Markov messages; fingerprint must
    # recover uncolumnar(7) as the top stack and beat the decoy null.
    msgs = [_markov(N, 120, rng) for _ in range(6)]
    enc = [columnar(m, 7) for m in msgs]
    res = fingerprint(enc, N, max_len=1, n_decoy=60, seed=1, top=5)
    top = res[0]
    out.append(("planted columnar recovered as top stack",
                top.stack == (("uncolumnar", 7),)))
    out.append(("recovered stack clears the decoy null", top.detected))

    # Null: uniform-random ciphertext -> no stack restores structure.
    rnd = [rng.integers(0, N, size=120).tolist() for _ in range(6)]
    res_null = fingerprint(rnd, N, max_len=1, n_decoy=60, seed=2, top=5)
    out.append(("uniform ciphertext -> no stack detected",
                not res_null[0].detected))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} cipher_fingerprint checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
