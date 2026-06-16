#!/usr/bin/env python3
"""EyeWitness triplet key-test — does each triplet hide its own keystream?

Tests the "pair + embedded key" model (Model B): within a triplet, is one member
the keystream for the other two?  Uses `noita_eye_core.embedded_key`.

Two honest guards built in:
  * Layer-0 cross-check: the committed glyph sheet must byte-match the corpus.
  * The verdict is taken on the **divergent region** (after each triplet's shared
    opening), because `decrypt(target, key)` over an identical opening is all
    zeros -- artificially "structured" -- and would manufacture a false hit. The
    full-region number is shown only for contrast.

Run:
    python3 triplet_keytest.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod      # noqa: E402
import embedded_key as ek        # noqa: E402

SHEET = HERE / "glyph_repetition_sheet.csv"


def cross_check_sheet(c: corpus_mod.Corpus) -> bool:
    """True iff the committed glyph sheet matches the corpus byte-for-byte."""
    if not SHEET.exists():
        return False
    rows = list(csv.reader(SHEET.open()))
    sheet = {}
    for r in rows:
        if len(r) > 2 and r[0].strip().isdigit() and r[1].strip():
            sheet[int(r[0])] = [int(x) for x in r[2:] if x.strip() != ""]
    if len(sheet) != c.num_messages:
        return False
    return all(sheet.get(i) == list(c.ciphertexts[i])
               for i in range(c.num_messages))


def common_prefix_len(messages, triplet) -> int:
    """End of the triple's shared opening, treated as the divergent-region start.

    Position 0 is the per-message ``sigma0`` (it differs by design), so we scan
    the shared run from position 1 and always strip position 0 as well — both are
    artifacts that would otherwise inflate `decrypt(target, key)` with a run of
    zeros where the members are identical.
    """
    L = min(len(messages[m]) for m in triplet)
    e = 1
    while e < L and all(messages[m][e] == messages[triplet[0]][e]
                        for m in triplet):
        e += 1
    return e


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    messages = [list(ct) for ct in c.ciphertexts]
    lab = c.labels

    print("=" * 70)
    print("EYEWITNESS — triplet embedded-key test (Model B: pair + key)")
    print("=" * 70)
    ok = cross_check_sheet(c)
    print(f"Layer-0 cross-check (committed glyph sheet == corpus): {ok}")
    print()

    for triplet in ek.CONSEC_TRIPLETS:
        names = "{" + ", ".join(lab[m] for m in triplet) + "}"
        P = common_prefix_len(messages, triplet)
        Lmin = min(len(messages[m]) for m in triplet)
        print("-" * 70)
        print(f"Triplet {triplet} = {names}   shared opening = {P} symbols")

        # PRIMARY: divergent region (after the shared opening).
        if Lmin - P >= 12:
            rep = ek.test_triplet(messages, triplet, N, region=(P, Lmin),
                                  n_null=1000, seed=0)
            b = rep.best
            print(f"  [divergent region {P}..{Lmin}]  PRIMARY VERDICT")
            print(f"    best: key={lab[b.key]} via '{b.mode}'  "
                  f"min-structure(IoC*N)={b.min_structure:.2f}  "
                  f"(null thresh {rep.threshold:.2f})")
            print(f"    detected embedded key: {rep.detected}")
            print(f"    {rep.reason}")
        else:
            print(f"  [divergent region too short ({Lmin-P}) to test]")

        # CONTRAST: full region (confounded by the shared opening).
        repf = ek.test_triplet(messages, triplet, N, n_null=600, seed=0)
        print(f"  [full region, CONFOUNDED by opening] best key="
              f"{lab[repf.best.key]} '{repf.best.mode}' "
              f"min-struct={repf.best.min_structure:.2f} "
              f"detected={repf.detected}  <- ignore if opening-driven")
        print()

    # The user's specific hypotheses, shown explicitly on the divergent region.
    print("-" * 70)
    print("Your specific hypotheses (implied decrypts on the divergent region):")
    for (triplet, keylab, tgts) in (((0, 1, 2), "East 2", ("East 1", "West 1")),
                                    ((6, 7, 8), "West 4", ("East 4", "East 5"))):
        key = lab.index(keylab)
        P = common_prefix_len(messages, triplet)
        Lmin = min(len(messages[m]) for m in triplet)
        print(f"  {keylab} as key for {tgts}  (region {P}..{Lmin}):")
        for tname in tgts:
            t = lab.index(tname)
            d = ek.decrypt_with_member(messages, t, key, "add", N, (P, Lmin))
            s = ek._structure(d, N)
            head = ",".join(str(x) for x in d[:18])
            print(f"    {tname} - {keylab} (add): IoC*N={s:.2f}  head=[{head} ...]")
    print()
    print("Reminder: a flat unigram makes this test underpowered on the real")
    print("corpus -- 'not detected' means 'not confirmable from statistics',")
    print("not 'false'. Confirming Model B needs a crib (one known word).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
