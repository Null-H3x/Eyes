# Field Report 2 — The Coincidence Spectrum, Decomposed

**Series note.** Second report of the iterative series opened by FR1. Doctrine remains
Field Guides 1–5; FG6 stays reserved. This cycle executes the K-echo probe nominated in
FR1 §8 and closes it — in the opposite direction from the one the community folklore
expected.

**Scope constraint (given).** Isomorphs untouched. Both instruments read-only. The
admissible family space is the FR1 survivor set: static Perfectly Isomorphic
(progressive / Gromark / general-K) plus the named residuals.

**One-paragraph verdict.** The replicated lag-4 glyph-coincidence excess (2.16×,
z = +4.23) — the corpus's most famous statistical anomaly — is **not a keystream
property and not a cipher-mechanism signal**. Under pre-registered thresholds it is
TEMPLATE-ANCHORED: masking the certified isomorph spans collapses it (masked z = 1.37),
an exactly-period-4 keystream is excluded outright (z(8) = −0.10 against z(4) = 4.23),
and the corpus contains **zero** clean co-location events — no evidence of
position-locked keystream structure. The complete event ledger attributes all 26
lag-4 coincidences to roughly five repeated plaintext features counted with occurrence
multiplicity. The bonus finding is new plaintext morphology: a 9-glyph signature — the
**XYZ-motif**, pairs at relative offsets {(0,7), (2,5), (4,8)} — occurs embedded at
fixed offsets inside three distinct certified passages of T1 and once solo, and its
Z-pair alone generates every starred lag-4 site in T1. FR1's K-echo question is
answered: there is no K echo. What the spectrum fingerprints is the plaintext.

---

## 1. Corrections and negatives first

**My instrument needed three calibrations, and the failures taught the physics.** The
clean co-location statistic (§4) initially failed its own planted selftest: on a
keystream-return plant at corpus-matched site counts the within-triplet signal did not
fire (0 of 8 power replicates). Root cause, worth recording: co-location power is
driven by spatial **contrast**, not anchoring intensity. Raising the keystream return
rate from 0.28 to 0.60 made detection *worse* — when most positions are anchors, sites
spread uniformly and clustering vanishes. The detectable regime is sparse anchors with
high plaintext collision. The shipped selftest verifies the mechanism in that regime
(p = 0.005 on the strong plant, cross-triplet control quiet at 0.66) and *measures*
rather than asserts power at corpus-like counts: 0/8 fired under diffuse anchoring.
Consequence, folded into the pre-registration wording before the corpus run: a quiet
corpus co-location result is weak evidence against diffuse anchoring, not proof of
absence.

**Disclosure of a design-input pre-peek.** Before this instrument existed, the
inside/outside-span split of the observed d = 4 sites (16 in / 10 out) was computed as
design arithmetic. That look preceded formal pre-registration of the masking threshold
and revealed the likely direction of S2. The thresholds were nonetheless frozen from the
plant suite, unchanged; the co-location statistics (S3/S4) and every other verdict
remained corpus-unpeeked until the selftest went green. Stated so the reader can weight
S2 accordingly; S3–S5 carry no such caveat.

**The d = 9 residual look is post-hoc.** After the registered run, the masked d = 9
residual (z = 2.52, the only statistic that did not collapse under atlas masking) was
inspected descriptively. It decodes as shared-*opening* template — E1/W1/E2 all carry
the same repeat at t = 4 (glyph 62), because the atlas mask covers certified body
isomorphs but not the literal opening repeats. Logged watch-grade; the fix (a
full-template mask) is pre-registered for the next cycle, not claimed here.

## 2. Problem set and the frame

FR1 left the static family standing and asked where the lag-4 excess could live. Under
the static model c_m[t] = C[(σ·p_m[t] + base_m + K_g[t]) mod 83], a same-message glyph
coincidence c[t] = c[t+d] holds iff σ(p[t] − p[t+d]) ≡ K[t+d] − K[t] (mod 83). The
coincidence rate at lag d is therefore the **inner product of the plaintext lag-d
difference distribution and the keystream lag-d increment distribution**. If either
factor is uniform, the rate is exactly 1/83. A 2.16× excess is a *joint* alignment
constraint — it cannot belong to K alone or to plaintext alone, and every hypothesis
about it must say which side carries the structure and where.

Under the progressive gauge this specializes cleanly: coincidence at distance d ⟺ the
de-drifted stream u[t] = p[t] + drift·t repeats at distance d. The whole spectrum is
then the autocorrelation fingerprint of u.

