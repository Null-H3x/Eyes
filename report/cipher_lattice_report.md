# Cipher-Construction Lattice — what fits the validated structure

*Reproduce: `python3 eyewitness/cipher_lattice.py`. Constructions are kept only if they fit EVERY validated structural fact.*

## The hard constraints (the filter)
1. N=83 (prime), flat unigram (IoC≈uniform).
2. **Interrelated alphabets** — isomorphs z≈117 (single mixed alphabet family; rules out independent-column / unrelated-alphabet OTP).
3. **Position-dependent within a message** — same plaintext at different positions gives different (isomorphic) ciphertext (E1@39 vs @67: 0/20 identical, same pattern).
4. **Per-message variation required** — E2 is isomorphic to E1 but value-shifted (different base), so a single global key is insufficient.
5. **Keys cluster** — E1≈W1 share a key: 44% identical glyphs, in blocks.
6. **Re-sync: 5 events** in E1/W1 (identical→differ→identical) — the difference does NOT propagate.
7. Literal universal (66,5) header; no periodicity, no transposition, no fractionation; hard-coded/offline-authored.

## SURVIVING family
**A position-indexed-keystream substitution over a single interrelated (mixed) alphabet C, with a per-message/per-group key offset (base).**

`c[m][t] = C[(p[m][t] + base_m + K[t]) mod 83]`, K a position keystream shared by all messages; base_m the per-message offset (clusters: E1=W1, E2 differs).

| construction | fits? | why |
|---|---|---|
| **A. Progressive / Trithemius** (K[t]=t, linear slide) + per-msg base | **FITS** | position-only keystream re-syncs; +base gives per-msg variation; single mixed alphabet = interrelated. The simplest survivor. |
| **B. General aperiodic position-keystream** (K[t] arbitrary, same for all msgs) + per-msg base | **FITS** | same as A but K need not be linear; isomorph data does not force K linear. |
| **C. Per-message/group MIXED-ALPHABET progressive** (C_m = S_m∘C, all related) | **FITS** | a per-message substitution stacked on the slide is absorbed into a per-message alphabet; still single-family/interrelated. |
| **D. Plaintext-autokey lag-1** (keystream = prior plaintext) + per-msg seed | **NOT EXCLUDED** | it re-syncs one position late; distinguishing it from A/B needs the plaintext (lag-0 vs lag-1). A residual alternative. |

## EXCLUDED constructions (with reason)
| construction | verdict | reason |
|---|---|---|
| Ciphertext-autokey (any lag) | **EXCLUDED** | difference would propagate; E1/W1 show 5 clean re-syncs (`resync`). |
| Single global key, no per-message base | **EXCLUDED** | E2 is isomorphic-not-identical to E1 (needs per-message base). |
| Pure progressive with NO per-message offset | **EXCLUDED** | would make shared openings identical; they are value-shifted across some msgs. |
| Transposition / cut-and-shuffle on glyph order | **EXCLUDED** | transposition ruled out; would also break the re-sync block alignment. |
| Fractionation / Trifid (on eye-marks) | **EXCLUDED** | eye-mark streams structureless; no period (`trifid`). |
| Periodic Vigenère / monoalphabetic / block / AES-CTR | **EXCLUDED** | prior calibrated tests. |

## Stacked-cipher (combination) note
- substitution ∘ position-keystream → absorbed into a per-message/group mixed alphabet (construction C).
- anything ∘ transposition → excluded (transposition out; breaks re-sync).
- two stacked position-keystreams → collapse to one combined K (B).
- a 0–82 'cut'/offset → exactly the per-message base in A/B/C.
So the community 'GAK/XGAK/stacked-with-cut' theories all reduce to the single surviving family above: **mixed-alphabet position-keystream + per-message base**, differing only in whether K is linear (A) or general (B) and whether the alphabet is global (A/B) or per-group (C).

## Honest open sub-questions
- K linear (progressive) vs general aperiodic — not yet distinguished.
- position-keystream (A/B) vs plaintext-autokey lag-1 (D) — needs plaintext.
- the per-message base grouping (why E1=W1 share, E2 differs).
- ALL of the above are moot for READING without the glyph→character ordering — the standing bottleneck.
