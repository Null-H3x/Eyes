"""Known-position crib attack on the 4x repeated refrain.

The extractor certified a 15-glyph passage that repeats at 4 KNOWN positions
(West1@38/@68, East2@43/@78) as the SAME plaintext. Under the live pure-progressive
model  c[t] = C[(p[t] + t) mod N]  (so x[c] := C^{-1}[c] = p[t] + t), a guessed
plaintext value p[i] at a KNOWN absolute position a pins the cipher alphabet
ABSOLUTELY:  x[c] = p[i] + a   (no rotation freedom — that is the power of a
known-position crib vs the structure-only extractor, which was under-determined).

Attack: given a candidate refrain phrase (+ a plaintext-alphabet ordering to turn
letters into values), pin x[c] from all 4 instances. A wrong guess makes a symbol
that recurs across slots demand two different x[c] -> CONTRADICTION (rejected).
A surviving guess pins up to ~60 symbol slots; decrypt every corpus position whose
ciphertext symbol is now pinned, and score the result's IoC against a null. A
CORRECT refrain lights IoC up across the whole corpus; a coincidental pass does not.

Honesty: the IoC signal depends on the chosen ordering (a wrong ordering scrambles
plaintext-value gaps). So this is a JOINT (phrase, ordering) test. It is sharp on
consistency and, for the right pair, decisive on IoC — validated on plants below.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# Character set read off noita-alphabet2.png (A-Z a-z 0-9 , . ? ' then symbols).
# The ORDERING is a hypothesis; only relative structure + rendering depend on it.
DEFAULT_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz"
                    "0123456789,.?'"
                    "!@#&*()_+-=[]:;<>/")

# The full 4x repeated region (message index, start position). The maximal extent
# where all four instances share plaintext is 25 glyphs (W1@32, W1@62, E2@37, E2@72);
# pinning it covers 59/83 symbols (~78% of the corpus). A shorter candidate phrase
# is placed at an offset inside this region (see refrain_attack.py's sweep).
DEFAULT_INSTANCES = [(1, 32), (1, 62), (2, 37), (2, 72)]
DEFAULT_LEN = 25


@dataclass
class AttackResult:
    consistent: bool
    contradiction_at: Optional[Tuple[int, int]]   # (instance, slot) if rejected
    symbols_pinned: int
    coverage: float                # fraction of corpus positions decryptable
    ioc: float
    ioc_null_mean: float
    ioc_null_sd: float
    ioc_z: float
    pinned: Dict[int, int] = field(default_factory=dict, repr=False)


def phrase_to_values(phrase: str, alphabet: str, N: int) -> Optional[List[int]]:
    idx = {ch: i for i, ch in enumerate(alphabet)}
    out = []
    for ch in phrase:
        if ch not in idx:
            return None
        out.append(idx[ch] % N)
    return out


def _ioc(seq) -> float:
    n = len(seq)
    return sum(v * (v - 1) for v in Counter(seq).values()) / (n * (n - 1)) if n > 1 else 0.0


def pin_from_refrain(messages, plain_values, instances, N):
    """Pin x[c] = p[i] + (pos+i) from every refrain instance. Returns
    (pinned, contradiction_at)."""
    pinned: Dict[int, int] = {}
    L = len(plain_values)
    for inst, (m, pos) in enumerate(instances):
        for i in range(L):
            c = int(messages[m][pos + i])
            v = (plain_values[i] + pos + i) % N
            if c in pinned and pinned[c] != v:
                return pinned, (inst, i)
            pinned[c] = v
    return pinned, None


def decrypt_with(messages, pinned, N) -> Tuple[List[int], int, int]:
    out, dec, tot = [], 0, 0
    for m in messages:
        for t, c in enumerate(m):
            tot += 1
            c = int(c)
            if c in pinned:
                out.append((pinned[c] - t) % N)
                dec += 1
    return out, dec, tot


def attack(messages, phrase_values, N, instances=None, n_null: int = 400,
           seed: int = 0) -> AttackResult:
    import numpy as np
    if instances is None:
        instances = DEFAULT_INSTANCES
    pinned, contra = pin_from_refrain(messages, phrase_values, instances, N)
    if contra is not None:
        return AttackResult(False, contra, len(pinned), 0.0, 0.0, 0.0, 0.0, 0.0, pinned)
    stream, dec, tot = decrypt_with(messages, pinned, N)
    obs = _ioc(stream)
    # null: random refrain plaintext of the same length, same pinning machinery
    rng = np.random.default_rng(seed)
    L = len(phrase_values)
    nulls = []
    for _ in range(n_null):
        q = [int(rng.integers(0, N)) for _ in range(L)]
        pj, cj = pin_from_refrain(messages, q, instances, N)
        if cj is not None:
            continue
        sj, _, _ = decrypt_with(messages, pj, N)
        nulls.append(_ioc(sj))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    return AttackResult(True, None, len(pinned), dec / max(1, tot), obs, nm, nsd,
                        (obs - nm) / (nsd + 1e-9), pinned)


def render(messages, pinned, alphabet, N) -> List[str]:
    out = []
    for m in messages:
        s = []
        for t, c in enumerate(m):
            c = int(c)
            if c in pinned:
                p = (pinned[c] - t) % N
                s.append(alphabet[p] if p < len(alphabet) else "·")
            else:
                s.append("·")
        out.append("".join(s))
    return out


# ---------------------------------------------------------------------------
# Selftest — validate on a planted pure-progressive corpus with a known refrain.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))               # secret cipher alphabet
    order = DEFAULT_ALPHABET                    # plaintext ordering (true)
    A = len(order)

    # low-entropy "language-like" plaintext over the alphabet; a fixed refrain
    # placed at 4 positions across 2 messages.
    w = np.array([8, 6, 5, 4, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1], dtype=float)
    vocab = [int(v) for v in rng.choice(A, size=16, replace=False)]
    def draw():
        return vocab[int(rng.choice(len(vocab), p=w / w.sum()))]
    refrain_vals = [draw() for _ in range(DEFAULT_LEN)]
    T = 120
    insts = [(0, 38), (0, 68), (1, 43), (1, 78)]
    msgs = []
    for m in range(2):
        p = [draw() for _ in range(T)]
        for (mm, pos) in insts:
            if mm == m:
                p[pos:pos + DEFAULT_LEN] = refrain_vals
        msgs.append([C[(p[t] + t) % N] for t in range(T)])

    # CORRECT refrain values -> consistent, large pin, high IoC
    r = attack(msgs, [v % N for v in refrain_vals], N, instances=insts, n_null=200)
    out.append(("correct refrain is consistent", r.consistent))
    out.append(("correct refrain pins many symbols (>=30)", r.symbols_pinned >= 30))
    out.append(("correct refrain lights IoC up (z>=8)", r.ioc_z >= 8))

    # WRONG refrain (shuffle) -> usually contradiction; if it survives, low IoC
    bad = list(refrain_vals); rng.shuffle(bad)
    bad = [(v + 1) % N for v in bad]
    rb = attack(msgs, bad, N, instances=insts, n_null=100)
    out.append(("a wrong refrain is rejected OR scores low (not a false hit)",
                (not rb.consistent) or rb.ioc_z < 4))

    # consistency is a genuine filter: random refrains mostly contradict
    rng2 = np.random.default_rng(7)
    surv = 0
    for _ in range(200):
        q = [int(rng2.integers(0, N)) for _ in range(DEFAULT_LEN)]
        _, c = pin_from_refrain(msgs, q, insts, N)
        if c is None:
            surv += 1
    out.append(("random refrains mostly contradict (consistency filters)",
                surv < 120))

    # phrase_to_values maps via ordering and rejects out-of-alphabet chars
    out.append(("phrase_to_values maps letters", phrase_to_values("BA", order, N) == [1, 0]))
    out.append(("phrase_to_values rejects unknown char",
                phrase_to_values("~", order, N) is None))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} refrain checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
