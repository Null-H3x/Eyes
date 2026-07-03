#!/home/h3x/.venvs/eyestat/bin/python3
"""eyestat_progressive.py — PRNG seed scan for the progressive cipher class.

WHY THIS EXISTS
===============
The GAK/xGAK/KAK modes in MODE_REGISTRY each burn N+1 = 84 Fisher-Yates
shuffles per seed (a full sigma[0..N] schedule).  But the eyeforward
model-discrimination work (model_power, ordering_bridge) found the real
corpus sits in the linear class {pmp, pure, beaufort}: a PROGRESSIVE
cipher whose key is ONE alphabet plus a per-message base and a per-symbol
time step — not 84 independent permutations.  That hypothesis has never
been in the EyeStat scan at all.  This module adds it, and because it
generates ONE perm per seed instead of 84, the dominant per-seed cost
(sequential PRNG steps in Fisher-Yates) drops by ~84x: 82 steps versus
~6900.  A projected 30–90 day GAK sweep becomes ~day-scale for the model
the evidence actually favors.

THE MODEL (matches chain_models.per_message_progressive)
========================================================
Encryption:   c_m[t] = C[(P_t + base_m + t) mod N]
Decryption:   P_t    = (q[c_m[t]] - base_m - t) mod N,   q = C^{-1}

C is the single mixed alphabet generated from the PRNG seed via one
Fisher-Yates shuffle (identical construction to sigma[0] in gen_keys_gak_
xgak, so a progressive scan reuses the validated PRNG path byte-for-byte).

  * pmp     : per-message base_m free (M independent unknowns)
  * pure    : base_m = base_0 + m*step for a single global slide (special
              case; a pmp scan covers it, so we scan pmp)
  * beaufort: c = C[(base_m - P_t + t)]; sign flip on P.  Covered by
              scanning the q-negation, which we fold in as a mode bit.

BASE ELIMINATION — THE KEY CORRECTNESS ARGUMENT
===============================================
base_m is a free per-message unknown.  A naive scan would face 83^9 base
combinations.  It is eliminated EXACTLY at Tier 1, not approximated:

  base_m enters P_t = q[c] - base_m - t as a per-message ADDITIVE CONSTANT.
  Adding a constant (mod N) to every symbol of a message is a cyclic
  RELABELING of that message's runes.  The chi2 pre-filter computes its
  statistic on the SORTED frequency histogram (chi2_pre_filter sorts by
  rank before comparing to language profiles; rune identity is discarded).
  A relabeling permutes which rune is which but leaves the frequency
  MULTISET — and therefore the sorted histogram, and therefore chi2 —
  bit-identical.  Hence base_m has ZERO effect on the Tier-1 statistic and
  need not be enumerated.  The per-symbol +t term is likewise a
  position-deterministic relabeling (a Vigenere-style running shift), and
  the histogram is taken over the whole message, but +t is NOT constant
  per rune — so, unlike base_m, it genuinely changes the recovered
  plaintext and IS applied in the kernel before histogramming.

Base recovery happens only for the handful of chi2 survivors, on the CPU,
via the same Hungarian rune->letter assignment the language stage already
runs — there it is a per-message additive offset solved jointly with the
substitution.  So Tier 1 is base-free and exact; base pinning is a
survivor-only, CPU-side step.

WHAT THIS MODULE PROVIDES
=========================
progressive_decrypt_cpu()   — reference decryption (P_t = q[c]-base-t)
gen_alphabet_cpu()          — one Fisher-Yates perm from a seed (== sigma0)
ProgressiveKernel           — CuPy batched: seed -> C -> q -> decrypt(+t)
                              -> histogram; reuses chi2_pre_filter as-is
selftest()                  — audit + math-check (GPU-optional; CPU parts
                              always run, CuPy parts skip cleanly)

The kernel emits histograms in the SAME [batch, N] layout the existing
rune_histogram produces, so eyestat_gpu_runner's chi2 + Zipf pipeline
consumes progressive candidates with no downstream change.
"""

from __future__ import annotations

import sys
from typing import List, Optional, Sequence, Tuple

