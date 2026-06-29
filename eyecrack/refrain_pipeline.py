#!/usr/bin/env python3
"""EyeCrack — refrain pipeline (compose → order_solve → report)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod    # noqa: E402
import refrain_pipeline as rp  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anchor", action="append", default=[], help="compose anchors")
    ap.add_argument("--compose-top", type=int, default=15)
    ap.add_argument("--template-max", type=int, default=500)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--html", metavar="PATH")
    args = ap.parse_args()

    c = corpus_mod.load()
    hits, meta = rp.run_pipeline(
        [list(x) for x in c.ciphertexts],
        c.N,
        labels=c.labels,
        anchors=args.anchor,
        compose_top=args.compose_top,
        template_max=args.template_max,
        top=args.top,
    )
    print(rp.format_report(hits, meta, labels=c.labels))
    if args.html:
        out = Path(args.html)
        if not out.is_absolute():
            out = HERE / out
        rp.write_html(str(out), hits, meta)
        print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
