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

import math
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

    # Viterbi for the EXACT 1st-order Markov MAP:
    #   score = sum_i [ uni(p_i[0]) + sum_{t>=1} bi(p_i[t-1], p_i[t]) ]
    # Every message starts at column 0, and message presence is contiguous, so
    # a message present at column t (t>=1) is present at t-1 too: each symbol
    # after position 0 is scored by exactly one bigram term, and only the first
    # symbol carries a unigram term.  (We must NOT add a per-column unigram at
    # t>=1 -- that would double-count, since bi already accounts for the target
    # symbol's probability given its predecessor.)
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
        # total[s_prev, s_cur] = dp[s_prev] + bigram(s_prev -> s_cur)
        total = dp[:, None] + trans
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
    """A language-like ground-truth 1st-order chain for the synthetic test:
    a non-uniform unigram (Dirichlet) plus a non-uniform, non-translation-
    invariant transition matrix (Dirichlet rows)."""
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


def _score_keystream(c: corpus_mod.Corpus, model: MarkovModel,
                     key: Sequence[int], mode: str) -> float:
    """The exact 1st-order MAP objective the Viterbi maximises, scored directly
    (for brute-force cross-checking)."""
    combiner = cipher_ops.get_mode(mode)
    N = c.N
    total = 0.0
    for ct in c.ciphertexts:
        p = [combiner.decrypt(ct[t], key[t], N) for t in range(len(ct))]
        total += float(model.uni_logp[p[0]])
        for t in range(1, len(p)):
            total += float(model.bi_logp[p[t - 1], p[t]])
    return total


def _brute_force_best(c: corpus_mod.Corpus, model: MarkovModel, mode: str
                      ) -> Tuple[List[int], float]:
    import itertools
    N = c.N
    L = c.max_length
    best_key: List[int] = []
    best_score = -math.inf
    for key in itertools.product(range(N), repeat=L):
        s = _score_keystream(c, model, list(key), mode)
        if s > best_score:
            best_score = s
            best_key = list(key)
    return best_key, best_score


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83

    # ---- DP correctness: Viterbi == brute-force optimum on a tiny instance --
    sN, sL = 4, 4
    srng = np.random.default_rng(41)
    tiny_model = MarkovModel.from_int_sequences(
        [list(srng.integers(0, sN, size=30)) for _ in range(8)], sN, add_k=0.4)
    tiny_key = [int(srng.integers(0, sN)) for _ in range(sL)]
    tcomb = cipher_ops.get_mode("add")
    tiny_plains = [[int(srng.integers(0, sN)) for _ in range(sL)]
                   for _ in range(3)]
    tiny_cts = tuple(tuple(tcomb.encrypt(tiny_plains[i][t], tiny_key[t], sN)
                           for t in range(sL)) for i in range(3))
    tiny_c = corpus_mod.Corpus(deck_size=sN, labels=("a", "b", "c"),
                               ciphertexts=tiny_cts, lengths=(sL, sL, sL),
                               sigma0_targets=None)
    vit = solve_keystream_viterbi(tiny_c, tiny_model, mode="add")
    bf_key, bf_score = _brute_force_best(tiny_c, tiny_model, "add")
    out.append(("Viterbi total_logprob == brute-force optimum",
                abs(vit.total_logprob - bf_score) < 1e-9))
    out.append(("Viterbi keystream achieves the optimal score",
                abs(_score_keystream(tiny_c, tiny_model, vit.keystream, "add")
                    - bf_score) < 1e-9))

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

    # (b)-(d): exercise EVERY linear combiner mode end to end, since _dec_index
    # and crib_drag differ per mode.  Same plaintexts/keystream, different
    # cipher.  Recovery and crib propagation must both hold for each.
    for m in ("add", "sub", "beaufort"):
        cm, pm = _synthetic_corpus(truth_model, lengths, keystream_true,
                                   m, seed=3, keep_prob=0.5)

        res = solve_keystream_viterbi(cm, est_model, mode=m)
        well = [t for t in range(cm.max_length) if res.column_samples[t] >= 5]
        key_acc = np.mean([res.keystream[t] == keystream_true[t]
                           for t in well])
        tot = corr = 0
        for i in range(len(pm)):
            for t in range(len(pm[i])):
                tot += 1
                if res.plaintext[i][t] == pm[i][t]:
                    corr += 1
        sym_acc = corr / tot
        out.append((f"synthetic [{m}]: keystream acc {key_acc:.2f} (>0.80) "
                    f"& symbol acc {sym_acc:.2f} (>0.5)",
                    key_acc > 0.80 and sym_acc > 0.5))

        # crib_drag is exact: feed a message's true plaintext as a crib and
        # verify every message's revealed span matches its true plaintext.
        ref, start, span_len = 4, 10, 25
        crib_plain = pm[ref][start:start + span_len]
        cr = crib_drag(cm, ref_index=ref, start=start, plain=crib_plain, mode=m)
        crib_ok = (cr.keystream == list(keystream_true[start:start + span_len]))
        for i in range(len(pm)):
            for off in range(span_len):
                t = start + off
                rec = cr.revealed[i][off]
                expect = pm[i][t] if t < len(pm[i]) else None
                if rec != expect:
                    crib_ok = False
        out.append((f"crib_drag [{m}]: keystream + all-message reveal exact",
                    crib_ok))

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

    # --- edge / error paths & determinism -----------------------------------
    # confirm_depth is deterministic for a fixed seed.
    r1 = confirm_depth(real, n_null=50, seed=123)
    r2 = confirm_depth(real, n_null=50, seed=123)
    out.append(("confirm_depth is deterministic for fixed seed",
                r1.significance.z == r2.significance.z
                and r1.mean_pair_diff_ioc == r2.mean_pair_diff_ioc))

    # crib_drag rejects a crib running past the reference message.
    try:
        crib_drag(real, ref_index=0, start=real.lengths[0] - 1,
                  plain=[1, 2, 3], mode="add")
        crib_caught = False
    except ValueError:
        crib_caught = True
    out.append(("crib_drag rejects over-long crib", crib_caught))

    # solver rejects a model whose alphabet differs from the corpus.
    wrong = MarkovModel.from_int_sequences([[0, 1]], 2, add_k=0.5)
    try:
        solve_keystream_viterbi(real, wrong, mode="add")
        model_caught = False
    except ValueError:
        model_caught = True
    out.append(("solver rejects mismatched model alphabet", model_caught))

    # _dec_index rejects an unsupported mode.
    try:
        _dec_index(0, "rot13", N)
        mode_caught = False
    except KeyError:
        mode_caught = True
    out.append(("_dec_index rejects unsupported mode", mode_caught))

    # _dec_index is exactly the per-key decrypt for every mode (cross-check
    # against cipher_ops for a couple of ciphertext values).
    dec_ok = True
    for m in ("add", "sub", "beaufort"):
        comb = cipher_ops.get_mode(m)
        for cv in (0, 17, 82):
            idx = _dec_index(cv, m, N)
            if any(int(idx[s]) != comb.decrypt(cv, s, N) for s in range(N)):
                dec_ok = False
    out.append(("_dec_index == cipher_ops.decrypt for all modes/keys", dec_ok))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} depth checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