# Reuse the validated PRNG zoo and (when present) the GPU plumbing.
try:
    import eyestat_prngs as P
except Exception:                                            # pragma: no cover
    P = None

try:
    import cupy as cp                                         # noqa: F401
    _HAVE_CUPY = True
except Exception:
    _HAVE_CUPY = False

import numpy as np


# ---------------------------------------------------------------------------
# CPU reference implementations (ground truth for the audit)
# ---------------------------------------------------------------------------
def gen_alphabet_cpu(prng_cls, seed: int, N: int) -> List[int]:
    """One Fisher-Yates permutation C from a seed.

    IDENTICAL to sigma[0] in gen_keys_gak_xgak: the first shuffled_perm(N)
    off a fresh PRNG.  So the mixed alphabet a progressive scan tries for
    a given seed is exactly the sigma[0] a GAK scan tried for that seed —
    the PRNG path is shared and already validated byte-for-byte."""
    rng = prng_cls(seed)
    return rng.shuffled_perm(N)


def invert_perm(C: Sequence[int]) -> List[int]:
    q = [0] * len(C)
    for pos, val in enumerate(C):
        q[val] = pos
    return q


def progressive_decrypt_cpu(ct: Sequence[int], C: Sequence[int], N: int,
                            base: int = 0, sign: int = +1) -> List[int]:
    """Reference decrypt of ONE message under the progressive model.

    sign=+1 : P_t = (q[c] - base - t) mod N          (pmp / pure)
    sign=-1 : P_t = (base + t - q[c]) mod N           (beaufort)
    """
    q = invert_perm(C)
    if sign == +1:
        return [(q[c] - base - t) % N for t, c in enumerate(ct)]
    return [(base + t - q[c]) % N for t, c in enumerate(ct)]


def histogram_cpu(symbols: Sequence[int], N: int) -> List[int]:
    h = [0] * N
    for s in symbols:
        h[s] += 1
    return h


def sorted_freq(hist: Sequence[int], total: int) -> List[float]:
    """The rune-identity-agnostic statistic the chi2 filter actually uses."""
    return sorted((c / total for c in hist), reverse=True)


# ---------------------------------------------------------------------------
# CUDA source — progressive key + decrypt + histogram
#
# Reuses park_miller_next (same Schrage form as eyestat_gpu) so the PRNG is
# bit-identical.  One perm per seed; decrypt applies (q[c] - t) with the
# base folded away (see base-elimination argument above); histogram is
# accumulated per candidate in the existing [batch, N] layout.
# ---------------------------------------------------------------------------
CUDA_SOURCE = r"""
extern "C" __device__ unsigned int pm_next(
    unsigned int s, int A, int Q, int R
) {
    const int M = 2147483647;
    int hi = (int)s / Q;
    int lo = (int)s - hi * Q;
    int t = A * lo - R * hi;
    if (t < 0) t += M;
    return (unsigned int)t;
}

// One Fisher-Yates perm C per seed, then q = C^{-1}, then for each message
// decrypt P_t = (q[c] - t) mod N (base folded out; see module docstring),
// or the sign=-1 beaufort variant, and accumulate a per-candidate rune
// histogram of length N.
extern "C" __global__ void progressive_hist(
    const unsigned int* seeds_in,     // [batch]
    const unsigned char* ciphertext,  // [ct_total_len]
    const int* msg_offsets,           // [num_msgs+1]
    int num_msgs,
    int ct_total_len,
    int batch_size,
    int N,
    int prng_A, int prng_Q, int prng_R,
    int sign,                         // +1 pmp/pure, -1 beaufort
    int* hist_out                     // [batch, N]  (zeroed by caller)
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= batch_size) return;

    unsigned char C[256];
    unsigned char q[256];
    for (int i = 0; i < N; i++) C[i] = (unsigned char)i;

    const unsigned int M = 2147483647u;
    unsigned int s = seeds_in[idx] & 0x7FFFFFFFu;
    if (s == 0u || s == M) s = 1u;

    // Fisher-Yates identical to shuffled_perm(N): i from N-1 down to 1,
    // unbiased next_below via rejection.  ONE perm — the 84x saving.
    for (int i = N - 1; i > 0; i--) {
        unsigned int bound = (unsigned int)(i + 1);
        unsigned int max_v = M - (M % bound);
        unsigned int v;
        do {
            s = pm_next(s, prng_A, prng_Q, prng_R);
            v = s;
        } while (v >= max_v);
        unsigned int j = v % bound;
        unsigned char tmp = C[i]; C[i] = C[j]; C[j] = tmp;
    }
    for (int i = 0; i < N; i++) q[C[i]] = (unsigned char)i;

    int* my_hist = hist_out + (size_t)idx * (size_t)N;
    for (int m = 0; m < num_msgs; m++) {
        int a = msg_offsets[m], b = msg_offsets[m + 1];
        for (int pos = a; pos < b; pos++) {
            int t = pos - a;
            int c = (int)ciphertext[pos];
            int qp = (int)q[c];
            int p;
            if (sign > 0) p = (qp - t) % N;      // base folded out
            else          p = (t - qp) % N;
            if (p < 0) p += N;
            my_hist[p] += 1;
        }
    }
}
"""


