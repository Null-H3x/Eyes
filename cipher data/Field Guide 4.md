# Cipher Family Field Guide 4 — The Competing Model, and a Simpler Cipher

*Field Guides 1–3 built a self-contained picture on the repo's **static** linear
model: mechanism (double-mixed clock, scattered embedding), a high-entropy
plaintext at unigram order, and a blocked second-order channel. This cycle turned
outward — a literature and community review — and turned up two things that
matter more than another statistic: (1) the broader community's leading model
**contradicts** the static assumption everything above rests on, and (2) a direct
measurement that **simplifies** our own model and hands us the sharpest
pin-acquisition target yet. This guide records both, plus the tooling we hadn't
ingested and a self-correction where an artifact nearly fooled me a third time.
Numbers are reproduced by the scripts in §9.*

Repo placement: `cipher_data/`. Companions: field guides 1–3;
`relax_structures.py`, `dedrift_probe.py`.

---

## 1. The fork we had been ignoring: static vs history-dependent

The repo concluded a **static** cipher: `c_m[t] = C[(σ·p_m[t] + base_m + drift·t)
mod N]`, autokey excluded. The public community, documented on the Noita wiki,
concluded the opposite — a **history-dependent** cipher. Their evidence:
classical **alphabet-chaining failed** on the eyes; Toboter inferred each
ciphertext character is conditionally dependent on the previous one and that the
mechanism has on the order of **83 internal states**; and Pyry **demonstrated**
matching isomorph structure with an **autokey Alberti** cipher whose ring rotates
by the previous plaintext character. Both camps independently found the **d=4
coincidence anomaly** (repeats at distance 4 at ~2× chance), which a stateful
mechanism explains more naturally than a static one.

This is a genuine, unresolved dispute, and **all of Field Guides 2–3 are
conditional on the static reading being correct.** If the cipher is
history-dependent, the de-drift `d[t] = q[c[t]] − drift·t` subtracts the wrong
state, and the "high-entropy plaintext" it produced is partly a
model-misspecification artifact — the residual of a running state the linear
de-drift never removed. This does not overturn Field Guides 2–3; it **widens
their error bars** and demotes "high-entropy secondary cipher" from *leading
hypothesis* to *one of three live readings*, alongside "seeded-hybrid cipher with
readable plaintext" and "dynamic cipher, unsolved."

The defense I had offered for static — the refrain's 9/9 de-drift consistency —
is weaker than I claimed. Under plaintext-autokey it requires only that one
30-symbol plaintext window sum to ≡ 30 (mod 83), which holds 1-in-83 by chance or
trivially by construction. So it does **not** strongly separate the models.

## 2. The test I ran to break the tie — and the artifact that nearly won

If the cipher is static, de-drift quality is flat with message depth; if it is
history-dependent, the linear de-drift should be good near the front (where the
state is freshly seeded and the shared sections align) and **decay** with depth.
The raw measurement looked decisive — de-drift IoC fell from **0.057** at the
front to ~0.015 in the body, exactly the dynamic-model signature.

It was mostly an artifact, and it is the **third** time this corpus's shared
sections have inflated an IoC on me. The shared openings live at the front; shared
plaintext de-drifts to identical values; those collisions inflate front IoC by
construction. After deduplicating shared-section instances (48 positions flagged),
the front elevation shrank from 0.057 to **0.030**, and the residual gradient
(0.030 front → 0.014 body, small-n) is a weak signal — consistent with a mild
dynamic decay, a mildly structured header, or noise. **Verdict: the depth test is
inconclusive.** It neither vindicates the community's model nor rescues a
"readable front." The lesson, now a standing rule: **any IoC on this corpus must
deduplicate shared sections first**, and any sparse-derived statistic needs a
randomization control (Field Guide 3 §5, §9).

## 3. SOLID new result — the bases are equal within each triplet

