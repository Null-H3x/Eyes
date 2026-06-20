#!/usr/bin/env python3
"""EyeCrack — passage template pipeline wrapper.

Same as ``eyewitness/passage_template.py``; lives under eyecrack for Attack menu.

    python3 passage_template.py --audit
    python3 passage_template.py --html --phrase seekeroftruth
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent.parent / "eyewitness" / "passage_template.py"
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name="__main__")