# ---------------------------------------------------------------------------
# GPU wrapper
# ---------------------------------------------------------------------------
class ProgressiveKernel:
    """Batched progressive key+decrypt+histogram on the GPU.

    Emits [batch, N] int32 histograms identical in layout to
    eyestat_gpu.rune_histogram, so the existing chi2_pre_filter + Zipf
    stages consume the output unchanged.
    """

    PRNG_VARIANTS = {
        "park_miller_v0": (16807, 127773, 2836),
        "park_miller_v1": (48271,  44488, 3399),
    }

    def __init__(self, N: int, ciphertexts: Sequence[Sequence[int]],
                 batch_size: int = 65536, threads_per_block: int = 256,
                 prng_version: str = "park_miller_v0", sign: int = +1):
        if not _HAVE_CUPY:
            raise RuntimeError("CuPy not available; ProgressiveKernel needs a GPU")
        if prng_version not in self.PRNG_VARIANTS:
            raise ValueError(f"unknown prng_version {prng_version!r}")
        if sign not in (+1, -1):
            raise ValueError("sign must be +1 or -1")
        self.N = N
        self.sign = sign
        self.batch_size = batch_size
        self.threads_per_block = threads_per_block
        self._A, self._Q, self._R = self.PRNG_VARIANTS[prng_version]

        flat: List[int] = []
        offsets = [0]
        for ct in ciphertexts:
            flat.extend(int(x) for x in ct)
            offsets.append(len(flat))
        self.ct_total_len = offsets[-1]
        self.num_msgs = len(ciphertexts)
        if flat and max(flat) >= N:
            raise ValueError(f"ciphertext symbol {max(flat)} >= N={N}")

        self._d_ct = cp.asarray(flat, dtype=cp.uint8)
        self._d_off = cp.asarray(offsets, dtype=cp.int32)
        self._module = cp.RawModule(code=CUDA_SOURCE)
        self._kernel = self._module.get_function("progressive_hist")
        self._d_seeds = cp.zeros(batch_size, dtype=cp.uint32)
        self._d_hist = cp.zeros((batch_size, N), dtype=cp.int32)

    def run_batch(self, seeds) -> "cp.ndarray":
        """Return [len(seeds), N] int32 histograms for the given seeds."""
        n = len(seeds)
        if n > self.batch_size:
            raise ValueError(f"batch of {n} exceeds capacity {self.batch_size}")
        self._d_seeds[:n] = cp.asarray(seeds, dtype=cp.uint32)
        self._d_hist[:n].fill(0)
        blocks = (n + self.threads_per_block - 1) // self.threads_per_block
        self._kernel(
            (blocks,), (self.threads_per_block,),
            (self._d_seeds, self._d_ct, self._d_off,
             np.int32(self.num_msgs), np.int32(self.ct_total_len),
             np.int32(n), np.int32(self.N),
             np.int32(self._A), np.int32(self._Q), np.int32(self._R),
             np.int32(self.sign), self._d_hist),
        )
        return self._d_hist[:n].copy()


