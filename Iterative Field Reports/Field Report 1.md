# Field Report 1 — The Divergence Channel

**Series note.** This opens the iterative Field Report series. Field Guides 1–5 remain the
standing doctrine; FG6 stays reserved for the day C partially falls. Field Reports are the
running lab record of the workflow loop: problem set → research → challenge → postulate →
challenge → test → publish.

**Scope constraint (given).** Every attempt must leave the isomorphs untouched. The admissible
family space is therefore: GAK, XGAK, Perfectly Isomorphic, Phrase Isomorphic, Isomorphic
ciphers — the black region of the community hierarchy diagram
(`data/updated_isomorphic_cipher_hierarchy.webp`). Both instruments in this report are
read-only: no corpus value is modified, no isomorph filtered, weighted, or perturbed.

**One-paragraph verdict.** Two independent channels — the within-message repeat channel and
the near-duplicate divergence channel — were tested this cycle, both with planted selftests
green before the corpus was touched and thresholds frozen beforehand. Result: the offset
stream shows **no detectable plaintext-fed component**. Pure lag-k GAK is excluded
deductively for all k ∈ [1, 25]. Lag terms riding a position clock (XGAK-lag) are excluded
at two-pair strength for k ∈ {3,4,5,6,7,9,10} and at one-pair strength for k ∈ {1,2,8},
with zero support anywhere. Σ-type autokey (GAK-Σ / Alberti / XGAK-Σ) is rejected on the
pooled re-sync ledger at p = 5.5 × 10⁻⁶ (robust to dropping the weakest pair: 6.9 × 10⁻⁶),
up to one stated loophole. Within the admissible space, the survivor is the **static family —
Perfectly Isomorphic: progressive / Gromark / general-K** — plus two named residuals. The
static-vs-dynamic fork (WAY_FORWARD P4) has moved, and the d = 4 anomaly can no longer be
an autokey echo.

---

## 1. Corrections and negatives first

**FG5 §2 sharpening.** The claim "under plaintext-autokey, re-syncs are free — identical
plaintext at aligned positions re-synchronizes the state automatically" is
family-dependent and was stated one family too wide. It is true for **lag-k** autokey
(state = p[t−k]; k positions of matching plaintext heal the state). It is **false for
Σ-type** autokey (state = running plaintext sum; matching subsequent plaintext *preserves*
the accumulated difference and never heals it — agreement can resume only when the running
difference-sum returns to 0 mod 83, a coincidence per opportunity). This report exploits
exactly that asymmetry.

**Instrument self-correction, logged.** The first two echo statistics I built failed their
own planted selftests and were discarded before any corpus contact. (i) Raw lag-k
co-disagreement: the run-preserving null absorbs nearly all of it at corpus densities
(z ≈ 3.7 under planted truth, below bar). (ii) "Clean echo" (isolated disagreement pairs at
spacing k): isolated edits are rare at 0.55–0.92 disagreement density, so the statistic
starves (z ≈ 0.5 under planted truth). The production statistics below were derived for the
high-density regime and only then passed plants. The selftest gate did its job twice.

**Pre-registration wording correction.** The alignment-guard note originally conflated two
cases. Corrected reading: trailing agreement below floor triggers an offset sweep; recovery
at a nonzero shift = indel desync (truncate); **flat at all shifts = no indel** — the tail
is genuine plaintext divergence and the pair remains frame-valid (heads and mid-body
agreement islands at shift 0 only prove the alignment). Both flagged pairs came back flat at
all shifts; no verdict in this report depends on the flagged pairs (robustness in §6).

**Priced accident, not perfection.** The lag falsifier is not literally zero-tolerant.
Plants (200 runs) verified the accident mechanism and rate: a fresh edit at t+k exactly
cancelling an echo (Δp pairs summing to 0 mod 83) occurs at ≈ (edit pairs at spacing k)/83
per pair — observed 23/200 plants, matching prediction — and one accident spawns violations
at both t and t+2k. The statistic therefore clusters violations 2k apart into single
*events*, and thresholds are priced off the measured accident rate.

---

## 2. Problem set

FG5's consolidated model: c_m[t] = C[(σ·p_m[t] + off_m[t]) mod 83]. The open fork (P4) is
the structure of `off`: **static** (position-driven only: progressive drift, Gromark
primer, general per-triplet K[t]) versus **dynamic** (a plaintext-fed term: lag-k or
running-sum Σ, pure or hybridized with a clock — GAK and XGAK). In hierarchy terms:
static ⇒ Perfectly Isomorphic; plaintext-fed ⇒ Phrase Isomorphic.

