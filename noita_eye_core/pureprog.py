"""Pure-progressive alphabet recovery + decryption attempt.

The literal universal (66,5) header forces the per-message-progressive family down
to PURE PROGRESSIVE: c[t] = C[(p[t] + t) mod N], so x[c] = (p[t] + t), x = C^{-1}.

Two consequences this module exploits:
  * RECOVERY. Isomorph pairs give x[D] - x[A] = (p2 - p1); chaining them recovers
    the cipher alphabet x up to ONE global rotation. There are no per-message
    bases (the header killed them), so cross-message pairs constrain x directly.
  * DECRYPTION. Once x is known (up to rotation r), the plaintext is
    p[t] = x[c[t]] - t  (= true plaintext + r), i.e. the whole corpus decrypts up
    to a single monoalphabetic relabel. IoC is invariant under that relabel, so the
    IoC of the recovered plaintext stream is a SHARP test: natural-language
    plaintext keeps its (elevated) IoC; a wrong/under-determined alphabet gives ~uniform.

Reality on the eye corpus (see eyewitness/pure_progressive.py): recovery is
UNDER-DETERMINED — the clean isomorphs are essentially one repeated passage, so x
is pinned for too few symbols and the decrypted IoC sits at noise (z~2, driven by
that known repeat), far below language. The machinery is correct (validated here
on a richly-covered plant); the corpus simply lacks enough independent repeated
structure. This tool is the re-runnable gate for when more structure is found.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Tuple

from isomorph import GFSystem, IsoPair, find_isomorphs
import chain_models as cm


def recover(messages: Sequence[Sequence[int]], pairs: List[IsoPair], N: int):
    """Chain pure-progressive constraints; return (x, linked_largest_component)."""
    gf = GFSystem(N)
    parent = list(range(N))

    def find(z):
        while parent[z] != z:
            parent[z] = parent[parent[z]]
            z = parent[z]
        return z
    for pr in pairs:
        for (row, rhs), i in zip(cm.pure_prog_rows(pr, messages, N), range(pr.length)):
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            gf.add(row, rhs)
            parent[find(A)] = find(D)
    val = gf.solve()
    x = {s: val[s] for s in range(N) if s in val}
    # largest linked component of symbols
    comp: Dict[int, List[int]] = {}
    for s in x:
        comp.setdefault(find(s), []).append(s)
    big = max(comp.values(), key=len) if comp else []
    return x, set(big)


def decrypt_stream(messages, x: Dict[int, int], N: int):
    """p[t] = x[c[t]] - t for every position whose ciphertext symbol is recovered."""
    out = []
    dec = tot = 0
    for msg in messages:
        for t, cc in enumerate(msg):
            tot += 1
            if cc in x:
                out.append((x[cc] - t) % N)
                dec += 1
    return out, dec, tot


def ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(seq).values()) / (n * (n - 1))


def _ioc_z_given_x(messages, x, N, n_null, seed) -> dict:
    import numpy as np
    stream, dec, tot = decrypt_stream(messages, x, N)
    obs = ioc(stream)
    rng = np.random.default_rng(seed)
    syms = list(x)
    nulls = []
    for _ in range(n_null):
        rp = {s: int(rng.integers(0, N)) for s in syms}
        ns = [(rp[cc] - t) % N for msg in messages
              for t, cc in enumerate(msg) if cc in rp]
        nulls.append(ioc(ns))
    nm = float(np.mean(nulls)); nsd = float(np.std(nulls))
    return {"recovered": len(x), "distinct_positions": len(set(x.values())),
            "decrypt_frac": dec / max(1, tot), "ioc": obs,
            "ioc_null_mean": nm, "ioc_null_sd": nsd,
            "ioc_z": (obs - nm) / (nsd + 1e-9)}


def ioc_test(messages, pairs, N, n_null: int = 300, seed: int = 0) -> dict:
    """Recover under pure progressive, decrypt, and score the stream's IoC against
    a random-alphabet null (assign random positions to the same recovered symbols)."""
    x, big = recover(messages, pairs, N)
    res = _ioc_z_given_x(messages, x, N, n_null, seed)
    res["injective_ratio"] = len(set(x.values())) / max(1, len(big))
    return res


# ---------------------------------------------------------------------------
# Selftest — the machinery RECOVERS + DECRYPTS when coverage is sufficient.
# ---------------------------------------------------------------------------

def _clean_pairs(M, positions, L):
    inst = [(m, p) for m in range(M) for p in positions]
    out = []
    for a in range(len(inst)):
        for b in range(a + 1, len(inst)):
            (m1, p1), (m2, p2) = inst[a], inst[b]
            out.append(IsoPair(m1, p1, m2, p2, L, False))
    return out


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    Cinv = {s: i for i, s in enumerate(C)}

    # (A) RECOVERY MATH (KAT): a constant-plaintext RUN gives offset-1 isomorphs
    #     that chain consecutive alphabet symbols into ONE component; recovery must
    #     match the true alphabet order up to a single rotation.
    T = 70
    m0 = [int(rng.integers(0, 40)) for _ in range(T)]
    for t in range(10, 55):
        m0[t] = 5                                   # constant run, value 5
    msgsA = [[C[(p + t) % N] for t, p in enumerate(m0)]]
    pairsA = [IsoPair(0, 10, 0, 11, 44, False)]     # run vs run shifted by 1
    x, big = recover(msgsA, pairsA, N)
    rot = Counter((x[s] - Cinv[s]) % N for s in big if s in Cinv)
    dom = rot.most_common(1)[0][1] if rot else 0
    out.append(("recovery math: linked component matches true alphabet up to one "
                "rotation", dom >= 40 and dom == sum(rot.values())))
    out.append(("recovery is injective over the linked component",
                len({x[s] for s in big}) == len(big) and len(big) >= 40))

    # (B) decrypt KAT: with the TRUE alphabet, p = x[c]-t recovers plaintext+rot.
    xt = dict(Cinv)
    dec, _, _ = decrypt_stream(msgsA, xt, N)
    true_p = list(m0)
    r = (dec[0] - true_p[0]) % N
    out.append(("decrypt with true alphabet == plaintext up to one constant",
                all((dec[i] - true_p[i]) % N == r for i in range(len(dec)))))

    # (C) IoC discrimination with the TRUE alphabet: a LOW-ENTROPY (language-like)
    #     plaintext keeps elevated IoC; a UNIFORM-random plaintext does not.
    lang = []
    for _ in range(6):
        p = [int(rng.choice(12, p=np.array([8, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1],
                                           dtype=float) / 38)) for _ in range(T)]
        lang.append([C[(p[t] + t) % N] for t in range(T)])
    zr_lang = _ioc_z_given_x(lang, xt, N, 200, 0)["ioc_z"]
    unif = [[C[(int(rng.integers(0, N)) + t) % N] for t in range(T)] for _ in range(6)]
    zr_unif = _ioc_z_given_x(unif, xt, N, 200, 0)["ioc_z"]
    out.append(("IoC test: low-entropy plaintext clears (z>=8) under true alphabet",
                zr_lang >= 8))
    out.append(("IoC test: uniform-random plaintext does NOT clear (z<4)",
                zr_unif < 4))

    out.append(("ioc() KAT", abs(ioc([1, 1, 2, 2, 2]) - (2 + 6) / 20) < 1e-9))
    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} pureprog checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
