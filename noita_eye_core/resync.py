"""Re-sync test: excludes content-dependent (autokey) keystreams.

Two messages that share a key and are near-duplicate plaintext (E1/W1: 44%
identical, in blocks) reveal the keystream's NATURE by how their ciphertext
behaves across plaintext edits:

  * POSITION-indexed keystream  c[t]=E(p[t], K(t))  — identical ciphertext iff
    identical plaintext (same key). Re-syncs to identical the instant plaintext
    re-matches, however many times. RE-SYNC EVENTS >> 0.
  * CONTENT-indexed keystream (autokey: keystream depends on prior plaintext or
    ciphertext) — once plaintext/ciphertext diverges, the keystream diverges and
    the difference PROPAGATES; ciphertext stays different even where plaintext
    re-matches. RE-SYNC EVENTS ~ 0.

So counting "identical → differ → identical-again" transitions in a shared-key
near-duplicate pair discriminates the two. The eye corpus E1/W1 show 5 re-sync
events.

PRECISION (audited): re-sync cleanly EXCLUDES *ciphertext*-autokey (keystream =
prior ciphertext; the difference propagates forever -> 0 re-sync). It does NOT by
itself exclude *plaintext*-autokey lag-1 (keystream = prior plaintext), which
re-syncs one position LATE wherever current AND prior plaintext re-match.
Distinguishing position-keystream (re-sync lag 0, identical exactly where plaintext
matches) from plaintext-autokey (re-sync lag 1) needs the plaintext, so it is left
open. Net: re-sync rules out ciphertext-autokey and is consistent with a
position-indexed keystream (and with lag-1 plaintext-autokey).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple


def block_structure(a: Sequence[int], b: Sequence[int]) -> List[Tuple[bool, int, int]]:
    """Runs of (identical?, start, end) over the aligned common prefix."""
    L = min(len(a), len(b))
    runs = []
    cur = None
    start = 0
    for t in range(L):
        s = (a[t] == b[t])
        if s != cur:
            if cur is not None:
                runs.append((cur, start, t - 1))
            cur, start = s, t
    if cur is not None:
        runs.append((cur, start, L - 1))
    return runs


def count_resync(a: Sequence[int], b: Sequence[int]) -> int:
    """Number of identical-run -> differing-run -> identical-run transitions."""
    runs = block_structure(a, b)
    n = 0
    for k in range(1, len(runs) - 1):
        if (not runs[k][0]) and runs[k - 1][0] and runs[k + 1][0]:
            n += 1
    return n


def identical_fraction(a, b) -> float:
    L = min(len(a), len(b))
    return sum(1 for t in range(L) if a[t] == b[t]) / L if L else 0.0


# ---------------------------------------------------------------------------
# Selftest — position keystream re-syncs; autokey does not.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    T = 120
    # a base plaintext; a near-duplicate with edited blocks
    p1 = [int(rng.integers(0, N)) for _ in range(T)]
    p2 = list(p1)
    for (s, e) in [(20, 26), (50, 58), (80, 90)]:        # edited blocks
        for t in range(s, e):
            p2[t] = int(rng.integers(0, N))

    # (1) POSITION-progressive (same base): c[t]=C[(p[t]+base+t)]
    base = 7
    c1 = [C[(p1[t] + base + t) % N] for t in range(T)]
    c2 = [C[(p2[t] + base + t) % N] for t in range(T)]
    rs_pos = count_resync(c1, c2)
    out.append(("position keystream RE-SYNCS (identical after edits), >=3 events",
                rs_pos >= 3))
    out.append(("position keystream: identical exactly where plaintext matches",
                all((c1[t] == c2[t]) == (p1[t] == p2[t]) for t in range(T))))

    # (2) CIPHERTEXT-AUTOKEY (same seed): c[t]=C[(p[t]+c[t-1])]
    def autokey(p, seed):
        c = []
        prev = seed
        for t in range(T):
            cc = C[(p[t] + prev) % N]
            c.append(cc)
            prev = cc
        return c
    a1 = autokey(p1, 5)
    a2 = autokey(p2, 5)
    rs_ak = count_resync(a1, a2)
    out.append(("autokey does NOT re-sync after an edit (events ~ 0)", rs_ak <= 1))
    out.append(("autokey re-sync << position re-sync (discriminates)",
                rs_ak < rs_pos))

    # (3) PLAINTEXT-AUTOKEY also fails to re-sync cleanly
    def pautokey(p, seed):
        c = []
        prev = seed
        for t in range(T):
            c.append(C[(p[t] + prev) % N])
            prev = p[t]
        return c
    b1 = pautokey(p1, 5); b2 = pautokey(p2, 5)
    # HONEST limit: plaintext-autokey lag-1 ALSO re-syncs (one position late), so
    # re-sync does NOT exclude it; only ciphertext-autokey is excluded.
    out.append(("plaintext-autokey ALSO re-syncs (so re-sync excludes only "
                "ciphertext-autokey, not plaintext-autokey)", count_resync(b1, b2) >= 2))
    # the discriminator vs plaintext-autokey is the LAG: position keystream is
    # identical EXACTLY where plaintext matches (lag 0); plaintext-autokey lags by 1.
    pos_lag0 = all((c1[t] == c2[t]) == (p1[t] == p2[t]) for t in range(T))
    pa_lag0 = all((b1[t] == b2[t]) == (p1[t] == p2[t]) for t in range(T))
    out.append(("lag-0 identity holds for position keystream but NOT plaintext-"
                "autokey (the remaining distinguisher needs plaintext)",
                pos_lag0 and not pa_lag0))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} resync checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
