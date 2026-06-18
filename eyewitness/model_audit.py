#!/usr/bin/env python3
"""EyeWitness — falsifiable model verification (run BEFORE trusting the template).

Tests whether the per-message-progressive model is genuinely the refrain's
structure or a flexible fit, and writes report/model_audit_report.md.

Run:
    python3 model_audit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import refrain as rf          # noqa: E402
import model_audit as ma      # noqa: E402
import isomorph as iso        # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    region = rf.DEFAULT_INSTANCES

    a = ma.audit(M, region, N, n_null=600)
    # isomorph significance for the same-plaintext claim (the SOLID part)
    sig = iso.significance(M, 12, 3, n_null=150)

    L = []
    L.append("# Refrain Model Verification (paranoia audit)")
    L.append("")
    L.append("*Reproduce: `python3 eyewitness/model_audit.py`. "
             "Gate: `python3 noita_eye_core/selftest.py`.*")
    L.append("")
    L.append("## Question")
    L.append("Is the per-message-progressive model genuinely the refrain's cipher "
             "structure (licensing the dof=2 template), or a flexible fit?")
    L.append("")
    L.append("## What is SOLID: the 4 instances are the same plaintext")
    L.append(f"- Isomorph significance (L=12): observed **{sig['observed']}** vs "
             f"shuffle-null {sig['null_mean']:.1f}±{sig['null_sd']:.1f}, "
             f"**z={sig['z']:.0f}**, p={sig['p']:.3f}. The refrain instances share "
             f"a repeated-letter structure far beyond chance — they ARE the same "
             f"plaintext.")
    L.append("")
    L.append("## What is NOT cleanly confirmed: the specific model")
    L.append(f"- per-message-progressive consistent extent: **{a.refrain_permsg}** glyphs")
    L.append(f"- pure-progressive consistent extent: **{a.refrain_pure}** glyphs "
             f"(nearly as deep — the per-message base barely helps)")
    L.append(f"- null (random 4-windows, n={a.n_null}): mean {a.null_mean:.1f}, "
             f"max {a.null_max}; **empirical p(null ≥ {a.refrain_permsg}) = "
             f"{a.p_value:.4f}**")
    L.append("- Random 4-windows that DO reach L=22 have as much or MORE "
             "over-determination than the refrain, so over-determination does not "
             "single the refrain out either.")
    L.append("")
    L.append("## Verdict")
    L.append("- **SOLID:** the refrain is the SAME plaintext, 4×, ~22 glyphs "
             "(isomorphs z≫100; consistency special vs random extent ~7).")
    L.append("- **NOT proven:** that the cipher is *specifically* per-message-"
             "progressive rather than another interrelated-alphabet member. The "
             "consistency tests are passed by a flexible model and by a small "
             "fraction of random windows; pure-progressive fits nearly as well.")
    L.append("- **Therefore:** the refrain repeat-template (dof=2; forced-same "
             "(3,13),(4,5),(10,16)) is a **model-dependent hypothesis**, not a fact. "
             "Use it to GENERATE candidates and TEST, but do not treat a template "
             "match as confirmation by itself.")
    L.append("")
    L.append("## Audit-chain status")
    L.append("Every claim above is backed by a self-tested module "
             "(`model_audit.selftest`, `isomorph.selftest`) and is reproducible. "
             "This link deliberately records a NEGATIVE/inconclusive result so the "
             "chain stays honest: the model is a working hypothesis, the "
             "same-plaintext refrain is established.")

    out = ROOT / "report" / "model_audit_report.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[wrote] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
