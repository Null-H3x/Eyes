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

# The 4x repeated region (message index, start position). The per-message-
# progressive-CONSISTENT extent is 22 glyphs (W1@32, W1@62, E2@37, E2@72); the
# plaintext diverges at position 22 (an all-distinct crib contradicts at L>=23).
# (An earlier within-instance-skeleton estimate said 25, but that is a weaker test.)
DEFAULT_INSTANCES = [(1, 32), (1, 62), (2, 37), (2, 72)]
DEFAULT_LEN = 22


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
    """Per-MESSAGE-progressive pinning: x[c] = p[i] + base_m + (pos+i).

    The body uses per-message bases (pure-progressive is contradicted across the 4
    refrain instances), so we gauge the first instance's message base to 0 and
    derive every other refrain-message base from a ciphertext symbol it shares with
    an already-pinned message. A wrong guess makes a shared symbol demand two
    different x[c] (or two different bases) -> contradiction. Returns
    (pinned x:{symbol->C^{-1} value up to global rotation}, contradiction_at).
    """
    L = len(plain_values)
    by_msg: Dict[int, list] = {}
    for inst, (m, pos) in enumerate(instances):
        by_msg.setdefault(m, []).append((inst, pos))
    pinned: Dict[int, int] = {}
    base: Dict[int, Optional[int]] = {m: None for m in by_msg}
    base[instances[0][0]] = 0
    # iterate: pin messages whose base is known; derive unknown bases from overlap
    pending = set(by_msg)
    progress = True
    while pending and progress:
        progress = False
        for m in list(pending):
            if base[m] is None:
                # try to derive base[m] from a symbol shared with the pinned set
                bm = None
                for inst, pos in by_msg[m]:
                    for i in range(L):
                        c = int(messages[m][pos + i])
                        if c in pinned:
                            bm = (pinned[c] - plain_values[i] - pos - i) % N
                            break
                    if bm is not None:
                        break
                if bm is None:
                    continue
                base[m] = bm
            # pin all of message m's refrain symbols
            for inst, pos in by_msg[m]:
                for i in range(L):
                    c = int(messages[m][pos + i])
                    v = (plain_values[i] + base[m] + pos + i) % N
                    if c in pinned and pinned[c] != v:
                        return pinned, (inst, i)
                    pinned[c] = v
            pending.discard(m)
            progress = True
    return pinned, None


def viable_offsets(messages, phrase, region_instances, region_len, N):
    """ORDERING-INDEPENDENT viability: place `phrase` at each offset in the region
    and check its letter-repeat pattern is compatible with the WITHIN-instance
    ciphertext collisions (per-message-progressive: bases are free, so only
    within-instance gaps + the candidate's same-letter equalities constrain it).
    Returns the list of offsets where the candidate is possible under SOME ordering.
    """
    from isomorph import OffsetDSU
    P = len(phrase)
    # within-instance collision constraints over region positions (p[a]-p[b]=b-a)
    def base_dsu():
        d = OffsetDSU(N)
        for (m, p) in region_instances:
            occ = {}
            for k in range(region_len):
                sym = int(messages[m][p + k])
                if sym in occ:
                    if not d.union(occ[sym], k, (occ[sym] - k) % N):
                        return None
                else:
                    occ[sym] = k
        return d
    # candidate same-letter pairs
    eqs = []
    first = {}
    for i, ch in enumerate(phrase):
        if ch in first:
            eqs.append((first[ch], i))
        else:
            first[ch] = i
    ok = []
    for off in range(region_len - P + 1):
        d = base_dsu()
        if d is None:
            return []
        good = True
        for (a, b) in eqs:
            if not d.union(off + a, off + b, 0):
                good = False
                break
        if good:
            ok.append(off)
    return ok


def decrypt_message(msg, pinned, N) -> List[int]:
    """Decrypt one message up to its per-message shift: p[t] = x[c]-t (the shift is
    a constant per message, which IoC is invariant to)."""
    return [(pinned[int(c)] - t) % N for t, c in enumerate(msg) if int(c) in pinned]