Three decompositions separate the candidate sources. **Template masking** (S2): excess
carried by the certified repeated passages vanishes when their spans are removed.
**Clean co-location** (S3): position-locked keystream structure (ΔK₄[t] = 0 at specific
sites) makes sites co-locate across messages sharing K — including at positions where
the two messages carry *different* glyph values, which removes the shared-plaintext
confound without needing base knowledge. Content-driven structure has no positional
anchor and co-locates at chance; cross-triplet pairs share no K and are the built-in
negative control. **Multiples** (S5): an exactly-period-4 K forces equal excess at
d = 8, 12, …

## 3. Instrument, plants, pre-registration

`eyecho.py`, stdlib-only, deterministic, read-only. Five planted families at
corpus-matched shapes: null, keystream-return (diffuse and sharp-contrast variants),
progressive content structure (Δp₄ concentrated at one value — spike fires, co-location
must stay quiet: the discriminator), template (repeated passage with internal d = 4
links — spike fires unmasked, dies under true-span masking), and exact period-4 K
(spikes at 4 *and* 8). Selftest 12/12 green with two printed power notes.

| rule | threshold |
|---|---|
| spectrum spike | z ≥ 3.0 vs per-message unigram-permutation null |
| masked d = 4 verdict | z < 2.0 → TEMPLATE-ANCHORED; z ≥ 3.0 → corpus-wide; between → inconclusive |
| co-location fires | within-triplet pooled p < 10⁻³ AND cross-triplet control p > 0.01 |
| quiet co-location | reported as "no detection (power-limited)", not absence |
| period-4 K excluded | z(8) < 2.0 while z(4) ≥ 4.0 |

## 4. Results

**S1 — spectrum (pooled, unigram-permutation z).** The anomaly replicates exactly:
d = 4 at 2.16× (26/1000), z = +4.23. The rest of the spectrum has structure of its own:
d = 1 is significantly *suppressed* (0/1027, z = −3.52 — the zero-adjacent-doubles fact,
now with its z), d = 2 sits at −2.00, and a trio of soft suppressions at d = 15, 19, 22
(z ≈ −2.1 to −2.4). Secondary elevations at d = 9 (+2.10), 13 (+2.53), 17 (+2.35) — the
same distances the certified class patterns are rich in.

**S5 — multiples.** z(8) = −0.10, z(12) = −1.16 against z(4) = 4.23:
**an exactly-period-4 keystream is EXCLUDED** under the pre-registered rule. Whatever
K is, it does not repeat with period 4.

**S2 — template masking.** With all certified isomorph spans removed, d = 4 drops to
10 hits over 551 comparisons: 1.51×, z = 1.37 → **TEMPLATE-ANCHORED** per
pre-registration. The companion lags behave consistently: masked d = 13 collapses
(z = 0.36), masked d = 17 drops to 1.76, masked d = 3 and d = 7 go *negative*
(−1.83, −1.53). The one survivor, masked d = 9 at z = 2.52, decodes post-hoc as
opening-template leakage (§1).

**S3 — clean co-location.** Site counts per message are 2–4. Within-triplet pooled
clean co-location: **observed 0** against a null mean of 0.51 (p = 1.0); cross-triplet
control 2 vs 1.81 (p = 0.55). No position-locking detected — power-limited by design at
these site counts, but the direction is unambiguous: not one clean co-location event
exists in the corpus.

**S4 — near-dup detail.** The only co-located site pairs among the near-dups are
E1/W1 at t = 44 and E4/E5 at t = 35, and both are fully confounded — all four glyphs
equal, i.e. shared plaintext, the template again.

## 5. The event ledger — all 26, attributed

The site census with atlas annotation closes the anomaly completely.

**T1 (7 events, all starred).** Every starred site in T1 — E1@44, E1@72, W1@44, W1@74,
E2@49, E2@84 — is the *same relative position* of one repeated feature: offset +4 of
the **XYZ-motif**. The motif is a 9-glyph signature with equal-pairs at relative
offsets {(0,7), (2,5), (4,8)} — precisely class #M's pattern, core `A.B.CB.AC`. The
embedding verification: #M's six certified occurrences sit at fixed offsets *inside*
the larger certified passages — offset +6 into every #1/#C1 occurrence (W1@34→40,
W1@64→70, E2@39→45, E2@74→80) and offset +10 into #F (E1@30→40, W1@30→40, E2@35→45) —
plus one solo occurrence at E1@68 with no parent passage. Three distinct repeated
passages of T1 carry the same 9-glyph sub-word at different internal positions, and it
also occurs free-standing. The motif's Z-pair (offsets 4 and 8) *is* T1's entire
contribution to the lag-4 anomaly. The remaining T1-region event, W1@21, is a
head-region singleton.

