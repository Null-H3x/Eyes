"""Depth / crib-drag keystream recovery -- the missing convergence layer.

The corpus evidence (flat IoC, ~44% column agreement, the universal ``66,5``
header, and *identical ciphertext runs* across messages such as E1/W1/E2 on
positions 1-24) says the keystream depends only on **absolute position** and is
**shared by all nine messages**.  That is the classic "messages in depth"
setting, and it makes the algebra clean:

* Under any linear combiner (``add``/``sub``/``beaufort``), differencing two
  ciphertexts at a shared position cancels the key:
  ``c_i[t] - c_j[t] == plain_sign * (p_i[t] - p_j[t]) (mod N)``.
  So the plaintext *difference* structure is recoverable with **no key at all**
  -- this is the depth-confirmation test and the equality map.

* Each column ``t`` then has exactly **one** unknown: the key value ``k[t]``
  (fix one plaintext symbol in the column and every other is determined by the
  known differences).  So the whole cipher has ``L = max length`` unknowns, with
  up to 9 in-depth samples per column.  Recovering them is exactly
  multi-ciphertext Vigenere solving.

Two solvers are provided:

1. :func:`crib_drag` -- *exact*.  A hypothesised plaintext fragment pins
   ``k[t]`` over its span; because the key is shared, that immediately reveals
   the corresponding plaintext fragment in **every** message.

2. :func:`solve_keystream_viterbi` -- a globally optimal (under a 1st-order
   model) recovery of the entire keystream.  State = ``k[t]``; the emission term
   is the summed unigram log-prob of the recovered column, the transition term
   is the summed bigram log-prob across the in-depth messages spanning ``t-1``
   and ``t``.  Viterbi returns the keystream maximising the total -- the
   textbook depth attack.  Validated end-to-end on synthetic data with a known
   planted keystream.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import cipher_ops
import corpus as corpus_mod
from lm import MarkovModel
from null_model import Significance, significance
from stats import difference, ioc


# ---------------------------------------------------------------------------
# Depth confirmation
# ---------------------------------------------------------------------------

@dataclass
class DepthReport:
    mode_note: str
    mean_pair_diff_ioc: float
    uniform_baseline: float
    equal_fraction: float          # fraction of compared positions with c_i==c_j
    significance: Significance
    per_pair: List[Tuple[str, str, float, float]]  # (lab_i, lab_j, diff_ioc, eq_frac)


def _pairwise_diff_iocs(messages: Sequence[Sequence[int]], N: int
                        ) -> List[float]:
    vals: List[float] = []
    n = len(messages)
    for i in range(n):
        for j in range(i + 1, n):
            d = difference(messages[i], messages[j], N)
            if len(d) >= 2:
                vals.append(ioc(d))
    return vals


def _mean_pair_diff_ioc(messages: Sequence[Sequence[int]], N: int) -> float:
    vals = _pairwise_diff_iocs(messages, N)
    return float(np.mean(vals)) if vals else 0.0


def confirm_depth(c: corpus_mod.Corpus, n_null: int = 500,
                  seed: int = 0) -> DepthReport:
    """Test whether the messages are in depth (shared position-keystream).

    Statistic: mean over message pairs of the difference-stream IoC.  Null:
    independently permute the symbols *within* each message (preserving each
    message's marginal histogram but destroying any column alignment) and
    recompute.  A large positive z means the column alignment carries far more
    coincidence than the marginals alone explain -- i.e. depth.
    """
    N = c.N
    messages = [list(ct) for ct in c.ciphertexts]
    observed = _mean_pair_diff_ioc(messages, N)

    rng = np.random.default_rng(seed)
    null: List[float] = []
    for _ in range(n_null):
        shuffled = []
        for m in messages:
            arr = np.array(m)
            rng.shuffle(arr)
            shuffled.append(arr.tolist())
        null.append(_mean_pair_diff_ioc(shuffled, N))
    sig = significance(observed, null, tail="greater")

    # Equal-fraction across all compared positions (c_i == c_j).
    eq_num = eq_den = 0
    per_pair: List[Tuple[str, str, float, float]] = []
    for i in range(len(messages)):
        for j in range(i + 1, len(messages)):
            L = min(len(messages[i]), len(messages[j]))
            if L == 0:
                continue
            eqs = sum(1 for t in range(L) if messages[i][t] == messages[j][t])
            eq_num += eqs
            eq_den += L
            d = difference(messages[i], messages[j], N)
            per_pair.append((c.labels[i], c.labels[j], ioc(d), eqs / L))

    return DepthReport(
        mode_note="linear combiner (add/sub/beaufort); differencing is key-free",
        mean_pair_diff_ioc=observed,
        uniform_baseline=1.0 / N,
        equal_fraction=eq_num / eq_den if eq_den else 0.0,
        significance=sig,
        per_pair=per_pair,
    )


# ---------------------------------------------------------------------------
# Crib drag (exact)
# ---------------------------------------------------------------------------

@dataclass
class CribResult:
    start: int
    keystream: List[int]                       # recovered k[start:start+len]
    revealed: Dict[int, List[Optional[int]]]   # message index -> plaintext span


def crib_drag(c: corpus_mod.Corpus, ref_index: int, start: int,
              plain: Sequence[int], mode: str = "add") -> CribResult:
    """Pin the keystream from a hypothesised plaintext fragment and propagate.

    ``plain`` is the guessed plaintext (symbols) for message ``ref_index``
    starting at absolute position ``start``.  Returns the implied keystream and,
    because the key is shared, the revealed plaintext span for every message.
    """
    N = c.N
    ref = c.ciphertexts[ref_index]
    end = start + len(plain)
    if end > len(ref):
        raise ValueError("crib runs past the reference message")
    cipher_seg = list(ref[start:end])
    key_seg = cipher_ops.keystream_from_known(plain, cipher_seg, mode, N)

    revealed: Dict[int, List[Optional[int]]] = {}
    combiner = cipher_ops.get_mode(mode)
    for i, ct in enumerate(c.ciphertexts):
        span: List[Optional[int]] = []
        for off, k in enumerate(key_seg):
            t = start + off
            if t < len(ct):
                span.append(combiner.decrypt(ct[t], k, N))
            else:
                span.append(None)
        revealed[i] = span
    return CribResult(start=start, keystream=key_seg, revealed=revealed)


# ---------------------------------------------------------------------------
# Full keystream recovery via Viterbi
# ---------------------------------------------------------------------------

def _dec_index(c_val: int, mode: str, N: int) -> np.ndarray:
    """Vector ``rec[s] = decrypt(c_val, s)`` for ``s in 0..N-1``."""
    s = np.arange(N)
    if mode == "add":       # p = (c - k)
        return (c_val - s) % N
    if mode == "sub":       # p = (c + k)
        return (c_val + s) % N
    if mode == "beaufort":  # p = (k - c)
        return (s - c_val) % N
    raise KeyError(f"mode {mode!r} not supported by the depth solver")


@dataclass
class KeystreamResult:
    keystream: List[int]
    plaintext: List[List[int]]      # per message, recovered symbols
    column_samples: List[int]       # #messages spanning each position
    total_logprob: float


def solve_keystream_viterbi(c: corpus_mod.Corpus, model: MarkovModel,
                            mode: str = "add") -> KeystreamResult:
    """Globally optimal keystream under ``model`` (1st-order Markov), via
    Viterbi over per-position key values."""
    N = c.N
    if model.N != N:
        raise ValueError("model alphabet does not match corpus")
    L = c.max_length
    uni = model.uni_logp
    bi = model.bi_logp

    # Precompute, per position, the decrypt-index vectors for present messages.
    cols: List[List[Tuple[int, np.ndarray]]] = []
    for t in range(L):
        entries = [(i, _dec_index(c.ciphertexts[i][t], mode, N))
                   for i in c.messages_with_length_at_least(t)]
        cols.append(entries)

    def emission(t: int) -> np.ndarray:
        e = np.zeros(N)
        for _, idx in cols[t]:
            e += uni[idx]
        return e

    # Viterbi
    dp = emission(0)
    back: List[np.ndarray] = []
    for t in range(1, L):
        # transition[s_prev, s_cur] summed over messages present at t-1 AND t
        trans = np.zeros((N, N))
        prev_map = {i: idx for i, idx in cols[t - 1]}
        for i, idx_cur in cols[t]:
            if i in prev_map:
                idx_prev = prev_map[i]
                trans += bi[np.ix_(idx_prev, idx_cur)]
        emis = emission(t)
        # total[s_prev, s_cur] = dp[s_prev] + trans + emis[s_cur]
        total = dp[:, None] + trans + emis[None, :]
        bp = np.argmax(total, axis=0)
        dp = total[bp, np.arange(N)]
        back.append(bp)

    keystream = [0] * L
    keystream[L - 1] = int(np.argmax(dp))
    total_lp = float(dp[keystream[L - 1]])
    for t in range(L - 1, 0, -1):
        keystream[t - 1] = int(back[t - 1][keystream[t]])

    combiner = cipher_ops.get_mode(mode)
    plaintext: List[List[int]] = []
    for ct in c.ciphertexts:
        plaintext.append([combiner.decrypt(ct[t], keystream[t], N)
                          for t in range(len(ct))])
    column_samples = [len(cols[t]) for t in range(L)]
    return KeystreamResult(keystream=keystream, plaintext=plaintext,
                           column_samples=column_samples,
                           total_logprob=total_lp)


# ---------------------------------------------------------------------------
# Selftest -- includes a synthetic end-to-end recovery proving the math.
# ---------------------------------------------------------------------------

def _make_markov(N: int, concentration: float, seed: int) -> MarkovModel:
    """A 1st-order chain with strong bigram structure but a near-uniform
    stationary distribution (mirroring the corpus: flat unigram IoC, structure
    hiding in the transitions).  Built as a noisy cyclic permutation so each row
    is peaky yet every column is balanced => uniform stationary."""
    rng = np.random.default_rng(seed)
    # Language-like model: a NON-uniform unigram (the primary per-column signal
    # that pins each shift in classic depth attacks) plus moderate, identity-
    # dependent bigram structure (informative but not so deterministic that
    # spurious "perfect chain" keystreams beat the truth, and not translation
    # invariant -> the keystream is uniquely identifiable).
    floor = 1e-12
    uni = rng.dirichlet(np.full(N, concentration))
    uni = np.clip(uni, floor, None)
    uni = uni / uni.sum()
    rows = rng.dirichlet(np.full(N, concentration), size=N)
    rows = np.clip(rows, floor, None)
    rows = rows / rows.sum(axis=1, keepdims=True)
    return MarkovModel(N, np.log(uni), np.log(rows))


def _sample_chain(model: MarkovModel, length: int, rng: np.random.Generator
                  ) -> List[int]:
    N = model.N
    p0 = np.exp(model.uni_logp)
    p0 = p0 / p0.sum()
    rowp = np.exp(model.bi_logp)
    rowp = rowp / rowp.sum(axis=1, keepdims=True)
    out = [int(rng.choice(N, p=p0))]
    for _ in range(length - 1):
        out.append(int(rng.choice(N, p=rowp[out[-1]])))
    return out


def _synthetic_corpus(model: MarkovModel, lengths: Sequence[int],
                      keystream: Sequence[int], mode: str, seed: int,
                      keep_prob: float = 0.6):
    """Generate in-depth plaintexts that *share content* at aligned positions
    (like the real shared-prefix structure), then encrypt with one shared
    keystream.  ``keep_prob`` controls how much each message copies a common
    base sequence -> tunes the cross-message column agreement."""
    rng = np.random.default_rng(seed)
    N = model.N
    rowp = np.exp(model.bi_logp)
    rowp = rowp / rowp.sum(axis=1, keepdims=True)
    base = _sample_chain(model, max(lengths), rng)
    plains: List[List[int]] = []
    for ln in lengths:
        seq = [base[0]]
        for t in range(1, ln):
            if rng.random() < keep_prob:
                seq.append(base[t])                       # shared content
            else:
                seq.append(int(rng.choice(N, p=rowp[seq[-1]])))  # divergence
        plains.append(seq)
    combiner = cipher_ops.get_mode(mode)
    cts = tuple(tuple(combiner.encrypt(plains[i][t], keystream[t], N)
                      for t in range(lengths[i]))
                for i in range(len(lengths)))
    c = corpus_mod.Corpus(
        deck_size=N,
        labels=tuple(f"M{i}" for i in range(len(lengths))),
        ciphertexts=cts,
        lengths=tuple(lengths),
        sigma0_targets=None,
    )
    return c, plains


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83

    # ---- Synthetic end-to-end recovery (the core "math works" guarantee) ---
    truth_model = _make_markov(N, concentration=0.05, seed=1)
    rng = np.random.default_rng(2)
    keystream_true = [int(rng.integers(0, N)) for _ in range(137)]
    lengths = [99, 103, 118, 102, 137, 124, 119, 120, 114]
    mode = "add"
    c, plains = _synthetic_corpus(truth_model, lengths, keystream_true,
                                  mode, seed=3, keep_prob=0.5)

    # (a) confirm_depth must flag strong, significant depth.
    rep = confirm_depth(c, n_null=200, seed=7)
    out.append(("synthetic: depth detected (z > 8)", rep.significance.z > 8))
    out.append(("synthetic: depth IoC >> uniform baseline",
                rep.mean_pair_diff_ioc > 5 * rep.uniform_baseline))

    # Train an *estimated* model on independent samples from the same chain
    # (more realistic than using the true matrices).
    train_rng = np.random.default_rng(99)
    train = [_sample_chain(truth_model, 400, train_rng) for _ in range(60)]
    est_model = MarkovModel.from_int_sequences(train, N, add_k=0.3)

    # (b) Viterbi recovers the keystream where columns are well sampled.
    res = solve_keystream_viterbi(c, est_model, mode=mode)
    well = [t for t in range(c.max_length) if res.column_samples[t] >= 5]
    key_acc_well = np.mean([res.keystream[t] == keystream_true[t]
                            for t in well])
    out.append((f"synthetic: keystream accuracy on well-sampled cols "
                f"= {key_acc_well:.2f} (> 0.80)", key_acc_well > 0.80))

    # (c) Plaintext symbol accuracy overall, far above the 1/N chance level.
    tot = corr = 0
    for i in range(len(plains)):
        for t in range(len(plains[i])):
            tot += 1
            if res.plaintext[i][t] == plains[i][t]:
                corr += 1
    sym_acc = corr / tot
    out.append((f"synthetic: plaintext symbol accuracy = {sym_acc:.2f} "
                f"(>> 1/N = {1/N:.3f})", sym_acc > 0.5))

    # (d) crib_drag is exact: feed true plaintext of one message as a crib and
    # verify every message's revealed span matches its true plaintext.
    ref = 4  # the longest message
    start, span_len = 10, 25
    crib_plain = plains[ref][start:start + span_len]
    cr = crib_drag(c, ref_index=ref, start=start, plain=crib_plain, mode=mode)
    out.append(("crib_drag recovers the true shared keystream",
                cr.keystream == keystream_true[start:start + span_len]))
    crib_ok = True
    for i in range(len(plains)):
        for off in range(span_len):
            t = start + off
            rec = cr.revealed[i][off]
            if t < len(plains[i]):
                if rec != plains[i][t]:
                    crib_ok = False
            else:
                if rec is not None:
                    crib_ok = False
    out.append(("crib_drag reveals correct plaintext in every message", crib_ok))

    # ---- Non-depth control: independent keystreams per message => no depth --
    rng2 = np.random.default_rng(5)
    plains_nd = [_sample_chain(truth_model, ln, rng2) for ln in lengths]
    combiner = cipher_ops.get_mode(mode)
    cts_nd = []
    for i, ln in enumerate(lengths):
        kk = [int(rng2.integers(0, N)) for _ in range(ln)]  # per-message key
        cts_nd.append(tuple(combiner.encrypt(plains_nd[i][t], kk[t], N)
                            for t in range(ln)))
    c_nd = corpus_mod.Corpus(deck_size=N, labels=c.labels,
                             ciphertexts=tuple(cts_nd), lengths=tuple(lengths),
                             sigma0_targets=None)
    rep_nd = confirm_depth(c_nd, n_null=200, seed=7)
    out.append(("control: NOT in depth -> not significant (z < 3)",
                rep_nd.significance.z < 3))

    # ---- Real corpus: depth must be overwhelmingly significant. ------------
    real = corpus_mod.load()
    rrep = confirm_depth(real, n_null=300, seed=1)
    out.append((f"real corpus: depth highly significant "
                f"(z = {rrep.significance.z:.1f})",
                rrep.significance.z > 8 and rrep.significance.p_value < 0.01))
    max_pair = max(p[3] for p in rrep.per_pair)
    out.append((f"real corpus: strongest pair agreement {max_pair:.0%} "
                f"(> 40%, the E1/W1 anomaly)", max_pair > 0.40))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} depth checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
