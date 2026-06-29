#!/usr/bin/env python3
"""EyeCrack — position-0 indicator → base_m analysis."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod  # noqa: E402
import pos0_base as p0       # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    c = corpus_mod.load()
    rep = p0.analyze([list(x) for x in c.ciphertexts], c.N, labels=c.labels)
    print(p0.format_report(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
