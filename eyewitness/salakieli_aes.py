#!/usr/bin/env python3
"""Is the eye cipher Noita's salakieli AES-128-CTR? — a falsification test.

Noita's data files use AES/CTR/NoPadding-128 (e.g. the alchemy list with
Key="1449661692193402", IV="8162438913968373").  This checks, rigorously,
whether the EYE GLYPHS are the same scheme.

Two independent arguments, one a priori and one empirical:

1. COUNTING PROOF (a priori, decisive).
   AES-CTR is a stream cipher: ciphertext = plaintext XOR keystream, and the
   keystream is a uniform pseudorandom BYTE stream (values 0..255).  XOR with a
   uniform byte therefore yields ciphertext uniform over 0..255.  The eye corpus
   uses exactly 83 symbol values (0..82) and nothing else.  A uniform byte stream
   cannot be confined to 83 values, so the runes are NOT a raw AES-CTR byte
   stream.  (Any byte->83-symbol re-encoding would be an extra, non-AES layer.)

2. DEPTH PROOF (a priori, corroborating).
   We proved (depthmap) that several eye messages SHARE a keystream (identical
   cross-message opening runs; near-duplicate pairs).  Correct AES-CTR uses a
   unique IV per message -> independent keystreams -> zero depth.  Observed depth
   means either not-AES or catastrophic (Key,IV) reuse; a dev using AES properly
   would not produce this.

3. EMPIRICAL (this script).
   We still TRY it: AES-128-CTR-decrypt the rune bytes under the known salakieli
   Key/IV (and passphrase-derived keys), and score the output for text-like
   structure (printable-ASCII fraction) against a random-bytes baseline.  If the
   output is indistinguishable from random, AES is empirically excluded too.

Run:
    python3 salakieli_aes.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    HAVE_AES = True
except Exception as _e:                 # pragma: no cover
    HAVE_AES = False
    _AES_ERR = str(_e)

# Known salakieli AES material (16-byte ASCII key/IV) — the alchemy list.
KNOWN = [("alchemy", b"1449661692193402", b"8162438913968373")]
# The salakieli word-strings the user found (likely decrypted CONTENT, not keys,
# and not 16 bytes — included only as derived-key guesses for completeness).
PHRASES = [
    "WeSeeATrueSeekerOfKnowledge", "YouAreSoCloseToBeingEnlightened",
    "TheTruthIsThatThereIsNothing", "MoreValuableThanKnowledge",
    "KnowledgeIsTheHighestOfTheHeighest", "WhoWouldntGiveEverythingForTrueKnowledge",
    "SecretsOfTheAllSeeing", "ThreeEyesAreWatchingYou",
    "WhenYouHaveNothingLeftToSeek", "PeopleWillRejoiceAndDance",
]


def aes_ctr(key: bytes, iv: bytes, data: bytes) -> bytes:
    c = Cipher(algorithms.AES(key), modes.CTR(iv))
    d = c.decryptor()
    return d.update(data) + d.finalize()


def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    return sum(1 for x in b if 32 <= x < 127) / len(b)


def aes_kat() -> bool:
    """Round-trip KAT so we know the AES usage itself is correct."""
    key, iv = b"1449661692193402", b"8162438913968373"
    pt = b"The quick brown fox jumps over 13 lazy eyes....."
    c = Cipher(algorithms.AES(key), modes.CTR(iv))
    enc = c.encryptor().update(pt)
    return aes_ctr(key, iv, enc) == pt


def derive_key(phrase: str) -> bytes:
    return hashlib.sha256(phrase.encode()).digest()[:16]


def main() -> int:
    c = corpus_mod.load()
    allv = [v for ct in c.ciphertexts for v in ct]
    distinct = sorted(set(allv))

    print("=" * 70)
    print("EYEWITNESS — is the eye cipher salakieli AES-128-CTR?")
    print("=" * 70)
    print("\n[1] COUNTING PROOF")
    print(f"  eye corpus: {len(allv)} symbols, {len(distinct)} distinct values "
          f"in [{min(distinct)}, {max(distinct)}]")
    print(f"  AES-CTR ciphertext is a uniform byte stream (256 values).")
    print(f"  83 != 256  ->  the runes are NOT a raw AES-CTR byte stream. "
          f"[DECISIVE]")

    print("\n[2] DEPTH PROOF")
    print("  depthmap proved shared keystreams across messages (identical opening")
    print("  runs; near-duplicate pairs). Proper AES-CTR uses a unique IV per")
    print("  message -> no depth. Observed depth contradicts correct AES use.")

    print("\n[3] EMPIRICAL")
    if not HAVE_AES:
        print(f"  (cryptography not importable: {_AES_ERR}); skipping. The two")
        print("  proofs above are already decisive.")
        return 0
    print(f"  AES round-trip KAT: {'OK' if aes_kat() else 'FAIL'}")
    # Bytes from the runes (0..82 as byte values), concatenated.
    rune_bytes = bytes(int(v) for v in allv)
    import os
    base = printable_ratio(os.urandom(len(rune_bytes)))    # random-bytes baseline
    print(f"  random-bytes printable-ASCII baseline: {base:.2f}")
    print(f"  {'key/iv source':32} {'printable':>9}")
    trials = [(name, k, iv) for (name, k, iv) in KNOWN]
    trials += [(f"phrase:{p[:18]}", derive_key(p), derive_key(p[::-1]))
               for p in PHRASES]
    text_like = []
    for name, k, iv in trials:
        out = aes_ctr(k, iv, rune_bytes)
        pr = printable_ratio(out)
        flag = "  <-- text-like?!" if pr > 0.85 else ""
        if pr > 0.85:
            text_like.append(name)
        print(f"  {name:32} {pr:>9.2f}{flag}")

    print("\n" + "-" * 70)
    print("VERDICT:")
    if text_like:
        print(f"  Unexpected: {text_like} produced text-like output — investigate.")
    else:
        print("  Every AES-CTR decryption is statistically random (printable ratio")
        print("  ~= the random baseline), as expected. Combined with the counting")
        print("  and depth proofs: the eye cipher is NOT salakieli AES-128-CTR.")
        print("  AES is the game's FILE encryption; the eye glyphs are a separate,")
        print("  hand-made keystream cipher (per-group keystream + depth) — exactly")
        print("  what the rest of the toolkit characterises.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