The untapped observable: each triplet contains a near-duplicate pair in body depth —
E1/W1 (44.9 % positionwise agreement over the 98-position overlap, t ≥ 1), W2/W3 (7.9 %),
E4/E5 (27.4 %) — replicating the keyspace ledger's figures exactly under full-overlap
alignment from position 0. Agreement at 25–45× the 1/83 noise floor is itself proof that
each pair shares effective base and keystream where plaintext matches. Consequently, in the
pairwise comparison **every position-driven term cancels** — base_m, drift·t, and any
per-triplet K[t] alike. The disagreement indicator D[t] = [c_A[t] ≠ c_B[t]] is a channel
that sees *only* the plaintext-fed component of the offset, if one exists. The pair channel
is a null test for dynamics, and it needs zero pins.

## 3. Deduction A — the repeat channel kills pure lag-k to k = 25

Under any pure lag-k autokey — off[t] = β + f(p[t−k]) for any function f, any σ, any
alphabet C — two same-plaintext instances **within one message** force glyph-**identical**
ciphertext at every interior position j ≥ k: plaintext and state both repeat, β is the same
message constant, and C is a fixed bijection. This is the same lever that killed
ciphertext-autokey, pointed at the plaintext-fed branch. The prediction is raw identity, not
isomorphism, and it is directly checkable against the certified atlas
(`data/isomorph_atlas.json`, values re-verified against corpus.json this session: PASS).

Every certified within-message pair violates it at every position:

| class | message | instances | L | forced-identity positions observed | last violating j |
|---|---|---|---|---|---|
| #1 | West 1 | @34 vs @64 | 18 | 0 | 17 |
| #1 | East 2 | @39 vs @74 | 18 | 0 | 17 |
| #M | East 1 | @40 vs @68 | 9 | 0 | 8 |
| #M | West 1 | @40 vs @70 | 9 | 0 | 8 |
| #M | East 2 | @45 vs @80 | 9 | 0 | 8 |
| #C0 | East 2 | @39 vs @74 | 24 | 0 | 23 |
| #C1 | West 1 | @34 vs @64 | 26 | 0 | 25 |
| #M- | E1/W1/E2 | three pairs | 8 | 0 | 7 |

A violation at position j kills every k ≤ j. The #C1 pair (L = 26) therefore excludes
**pure lag-k GAK for all k ∈ [1, 25]**, deductively, with no statistics involved.

Scope, stated precisely: the deduction uses within-message pairs only (β cancels trivially;
cross-message pairs would need the shared-base premise and are not used). k ≥ 26 is
untouched by this channel. XGAK-lag survives it (the clock term drift·d breaks the identity
forcing and yields exactly the observed skeleton isomorphs), as do Σ-type generators
(Δ = intervening plaintext sum). Those go to the pair channel.

## 4. The pair channel — derivations

Write Δp[t] = p_A[t] − p_B[t] over the aligned overlap (analysis window t ≥ 1; position 0
is the per-message indicator and disagrees by construction).

**Static.** off_A ≡ off_B, so agree(t) ⟺ Δp[t] = 0. D is the plaintext edit set —
no structure beyond the edits.

**Lag-k term (pure or XGAK-lag; the clock cancels pairwise).**
agree(t) ⟺ σΔp[t] + Δp[t−k] ≡ 0 (mod 83). To first order D = P ∪ (P + k): every edit
echoes k later. Two consequences carry the analysis at any edit density:

*Falsifier — flanked-violation events v_ev(k).* A position with D[t] = 1 and agreement at
**both** t − k and t + k requires an exact mod-83 cancellation: if the edit is at t, the
echo forces D[t+k]; if it is at t − k, the edit itself forces D[t−k]. Plants verified the
accident price (§1); violations 2k apart are one accident and are clustered into one event.
Under lag-k truth E[v_ev(k)] ≈ 0.1 at corpus sizes and v_ev is large at every *other* lag —
the census both falsifies wrong k and identifies the true one.

