# Noita Eye — Crib Lexicon

A matched-filter reference bank for the crib→cascade sweep, built from the *translated
in-game lore* (guide-stone god-messages G1–G12, the Volume tablets, and the Finnish
creation myth). The bet is narrow and explicit: **if** the eye plaintext is lore in the
author's register, the correct crib is a phrase in this voice. It won't help if the body
is high-entropy non-language (the static reading) — it's the ammunition for the
clock/language branch.

## Files

- **`lore_en.txt` / `lore_fi.txt`** — the raw lore corpora. Feed these to a k-gram model
  to score decrypts in the author's *actual* register, not generic English/Finnish.
- **`phrase_bank.tsv`** — every discrete lore utterance, with unspaced length. The
  source-of-truth phrases.
- **`sized_candidates.tsv`** — the sweep input. Candidate plaintexts cut to the exact
  length of each target, unspaced, lowercase, with a **tier**:
  - `tier 1` — a full voice-phrase or bank phrase that is *exactly* the target length. Highest signal; test these first.
  - `tier 2` — a window of a real lore phrase starting at a **word boundary**.
  - `tier 3` — a truncation/mid-phrase window. Lowest signal; the safety net.
  Columns: `target_len  tier  candidate  source`. Target lengths map:
  20→t3open, 23→t2pass, 24→t1open, 25→refrain, 30→t3dof1.

## The author's voice (the intelligence product)

Three registers, all in the corpus, in descending likelihood for the eye messages:

**Guide-stone / god voice (closest to the eyes).** Second-person, accusatory, rhetorical
questions. A god addressing the reader directly. Signature moves: *"you think you
know/have X, but you don't"*; *"we created/allowed/gave you your X"*; *"we wanted/made you
come here"*; *"we are watching you"*; run-on *"...and your X and your Y and all the Z."*
Quirks that matter for a crib: **dropped pronouns** ("Why else would be reading this?"),
**capitalized epithets** ("Knower to Be", "The Gods"), **no terminal punctuation** on many
lines. Vocabulary core: god / gods / true god / god of gods; worship; free will; true
knowledge / wisdom; answer(s); treasure; seeker; knower; watching; monster.

**Volume / tablet voice.** Aphoristic, archaic, imperative: *"Prove thine knowledge…"*,
*"…think for thyself!"*, *"To have/gain true knowledge…"*, *"True knowledge is a slippery
thing."* Note the **thine/thyself** archaisms — a crib in this voice looks different.

**Finnish myth voice.** Creation cosmology: egg → life/death, white→west→cold/ice,
yolk→east→heat/fire, then Nature, Magic, Technology born from the eggs. Formal narrative.
Directionally interesting: the myth explicitly ties **west↔cold, east↔heat**, and the eye
messages are literally labeled East/West — a thematic hook if the plaintext is the myth.

## How the sweep uses it

For each target, iterate its sized candidates (tier 1 → 2 → 3), place each as plaintext,
solve the implied partial alphabet under the working model, and **cascade**: does that
alphabet decrypt the *rest* of the corpus toward this same lore register? Consistency at
the target is necessary; cascade is the verdict. Score decrypts with a k-gram model built
from `lore_en.txt`/`lore_fi.txt` so "reads like the author" is measured, not eyeballed.

## Limitations / honest flags

- **It bets on lore-in-voice.** The flat body distribution argues the static reading isn't
  language at all; this lexicon only pays off if the family is clock/language.
- **Template fills include nonsense.** The generator combines vocabulary by syntax, so some
  tier-1 lines are grammatically odd ("weallowedyoutoallowedhere"). Harmless — the sweep
  is cheap — but don't read the tier-1 list as all-coherent.
- **Register, not content.** Matching the voice raises the odds a guess is plausible; it
  does not make it correct. Only cascade decides.
- **Two languages, one guess.** English and Finnish are both here; the plaintext is one or
  neither. Score under both; let cascade separate them.
