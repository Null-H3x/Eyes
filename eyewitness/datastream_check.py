#!/usr/bin/env python3
"""EyeWitness — datastream consistency / accountability check.

Validates the data that every tool consumes, three independent ways, and prints a
recountable fingerprint. Exit code 0 iff all (non-skipped) checks pass.

  TIER 1  internal integrity + single-source: corpus.json structure, symbol range,
          deterministic load, corpus.json == EyeStat archive, SHA256 fingerprint.
  TIER 2  independent re-derivation: a pure brute-force skeleton scan (no toolkit
          imports) re-finds the 4x repeated isomorph target — proving it is a real
          data feature, not a tool artifact.
  TIER 3  independent source cross-check: corpus.json == the WarFairy BASE10
          transcription in data/ (best-effort; needs xlrd + the .xls).

Run:
    python3 eyewitness/datastream_check.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


def _sk(seq):
    f = {}
    return tuple(f.setdefault(v, i) for i, v in enumerate(seq))


def main() -> int:
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    results = []

    print("=" * 70)
    print("EYEWITNESS — datastream consistency check")
    print("=" * 70)

    # ---- TIER 1: integrity + single source + fingerprint
    print("\n[Tier 1] Internal integrity + single source")
    syms = set()
    for ct in M:
        syms |= set(ct)
    ok_struct = (c.num_messages == 9 and c.N == 83
                 and min(syms) >= 0 and max(syms) <= 82)
    results.append(("structure: 9 messages, N=83, symbols in [0,82]", ok_struct))
    results.append(("all 83 symbols are used", len(syms) == 83))
    results.append(("deterministic load",
                    corpus_mod.load().ciphertexts == c.ciphertexts))
    # corpus.selftest covers validate + EyeStat single-source
    st = corpus_mod.selftest()
    results.append((f"corpus.selftest ({sum(b for _, b in st)}/{len(st)})",
                    all(b for _, b in st)))
    blob = json.dumps([list(ct) for ct in M], separators=(",", ":")).encode()
    sha = hashlib.sha256(blob).hexdigest()
    print(f"   lengths={list(c.lengths)} total={sum(c.lengths)}")
    print(f"   corpus content SHA256: {sha}")
    for label, ok in results:
        print(f"   [{PASS if ok else FAIL}] {label}")

    # ---- TIER 2: independent re-derivation of the 4x target (no toolkit)
    print("\n[Tier 2] Independent re-derivation of the 4x repeated target")
    L = 15
    target_sk = (0, 1, 2, 3, 4, 5, 6, 4, 8, 2, 6, 11, 3, 13, 14)
    hits = [(m, p) for m, msg in enumerate(M)
            for p in range(len(msg) - L + 1) if _sk(msg[p:p + L]) == target_sk]
    expected = [(1, 38), (1, 68), (2, 43), (2, 78)]
    vals = [tuple(M[m][p:p + L]) for m, p in hits]
    t2 = (sorted(hits) == sorted(expected) and len(set(vals)) == len(vals))
    results.append(("brute-force scan re-finds the 4x target (different-value)", t2))
    for m, p in hits:
        print(f"   {c.labels[m]}@{p}")
    print(f"   [{PASS if t2 else FAIL}] matches expected {expected} & all distinct")

    # ---- TIER 3: cross-check vs WarFairy BASE10 transcription (best-effort)
    print("\n[Tier 3] Independent source cross-check (WarFairy BASE10)")
    xls = ROOT / "data" / "WarFairy_Eye_Data_Conversion_Sets.xls"
    t3 = None
    try:
        import xlrd  # noqa: F401
        if not xls.exists():
            raise FileNotFoundError(xls)
        wb = xlrd.open_workbook(str(xls))
        sh = wb.sheet_by_name("Finished Conversion")
        labels = ["East 1", "West 1", "East 2", "West 2", "East 3",
                  "West 3", "East 4", "West 4", "East 5"]
        mism = checked = 0
        for ri, lab in enumerate(labels, start=1):
            if sh.cell_value(ri, 0) != lab:
                mism += 1
                continue
            wf = []
            for col in range(1, sh.ncols):
                v = sh.cell_value(ri, col)
                if v == "":
                    break
                wf.append(int(v))
            cor = M[ri - 1]
            n = min(len(wf), len(cor))
            mism += sum(1 for t in range(n) if wf[t] != cor[t])
            mism += abs(len(wf) - len(cor))
            checked += n
        t3 = (mism == 0)
        print(f"   cross-checked {checked} symbols, {mism} mismatches")
        results.append(("corpus.json == WarFairy BASE10 transcription", t3))
        print(f"   [{PASS if t3 else FAIL}] independent transcription agrees")
    except Exception as e:
        print(f"   [{SKIP}] WarFairy cross-check skipped ({type(e).__name__}: {e})")
        print("          install xlrd to enable: pip install xlrd")

    n_ok = sum(1 for _, ok in results if ok)
    allgood = all(ok for _, ok in results)
    print("\n" + "-" * 70)
    print(f"{n_ok}/{len(results)} datastream checks passed"
          + ("" if t3 is not None else "  (Tier 3 skipped)"))
    print("DATASTREAM CONSISTENT" if allgood else "DATASTREAM PROBLEM — investigate")
    return 0 if allgood else 1


if __name__ == "__main__":
    sys.exit(main())
