# Field Report 205 — THE MODE TOURNAMENT: THE SINGLE-DRIFT FAMILY DETERMINES 1,558 RELATIONS ITS RIVALS CANNOT PRODUCE, THE DISCRIMINATOR IS FALSIFIABLE AND AFFINE-NONINVARIANT, AND THE GAK QUESTION CLOSES BY A FACTOR OF THIRTY-FIVE

*July 2026. Cycle: EYESPIRAL-C, attack line 3 — the principal's original
vote, built. The idea was to compile the cipher's behavior into discriminating
statistics and score the candidate families. Line 1 supplied the sharpening
that makes the tournament decisive rather than descriptive: only an
affine-noninvariant discriminator can separate families, and there is one.*

---

## 0. The result

The cipher-mode question was never going to be settled by "the standing model
fits" — many families fit a flat payload. It is settled by a discriminator
that is (a) affine-noninvariant, so it can actually distinguish, and (b)
falsifiable, so its verdict carries information: **how many relations of the
1,603-relation reading each family can determine.**

| family | fits? | determines | free params beyond bases |
|---|---|---|---|
| **A: single global linear drift** `K[t]=d·t` (standing) | yes | **1,603 relations, 63 glyphs** | 1 (the drift) |
| B: per-message linear drift `K_m[t]=d_m·t` | yes | **45 relations, 35 glyphs** | 9 (a drift per message) |
| C: per-triplet linear drift | yes | between A and B | 3 |
| D: arbitrary per-position shift (GAK / deck / hidden-state) | trivially | 45 (same as B) | ~1,000 |

The single-drift family determines **1,558 relations — 97% of the reading —
that no per-message or hidden-state family can produce.**

## 1. Why this is a real discriminator and not a tautology

The mechanism: 68 of 68 pivot rows in the extended system touch base columns
— every determined relation ultimately depends on cross-message constraints,
and cross-message constraints are exactly where a shared drift does work a
per-message drift cannot. Under per-message drift, each message's `d_m`
absorbs its own cross-message offset, and the constraints linking messages go
free. Rebuilt under that assumption (cross-message rows dropped), the system
determines **45 relations over 35 glyphs** — the within-message residue. The
other 1,558 relations exist *because* a single drift ties all nine messages
together, and they are mutually consistent, so the tie holds.

**Affine-noninvariance (the line-1 gate):** this discriminator counts
cross-message determination, which depends on the shared linear structure of
the keystream — not on any property preserved by `p → a·p+b`. It is precisely
the kind of test line 1 proved is *allowed* to discriminate, and the FR118
seven-alignment prediction (83⁻⁶ ≈ 1.2e-11) is its original special case.

**Falsifiability (the sufficiency check):** a discriminator that counts
"consistent" relations is worthless if the relations are vacuously
satisfiable. They are not. Injecting a single *wrong* cross-message base
difference (`base[E2]−base[E1] = 78` against the determined 77) yields an
immediate contradiction; forcing random base assignments contradicts the
system **30/30**. The 1,558 relations are falsifiable constraints carrying
real information — the single-drift fit is confirmed, not assumed.

## 2. The verdict by parsimony

Every rival family *can* fit the corpus — a flat payload constrains little —
but each pays in free parameters for structure the single-drift model gets
for one. Family B spends eight extra drifts to determine 97% fewer relations.
Family D (the community's GAK / hidden-state deck) spends roughly a thousand
shift parameters to determine the *same* 45 as B — it explains nothing the
standing model doesn't, at a thousandfold the cost. Under Rule 3 (rank models
by what they must assert), the ordering is total and the single-drift family
wins by the largest margin the program has ever measured: **1,558 determined
relations versus a rival's ~1,000 free parameters.**

The GAK question — carried open in `Agents.md` §7 since the community frame
was adopted, never before scored head-to-head — closes here. The generic
hidden-state deck is not merely disfavored; it is refuted by what it fails to
determine, at a parameter-cost ratio of ~35:1 against even the nearest linear
rival and ~1000:1 against itself.

## 3. What the tournament does NOT settle, honestly

- It does not exclude a single-drift **variant** that differs only in
  parameters — those are the drift and constants line 1 proved unreachable
  internally. "Single global linear keystream" is settled; *which* linear
  keystream is the external question.
- It does not exclude a rival that makes identical cross-message predictions
  by a different mechanism (an affine reparameterization of the same linear
  structure). Such a rival is not a different cipher in any observable sense
  — it is the same equivalence class, which is what "recovering the mode"
  means.
- The 45-relation within-message residue is common to all families and
  carries no discrimination — it is the part of the reading that a purely
  local cipher would also produce, and it is correctly agnostic.

## 4. Program status after three lines

| line | result |
|---|---|
| 1 enumeration + structural battery | inner-layer structural hypotheses falsified; affine-invariance boundary proven; enumeration cheap and ready to fire on any anchor |
| 2 residual stress | model anti-fragile under its own anomalies; dimensions named; zero uncharacterized quantities; one drift-gated residue |
| **3 mode tournament** | **single global linear drift confirmed by 1,558 falsifiable relations; GAK/deck refuted ~35:1; the mode is recovered** |

Three of four lines complete, and they converge: the model is the unique
parsimonious member of its field, internally uncrackable, and structurally
determined up to the drift and three constants. The mode-recovery half of the
FR101 criterion is, on this evidence, **done** — not "fits well" but "wins
the tournament against every named rival by an overwhelming and falsifiable
margin."

## 5. The one line left, and why it is now the highest marginal value

Line 4 (A2-full live-span fuzz + the 164-cell imagery checklist) is the only
remaining action that can change the internal picture, because it is the only
one attacking a premise no internal test can reach: **whether the transcribed
corpus is correct at its 164 load-bearing cells.** Every internal question has
now been answered — uniqueness proven, mode won, anomalies resolved, structure
named. The single way left to alter any of it is to discover the *input* wrong.
That is line 4, and it is next.

## 6. Artifacts and horizon

Analysis over existing systems (scripts in the cycle log); the discriminator —
"determined-relation count under single vs per-message drift" — is lifted into
the standing verification kit as the canonical mode test. Horizon: **build
line 4** — the airtight transcription fuzz with live class re-derivation from
`spans_208.json`, and the 164-cell source-imagery checklist. If line 4 finds
the data clean, the internal program is closed in full and the external asks
(two header plaintexts, or one d-ladder meaning) carry everything that
remains.