**T2/T3 (starred: 10 events).** All are the #2-family's two internal pairs. #2⁻
(L = 25, occurrences E3@64, E4@73, W4@76, E5@74) carries d = 4 pairs at relative
offsets {0, 17}, generating E3@{64, 81}, E4@{73, 90}, W4@{76, 93}, E5@{74, 91} — eight
events, verified exactly against the census. #S (W4@36, E5@35) carries a d = 4 pair at
offset 0 — two more. This is also the answer to the T3-heaviness of the raw excess
(2.92× vs 1.89/1.66): the d = 4-dense #2 family *lives* in T2/T3. Class residency, not
keystream character.

**Unstarred residue (10 events).** E4@6, W4@6, E5@6 — one shared-T3-opening feature
(c[6] = c[10] = glyph 2 in all three messages) counted three times; the atlas mask does
not cover openings. E4@35 — the #S feature surviving in E4 outside a certified span
(its near-dup partner E5@35 is starred; the pair is glyph-identical there). E3@12 and
W1@21 — head-region singletons. W2@56, W2@73, W3@65, W3@78 — four genuine body
singletons in T2's Wests, against ≈ 7 expected corpus-wide at baseline.

**Deduplicated:** the 26 events reduce to ~5 repeated plaintext features (motif-Z,
#2-family pair A, pair B, #S pair, T3-opening pair) amplified by occurrence
multiplicity, plus ~7–8 background singletons at the noise floor. There is nothing
left for the keystream to explain.

## 6. Verdicts

1. **The d = 4 anomaly is retired as a cipher-mechanism signal.** It is
   template-anchored plaintext repetition. Any argument that used it to constrain the
   cipher mechanism — including the autokey-echo folklore FR1 already killed from the
   other side, and the long-retired small-plaintext-alphabet forcing — should cite this
   attribution.
2. **Exact period-4 K excluded** (pre-registered, S5).
3. **No position-locked keystream structure detected** (S3; power-limited, direction
   clean). FR1's K-echo probe returns empty: within the reach of these channels, K
   carries no lag-4 structure.
4. **The spectrum is a plaintext fingerprint.** Under the progressive gauge it is the
   autocorrelation of the de-drifted stream u: hard-forbidden repeats at d ∈ {1, 2},
   soft suppression at {15, 19, 22}, enrichment only at the repeated features'
   internal distances. Any C-candidate or crib whose de-drifted plaintext violates
   this profile is wrong. Conditional on the gauge, per FG4 discipline.

## 7. New plaintext morphology — the XYZ-motif

The motif is the report's constructive yield. A 9-glyph unit recurring inside three
different certified passages *at different internal offsets*, and once alone, behaves
like a **word or particle of the underlying text**, not an accident of one passage. Its
signature — same-value pairs at {(0,7), (2,5), (4,8)}, under progressive gauge
u-repeats at those spacings — is a hard shape constraint on any refrain crib: nine
consecutive plaintext tokens where positions 0/7, 2/5, and 4/8 carry equal de-drifted
values. Conversely, candidate wordlists can be screened for 9-token units with that
internal equality pattern. The #2-family's double-pair at spacing 17 and the #S pair
are the analogous fingerprints for the T2/T3 passages, and the fact that T1's motif
geometry differs from T2/T3's says the repeated passages are built from different
lexical material.

## 8. Horizon

(1) **Full-template mask, pre-registered next cycle:** atlas spans plus the
shared-opening depth spans (the literal repeats the atlas does not certify). Prediction
from this cycle's post-hoc look: the masked d = 9 residual collapses; if anything
survives a full-template mask at any lag, *that* is the first genuine corpus-wide
spectral signal. (2) **Occurrence-relative co-location:** absolute-position co-location
is the wrong coordinate for template structure; an instrument aligned on occurrence
starts can test whether template-internal coincidences constrain K increments across
occurrences — the one place template events still touch K under general-K. (3) **Motif
exploitation:** fold the XYZ shape constraint into the crib machinery (Eye Crib Tester
cascade) for refrain-region candidates. (4) **P1 stands.** Cross-triplet bridge pins
remain the strategic priority; this cycle spent no pins and removed a false lead from
the board.

## 9. Reproduction

`eyecho.py`: `python3 eyecho.py --selftest` (12 planted checks, gate; two power notes),
`python3 eyecho.py` (gate then corpus: S1 spectrum, S5 multiples, S2 masking, S3/S4
co-location, site census). Expects `noita_eye_core/corpus.json` and
`data/isomorph_atlas.json` (`EYE_CORPUS` / `EYE_ATLAS` overrides). Atlas values are
re-verified against the corpus before any statistic is printed; mismatch hard-fails
with prefix `XD-MBYG04K-URS3LF`. The motif embedding offsets in §5 are checkable by
hand from the atlas instance table in under a minute — the arithmetic is
start + 6 and start + 10.
