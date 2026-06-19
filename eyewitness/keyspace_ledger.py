#!/usr/bin/env python3
"""EyeWitness — keyspace ledger from validated block structure.

Consolidates live outputs from depthmap, keystream_scope, pairdiff, resync,
and header_test into report/keyspace_ledger.md + JSON.

Run:
    python3 keyspace_ledger.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import depthmap as dm           # noqa: E402
import header_test as ht        # noqa: E402
import keystream_scope as ks    # noqa: E402
import pairdiff as pd           # noqa: E402
import resync                   # noqa: E402

TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def build_ledger(messages, labels, N):
    dm_map = dm.build(messages, N)
    scope_body = ks.scope_report(messages, N, body_start=25)
    scope_full = ks.scope_report(messages, N, body_start=0)

    triplet_pairs = []
    for gi, g in enumerate(TRIPLETS):
        td = pd.analyze_triplet(messages, g, N)
        triplet_pairs.append({
            "triplet": gi + 1,
            "members": [labels[i] for i in g],
            "near_dup_pair": [labels[i] for i in td.pair],
            "odd": labels[td.odd],
            "body_agreement": round(td.pair_stat.body_frac, 4),
            "edit_runs_z": round(td.pair_stat.edit_runs_z, 2),
        })

    e1w1 = dm_map.pairs[0]  # E1/W1 is index 0 in combinations (0,1)
    for ev in dm_map.pairs:
        if ev.i == 0 and ev.j == 1:
            e1w1 = ev
            break
    rs = resync.count_resync(messages[0], messages[1])

    body_proven = [
        {"pair": [labels[ev.i], labels[ev.j]],
         "z_body": round(ev.z_body, 1),
         "exploitable": ev.exploitable}
        for ev in dm_map.pairs if ev.body_proven
    ]

    hypotheses = [
        {"id": 1, "name": "Progressive + per-msg bases",
         "keyspace": "~83^6 with pair clustering", "status": "FITS", "searchable": True},
        {"id": 2, "name": "General aperiodic K per triplet",
         "keyspace": "83^300 approx", "status": "FITS", "searchable": False},
        {"id": 5, "name": "PRNG seed x GAK",
         "keyspace": "~3.4e11", "status": "MOOT (offline author)", "searchable": False},
        {"id": 8, "name": "Ciphertext-autokey", "status": "EXCLUDED", "searchable": False},
        {"id": 9, "name": "Mono/Vigenere/AES/OTP/transposition",
         "status": "EXCLUDED", "searchable": False},
    ]

    return {
        "N": N,
        "keystream_scope_body": scope_body.verdict,
        "keystream_scope_cross_z": round(scope_body.cross_sig.z, 2),
        "keystream_scope_within_z": round(scope_body.within_sig.z, 2),
        "keystream_scope_full_cross_z": round(scope_full.cross_sig.z, 2),
        "exploitable_depth": dm_map.exploitable_total,
        "body_proven_pairs": body_proven,
        "e1_w1_resync_events": rs,
        "literal_header_positions": [pc.pos for pc in ht.classify_positions(messages, N)
                                     if pc.kind == "literal/shared"],
        "triplet_near_dup": triplet_pairs,
        "surviving_family": "c[m][t] = C[(p[m][t] + base_m + K_g[t]) mod 83]",
        "hypotheses": hypotheses,
        "search_priority": [
            "Per-triplet progressive + clustered bases",
            "Refrain/template plaintext (pins C)",
            "Position-0 indicator -> base_m",
            "General K_g after #1 fails with calibrated null",
        ],
    }


def render_md(data: dict) -> str:
    L = ["# Keyspace Ledger — deduced from validated block structure", "",
         "*Reproduce: `python3 eyewitness/keyspace_ledger.py`*", "",
         "## Surviving construction", "",
         f"`{data['surviving_family']}`", "",
         "## Live measurements", "",
         f"- Body keystream scope: **{data['keystream_scope_body']}** "
         f"(cross z={data['keystream_scope_cross_z']}, within z="
         f"{data['keystream_scope_within_z']})",
         f"- Full-overlap cross z (confounded): {data['keystream_scope_full_cross_z']}",
         f"- Exploitable 2-deep positions: **{data['exploitable_depth']}**",
         f"- E1/W1 re-sync events: **{data['e1_w1_resync_events']}** (excludes ciphertext-autokey)",
         f"- Literal header positions: {data['literal_header_positions']}", ""]
    L.append("## Triplet near-duplicate pairs")
    L.append("")
    L.append("| triplet | near-dup | odd | body agree | runs z |")
    L.append("|---|---|---|---|---|")
    for t in data["triplet_near_dup"]:
        L.append(f"| {t['triplet']} | {'/'.join(t['near_dup_pair'])} | {t['odd']} | "
                 f"{t['body_agreement']:.1%} | {t['edit_runs_z']} |")
    L.append("")
    L.append("## Body-proven shared keystream pairs")
    L.append("")
    for bp in data["body_proven_pairs"]:
        L.append(f"- {'/'.join(bp['pair'])}: z={bp['z_body']}, exploitable={bp['exploitable']}")
    L.append("")
    L.append("## Hypothesis keyspace ledger")
    L.append("")
    L.append("| id | hypothesis | keyspace | status | searchable |")
    L.append("|---|---|---|---|---|")
    for h in data["hypotheses"]:
        L.append(f"| {h['id']} | {h['name']} | {h.get('keyspace', '—')} | "
                 f"{h['status']} | {h.get('searchable', '—')} |")
    L.append("")
    L.append("## Search priority")
    L.append("")
    for i, p in enumerate(data["search_priority"], 1):
        L.append(f"{i}. {p}")
    L.append("")
    return "\n".join(L)


def main() -> int:
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    data = build_ledger(M, c.labels, c.N)
    md_path = ROOT / "report" / "keyspace_ledger.md"
    json_path = ROOT / "report" / "keyspace_ledger.json"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_md(data), encoding="utf-8")
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    print(f"Body verdict: {data['keystream_scope_body']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