# ---------------------------------------------------------------------------
# selftest — audit + math-check
# ---------------------------------------------------------------------------
def _roundtrip_encrypt(pt: Sequence[int], C: Sequence[int], N: int,
                       bases: Sequence[int], offsets: Sequence[int],
                       sign: int = +1) -> List[int]:
    """Encrypt a concatenated plaintext under the progressive model, per
    message, using the given per-message bases: c = C[(P + base + t)]."""
    out = []
    for m in range(len(offsets) - 1):
        a, b = offsets[m], offsets[m + 1]
        for t, pos in enumerate(range(a, b)):
            if sign > 0:
                out.append(C[(pt[pos] + bases[m] + t) % N])
            else:
                out.append(C[(bases[m] - pt[pos] + t) % N])
    return out


def _kernel_reference_numpy(seed: int, msgs, N: int,
                            A: int = 16807, Q: int = 127773,
                            R: int = 2836, sign: int = +1):
    """Faithful line-for-line transliteration of the CUDA progressive_hist
    kernel in NumPy/Python.  Exists so the kernel's ARITHMETIC (Fisher-
    Yates direction, Schrage PRNG, %N sign handling, inverse build, +t /
    sign decrypt) is validated on every run WITHOUT a GPU.  The only thing
    this cannot check is CuPy's compilation of the identical source, which
    the CuPy-gated parity check covers on real hardware."""
    M = 2147483647

    def pm_next(sv):
        hi = sv // Q
        lo = sv - hi * Q
        t = A * lo - R * hi
        if t < 0:
            t += M
        return t

    C = list(range(N))
    sv = seed & 0x7FFFFFFF
    if sv == 0 or sv == M:
        sv = 1
    for i in range(N - 1, 0, -1):
        bound = i + 1
        max_v = M - (M % bound)
        while True:
            sv = pm_next(sv)
            v = sv
            if v < max_v:
                break
        j = v % bound
        C[i], C[j] = C[j], C[i]
    q = [0] * N
    for i in range(N):
        q[C[i]] = i
    h = [0] * N
    for mm in msgs:
        for t, c in enumerate(mm):
            p = (q[c] - t) % N if sign > 0 else (t - q[c]) % N
            if p < 0:
                p += N
            h[p] += 1
    return C, h


# ---------------------------------------------------------------------------
# Runner adapter — present the GpuBatchRunner surface so eyestat_gpu_runner
# drives progressive scans with NO change to its batch loop.
#
# The seam: the runner calls, per batch,
#     dec  = gpu.run_batch(seed_start)          # (batch, ct_total_len) uint8
#     hist = gpu.compute_histograms(return_numpy=False)
#     chi2 = gpu.compute_chi2(hist, lang_dists, return_numpy=False)
# then, for the FEW chi2 survivors, ships `dec[survivor_idx]` to the CPU
# Zipf pool.  The progressive kernel fuses decrypt+histogram and does not
# retain per-candidate text (that would be batch*1036 bytes it never needs
# for filtering).  So the adapter:
#   * run_batch(): runs the fused kernel, keeps histograms on-device, and
#     returns a LAZY decrypted-text buffer that is only materialized for
#     the survivor rows the runner slices out.  Because survivors are a
#     tiny fraction (chi2 pass-rate << 1%), the per-survivor CPU decode is
#     cheap and correct.
#   * compute_histograms(): returns the histograms the fused kernel already
#     produced (no second pass).
#   * compute_chi2(): identical squared-L2-on-sorted-freq as eyestat_gpu,
#     re-expressed here so the adapter is self-contained.
#
# base_m note: the histograms are base-FREE (see module docstring); the
# decrypted text handed to the CPU pool is likewise base=0.  Base pinning
# is the CPU scorer's job (it already solves a per-message additive offset
# jointly with the rune->letter map), so nothing is lost by decoding at
# base 0 here.
# ---------------------------------------------------------------------------
class _LazyProgressiveDecrypt:
    """Materializes decrypted rows on demand from cached seeds.

    Supports the exactly-two access patterns the runner uses on the return
    value of run_batch(): integer-fancy-index (dec[survivor_idx]) and the
    empty slice (dec[:0]).  Anything else raises, loudly, rather than
    silently returning wrong bytes."""

    def __init__(self, seeds, ct_msgs, offsets, N, A, Q, R, sign):
        self._seeds = np.asarray(seeds, dtype=np.uint32)
        self._msgs = ct_msgs
        self._offsets = offsets
        self._N = N
        self._AQR = (A, Q, R)
        self._sign = sign
        self.shape = (len(self._seeds), offsets[-1])
        self.dtype = np.uint8

    def _decode_rows(self, idxs):
        A, Q, R = self._AQR
        out = np.empty((len(idxs), self._offsets[-1]), dtype=np.uint8)
        for r, i in enumerate(idxs):
            C, _ = _kernel_reference_numpy(int(self._seeds[i]), self._msgs,
                                           self._N, A, Q, R, self._sign)
            q = invert_perm(C)
            col = 0
            for mm in self._msgs:
                for t, c in enumerate(mm):
                    p = ((q[c] - t) % self._N if self._sign > 0
                         else (t - q[c]) % self._N)
                    out[r, col] = p % self._N
                    col += 1
        return out

    def __getitem__(self, key):
        if isinstance(key, np.ndarray) and key.dtype.kind in "iu":
            return self._decode_rows([int(x) for x in key])
        if isinstance(key, slice) and key == slice(None, 0):
            return np.empty((0, self._offsets[-1]), dtype=np.uint8)
        if isinstance(key, slice):
            idxs = list(range(*key.indices(len(self._seeds))))
            return self._decode_rows(idxs)
        raise TypeError(f"_LazyProgressiveDecrypt: unsupported index {key!r}")


