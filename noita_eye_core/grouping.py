"""Message-grouping structure — the EyeWitness core.

The two community theories about the 9-message corpus are, at bottom, the two
ways to factor 9:

* **Theory 1 ("8 + 1")** — four pairs ``(E_k, W_k)`` plus a leftover ``E5`` that
  is "special" (the key, or the real message).  Forced by parity: pairs cannot
  tile an odd count.
* **Theory 2 ("3 + 3 + 3")** — three triplets; ``E5`` is just the third element
  of the last group and nothing is special.

Both are claims about **which messages are grouped**, and grouping is decidable
from the runes because the corpus is already (independently) established to share
a position-indexed keystream (the depth finding).  Under any linear combiner with
a shared keystream::

    c_i[t] == c_j[t]   <=>   p_i[t] == p_j[t]      (mod N)

so *identical ciphertext over a span* is *identical plaintext over that span*.
That turns "which messages converge" from interpretation into arithmetic.

What this module provides
-------------------------
* :func:`pairwise_agreement` / :func:`agreement_significance` — the n*n equal-rate
  matrix and, per pair, its excess over the chance collision rate with a
  Monte-Carlo (within-message shuffle) null.
* :func:`significant_pair_graph` + :func:`maximal_cliques` — a *data-driven* view:
  threshold the significant-agreement graph and read off whether its maximal
  cliques are size 2 (pairs) or 3 (triplets), with no theory imposed.
* :func:`equal_spans` / :func:`top_spans` — maximal identical runs across a subset
  of messages (the cribs EyeCrack will consume), each with a run-length p-value.
* :func:`score_partition` / :func:`compare_partitions` — principled **model
  selection** over named groupings: each within-group pair is modelled as "linked"
  (one Binomial collision rate) and each across-group pair as "unlinked"
  (another), and partitions are ranked by profile log-likelihood.  This is what
  actually adjudicates Theory 1 vs Theory 2, with a likelihood-ratio against a
  no-structure baseline.

Honesty
-------
Elevated agreement implies a *shared* keystream, not necessarily an *additive*
one — but identical multi-symbol runs under *independent* keys are astronomically
unlikely, so the shared-keystream premise (already z~60 in :mod:`depth`) is firm.
Power at ~100-140 symbols/message is finite; every claim carries a null and a
p-value, and :func:`min_detectable_run` states the shortest run we could even
call significant.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import corpus as corpus_mod
from null_model import benjamini_hochberg

Partition = Tuple[Tuple[int, ...], ...]

# The two theories, as concrete partitions of the 9 messages
# (indices: 0=E1 1=W1 2=E2 3=W2 4=E3 5=W3 6=E4 7=W4 8=E5).
PAIRS_PLUS_E5: Partition = ((0, 1), (2, 3), (4, 5), (6, 7), (8,))
TRIPLETS: Partition = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
ALL_NINE: Partition = ((0, 1, 2, 3, 4, 5, 6, 7, 8),)
ALL_SINGLETON: Partition = tuple((i,) for i in range(9))

NAMED_PARTITIONS: Dict[str, Partition] = {
    "PAIRS_PLUS_E5": PAIRS_PLUS_E5,    # Theory 1
    "TRIPLETS": TRIPLETS,              # Theory 2
    "ALL_NINE": ALL_NINE,
    "ALL_SINGLETON": ALL_SINGLETON,
}


# ---------------------------------------------------------------------------
# Pairwise agreement
# ---------------------------------------------------------------------------

def _overlap(a: Sequence[int], b: Sequence[int]) -> int:
    return min(len(a), len(b))


def _equal_count(a: Sequence[int], b: Sequence[int]) -> Tuple[int, int]:
    L = _overlap(a, b)
    eq = sum(1 for t in range(L) if a[t] == b[t])
    return eq, L


def pairwise_agreement(messages: Sequence[Sequence[int]]) -> np.ndarray:
    """``n*n`` matrix of equal-rate over the overlapping prefix (diag = 1.0)."""
    n = len(messages)
    M = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            eq, L = _equal_count(messages[i], messages[j])
            M[i, j] = M[j, i] = (eq / L) if L else 0.0
    return M


@dataclass
class PairStat:
    i: int
    j: int
    overlap: int
    equal_rate: float
    chance_rate: float
    z: float
    p_value: float
    q_value: float = 1.0


def depth_baseline_rate(messages: Sequence[Sequence[int]]) -> float:
    """Robust estimate of the *depth-only* equal-rate: the chance that two
    in-depth messages agree at a column with NO shared plaintext.

    Under a shared keystream this equals the plaintext collision rate, and it is
    the same for every cross-group pair.  Within-group pairs sit ABOVE it.  We
    take the median over all pairwise rates: grouping links are always a minority
    of the C(n,2) pairs (4/36 for pairs, 9/36 for triplets), so the median is a
    clean cross-pair (no-grouping) rate.
    """
    rates = [x / n for (x, n) in _pair_counts(messages).values() if n]
    return float(np.median(rates)) if rates else 0.0


def _binom_upper_p(x: int, n: int, q: float) -> Tuple[float, float]:
    """Closed-form normal-approximation upper-tail test of ``x`` successes in
    ``n`` Bernoulli(q) trials.  Returns ``(z, p)``.  Exact enough at n~100 and,
    unlike a Monte-Carlo p, not floored at ``1/(n_null+1)`` — which matters
    because BH across 36 pairs needs genuinely small p-values to flag links."""
    if n == 0:
        return 0.0, 1.0
    q = min(max(q, 1e-9), 1 - 1e-9)
    sd = math.sqrt(q * (1 - q) / n)
    obs = x / n
    if sd == 0:
        return (math.inf if obs > q else 0.0), (0.0 if obs > q else 1.0)
    z = (obs - q) / sd
    p = 0.5 * math.erfc(z / math.sqrt(2))      # upper tail
    return z, p


def agreement_significance(messages: Sequence[Sequence[int]], N: int,
                           baseline: Optional[float] = None) -> List[PairStat]:
    """Per-pair equal-rate vs the **depth baseline**, NOT vs a shuffle.

    A within-message shuffle destroys the shared-keystream alignment and so only
    tests for *depth* (which every pair already has — see :mod:`depth`).  The
    grouping signal is agreement *above* the depth collision rate, so the null
    here is "this pair is an ordinary in-depth pair with no shared plaintext":
    Binomial(overlap, q_depth).  BH-corrected across all pairs.
    """
    arrs = [np.asarray(m) for m in messages]
    pc = _pair_counts(arrs)
    q_depth = baseline if baseline is not None else depth_baseline_rate(arrs)

    stats: List[PairStat] = []
    raw_p: List[float] = []
    for (i, j), (x, n) in pc.items():
        z, p = _binom_upper_p(x, n, q_depth)
        ps = PairStat(i=i, j=j, overlap=n, equal_rate=(x / n) if n else 0.0,
                      chance_rate=q_depth, z=z, p_value=p)
        stats.append(ps)
        raw_p.append(p)

    qs = benjamini_hochberg(raw_p)
    for ps, q in zip(stats, qs):
        ps.q_value = q
    return stats


def significant_pair_graph(stats: Sequence[PairStat], alpha: float = 0.01
                           ) -> Dict[int, set]:
    """Adjacency (by BH q-value < alpha) over message indices."""
    adj: Dict[int, set] = {}
    for ps in stats:
        if ps.q_value < alpha:
            adj.setdefault(ps.i, set()).add(ps.j)
            adj.setdefault(ps.j, set()).add(ps.i)
    return adj


def maximal_cliques(adj: Dict[int, set]) -> List[Tuple[int, ...]]:
    """Bron-Kerbosch maximal cliques (the data-driven grouping)."""
    nodes = set(adj.keys())
    out: List[Tuple[int, ...]] = []

    def bk(R: set, P: set, X: set) -> None:
        if not P and not X:
            if len(R) >= 2:
                out.append(tuple(sorted(R)))
            return
        pivot = next(iter(P | X))
        for v in list(P - adj.get(pivot, set())):
            bk(R | {v}, P & adj.get(v, set()), X & adj.get(v, set()))
            P = P - {v}
            X = X | {v}

    bk(set(), set(nodes), set())
    return sorted(out, key=lambda c: (-len(c), c))


# ---------------------------------------------------------------------------
# Equal spans (cribs)
# ---------------------------------------------------------------------------

@dataclass
class Span:
    members: Tuple[int, ...]
    start: int
    length: int
    symbols: Tuple[int, ...]
    p_value: float = 1.0


def equal_spans(messages: Sequence[Sequence[int]], members: Sequence[int],
                min_len: int = 4) -> List[Span]:
    """Maximal runs where *all* ``members`` carry the same symbol."""
    members = tuple(members)
    L = min(len(messages[m]) for m in members)
    spans: List[Span] = []
    t = 0
    while t < L:
        s0 = messages[members[0]][t]
        if all(messages[m][t] == s0 for m in members[1:]):
            start = t
            run = [s0]
            t += 1
            while t < L and all(messages[m][t] == messages[members[0]][t]
                                for m in members):
                run.append(messages[members[0]][t])
                t += 1
            if len(run) >= min_len:
                spans.append(Span(members=members, start=start, length=len(run),
                                  symbols=tuple(run)))
        else:
            t += 1
    return spans


def _longest_common_run(messages: Sequence[np.ndarray], members: Sequence[int]
                        ) -> int:
    L = min(len(messages[m]) for m in members)
    best = cur = 0
    base = messages[members[0]]
    for t in range(L):
        if all(messages[m][t] == base[t] for m in members):
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def span_significance(messages: Sequence[Sequence[int]], members: Sequence[int],
                      n_null: int = 500, seed: int = 0) -> float:
    """Monte-Carlo p-value for the observed longest common run of ``members``
    (within-message shuffle null)."""
    rng = np.random.default_rng(seed)
    arrs = [np.asarray(m) for m in messages]
    obs = _longest_common_run(arrs, members)
    exceed = 0
    for _ in range(n_null):
        sh = [rng.permutation(a) for a in arrs]
        if _longest_common_run(sh, members) >= obs:
            exceed += 1
    return (1 + exceed) / (1 + n_null)


def top_spans(messages: Sequence[Sequence[int]], N: int, subset_sizes=(2, 3),
              min_len: int = 5, n_null: int = 300, seed: int = 0,
              max_report: int = 20) -> List[Span]:
    """Enumerate equal-spans across all pairs/triples, keep the longest, attach a
    Monte-Carlo p-value to each reported span's subset."""
    n = len(messages)
    found: List[Span] = []
    for k in subset_sizes:
        for members in combinations(range(n), k):
            found.extend(equal_spans(messages, members, min_len=min_len))
    found.sort(key=lambda s: -s.length)
    found = found[:max_report]
    for sp in found:
        sp.p_value = span_significance(messages, sp.members, n_null=n_null,
                                       seed=seed)
    return found


