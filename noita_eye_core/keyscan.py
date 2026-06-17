"""Keystream seed-scan engine — combiner-pluggable, generator-pluggable.

Tests the keystream-cipher hypothesis directly: does some (generator, seed,
combiner) reproduce a keystream that makes a triplet's three messages decrypt to
joint structure?  Built per-triplet (the keystream is per-triplet) and
combiner-pluggable so it covers BOTH live models —

* **additive / affine** (`c = p + K`): scalar keystream; this is the branch
  crib-drag and the exact crib-filter can accelerate, and the natural fit for
  scalar PRNGs;
* **injective per position** (`c[t] = S_t(p[t])`): a shared per-column bijection
  (rotor/deck cipher); the natural fit for deck/permutation generators.

Each candidate is scored by the joint structure of the triplet's decrypts and
gauged against a decoy (random-seed) best-of-N null, so a "hit" is trustworthy
rather than the best of billions of coincidences.  A ``--crib`` plaintext
fragment turns the scan into an exact, high-power filter.

Honesty about power and scope
-----------------------------
Without a crib the structure oracle is weak (the corpus has a flat unigram), so a
broad scan most likely returns *no trustworthy hit* — which is itself evidence
(against a keystream from the tried generators).  The crib-filter is the
high-power path.  The generators here are a sound starter zoo (Noita NollaPRNG,
MINSTD, xorshift, an LFSR, and a deck cipher); GAK/xGAK and the full PRNG zoo are
a follow-on (EyeStat already implements those kernels).  This is a CPU reference
(multiprocessing-friendly, pure functions) whose inner loop is GPU-portable.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from langdetect import order_predictability
from prng import NollaPRNG

N_DEFAULT = 83
TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


# ---------------------------------------------------------------------------
# Scalar keystream generators  (seed, N, length) -> [k0, k1, ...]
# ---------------------------------------------------------------------------

def gen_nolla(seed: int, N: int, L: int) -> List[int]:
    return NollaPRNG(seed).keystream_mod(N, L)


def gen_minstd(seed: int, N: int, L: int) -> List[int]:
    x = (seed % 2147483646) + 1
    out = []
    for _ in range(L):
        x = (16807 * x) % 2147483647
        out.append(x % N)
    return out


def gen_xorshift32(seed: int, N: int, L: int) -> List[int]:
    x = (seed & 0xFFFFFFFF) or 0x1234
    out = []
    for _ in range(L):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        out.append(x % N)
    return out


def gen_lfsr32(seed: int, N: int, L: int) -> List[int]:
    x = (seed & 0xFFFFFFFF) or 0xACE1
    out = []
    for _ in range(L):
        lsb = x & 1
        x >>= 1
        if lsb:
            x ^= 0xA3000000          # a (non-certified) tap set
        out.append(x % N)
    return out


SCALAR_GENERATORS: Dict[str, Callable[[int, int, int], List[int]]] = {
    "nolla": gen_nolla, "minstd": gen_minstd,
    "xorshift32": gen_xorshift32, "lfsr32": gen_lfsr32,
}


# ---------------------------------------------------------------------------
# Deck (permutation) generator for the injective-per-position combiner
# ---------------------------------------------------------------------------

def deck_nolla(seed: int, N: int, L: int) -> List[List[int]]:
    """A per-position bijection sequence (dynamic substitution): seed a deck via
    NollaPRNG, emit it, then advance by one swap per position.  Not GAK/xGAK
    (that is a follow-on), but a sound deck-cipher model for the injective branch.
    """
    rng = NollaPRNG(seed)
    deck = list(range(N))
    for i in range(N - 1, 0, -1):
        j = rng.random(0, i)
        deck[i], deck[j] = deck[j], deck[i]
    perms: List[List[int]] = []
    for _ in range(L):
        perms.append(list(deck))
        i = rng.random(0, N - 1)
        j = rng.random(0, N - 1)
        deck[i], deck[j] = deck[j], deck[i]
    return perms


# ---------------------------------------------------------------------------
# Combiners: decrypt a message given the generator output
# ---------------------------------------------------------------------------

def _decrypt_scalar(msg: Sequence[int], ks: Sequence[int], mode: str, N: int
                    ) -> List[int]:
    if mode == "add":
        return [(msg[t] - ks[t]) % N for t in range(len(msg))]
    if mode == "sub":
        return [(msg[t] + ks[t]) % N for t in range(len(msg))]
    if mode == "beaufort":
        return [(ks[t] - msg[t]) % N for t in range(len(msg))]
    raise KeyError(mode)


def _decrypt_subst(msg: Sequence[int], decks: Sequence[Sequence[int]], N: int
                   ) -> List[int]:
    out = []
    for t in range(len(msg)):
        S = decks[t]
        inv = [0] * N
        for sym, val in enumerate(S):
            inv[val] = sym
        out.append(inv[msg[t]])
    return out


def decrypt_triplet(messages: Sequence[Sequence[int]], seed: int, generator: str,
                    combiner: str, N: int) -> List[List[int]]:
    Lmax = max(len(m) for m in messages)
    if combiner == "subst":
        decks = deck_nolla(seed, N, Lmax)
        return [_decrypt_subst(m, decks, N) for m in messages]
    ks = SCALAR_GENERATORS[generator](seed, N, Lmax)
    return [_decrypt_scalar(m, ks, combiner, N) for m in messages]


# ---------------------------------------------------------------------------
# Scoring + scan
# ---------------------------------------------------------------------------

def structure_score(decrypts: Sequence[Sequence[int]], body_start: int = 0
                    ) -> float:
    vals = []
    for d in decrypts:
        t = list(d)[body_start:]
        if len(t) >= 10:
            vals.append(order_predictability(t))
    return float(np.mean(vals)) if vals else 0.0


def crib_ok(messages: Sequence[Sequence[int]], member: int, seed: int,
            generator: str, combiner: str, N: int, start: int,
            crib: Sequence[int]) -> bool:
    dec = decrypt_triplet(messages, seed, generator, combiner, N)[member]
    return all(dec[start + o] == crib[o] for o in range(len(crib)))


# ---------------------------------------------------------------------------
# Crib -> seed-filter bridge
# ---------------------------------------------------------------------------
# Two power levels, both per-triplet:
#
#   * MAPPING-FREE (a word's repeat pattern).  We do NOT know which symbol is
#     which letter, but a repeated letter forces equal plaintext at those
#     positions, which under an additive keystream forces
#         K[p+i] - K[p+j] == c[p+i] - c[p+j]   (a known value).
#     Each repeated-letter pair is one mod-N constraint => filters seeds by ~1/N.
#     "eye" (e..e) and "see" (.ee) each give ONE constraint (1/83) — weak, but
#     free.  A word with several repeats (e.g. "sisaltaa", "muna") gives several.
#
#   * MAPPING-COMMITTED (exact symbols).  If you commit the crib's letters to
#     specific symbols, every position is a constraint => ~1/N^L (use ``crib=``).
#
# Survivors are then scored with the decoy-calibrated structure gate, so the
# bridge is a *calibrated* seed scan that any confident word sharpens.

def repeat_constraints(word: str) -> List[Tuple[int, int]]:
    """Equal-letter position pairs ``(i, j)`` (i<j) — the mapping-free
    constraints a word imposes.  Empty if the word has no repeated letter."""
    first: Dict[str, int] = {}
    cons: List[Tuple[int, int]] = []
    for i, ch in enumerate(word):
        if ch in first:
            cons.append((first[ch], i))
        else:
            first[ch] = i
    return cons


def crib_power(word: str, N: int) -> Tuple[int, float]:
    """(number of mapping-free constraints, expected survivor fraction ~1/N^k)."""
    k = len(repeat_constraints(word))
    return k, (1.0 / (N ** k) if k else 1.0)


def crib_seed_bridge(messages: Sequence[Sequence[int]], triplet: Sequence[int],
                     word: str, position: int, member: int, generator: str,
                     combiner: str, seed_start: int, count: int,
                     N: int = N_DEFAULT, body_start: int = 25,
                     decoy_batches: int = 8, topk: int = 10) -> TripletScan:
    """Mapping-free repeat-pattern crib filter + calibrated survivor scoring.

    Keeps seeds whose keystream is consistent with ``word`` sitting at
    ``position`` in ``member`` (additive combiner), then scores the survivors'
    joint decrypt against a decoy null.  With no repeated letters this degrades
    to a calibrated full scan (and says so via ``crib_power``).
    """
    if combiner not in ("add", "sub", "beaufort"):
        raise ValueError("repeat-pattern bridge is for scalar/additive combiners")
    msgs = [list(messages[i]) for i in triplet]
    m = msgs[member]
    L = len(word)
    if position + L > len(m):
        raise ValueError("crib runs past the end of the member message")
    cons = repeat_constraints(word)
    # required keystream differences (== ciphertext differences at equal letters)
    req = [(i, j, (m[position + i] - m[position + j]) % N) for (i, j) in cons]
    Lmax = max(len(x) for x in msgs)

    survivors: List[int] = []
    for s in range(count):
        seed = seed_start + s
        ks = SCALAR_GENERATORS[generator](seed, N, Lmax)
        if all((ks[position + i] - ks[position + j]) % N == d for (i, j, d) in req):
            survivors.append(seed)

    scored = [ScanHit(seed, structure_score(
        decrypt_triplet(msgs, seed, generator, combiner, N), body_start))
        for seed in survivors]
    scored.sort(key=lambda h: -h.score)
    best = scored[:topk]

    rng = np.random.default_rng(0)
    decoy_max = []
    for b in range(decoy_batches):
        base = 1_000_000_000 + b * max(count, 1)
        vals = [structure_score(decrypt_triplet(msgs, base + s, generator,
                combiner, N), body_start) for s in range(max(count, 1))]
        decoy_max.append(max(vals))
    dm = np.array(decoy_max, dtype=float)
    mu, sd = float(dm.mean()), float(dm.std(ddof=1) or 1e-9)
    for h in best:
        h.z = (h.score - mu) / sd
        h.trustworthy = bool(h.z > 5 and h.score > dm.max())

    sc = TripletScan(tuple(triplet), generator, combiner, seed_start, count,
                     best, mu, sd)
    sc.crib_matches = survivors
    return sc


@dataclass
class ScanHit:
    seed: int
    score: float
    z: float = 0.0
    trustworthy: bool = False


@dataclass
class TripletScan:
    triplet: Tuple[int, ...]
    generator: str
    combiner: str
    seed_start: int
    count: int
    hits: List[ScanHit]
    decoy_mean: float
    decoy_std: float
    crib: Optional[List[int]] = None
    crib_matches: List[int] = field(default_factory=list)
    elapsed_s: float = 0.0


def scan_triplet(messages: Sequence[Sequence[int]], triplet: Sequence[int],
                 generator: str, combiner: str, seed_start: int, count: int,
                 N: int = N_DEFAULT, body_start: int = 25, topk: int = 10,
                 decoy_batches: int = 8, crib: Optional[Sequence[int]] = None,
                 crib_member: int = 0, crib_start: int = 0) -> TripletScan:
    msgs = [list(messages[i]) for i in triplet]

    if crib is not None:
        matches = [seed_start + s for s in range(count)
                   if crib_ok(msgs, crib_member, seed_start + s, generator,
                              combiner, N, crib_start, crib)]
        return TripletScan(tuple(triplet), generator, combiner, seed_start,
                           count, [], 0.0, 0.0, list(crib), matches)

    scored: List[ScanHit] = []
    for s in range(count):
        seed = seed_start + s
        dec = decrypt_triplet(msgs, seed, generator, combiner, N)
        scored.append(ScanHit(seed, structure_score(dec, body_start)))
    scored.sort(key=lambda h: -h.score)
    best = scored[:topk]

    # Decoy best-of-N calibration (the structscan trust gate).
    rng = np.random.default_rng(0)
    decoy_max = []
    for b in range(decoy_batches):
        base = 1_000_000_000 + b * count
        vals = [structure_score(decrypt_triplet(msgs, base + s, generator,
                combiner, N), body_start) for s in range(count)]
        decoy_max.append(max(vals))
    dm = np.array(decoy_max, dtype=float)
    mu, sd = float(dm.mean()), float(dm.std(ddof=1) or 1e-9)
    for h in best:
        h.z = (h.score - mu) / sd
        h.trustworthy = bool(h.z > 5 and h.score > dm.max())
    return TripletScan(tuple(triplet), generator, combiner, seed_start, count,
                       best, mu, sd)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _markov(N: int, T: int, rng: np.random.Generator, conc: float = 30.0
            ) -> List[int]:
    """Strongly-structured chain so a CORRECT decrypt is clearly distinguishable
    from a wrong one (validates the trust gate; the real corpus is far flatter)."""
    bi = np.zeros((N, N))
    for a in range(N):
        row = rng.random(N) ** 6
        row[(a + 1) % N] += conc
        row[(a * 7 + 3) % N] += conc / 2
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
    rng = np.random.default_rng(3)

    # Generator KAT: NollaPRNG keystream is deterministic.
    out.append(("nolla generator deterministic",
                gen_nolla(42, N, 8) == gen_nolla(42, N, 8)))

    # Combiner round-trips.
    p = [rng.integers(0, N) for _ in range(30)]
    ks = gen_minstd(99, N, 30)
    c_add = [(p[t] + ks[t]) % N for t in range(30)]
    out.append(("additive decrypt round-trips",
                _decrypt_scalar(c_add, ks, "add", N) == p))
    decks = deck_nolla(7, N, 30)
    c_sub = [decks[t][p[t]] for t in range(30)]      # encrypt: c = S_t(p)
    out.append(("injective decrypt round-trips",
                _decrypt_subst(c_sub, decks, N) == p))

    # Plant: Markov plaintext + nolla additive keystream (true seed) in a triplet.
    true_seed = 1234567
    T = 120
    ks_true = gen_nolla(true_seed, N, T)
    plains = [_markov(N, T, rng) for _ in range(3)]
    cipher = [[(plains[i][t] + ks_true[t]) % N for t in range(T)]
              for i in range(3)]
    sc = scan_triplet(cipher, (0, 1, 2), "nolla", "add",
                      seed_start=true_seed - 60, count=120, N=N, body_start=0,
                      decoy_batches=6)
    out.append(("additive scan: true seed is the top hit",
                sc.hits[0].seed == true_seed))
    out.append(("additive scan: true seed clears the decoy null",
                sc.hits[0].trustworthy))

    # Crib filter recovers the seed exactly.
    crib = plains[0][30:36]
    scc = scan_triplet(cipher, (0, 1, 2), "nolla", "add",
                       seed_start=true_seed - 300, count=600, N=N,
                       crib=crib, crib_member=0, crib_start=30)
    out.append(("crib filter recovers the true seed uniquely",
                scc.crib_matches == [true_seed]))

    # Injective plant: Markov plaintext + deck cipher (true seed).
    seed2 = 222333
    decks2 = deck_nolla(seed2, N, T)
    plains2 = [_markov(N, T, rng) for _ in range(3)]
    cipher2 = [[decks2[t][plains2[i][t]] for t in range(T)] for i in range(3)]
    sc2 = scan_triplet(cipher2, (0, 1, 2), "nolla", "subst",
                       seed_start=seed2 - 40, count=80, N=N, body_start=0,
                       decoy_batches=6)
    out.append(("injective scan: true deck seed is the top hit",
                sc2.hits[0].seed == seed2))

    # Crib->seed bridge (mapping-free repeat pattern). Plant a word with several
    # repeats so the filter is tight enough to recover the seed in a small range.
    word = "sisaltaa"                       # s,i repeats -> 3 constraints
    cons = repeat_constraints(word)
    out.append(("repeat_constraints finds equal-letter pairs", len(cons) == 3))
    # symbols: distinct symbol per distinct letter
    letters = sorted(set(word))
    sigma = {ch: (i * 7 + 5) % N for i, ch in enumerate(letters)}
    pos = 40
    plant = [_markov(N, T, rng) for _ in range(3)]
    for o, ch in enumerate(word):
        plant[0][pos + o] = sigma[ch]       # embed the word in member 0
    bseed = 7654321
    ksb = gen_nolla(bseed, N, T)
    cipherb = [[(plant[i][t] + ksb[t]) % N for t in range(T)] for i in range(3)]
    scb = crib_seed_bridge(cipherb, (0, 1, 2), word, position=pos, member=0,
                           generator="nolla", combiner="add",
                           seed_start=bseed - 4000, count=8000, N=N,
                           body_start=0, decoy_batches=6)
    out.append(("repeat-pattern bridge keeps the true seed",
                bseed in scb.crib_matches))
    out.append(("repeat-pattern bridge filters most seeds (~1/N^k)",
                len(scb.crib_matches) < 8000 // 10))
    out.append(("repeat-pattern bridge: true seed tops survivors",
                scb.hits and scb.hits[0].seed == bseed))
    _, frac = crib_power("eye", N)
    out.append(("crib_power flags a 3-letter single-repeat word as weak",
                abs(frac - 1.0 / N) < 1e-12))

    # Null: uniform ciphertext -> no trustworthy additive hit.
    rnd = [rng.integers(0, N, size=T).tolist() for _ in range(3)]
    scn = scan_triplet(rnd, (0, 1, 2), "nolla", "add", seed_start=0, count=120,
                       N=N, body_start=0, decoy_batches=6)
    out.append(("uniform ciphertext -> no trustworthy hit",
                not scn.hits[0].trustworthy))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} keyscan checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