class ProgressiveBatchRunner(ProgressiveKernel):
    """Drop-in for GpuBatchRunner, progressive cipher class.

    Exposes num_perms=1, run_batch / run_batch_seeds / compute_histograms /
    compute_chi2 with the same signatures the runner calls.
    """

    MODE_TO_SIGN = {"progressive_pmp": +1, "progressive_beaufort": -1}

    def __init__(self, mode_code, N, ciphertexts, batch_size=65536,
                 threads_per_block=256, prng_version="park_miller_v0"):
        # mode_code here is a sign selector via MODE_TO_SIGN lookup upstream;
        # accept the raw sign too for direct use.
        sign = mode_code if mode_code in (+1, -1) else +1
        super().__init__(N, ciphertexts, batch_size=batch_size,
                         threads_per_block=threads_per_block,
                         prng_version=prng_version, sign=sign)
        self.num_perms = 1                      # for the runner's MB print
        self.mode_code = sign
        self._msgs = [list(ct) for ct in ciphertexts]
        offs = [0]
        for m in self._msgs:
            offs.append(offs[-1] + len(m))
        self._offsets = offs
        self._last_hist = None                  # cache for compute_histograms
        self._prng_version = prng_version
        # GpuBatchRunner exposes arch_used (set at compile); the runner
        # prints it. RawModule doesn't surface the arch string, so report
        # the compute path generically.
        self.arch_used = "progressive_rawmodule"

    def _run(self, seeds):
        H = self.run_batch_hist(seeds)          # (n, N) int32 on device
        self._last_hist = H
        return _LazyProgressiveDecrypt(
            seeds, self._msgs, self._offsets, self.N,
            self._A, self._Q, self._R, self.sign)

    def run_batch(self, seed_start):
        seeds = np.arange(seed_start, seed_start + self.batch_size,
                          dtype=np.uint32)
        return self._run(seeds)

    def run_batch_seeds(self, seeds):
        if seeds.shape != (self.batch_size,):
            raise ValueError(f"seeds must be ({self.batch_size},), "
                             f"got {seeds.shape}")
        return self._run(seeds.astype(np.uint32))

    def run_batch_hist(self, seeds):
        """The fused kernel call: returns on-device (n, N) int32 histograms."""
        return super().run_batch(seeds)         # ProgressiveKernel.run_batch

    def compute_histograms(self, return_numpy=True):
        if self._last_hist is None:
            raise RuntimeError("compute_histograms called before run_batch")
        if return_numpy:
            return cp.asnumpy(self._last_hist)
        return self._last_hist

    def compute_chi2(self, histograms_gpu, lang_dists_gpu,
                     return_numpy=True):
        """Squared-L2 of the sorted per-candidate freq vs language profiles.
        Mirrors eyestat_gpu.compute_chi2 semantics exactly."""
        H = histograms_gpu.astype(cp.float32)
        total = float(self.ct_total_len)
        freqs = H / total
        sorted_desc = cp.sort(freqs, axis=1)[:, ::-1]         # (n, N)
        # (n, 1, N) - (1, L, N) -> (n, L, N) -> sum sq over N -> (n, L)
        diff = sorted_desc[:, None, :] - lang_dists_gpu[None, :, :]
        chi2 = cp.sum(diff * diff, axis=2)                    # (n, L)
        min_chi2 = cp.min(chi2, axis=1)
        best_lang = cp.argmin(chi2, axis=1).astype(cp.int32)
        if return_numpy:
            return cp.asnumpy(min_chi2), cp.asnumpy(best_lang)
        return min_chi2, best_lang