def min_detectable_run(messages: Sequence[Sequence[int]], members: Sequence[int],
                       N: int, n_null: int = 500, seed: int = 0,
                       alpha: float = 0.01) -> int:
    """Shortest common run that would clear ``alpha`` under the shuffle null —
    the power statement for span claims."""
    rng = np.random.default_rng(seed)
    arrs = [np.asarray(m) for m in messages]
    null_runs = sorted(_longest_common_run([rng.permutation(a) for a in arrs],
                                            members) for _ in range(n_null))
    idx = min(n_null - 1, int(math.ceil((1 - alpha) * n_null)))
    return int(null_runs[idx]) + 1


# ---------------------------------------------------------------------------
# Partition model selection (the adjudicator)
# ---------------------------------------------------------------------------

@dataclass
class PartitionScore:
    name: str
    partition: Partition
    loglik: float                 # profile log-likelihood (comparable term only)
    q_link: float                 # fitted within-group collision rate
    q_unlink: float               # fitted across-group collision rate
    n_link_pairs: int
    n_unlink_pairs: int
    lr_vs_baseline: float         # 2*(loglik - baseline_loglik)
    mean_within: float
    mean_across: float


def _pair_counts(messages: Sequence[Sequence[int]]
                 ) -> Dict[Tuple[int, int], Tuple[int, int]]:
    n = len(messages)
    out: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for i in range(n):
        for j in range(i + 1, n):
            out[(i, j)] = _equal_count(messages[i], messages[j])
    return out


