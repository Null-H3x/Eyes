#!/usr/bin/env python3
"""Split the 9-message EyeStat corpus into 3 per-triplet data files.

The keystream is per-triplet (EyeWitness `keystream_scope`), so a global EyeStat
scan — which scores a seed against all nine messages — cannot find a per-triplet
seed (no single seed satisfies all nine).  This writes one EyeStat-format data
file per triplet so EyeStat can be run three times, each scoring a seed against
only the three messages that actually share a keystream.

    python3 split_triplets.py          # writes noita_eye_triplet_{0,1,2}.json
Then run EyeStat per triplet, e.g.:
    python3 eyestat_gpu_runner.py --data noita_eye_triplet_0.json --modes all \
        --prngs all --seed-end 100000000
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
LIST_FIELDS = ("message_labels", "message_lengths", "ciphertexts",
               "sigma0_ct_targets")


def main() -> int:
    src = HERE / "noita_eye_data.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    written = []
    for ti, members in enumerate(TRIPLETS):
        out = {k: v for k, v in data.items() if not isinstance(v, list)}
        out["_comment"] = (f"Per-triplet subset {members} of {src.name} "
                           f"(members {[data['message_labels'][m] for m in members]}). "
                           "Keystream is per-triplet; scan each triplet separately.")
        out["num_messages"] = len(members)
        for f in LIST_FIELDS:
            if f in data:
                out[f] = [data[f][m] for m in members]
        path = HERE / f"noita_eye_triplet_{ti}.json"
        path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        labels = ", ".join(data["message_labels"][m] for m in members)
        print(f"  wrote {path.name}  ({labels})")
        written.append(path)
    print(f"\n{len(written)} per-triplet files written. Run EyeStat on each, e.g.:")
    print("  python3 eyestat_gpu_runner.py --data noita_eye_triplet_0.json "
          "--modes all --prngs all --seed-end 100000000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