*Signature — agreement echo Y(k).* Under lag-k, agreement at t requires edit-free plaintext
at {t, t−k}, so P(agree at t ∧ t+k) = (1−p)³ versus (1−p)⁴ generically: a forced
autocorrelation spike at exactly k. Scored against a run-permutation null (agreement- and
disagreement-run multisets preserved, order shuffled, 2000 samples) so content clumping is
absorbed. Honest power note from plants: at corpus densities the per-pair echo z under truth
averages only ≈ 1.5 (n ≈ 100); the census is the primary statistic, the echo confirmatory.

**Σ-type term (GAK-Σ / Alberti; XGAK-Σ identical pairwise).**
agree(t) ⟺ σΔp[t] + S[t] ≡ 0 with S[t] = Σ_{j<t} Δp[j] mod 83. S moves only at edits;
divergence persists until S returns to 0. Every resumption of agreement after first
divergence is a mod-83 coincidence. Ledger: R = agreement-run resumptions, with the
maximally conservative null that *every* disagreement position is an edit granting a fresh
1/83 return draw: p_Σ = P(Binom(|D|, 1/83) ≥ R). Anything the null concedes makes the test
weaker, never stronger.

**Loophole, stated.** Value-multiset-balanced rewrites (anagram-grade edits) return S to 0
by construction and evade the Σ ledger. Given a puzzle author with documented affection for
secret permutations, this is not a throwaway caveat; it is the one door left open on the Σ
side.

## 5. Pre-registered thresholds (frozen on plants, before corpus)

| rule | threshold | pricing basis |
|---|---|---|
| lag-k rejected (per pair) | v_ev(k) ≥ 2 | P(v_ev(k_true) ≥ 2) ≤ 1/40 per pair on 40-plant sweeps per density |
| lag-k alive (per pair) | v_ev(k) ≤ 1 | one priced accident allowed |
| lag-k excluded (family) | rejected on ≥ 2 guard-valid pairs | ≈ 0.2 % false-exclusion of a true k |
| per-pair watch | v_ev ≤ 1 ∧ Y-z ≥ 2.5 | 0/30 static plants reached 2.5 at 0.55 |
| family support | census-unique survivor + pooled z ≥ 2.5 (watch) / ≥ 4.0 (full) | plant-pooled z = 4.6 under truth |
| Σ rejected | pooled p_Σ < 10⁻⁴ | conservative binomial null |
| alignment guard | floor 0.05 + offset sweep ±5 | §1 wording correction |

Selftest: 18/18 green across static, lag-4, XGAK-lag-4, Σ, XGAK-Σ, clustered-edit, and
dense regimes, including 10/10 no-false-watch on static at density 0.55. Census power,
measured: 40/40 at density 0.35, 34/40 at 0.55, 4/40 at 0.73 — the two denser corpus pairs
carry progressively less lag-census weight, and the report treats them accordingly.

## 6. Corpus results

Replication anchors first: agreement rates match the keyspace ledger exactly (0.449 / 0.079
/ 0.274 on the t ≥ 1 window; 0.444 / 0.078 / 0.272 from position 0), and the E1/W1 ledger
returns R = 5 — the same five clean re-syncs that killed CTAK, now doing second duty.

**E1/W1** (n = 98, guard PASS). Shared head through t = 24, then six disagreement runs
(30, 10, 5, 4, 4, 1) interleaved with agreement runs 13, 4, 1, 1, 1.
Σ ledger: R = 5, |D| = 54, p_Σ = 4.9 × 10⁻⁴ — five sum-returns demanded of a running walk
on Z₈₃. Lag census: k ∈ {3,4,5,6,7,9,10} REJECTED (v_ev 2–5). k ∈ {1,2,8} carry v_ev = 0,
but the null says v = 0 is unremarkable there (P(v0|null) = 0.16, 0.83, 0.04) and no z
reaches watch (max 1.91 at k = 8; k = 2 sits at −2.27, an unregistered curiosity logged as
watch-grade). Nothing supported.

**W2/W3** (n = 101, guard flat-at-all-shifts ⇒ no indel). Head of 5, then near-total
divergence (runs 34, 33, 19, 7) with three single-position agreement islands. This is the
one pair whose surface *looks* Σ-like; its own ledger (R = 3, |D| = 93, p = 0.10) neither
condemns nor clears Σ, and the lag census abstains at this density, exactly as plants
predicted. It contributes to the pooled ledger and nothing else.