def _binom_term(x: int, n: int, q: float) -> float:
    """x*log q + (n-x)*log(1-q); the part of the Binomial logpmf that varies with
    the model (the log C(n,x) term is constant across partitions)."""
    if n == 0:
        return 0.0
    eps = 1e-9
    q = min(max(q, eps), 1 - eps)
    return x * math.log(q) + (n - x) * math.log(1 - q)


def _within_pairs(partition: Partition) -> set:
    s = set()
    for g in partition:
        for a, b in combinations(sorted(g), 2):
            s.add((a, b))
    return s


def score_partition(partition: Partition,
                    pair_counts: Dict[Tuple[int, int], Tuple[int, int]],
                    name: str = "") -> PartitionScore:
    """Profile log-likelihood of a partition under the link/unlink Binomial
    model (collision rate ``q_link`` within groups, ``q_unlink`` across)."""
    within = _within_pairs(partition)
    sum_x_in = sum_n_in = sum_x_out = sum_n_out = 0
    within_rates: List[float] = []
    across_rates: List[float] = []
    for (i, j), (x, n) in pair_counts.items():
        if (i, j) in within:
            sum_x_in += x
            sum_n_in += n
            if n:
                within_rates.append(x / n)
        else:
            sum_x_out += x
            sum_n_out += n
            if n:
                across_rates.append(x / n)
    q_link = (sum_x_in / sum_n_in) if sum_n_in else 0.0
    q_unlink = (sum_x_out / sum_n_out) if sum_n_out else 0.0

    loglik = 0.0
    for (i, j), (x, n) in pair_counts.items():
        q = q_link if (i, j) in within else q_unlink
        loglik += _binom_term(x, n, q)

    # Baseline: a single q for every pair (no grouping structure at all).
    tot_x = sum_x_in + sum_x_out
    tot_n = sum_n_in + sum_n_out
    q0 = (tot_x / tot_n) if tot_n else 0.0
    base = sum(_binom_term(x, n, q0) for (x, n) in pair_counts.values())

    return PartitionScore(
        name=name, partition=partition, loglik=loglik,
        q_link=q_link, q_unlink=q_unlink,
        n_link_pairs=len(within), n_unlink_pairs=len(pair_counts) - len(within),
        lr_vs_baseline=2 * (loglik - base),
        mean_within=float(np.mean(within_rates)) if within_rates else 0.0,
        mean_across=float(np.mean(across_rates)) if across_rates else 0.0,
    )