def decrypt_with(messages, pinned, N) -> Tuple[List[int], int, int]:
    out, dec, tot = [], 0, 0
    for m in messages:
        tot += len(m)
        d = decrypt_message(m, pinned, N)
        out.extend(d); dec += len(d)
    return out, dec, tot


def per_message_ioc(messages, pinned, N) -> float:
    """Mean per-message IoC of the decryptable positions (shift-invariant, so the
    unknown per-message base does not matter for this score)."""
    vals = []
    for m in messages:
        d = decrypt_message(m, pinned, N)
        if len(d) >= 8:
            vals.append(_ioc(d))
    return sum(vals) / len(vals) if vals else 0.0


def attack(messages, phrase_values, N, instances=None, n_null: int = 400,
           seed: int = 0) -> AttackResult:
    import numpy as np
    if instances is None:
        instances = DEFAULT_INSTANCES
    pinned, contra = pin_from_refrain(messages, phrase_values, instances, N)
    if contra is not None:
        return AttackResult(False, contra, len(pinned), 0.0, 0.0, 0.0, 0.0, 0.0, pinned)
    stream, dec, tot = decrypt_with(messages, pinned, N)
    obs = per_message_ioc(messages, pinned, N)
    rng = np.random.default_rng(seed)
    L = len(phrase_values)
    nulls = []
    for _ in range(n_null):
        q = [int(rng.integers(0, N)) for _ in range(L)]
        pj, cj = pin_from_refrain(messages, q, instances, N)
        if cj is not None:
            continue
        nulls.append(per_message_ioc(messages, pj, N))
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
# Selftest — validate on a planted PER-MESSAGE-progressive corpus (the body's
# actual model: each message has its own base) with a known refrain.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))               # secret cipher alphabet
    order = DEFAULT_ALPHABET
    A = len(order)

    w = np.array([8, 6, 5, 4, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1], dtype=float)
    vocab = [int(v) for v in rng.choice(A, size=16, replace=False)]
    def draw():
        return vocab[int(rng.choice(len(vocab), p=w / w.sum()))]
    refrain_vals = [draw() for _ in range(DEFAULT_LEN)]
    T, Mn = 120, 5
    insts = [(0, 38), (0, 68), (1, 43), (1, 78)]   # refrain in messages 0 and 1
    bases = [int(b) for b in rng.integers(0, N, size=Mn)]   # PER-MESSAGE bases
    msgs = []
    for m in range(Mn):
        p = [draw() for _ in range(T)]
        for (mm, pos) in insts:
            if mm == m:
                p[pos:pos + DEFAULT_LEN] = refrain_vals
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    # CORRECT refrain values -> consistent, large pin, high per-message IoC
    r = attack(msgs, [v % N for v in refrain_vals], N, instances=insts, n_null=200)
    out.append(("correct refrain is consistent (per-message-progressive)",
                r.consistent))
    out.append(("correct refrain pins many symbols (>=30)", r.symbols_pinned >= 30))
    out.append(("correct refrain lights per-message IoC up (z>=8)", r.ioc_z >= 8))

    # the recovered alphabet x must decrypt ALL messages (not just the refrain two),
    # since x = C^{-1} is global; per-message IoC elevated across messages.
    iocs = [_ioc(decrypt_message(m, r.pinned, N)) for m in msgs
            if len(decrypt_message(m, r.pinned, N)) >= 8]
    out.append(("global alphabet decrypts every message to language "
                "(min per-msg IoC high)", min(iocs) > 2 * (1 / N)))

    # WRONG refrain -> rejected or low IoC
    bad = list(refrain_vals); rng.shuffle(bad); bad = [(v + 1) % N for v in bad]
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
    # viable_offsets: a phrase with NO repeated letters is viable at every offset
    # (no letter-equality constraints to conflict with collisions).
    vo = viable_offsets(msgs, "abcdefgh", insts, DEFAULT_LEN, N)
    out.append(("viable_offsets: distinct-letter phrase viable at all offsets",
                len(vo) == DEFAULT_LEN - 8 + 1))

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