Shared plaintext between two messages appears as a run where the de-drifted
difference `d_m1 − d_m2` goes **constant**, and that constant *is* the base
difference (the plaintext cancels). Scanning alignment offsets for each message
pair (a cross-correlation for the shared section) gives the base-delta graph:

```
pair          scope          base Δ   support   verdict
E1–W1         Triplet 1        0        15       equal base
E1–E2         Triplet 1        0         7       equal base
W1–E2         Triplet 1        0         8       equal base
E4–W4         Triplet 3        0         5       equal base   (independent pins)
E4–E5         Triplet 3        0         7       equal base   (independent pins)
W4–E5         Triplet 3        0         7       equal base   (independent pins)
W2–E4 / W2–W4 cross-triplet   17 / 0     3       CONTRADICTORY (too sparse)
A ↔ B (any)   across comp.   37/50/54  ≤ 3       spurious
```

**Within every triplet the per-message bases are equal — delta exactly 0.** The
Triplet-3 rows are the load-bearing ones: those bases were measured with pins
derived from **Triplet 1**, an independent instrument, and 5–7 aligned positions
agree on zero (spurious probability ~1/83⁴). This is robust to the static-vs-
dynamic question, because it is measured at shared-plaintext sections where the
state matches under either model.

### Consequence — a simpler cipher

Equal bases within a triplet, plus the universal linear drift, mean you do **not**
need separate per-triplet keystreams. The model collapses to

```
c_m[t] = C[(σ·p_m[t] + base_{triplet(m)} + drift·t) mod N]
```

— one universal progression offset by **one of three** per-triplet base
constants. Four numbers (drift + three bases) where "per-triplet keystreams"
implied hundreds, and it reproduces every observable: within-triplet depth (equal
base → coincidences when plaintext matches) and cross-triplet non-depth
(different base → coincidences wash to chance, the `keystream_scope` κ result).
This is a HYPOTHESIS-grade simplification (it assumes the static reading for the
"universal drift" interpretation), but the base-equality it rests on is SOLID.

## 4. The scope question — global key vs per-triplet — is still open, and here is the block

Toboter's "the key is the same across all messages" would require the three
*triplet* bases to also be equal. **We cannot test that:** Triplet 1 (component A)
and Triplet 3 (component B) share no plaintext, so there is no bridge — the A↔B
rows are noise. The only potential bridge, the cross-triplet W2/E4/W4 passage, is
too pin-sparse to read (W2–W4 says Δ0, W2–E4 says Δ17, mutually inconsistent given
E4 = W4). So the community's global-key claim is now **plausible but unproven**,
and the repo's per-triplet picture is **simplified but not contradicted**.

This is the payoff of the cycle: a **bounded, checkable pin target**. Firming up
the cross-triplet bridge — even a handful more pins on the W2/E4/W4 passage —
yields one cross-triplet base delta. If that (with the E3/W3 links) chains the
triplets, **all nine messages align into a single depth stack** — the global-key
scenario made real, and a nine-deep stack is a far larger exploitable surface than
three isolated triplets. Unlike "recover more of C," this target has a defined
endpoint and a defined prize.

## 5. Tooling we had not ingested

- **`stblake/polyalphabetic`** — a shotgun hill-climber (multi-restart, with
  backtracking) built specifically for Vigenere, Porta, Beaufort, **Autokey**,
  and **Quagmire I–IV**. It spans *both* competing models in one tool: Quagmire =
  our static double-mixed reading, Autokey = the community's dynamic reading. It
  uses the strong n-gram-log-likelihood objective our embedding-invariant climb
  lacked (Field Guide 3 §3), so it can actually search where ours floored.
- **AZDecrypt** — the field's strongest classical solver (~200 homophonic ciphers
  /sec, 99%+ solve rate). Two features are directly useful: **crib-anchored
  search** (enter partial plaintext, solve the rest — plug our `jointcrib`
  cribs), and a **non-contributing-symbol detector** (flags cipher symbols that do
  not map to plaintext — a null/padding finder, relevant given the "no doubles"
  and the odd 83-of-125 alphabet).
