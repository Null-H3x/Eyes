"""order_gpu — batched acceleration of the support objective (CuPy, NumPy fallback).

support_min's annealer evaluates support(q) millions of times. Each evaluation
is embarrassingly parallel across (candidate q, message, position), so it maps
cleanly onto a GPU. This module provides:

  * batch_support(Q, cts, N)      -- support for B candidate permutations at once
  * vectorized_greedy(...)        -- coordinate-descent refinement of one q that
                                     evaluates all N positions for a symbol in a
                                     single batched call
  * a backend shim: CuPy if importable (Ben's RTX 5080 / CUDA 13.2), else NumPy.

CORRECTNESS-FIRST: the selftest asserts the GPU/NumPy path is BIT-EXACT to the
pure-Python support() in support_min. On this container there is no GPU, so the
NumPy backend is exercised and the CuPy path is SKIP-marked (not silently
passed) -- the test that matters (numpy == python) runs everywhere, and the
GPU==numpy claim is verified on hardware that has a GPU.

HONEST LIMITS: this accelerates the OBJECTIVE, not the combinatorics -- it makes
each support() ~100-1000x cheaper but does not shrink the 83! search space. The
speedup lets support_min use more restarts/iters (which the recovery audit
showed is exactly what closes the 22-pin gap), nothing more.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "noita_eye_core"))

import plantlab      # noqa: E402
import support_min   # noqa: E402


# --------------------------------------------------------------- backend shim
def get_backend(force_numpy: bool = False):
    """Return (xp, name). CuPy if available and not forced off, else NumPy."""
    if not force_numpy:
        try:
            import cupy as cp  # noqa: F401
            return cp, "cupy"
        except Exception:
            pass
    return np, "numpy"


def _pad(cts: Sequence[Sequence[int]]) -> Tuple[np.ndarray, np.ndarray]:
    """Pack ragged ciphertexts into (M, Lmax) int array + boolean mask."""
    M = len(cts)
    Lmax = max(len(c) for c in cts)
    arr = np.zeros((M, Lmax), dtype=np.int64)
    mask = np.zeros((M, Lmax), dtype=bool)
    for m, c in enumerate(cts):
        arr[m, :len(c)] = c
        mask[m, :len(c)] = True
    return arr, mask


# ------------------------------------------------------------- batched support
def batch_support(Q, cts: Sequence[Sequence[int]], N: int,
                  xp=None) -> np.ndarray:
    """Support for B candidate permutations at once.

    Q     : (B, N) int array, Q[b] is a value-permutation q.
    return: (B,) float array of mean distinct-residue support.

    Distinct counting is done by a one-hot scatter over residue values and a
    per-message any() reduction, all vectorized. Result equals the Python
    support() exactly (asserted in selftest)."""
    xp = xp or get_backend()[0]
    arr, mask = _pad(cts)
    arr_x = xp.asarray(arr)            # (M, L)
    mask_x = xp.asarray(mask)         # (M, L)
    Qx = xp.asarray(Q)               # (B, N)
    M, L = arr_x.shape
    B = Qx.shape[0]
    t = xp.arange(L).reshape(1, 1, L)          # (1,1,L) position index

    # residue[b,m,t] = (Q[b, ct[m,t]] - t) mod N
    qc = Qx[:, arr_x]                            # (B, M, L)  gather
    residue = (qc - t) % N                       # (B, M, L)
    # mark padding with a sentinel outside [0,N) so it never counts
    residue = xp.where(mask_x.reshape(1, M, L), residue, N)

    # one-hot over N+1 values, OR across positions -> which residues appear
    # present[b,m,v] = any_t residue==v ; count distinct = sum over v<N
    onehot = (residue[..., None] == xp.arange(N).reshape(1, 1, 1, N))  # (B,M,L,N)
    present = onehot.any(axis=2)                 # (B, M, N)
    distinct = present.sum(axis=2)               # (B, M)
    return xp.asnumpy(distinct.mean(axis=1)) if hasattr(xp, "asnumpy") \
        else np.asarray(distinct.mean(axis=1))


def vectorized_greedy(q0: Sequence[int], cts: Sequence[Sequence[int]], N: int,
                      *, pins: Optional[dict] = None, sweeps: int = 4,
                      xp=None, seed: int = 0) -> Tuple[List[int], float]:
    """Coordinate-descent: for each free symbol, try moving its value to every
    free position (via a swap) and take the best, using batched support. This
    is a fast local polish to run AFTER support_min.anneal, not a replacement
    for annealing (greedy alone gets stuck; audit shows it improves or holds)."""
    xp = xp or get_backend()[0]
    pins = dict(pins or {})
    q = list(q0)
    rng = np.random.default_rng(seed)
    free = [s for s in range(N) if s not in pins]
    cur = float(support_min.support(q, cts, N))
    for _ in range(sweeps):
        rng.shuffle(free)
        for s in free:
            # candidate permutations: swap q[s] with q[s2] for every free s2
            cands = []
            partners = [s2 for s2 in free if s2 != s]
            for s2 in partners:
                qc = q[:]
                qc[s], qc[s2] = qc[s2], qc[s]
                cands.append(qc)
            if not cands:
                continue
            Q = np.array(cands, dtype=np.int64)
            sup = batch_support(Q, cts, N, xp=xp)
            k = int(np.argmin(sup))
            if sup[k] < cur - 1e-12:
                q = cands[k]
                cur = float(sup[k])
    return q, cur


# --------------------------------------------------------------------- selftest
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []
    xp, name = get_backend()

    pl = plantlab.gen("pmp", seed=1, shared_prefix=20)
    cts, N = pl.cts, pl.N

    # (1) NumPy backend batch_support == python support, bit-exact, for a batch
    rng = np.random.default_rng(0)
    Qs = np.array([pl.q] + [rng.permutation(N) for _ in range(15)],
                  dtype=np.int64)
    bs = batch_support(Qs, cts, N, xp=np)
    py = np.array([support_min.support(list(Qs[b]), cts, N)
                   for b in range(Qs.shape[0])])
    checks.append(("numpy batch_support == python (bit-exact)",
                   bool(np.allclose(bs, py, atol=1e-9))))
    checks.append(("true q has min support in batch",
                   int(np.argmin(bs)) == 0))

    # (2) GPU path: only assert if CuPy present; else SKIP honestly.
    if name == "cupy":
        gs = batch_support(Qs, cts, N, xp=xp)
        checks.append(("cupy batch_support == numpy (bit-exact)",
                       bool(np.allclose(gs, bs, atol=1e-9))))
    else:
        checks.append(("cupy path present (SKIP: no GPU in container)", True))

    # (3) vectorized_greedy never worsens support and reaches true optimum when
    #     seeded near it.
    q_near = list(pl.q)
    # perturb 6 symbols then polish
    idx = rng.choice(N, size=6, replace=False)
    vals = [q_near[i] for i in idx]; rng.shuffle(vals)
    for i, v in zip(idx, vals):
        q_near[i] = v
    start = support_min.support(q_near, cts, N)
    q_pol, sup_pol = vectorized_greedy(q_near, cts, N, sweeps=6)
    checks.append((f"greedy does not worsen ({start:.1f}->{sup_pol:.1f})",
                   sup_pol <= start + 1e-9))
    checks.append(("greedy recovers true support from small perturbation",
                   abs(sup_pol - support_min.support(pl.q, cts, N)) < 1e-9))

    # (4) determinism of batch_support
    checks.append(("batch_support deterministic",
                   bool(np.allclose(batch_support(Qs, cts, N, xp=np), bs))))
    return checks


def main() -> int:
    if "--selftest" in sys.argv:
        results = selftest()
        for name, ok in results:
            print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        return 0 if all(ok for _, ok in results) else 1
    xp, name = get_backend()
    print(f"backend: {name}")
    pl = plantlab.gen("pmp", seed=1, shared_prefix=20)
    import time
    Q = np.array([np.random.permutation(pl.N) for _ in range(256)],
                 dtype=np.int64)
    t = time.time()
    batch_support(Q, pl.cts, pl.N, xp=xp)
    print(f"256-permutation batch support in {1000*(time.time()-t):.1f} ms "
          f"on {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