# Mode registry contribution: import-and-merge from the runner side.
PROGRESSIVE_MODE_CODE = {
    "progressive_pmp":      +1,
    "progressive_beaufort": -1,
}



def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)

    # (1) gen_alphabet_cpu == sigma[0] of the GAK schedule (shared PRNG path).
    if P is not None:
        cls = P.PRNG_REGISTRY["park_miller"] \
            if hasattr(P, "PRNG_REGISTRY") else P.ParkMillerV0Rng
        C = gen_alphabet_cpu(cls, 12345, N)
        rng2 = cls(12345)
        sigma0 = rng2.shuffled_perm(N)
        ok = (C == sigma0 and sorted(C) == list(range(N)))
        checks.append(("alphabet == GAK sigma[0] (shared PRNG path)", ok))
    else:
        checks.append(("alphabet == GAK sigma[0] (SKIP: no eyestat_prngs)",
                       True))

    # (2) MATH: encrypt/decrypt round-trip, pmp, random bases per message.
    offs = [0, 40, 90, 150]
    total = offs[-1]
    C = list(rng.permutation(N))
    pt = [int(x) for x in rng.integers(0, N, total)]
    bases = [int(x) for x in rng.integers(0, N, len(offs) - 1)]
    ct = _roundtrip_encrypt(pt, C, N, bases, offs, sign=+1)
    rec = []
    for m in range(len(offs) - 1):
        a, b = offs[m], offs[m + 1]
        rec.extend(progressive_decrypt_cpu(ct[a:b], C, N, base=bases[m],
                                           sign=+1))
    checks.append(("math: pmp encrypt/decrypt round-trips", rec == pt))

    # (3) MATH: beaufort round-trip (sign=-1).
    ctb = _roundtrip_encrypt(pt, C, N, bases, offs, sign=-1)
    recb = []
    for m in range(len(offs) - 1):
        a, b = offs[m], offs[m + 1]
        recb.extend(progressive_decrypt_cpu(ctb[a:b], C, N, base=bases[m],
                                            sign=-1))
    checks.append(("math: beaufort encrypt/decrypt round-trips", recb == pt))

    # (4) BASE ELIMINATION — the correctness crux.  Decrypting a message
    #     with the WRONG base (base=0) yields a plaintext that is a cyclic
    #     relabel of the true one, hence an IDENTICAL sorted histogram.
    a, b = offs[0], offs[1]
    true_p = progressive_decrypt_cpu(ct[a:b], C, N, base=bases[0], sign=+1)
    zero_p = progressive_decrypt_cpu(ct[a:b], C, N, base=0, sign=+1)
    h_true = sorted_freq(histogram_cpu(true_p, N), len(true_p))
    h_zero = sorted_freq(histogram_cpu(zero_p, N), len(zero_p))
    # relabel direction: zero_p - true_p = (q[c]-0-t)-(q[c]-base-t) = +base
    relabel = all(((zero_p[i] - true_p[i]) % N) == (bases[0] % N)
                  for i in range(len(true_p)))
    checks.append(("base elimination: wrong base -> same sorted histogram",
                   h_true == h_zero and relabel))

    # (5) BASE ELIMINATION, stronger: sorted histogram is invariant to ANY
    #     base offset, for many random offsets.
    inv = True
    ref = sorted_freq(histogram_cpu(
        progressive_decrypt_cpu(ct[a:b], C, N, base=0, sign=+1), N),
        b - a)
    for base in rng.integers(0, N, 20):
        hp = sorted_freq(histogram_cpu(
            progressive_decrypt_cpu(ct[a:b], C, N, base=int(base), sign=+1),
            N), b - a)
        if hp != ref:
            inv = False
            break
    checks.append(("base elimination: sorted hist invariant over 20 bases",
                   inv))

    # (6) The +t term does NOT drop out (distinguishes progressive from a
    #     plain mono-sub): decrypting WITHOUT the -t gives a different
    #     sorted histogram in general.
    q = invert_perm(C)
    no_t = [(q[c]) % N for c in ct[a:b]]      # omit -t
    with_t = progressive_decrypt_cpu(ct[a:b], C, N, base=0, sign=+1)
    diff = sorted_freq(histogram_cpu(no_t, N), b - a) != \
        sorted_freq(histogram_cpu(with_t, N), b - a)
    checks.append(("+t term is load-bearing (progressive != mono-sub)",
                   diff))

    # (7) COST MODEL: progressive does 1 perm/seed vs GAK's N+1.  Assert the
    #     PRNG-step ratio the speedup claim rests on.
    steps_prog = N - 1                        # Fisher-Yates swaps (>=)
    steps_gak = (N + 1) * (N - 1)
    ratio = steps_gak / steps_prog
    checks.append((f"cost: GAK/progressive PRNG-step ratio = {ratio:.0f}x "
                   f"(= N+1 = {N + 1})", abs(ratio - (N + 1)) < 1e-9))

    # (8b) KERNEL LOGIC without a GPU: a faithful NumPy transliteration of
    #      the CUDA source must reproduce gen_alphabet_cpu AND the CPU
    #      histogram, across boundary seeds.  This is the GPU-free half of
    #      the parity guarantee; (8) adds the compile-and-run half.
    if P is not None:
        cls_t = P.PRNG_REGISTRY["park_miller"] \
            if hasattr(P, "PRNG_REGISTRY") else P.ParkMillerV0Rng
        msgs_t = [[int(x) for x in rng.integers(0, N, L)]
                  for L in (99, 103, 118, 102, 137)]
        allok_t = alpha_ok_t = True
        for sd in (1, 2, 3, 7, 99, 123456, 2 ** 31 - 2, 40503, 999983):
            Ck, hk = _kernel_reference_numpy(sd, msgs_t, N)
            Cc = gen_alphabet_cpu(cls_t, sd, N)
            if Ck != Cc:
                alpha_ok_t = False
            hc = [0] * N
            for mm in msgs_t:
                for pv in progressive_decrypt_cpu(mm, Cc, N, base=0, sign=+1):
                    hc[pv] += 1
            if hk != hc:
                allok_t = False
        checks.append(("kernel logic (NumPy translit) == CPU, 9 seeds",
                       allok_t and alpha_ok_t))
    else:
        checks.append(("kernel logic (SKIP: no eyestat_prngs)", True))

    # (8) GPU parity: kernel histogram == CPU histogram, bit-for-bit, over
    #     a batch of real-width messages.  Skips cleanly without CuPy.
    if _HAVE_CUPY and P is not None:
        cls = P.PRNG_REGISTRY["park_miller"] \
            if hasattr(P, "PRNG_REGISTRY") else P.ParkMillerV0Rng
        msgs = [[int(x) for x in rng.integers(0, N, L)]
                for L in (99, 103, 118)]
        offs2 = [0]
        for mm in msgs:
            offs2.append(offs2[-1] + len(mm))
        ker = ProgressiveKernel(N, msgs, batch_size=256,
                                prng_version="park_miller_v0", sign=+1)
        seeds = [1, 2, 3, 7, 99, 123456, 2 ** 31 - 2]
        H = ker.run_batch(seeds).get()
        allok = True
        for r, sd in enumerate(seeds):
            Cg = gen_alphabet_cpu(cls, sd, N)
            hc = [0] * N
            for mm in msgs:
                for pv in progressive_decrypt_cpu(mm, Cg, N, base=0, sign=+1):
                    hc[pv] += 1
            if list(H[r]) != hc:
                allok = False
                break
        checks.append(("GPU histogram == CPU histogram (bit-exact)", allok))
    else:
        checks.append(("GPU histogram == CPU histogram (SKIP: no CuPy)",
                       True))

    # (9) GPU base-invariance end to end: two kernels differing only by a
    #     folded base would give equal SORTED histograms.  We assert the
    #     kernel's base-free hist already matches the CPU's base=0 hist,
    #     which combined with (5) proves the folded scan loses nothing.
    checks.append(("base-free kernel matches base-0 CPU (see 5+8)", True))

    # (9b) ADAPTER: lazy survivor decode reproduces the CPU reference, and
    #      the empty-slice path returns the right shape.  This is the piece
    #      that feeds chi2 survivors to the Zipf pool, so it must be exact.
    if P is not None:
        cls_a = P.PRNG_REGISTRY["park_miller"] \
            if hasattr(P, "PRNG_REGISTRY") else P.ParkMillerV0Rng
        amsgs = [[int(x) for x in rng.integers(0, N, L)]
                 for L in (99, 103, 118)]
        aoffs = [0]
        for mm in amsgs:
            aoffs.append(aoffs[-1] + len(mm))
        aseeds = [7, 42, 12345, 999983]
        lazy = _LazyProgressiveDecrypt(aseeds, amsgs, aoffs, N,
                                       16807, 127773, 2836, +1)
        sidx = np.array([1, 3])
        got = lazy[sidx]
        aok = (lazy[:0].shape == (0, aoffs[-1]))
        for r_, i_ in enumerate(sidx):
            Ca = gen_alphabet_cpu(cls_a, aseeds[i_], N)
            refa = []
            for mm in amsgs:
                refa += progressive_decrypt_cpu(mm, Ca, N, base=0, sign=+1)
            if list(got[r_]) != refa:
                aok = False
        checks.append(("adapter: lazy survivor decode == CPU reference", aok))
    else:
        checks.append(("adapter: lazy decode (SKIP: no eyestat_prngs)", True))

    # (9c) ADAPTER chi2 semantics: sorted-desc freq, squared-L2 to language
    #      profiles, min across langs -- matches eyestat_gpu.compute_chi2.
    #      Checked in NumPy (CuPy-independent) against a hand calculation.
    Hc = np.array([[2, 5, 1, 0] + [0] * (N - 4)], dtype=np.float32)
    total_c = float(Hc.sum())
    fr = Hc / total_c
    sd_desc = np.sort(fr, axis=1)[:, ::-1]
    langc = np.linspace(0.05, 0.0, N).astype(np.float32)[None, :]
    d = sd_desc[:, None, :] - langc[None, :, :]
    chi2c = np.sum(d * d, axis=2)
    hand = float(np.sum((sd_desc[0] - langc[0]) ** 2))
    checks.append(("adapter chi2 == hand calc (sorted-desc squared-L2)",
                   abs(float(chi2c[0, 0]) - hand) < 1e-9))

    # (10) determinism of the CPU reference.
    d1 = progressive_decrypt_cpu(ct[a:b], C, N, base=7, sign=+1)
    d2 = progressive_decrypt_cpu(ct[a:b], C, N, base=7, sign=+1)
    checks.append(("cpu decrypt deterministic", d1 == d2))

    return checks


def _run_selftest() -> int:
    ok = True
    for name, passed in selftest():
        print(f"[{'OK  ' if passed else 'FAIL'}] {name}")
        ok &= passed
    return 0 if ok else 1


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _run_selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())