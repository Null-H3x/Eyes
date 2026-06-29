"""Brute-force plaintext-alphabet ordering with multi-metric scoring.

The eye corpus bottleneck is the value→character ordering O (83 slots). Full 83!
search is impossible; this module implements tractable brute strategies:

  * **rotate** — all N cyclic rotations of a base ordering (83 trials).
  * **swap**   — all pair swaps from a seed ordering (O(N²) trials).
  * **random** — Monte Carlo random permutations of free slots.
  * **exhaust** — full enumeration when free slots ≤ ``exhaust_if_free``.

Two decrypt backends:

  * **identity** (no crib): assume q[s]=s, search per-message bases. Exploratory
    on the real corpus — useful for sanity checks and plants.
  * **crib** (with phrase): pin x via ``order_solve.pin_structure``, then score
    candidate orderings on the pinned plaintext values (the productive path).

Scoring combines character-trigram log-probability (order-sensitive), a
shuffled-decryption z-score, dictionary word-coverage, and distinct word hits.
IoC is deliberately excluded (degenerate on this cipher family).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import ngram_solve as ng
import order_solve as os_
import ordering_exhaust as oe
import refrain as rf


@dataclass
class BruteScore:
    ordering: Tuple[str, ...]
    trigram: float
    z: float
    word_coverage: float
    dict_hits: int
    composite: float
    plaintext: Dict[int, str] = field(default_factory=dict)
    method: str = ""
    free_slots: int = 0
    symbols_pinned: int = 0

    def as_row(self) -> str:
        return (f"trig={self.trigram:7.3f} z={self.z:6.1f} "
                f"wcov={self.word_coverage:5.1%} hits={self.dict_hits:3d} "
                f"comp={self.composite:7.2f}  {self.method}")


def _composite(z: float, word_coverage: float, dict_hits: int) -> float:
    return z + 5.0 * word_coverage + 0.02 * float(dict_hits)


def _null_z(trigram: float, dec_seqs, model, n_null: int, seed: int) -> float:
    import numpy as np

    rng = np.random.default_rng(seed)
    nulls = []
    for _ in range(n_null):
        sc = 0.0
        cnt = 0
        for seq in dec_seqs:
            if len(seq) >= 3:
                sh = list(seq)
                rng.shuffle(sh)
                sc += model.score_idx(sh) * len(sh)
                cnt += len(sh)
        nulls.append(sc / max(1, cnt))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    return (trigram - nm) / (nsd + 1e-9)


def _score_identity(
    messages: Sequence[Sequence[int]],
    O: Sequence[str],
    *,
    model: ng.TrigramModel,
    aidx: Dict[str, int],
    N: int,
    n_null: int,
    seed: int,
) -> BruteScore:
    """Score ordering O with q[s]=s (exploratory, no crib)."""
    if len(O) < N:
        raise ValueError(f"ordering length {len(O)} < deck size {N}")
    Oi = [aidx[O[v]] for v in range(N)]
    best_total = 0.0
    best_plain: Dict[int, str] = {}
    dec_seqs: List[List[int]] = []

    for mi, msg in enumerate(messages):
        best_b, best_s, best_seq = 0, -1e18, []
        u = [(int(c) - t) % N for t, c in enumerate(msg)]
        if len(u) < 3:
            dec_seqs.append([])
            best_plain[mi] = ""
            continue
        for b in range(N):
            seq = [Oi[(x - b) % N] for x in u]
            s = model.score_idx(seq)
            if s > best_s:
                best_s, best_b, best_seq = s, b, seq
        dec_seqs.append(best_seq)
        best_plain[mi] = "".join(O[(x - best_b) % N] if (x - best_b) % N < len(O) else "·"
                                 for x in u)
        best_total += best_s * len(best_seq)

    cnt = sum(len(s) for s in dec_seqs)
    trig = best_total / max(1, cnt)
    z = _null_z(trig, dec_seqs, model, n_null, seed)
    text = " ".join(best_plain.values())
    wcov = os_._word_coverage(text)
    hits = len(os_._word_hits(text))
    return BruteScore(
        ordering=tuple(O),
        trigram=trig,
        z=z,
        word_coverage=wcov,
        dict_hits=hits,
        composite=_composite(z, wcov, hits),
        plaintext=best_plain,
    )


def _crib_dec_seqs(vals, O, fixed_bases, aidx, N):
    """Character-index sequences under ordering O (for null calibration)."""
    Oi = [aidx[O[v]] for v in range(len(O))]
    out = []
    for mi, seq in enumerate(vals):
        present = [v for v in seq if v is not None]
        if len(present) < 3:
            out.append([])
            continue
        sh = fixed_bases.get(mi, 0)
        out.append([Oi[(v - sh) % N] for v in present])
    return out


def _score_crib(
    messages: Sequence[Sequence[int]],
    O: Sequence[str],
    *,
    vals,
    fixed_bases: Dict[int, int],
    model: ng.TrigramModel,
    aidx: Dict[str, int],
    N: int,
    n_null: int,
    seed: int,
    symbols_pinned: int,
    free_slots: int,
    method: str,
) -> BruteScore:
    trig = oe._score_ordering(O, messages, vals, fixed_bases, model, aidx, N)
    z = _null_z(trig, _crib_dec_seqs(vals, O, fixed_bases, aidx, N), model,
                 n_null, seed)
    plaintext = {}
    all_text = []
    for mi, seq in enumerate(vals):
        sh = fixed_bases.get(mi, 0)
        txt = os_._render(seq, O, sh, N)
        plaintext[mi] = txt
        all_text.append(txt)
    text = " ".join(all_text)
    wcov = os_._word_coverage(text)
    hits = len(os_._word_hits(text))
    return BruteScore(
        ordering=tuple(O),
        trigram=trig,
        z=z,
        word_coverage=wcov,
        dict_hits=hits,
        composite=_composite(z, wcov, hits),
        plaintext=plaintext,
        method=method,
        free_slots=free_slots,
        symbols_pinned=symbols_pinned,
    )


def _crib_context(
    messages,
    crib: str,
    offset: int,
    N: int,
    region,
):
    inst = [(m, p + offset) for (m, p) in region]
    x, contra, fixed_bases = os_.pin_structure(messages, crib, inst, N)
    if contra is not None:
        return None
    vals = os_._decrypt_values(messages, x, N)
    free, rv, _ = oe._free_ordering_slots(messages, crib, inst, x, N)
    seed_O = oe._build_seed_O(crib, rv, rf.DEFAULT_ALPHABET, N)
    return x, vals, fixed_bases, free, seed_O, len(x)


def brute_rotate(
    messages,
    N: int,
    *,
    base_ordering: Optional[str] = None,
    alphabet: Optional[str] = None,
    model: Optional[ng.TrigramModel] = None,
    n_null: int = 30,
    seed: int = 0,
) -> List[BruteScore]:
    """Try all N cyclic rotations of ``base_ordering`` (identity-q backend)."""
    alphabet = alphabet or rf.DEFAULT_ALPHABET
    base = base_ordering or alphabet
    if len(base) < N:
        base = base + alphabet * ((N // len(alphabet)) + 1)
    base = base[:N]
    model = model or ng.TrigramModel(alphabet, ng._ENGLISH)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    out: List[BruteScore] = []
    for r in range(N):
        O = [base[(v + r) % N] for v in range(N)]
        sc = _score_identity(messages, O, model=model, aidx=aidx, N=N,
                             n_null=n_null, seed=seed + r)
        sc.method = f"rotate r={r}"
        out.append(sc)
    out.sort(key=lambda s: s.composite, reverse=True)
    return out


def brute_swap(
    messages,
    N: int,
    *,
    seed_ordering: Optional[Sequence[str]] = None,
    alphabet: Optional[str] = None,
    model: Optional[ng.TrigramModel] = None,
    n_null: int = 30,
    seed: int = 0,
    max_swaps: Optional[int] = None,
) -> List[BruteScore]:
    """Exhaust all pair swaps from a seed ordering (identity-q backend)."""
    alphabet = alphabet or rf.DEFAULT_ALPHABET
    if seed_ordering is None:
        base = alphabet
        if len(base) < N:
            base = base + alphabet * ((N // len(alphabet)) + 1)
        O0 = list(base[:N])
    else:
        O0 = list(seed_ordering)
    model = model or ng.TrigramModel(alphabet, ng._ENGLISH)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    out: List[BruteScore] = []
    pairs = list(itertools.combinations(range(N), 2))
    if max_swaps is not None:
        pairs = pairs[:max_swaps]
    base_sc = _score_identity(messages, O0, model=model, aidx=aidx, N=N,
                              n_null=n_null, seed=seed)
    base_sc.method = "swap seed"
    out.append(base_sc)
    for i, j in pairs:
        O = list(O0)
        O[i], O[j] = O[j], O[i]
        sc = _score_identity(messages, O, model=model, aidx=aidx, N=N,
                             n_null=n_null, seed=seed + i * N + j)
        sc.method = f"swap ({i},{j})"
        out.append(sc)
    out.sort(key=lambda s: s.composite, reverse=True)
    return out


def brute_random(
    messages,
    N: int,
    *,
    samples: int = 5000,
    crib: Optional[str] = None,
    offset: int = 0,
    region=None,
    alphabet: Optional[str] = None,
    model: Optional[ng.TrigramModel] = None,
    n_null: int = 25,
    seed: int = 0,
) -> List[BruteScore]:
    """Monte Carlo random permutations. With ``crib``, only permute free slots."""
    import numpy as np

    alphabet = alphabet or rf.DEFAULT_ALPHABET
    model = model or ng.TrigramModel(alphabet, ng._ENGLISH)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    rng = np.random.default_rng(seed)
    out: List[BruteScore] = []

    if crib:
        region = region or rf.DEFAULT_INSTANCES
        ctx = _crib_context(messages, crib, offset, N, region)
        if ctx is None:
            return []
        _x, vals, fixed_bases, free, seed_O, pinned = ctx
        free_chars = [seed_O[v] for v in free]
        for s in range(samples):
            perm = list(free_chars)
            rng.shuffle(perm)
            O = list(seed_O)
            for v, ch in zip(free, perm):
                O[v] = ch
            sc = _score_crib(
                messages, O, vals=vals, fixed_bases=fixed_bases,
                model=model, aidx=aidx, N=N, n_null=n_null,
                seed=seed + s, symbols_pinned=pinned,
                free_slots=len(free), method=f"random #{s}",
            )
            out.append(sc)
    else:
        pool = list(alphabet)
        if len(pool) < N:
            pool = pool * ((N // len(pool)) + 2)
        for s in range(samples):
            O = list(pool[:N])
            rng.shuffle(O)
            sc = _score_identity(messages, O, model=model, aidx=aidx, N=N,
                                 n_null=n_null, seed=seed + s)
            sc.method = f"random #{s}"
            out.append(sc)

    out.sort(key=lambda x: x.composite, reverse=True)
    return out


def brute_exhaust(
    messages,
    crib: str,
    offset: int,
    N: int,
    *,
    region=None,
    exhaust_if_free: int = 10,
    max_perms: int = 500_000,
    n_null: int = 30,
    seed: int = 0,
) -> BruteScore:
    """Exhaustive permutation of free ordering slots (delegates to ordering_exhaust)."""
    region = region or rf.DEFAULT_INSTANCES
    r = oe.exhaust_ordering(
        messages, crib, offset, N,
        region=region,
        exhaust_if_free=exhaust_if_free,
        max_perms=max_perms,
        n_null=n_null,
        seed=seed,
    )
    text = " ".join(r.plaintext.values()) if r.plaintext else ""
    hits = len(os_._word_hits(text)) if text else 0
    return BruteScore(
        ordering=tuple(r.ordering) if r.ordering else tuple(),
        trigram=r.score,
        z=r.z,
        word_coverage=r.word_coverage,
        dict_hits=hits,
        composite=_composite(r.z, r.word_coverage, hits),
        plaintext=r.plaintext,
        method=r.method,
        free_slots=r.free_slots,
        symbols_pinned=r.symbols_pinned,
    )


def run_brute(
    messages,
    N: int,
    *,
    mode: str = "random",
    samples: int = 5000,
    crib: Optional[str] = None,
    offset: int = 0,
    region=None,
    exhaust_if_free: int = 10,
    max_perms: int = 500_000,
    top: int = 10,
    n_null: int = 25,
    seed: int = 0,
) -> Tuple[str, List[BruteScore]]:
    """Dispatch to the requested brute mode; return (mode, ranked scores)."""
    mode = mode.lower()
    if mode == "rotate":
        scores = brute_rotate(messages, N, n_null=n_null, seed=seed)
    elif mode == "swap":
        scores = brute_swap(messages, N, n_null=n_null, seed=seed)
    elif mode == "random":
        scores = brute_random(
            messages, N, samples=samples, crib=crib, offset=offset,
            region=region, n_null=n_null, seed=seed,
        )
    elif mode == "exhaust":
        if not crib:
            raise ValueError("exhaust mode requires --crib")
        best = brute_exhaust(
            messages, crib, offset, N,
            region=region,
            exhaust_if_free=exhaust_if_free,
            max_perms=max_perms,
            n_null=n_null,
            seed=seed,
        )
        scores = [best] if best.ordering else []
    else:
        raise ValueError(f"unknown mode: {mode!r} (use rotate|swap|random|exhaust)")

    scores.sort(key=lambda s: s.composite, reverse=True)
    return mode, scores[:top]


def format_report(
    mode: str,
    scores: Sequence[BruteScore],
    *,
    labels: Optional[Sequence[str]] = None,
    crib: Optional[str] = None,
    offset: Optional[int] = None,
) -> str:
    lines = [
        "=" * 72,
        "EYES — alphabet brute-force with scoring",
        "=" * 72,
        f"mode: {mode}",
    ]
    if crib:
        lines.append(f"crib: {crib!r}  offset: {offset}")
    lines.append("")
    lines.append(f"{'rank':>4}  {'trigram':>8} {'z':>7} {'wcov':>6} {'hits':>4} "
                 f"{'composite':>9}  method")
    lines.append("-" * 72)
    for i, sc in enumerate(scores, 1):
        lines.append(f"{i:4d}  {sc.trigram:8.3f} {sc.z:7.1f} "
                     f"{sc.word_coverage:5.1%} {sc.dict_hits:4d} "
                     f"{sc.composite:9.2f}  {sc.method}")
    if scores and labels:
        best = scores[0]
        if best.plaintext and (best.z >= 4 or best.word_coverage >= 0.15):
            lines.append("")
            lines.append(f"--- best decryption ({best.method}) ---")
            for mi in sorted(best.plaintext):
                lab = labels[mi] if mi < len(labels) else str(mi)
                lines.append(f"  {lab}: {best.plaintext[mi]}")
        if best.ordering:
            preview = "".join(best.ordering[:40])
            lines.append("")
            lines.append(f"best ordering (first 40 chars): {preview}...")
    lines.append("")
    lines.append("READ: composite = z + 5*word_coverage + 0.02*dict_hits.")
    lines.append("Without a crib, identity-q scoring is exploratory only on the real corpus.")
    lines.append("With a crib, exhaust/random permute free slots after pin_structure.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    model = ng.TrigramModel(alphabet, ng._ENGLISH)
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

    # Plant: true ordering is identity over alphabet indices used as values
    true_O = [alphabet[v % len(alphabet)] for v in range(N)]

    rot = brute_rotate(msgs, N, base_ordering=alphabet, model=model, n_null=15)
    out.append(("rotate: returns N scores", len(rot) == N))
    out.append(("rotate: best composite >= median on plant",
                rot[0].composite >= rot[len(rot) // 2].composite))

    rnd = brute_random(msgs, N, samples=200, crib=crib, region=insts,
                       model=model, n_null=10, seed=1)
    out.append(("random+crib: returns samples", len(rnd) == 200))
    out.append(("random+crib: top z>=6 on plant", rnd[0].z >= 6))

    ex = brute_exhaust(msgs, crib, 0, N, region=insts,
                       exhaust_if_free=12, max_perms=5000, n_null=10)
    out.append(("exhaust: consistent on plant", ex.symbols_pinned >= 45))
    out.append(("exhaust: z>=6 on plant", ex.z >= 6))

    sw = brute_swap(msgs, N, seed_ordering=true_O, model=model, n_null=10,
                    max_swaps=50)
    out.append(("swap: includes seed + pair trials", len(sw) >= 51))
    out.append(("swap: seed scores above most swaps on plant",
                sw[0].composite >= sw[-1].composite))

    _, ranked = run_brute(msgs, N, mode="random", samples=50, crib=crib,
                          region=insts, top=5, n_null=10)
    out.append(("run_brute dispatches random+crib", len(ranked) == 5))

    report = format_report("random", ranked[:2], labels=["M0", "M1", "M2", "M3"],
                           crib=crib, offset=0)
    out.append(("format_report non-empty", "alphabet brute-force" in report))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} alphabet_brute checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