**E4/E5** (n = 113, guard flat-at-all-shifts ⇒ no indel). Head of 20, one 71-long
disagreement run, five short agreement islands (3, 3, 3, 1, 1). Σ ledger: R = 5, |D| = 82,
p_Σ = 3.2 × 10⁻³. Lag census: **all ten lags REJECTED** (v_ev 2–5).

**Family aggregation.**

*Lag terms (with or without a clock), k ∈ 1–10:* k ∈ {3,4,5,6,7,9,10} rejected on two
pairs → **EXCLUDED**. k ∈ {1,2,8} rejected on E4/E5, abstained-without-support on E1/W1 →
excluded at one-pair strength; no k anywhere reached even per-pair watch. Combined with
Deduction A, the lag branch retains only: k ≥ 11 riding a position clock, and k ≥ 26 pure.

*Σ branch:* pooled R = 13 over |D| = 229 → **p_Σ = 5.5 × 10⁻⁶, REJECTED**. Robustness:
dropping W2/W3 entirely leaves R = 10 over 136, p = 6.9 × 10⁻⁶; E1/W1 alone sits at
4.9 × 10⁻⁴. The verdict does not lean on the flagged pair, and thirteen independent
returns-to-zero of a Z₈₃ walk is not a thing unstructured edits do.

**Verdict (pair channel, family level).** No plaintext-fed offset component detected.
Within the admissible isomorph-preserving space, the survivors are the **static family —
Perfectly Isomorphic: progressive / Gromark / general per-triplet K** — plus two named
residuals: (i) Σ-type with value-multiset-balanced rewrites, (ii) lag terms outside the
tested windows (k ≥ 11 with clock; k ≥ 26 pure).

## 7. Consequences

**The d = 4 anomaly loses its autokey explanation.** Lag-4 specifically is the hardest-hit
hypothesis in this report: deductively dead as pure autokey (Deduction A), two-pair
excluded as a clocked term (v_ev = 5 on E1/W1, 4 on E4/E5). The replicated lag-4
coincidence excess (≈ 2.2×) must now be sourced **inside the static family** — a
per-triplet K[t] with lag-4 autocorrelation (a period-4 component, a Gromark-style
length-4 primer cycle, or kin) or plaintext periodicity. This converts P4 from
"static vs dynamic" into a sharper question: *what static keystream structure produces a
lag-4 echo in depth?*

**FG2/3's plaintext measurement firms up.** The high-entropy de-drift result (unigram IoC
0.0126, effective alphabet ≈ 79) carried FG4's widened error bars "if dynamic." The dynamic
branch is now reduced to the two residuals above; the static reading under which the
measurement was taken is the surviving default, not one fork of two.

**Scoreboard deltas to apply.** Per-message-progressive: SUPPORTED holds and strengthens.
Free-delta/autokey-1 (PERMISSIVE): the lag-1 clocked variant is now one-pair excluded with
no support and its pure form is deductively dead — the row should move. A new row for
Σ-family: REJECTED-with-loophole, p = 5.5 × 10⁻⁶.

## 8. Horizon — next iteration targets

The loop's next most-valuable test, in order: (1) **K-echo probe** — under the static
survivor, the d = 4 excess predicts lag-4 autocorrelation *in the per-triplet keystream
itself*; the depth tree's 2-deep positions (136 of them) let K-differences be probed
without pins — design the statistic, pre-register, plant, run. (2) **Balanced-edit probe**
— the Σ loophole is testable in principle: under balanced-Σ, agreement islands must
coincide with edit blocks that are internally multiset-balanced, which constrains island
spacing; quantify whether the observed island geometry (E4/E5's five islands inside one
71-run neighborhood) is loophole-compatible. (3) **Bridge synergy (P1)** — the pair-channel
machinery transfers as-is to any cross-triplet near-alignment candidates surfaced while
hunting W2/E4/W4 bridge pins.

## 9. Reproduction

`eyefork.py` (stdlib only, deterministic, error prefix `XD-MBYG04K-URS3LF`):
`python3 eyefork.py --selftest` (18 planted checks, gate), `python3 eyefork.py --atlas`
(Deduction A table), `python3 eyefork.py` (selftest gate then corpus run; refuses on red).
Expects `noita_eye_core/corpus.json` and `data/isomorph_atlas.json` (paths overridable via
`EYE_CORPUS` / `EYE_ATLAS`). Both instruments read-only with respect to the corpus; the
atlas-vs-corpus value check hard-fails on any mismatch before any deduction is printed.