- Both consume **n-gram language models**; decipherment of historical ciphers
  benefits from **era- and language-specific** models, so Finnish / Karelian /
  Kalevala-era models matter, not just modern text.

## 6. Encryption-vs-compression — a hard bound on the secondary-cipher question

The cybersecurity literature is blunt: distinguishing encrypted from compressed
data reliably **fails on small fragments**, and even learning-based state of the
art reaches only ~92% at 8 KB. Our payload is ~1 KB. So Field Guide 3's "cannot
resolve A vs B at this coverage" has a formal bound behind it, not just a coverage
excuse. One refinement, though: a secondary **classical** cipher would leave
language structure we do not see, so *if* it is a secondary cipher it is
compression or a modern/uniform layer — not another pen-and-paper cipher. And the
whole A-vs-B question is **moot if the cipher is history-dependent**, since then
the observed high entropy is the de-drift artifact of §1, not a property of the
payload.

## 7. Reassessed assumption ledger

| Assumption | Prior status | Status now |
|---|---|---|
| Static linear cipher | treated as settled | **contested** (community: dynamic); our work conditional on it |
| Plaintext is high-entropy | SOLID (Field Guide 2) | SOLID **only if static**; else a de-drift artifact |
| Per-triplet keystreams | SOLID (repo) | **simplified** → universal drift + 3 per-triplet bases |
| Bases per-message | implicit | **equal within triplet** (SOLID) |
| Key scope | per-triplet (repo) vs global (community) | **open**; blocked by A/B disconnection |
| Secondary cipher = leading | leading (Field Guide 3) | one of three live readings |

## 8. Standing conclusion

The cycle tightened the **mechanism** (simpler than believed — universal drift,
three bases, one alphabet) and loosened the **certainties** (the static reading is
contested, so the high-entropy conclusion is conditional). It also produced the
first pin target with a bounded payoff: the **cross-triplet W2/E4/W4 bridge**,
whose few extra pins would test the global-key hypothesis and potentially align
the whole corpus into one depth stack. And it put two off-the-shelf,
strong-objective solvers (`stblake/polyalphabetic`, AZDecrypt) on the table that
can test the static and dynamic models directly — the highest-leverage untried
action, because a readable hit from either resolves both the model and the
language at once.

## 9. Reproduce

```bash
# base-scope test (§3): constant-difference shared-section scan -> base deltas
python3 relax_structures.py                 # pins per structure (context)
# de-drift depth gradient with dedup control (§2), base-delta graph (§3):
#   inline scripts in the session log; both use iso_relax pins + the de-drift
#   d[t] = (q[c[t]] - drift*t) mod 83, then (a) IoC by depth band with/without
#   shared-section dedup, (b) offset-scan of d_m1 - d_m2 for constant runs.
```

## 10. Sources

- Noita Wiki, *Eye Messages* (community model: chaining failure, ciphertext
  dependency, ~83 internal states, Pyry's autokey-Alberti isomorph demonstration,
  the d=4 observation). https://noita.wiki.gg/wiki/Eye_Messages
- `stblake/polyalphabetic` — hill climber for Vigenere/Porta/Beaufort/Autokey/
  Quagmire I–IV. https://github.com/stblake/polyalphabetic
- D. Van Eycke, **AZDecrypt**; capabilities and solve rates surveyed in Blake &
  Ergün et al., *The Solution of the Zodiac Killer's 340-Character Cipher*
  (arXiv:2403.17350). https://github.com/doranchak/azdecrypt
- Encryption-vs-compression detection limits: EnCoD (arXiv:2010.07754) and HEDGE
  (Neural Computing and Applications, 2022) — χ² and NIST SP800-22 subsets for
  short fragments, and the difficulty of the compressed-vs-encrypted split.

*Sequential record. Field Guide 5 is whenever the cross-triplet bridge yields
pins, an off-the-shelf solver returns a readable hit, or an external anchor lands
— any of which would move a "conditional" in §7 to "settled."*