def compare_partitions(messages: Sequence[Sequence[int]],
                       candidates: Optional[Dict[str, Partition]] = None
                       ) -> List[PartitionScore]:
    """Rank candidate partitions by profile log-likelihood (best first)."""
    if candidates is None:
        candidates = NAMED_PARTITIONS
    pc = _pair_counts(messages)
    scored = [score_partition(p, pc, name=name)
              for name, p in candidates.items()]
    scored.sort(key=lambda s: -s.loglik)
    return scored


# ---------------------------------------------------------------------------
# Selftest — planted groupings of known type
# ---------------------------------------------------------------------------

def _planted_corpus(partition: Partition, N: int, T: int, share_len: int,
                    rng: np.random.Generator) -> List[List[int]]:
    """Build 9 messages that share ONE position keystream; within each planted
    group the messages share identical plaintext on ``[0, share_len)`` (so their
    ciphertext is identical there), and are independent elsewhere."""
    key = rng.integers(0, N, size=T)
    # Non-uniform plaintext so chance agreement stays low off the shared span.
    w = 1.0 / np.arange(1, 31)
    pmf = np.concatenate([w, np.zeros(N - 30)])
    pmf /= pmf.sum()

    group_of = {}
    for gi, g in enumerate(partition):
        for m in g:
            group_of[m] = gi
    shared_plain = {gi: rng.choice(N, size=share_len, p=pmf)
                    for gi in range(len(partition))}

    messages: List[List[int]] = []
    for m in range(9):
        p = rng.choice(N, size=T, p=pmf)
        gi = group_of[m]
        if len(partition[gi]) >= 2:        # singletons keep independent plaintext
            p[:share_len] = shared_plain[gi]
        c = [(int(p[t]) + int(key[t])) % N for t in range(T)]
        messages.append(c)
    return messages


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(17)

    # (1) Planted TRIPLETS -> TRIPLETS must win the model selection.
    trip = _planted_corpus(TRIPLETS, N, T=120, share_len=40, rng=rng)
    ranked = compare_partitions(trip)
    out.append(("planted triplets -> TRIPLETS wins",
                ranked[0].name == "TRIPLETS"))
    out.append(("planted triplets -> beats no-structure baseline",
                ranked[0].lr_vs_baseline > 50))

    # (2) Planted PAIRS+E5 -> PAIRS_PLUS_E5 must win.
    pairs = _planted_corpus(PAIRS_PLUS_E5, N, T=120, share_len=40, rng=rng)
    ranked_p = compare_partitions(pairs)
    out.append(("planted pairs+E5 -> PAIRS_PLUS_E5 wins",
                ranked_p[0].name == "PAIRS_PLUS_E5"))
    out.append(("planted pairs+E5 -> within >> across agreement",
                ranked_p[0].mean_within > 0.25
                and ranked_p[0].mean_within > 2 * ranked_p[0].mean_across))

    # (3) No structure (shared key, independent plaintext) -> no partition
    #     should look much better than baseline.
    none = _planted_corpus(ALL_SINGLETON, N, T=120, share_len=0, rng=rng)
    ranked_n = compare_partitions(none)
    best_struct = max(s.lr_vs_baseline for s in ranked_n
                      if s.name in ("TRIPLETS", "PAIRS_PLUS_E5"))
    out.append(("no structure -> grouping LR stays small",
                best_struct < 20))

    # (4) Data-driven cliques recover the planted clique SIZE.
    stats = agreement_significance(trip, N)
    cliques = maximal_cliques(significant_pair_graph(stats, alpha=0.01))
    out.append(("triplet cliques are size 3",
                len(cliques) >= 1 and max(len(c) for c in cliques) == 3))
    stats_p = agreement_significance(pairs, N)
    cliques_p = maximal_cliques(significant_pair_graph(stats_p, alpha=0.01))
    out.append(("pair cliques are size 2",
                len(cliques_p) >= 1 and max(len(c) for c in cliques_p) == 2))

    # (5) Equal-span recovery: a planted triplet shares a >= share_len run.
    sp = equal_spans(trip, TRIPLETS[0], min_len=10)
    out.append(("equal_spans finds the planted shared run",
                any(s.length >= 35 for s in sp)))
    pval = span_significance(trip, TRIPLETS[0], n_null=200, seed=5)
    out.append(("planted span is significant", pval < 0.01))

    # (6) Identity: equal ciphertext <=> equal plaintext is what we rely on;
    #     check agreement matrix is symmetric with unit diagonal.
    M = pairwise_agreement(trip)
    out.append(("agreement matrix symmetric, unit diagonal",
                np.allclose(M, M.T) and np.allclose(np.diag(M), 1.0)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} grouping checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
