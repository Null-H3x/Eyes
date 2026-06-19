#!/usr/bin/env python3
"""Build the EYES evidence-ledger dashboard.

Runs the math gate, computes every hypothesis from the selftested core modules,
scores them, renders a self-contained Grimoire HTML, and appends a run summary to
ledger.json.

    python3 build.py [--out report.html] [--open]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(HERE))

import corpus as corpus_mod          # noqa: E402
import core                          # noqa: E402
import hypotheses as H               # noqa: E402


# Module selftests we surface as validation badges.
_GATE_MODULES = ["corpus", "cipher_ops", "stats", "lm", "null_model", "prng",
                 "trigram", "depth", "classify", "grouping", "oracle",
                 "embedded_key", "keystream_scope", "header_test", "numbertest",
                 "depthmap", "pairdiff", "langdetect", "cribdrag",
                 "cipher_fingerprint", "repeats", "isomorph", "eyescoreboard"]


def run_gate():
    """Run each module selftest; return (validations, passed, total, ok)."""
    validations = {}
    passed = total = 0
    for name in _GATE_MODULES:
        try:
            mod = __import__(name)
            results = mod.selftest()
            p = sum(1 for _, ok in results if ok)
            t = len(results)
        except Exception as e:                       # pragma: no cover
            p, t = 0, 1
            print(f"  [ERROR] {name}: {e}")
        validations[name] = (p, t)
        passed += p
        total += t
    return validations, passed, total, (passed == total)


def corpus_hash(c: corpus_mod.Corpus) -> str:
    blob = json.dumps({"deck_size": c.deck_size,
                       "ciphertexts": [list(ct) for ct in c.ciphertexts]},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the EYES dashboard")
    ap.add_argument("--out", default=str(HERE.parent / "report.html"))
    ap.add_argument("--open", action="store_true", help="open in a browser")
    args = ap.parse_args()

    print("Running math gate ...")
    validations, gpass, gtot, gate_ok = run_gate()
    gate_summary = f"{gpass}/{gtot} checks across {len(_GATE_MODULES)} modules"
    print(f"  {gate_summary} -> {'GREEN' if gate_ok else 'FAILING'}")

    c = corpus_mod.load()
    ctx = H.Context(corpus=c, validations=validations)

    print("Evaluating hypotheses ...")
    results = []
    for fn in H.HYPOTHESES:
        try:
            r = core.apply_scoring(fn(ctx))
            print(f"  {r.tier:12} {r.score:3}  {r.title}")
            results.append(r)
        except Exception as e:                        # pragma: no cover
            print(f"  [ERROR] {fn.__name__}: {e}")
    results.sort(key=lambda r: -r.score)

    meta = {
        "corpus_sha256": corpus_hash(c)[:16] + "…",
        "messages": c.num_messages,
        "alphabet_N": c.N,
        "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        "gate": gate_summary,
    }
    out_path = Path(args.out)
    out_path.write_text(core.render_report(results, meta, gate_ok, gate_summary),
                        encoding="utf-8")
    print(f"\nWrote {out_path}")

    # Append to the ledger (history of scored runs).
    ledger_path = HERE / "ledger.json"
    ledger = []
    if ledger_path.exists():
        try:
            ledger = json.loads(ledger_path.read_text())
        except Exception:
            ledger = []
    ledger.append({
        "built": meta["built"], "corpus_sha256": corpus_hash(c),
        "gate_ok": gate_ok, "gate": gate_summary,
        "results": [{"id": r.id, "tier": r.tier, "score": r.score,
                     "verdict": r.verdict} for r in results]})
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    if args.open:
        webbrowser.open(out_path.resolve().as_uri())
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
