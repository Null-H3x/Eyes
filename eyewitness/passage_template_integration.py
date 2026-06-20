#!/usr/bin/env python3
"""Integration smoke test — passage template pipeline plumbing + expected behavior.

Validates that discovery, extend, template extraction, collision constraints,
crib validation, CLIs, and reports are wired and produce known-good results on
the real corpus and on a planted control.

Run:
    python3 eyewitness/passage_template_integration.py

Exit 0 iff every check passes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
EYECRACK = ROOT / "eyecrack"
REPORT = ROOT / "report"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod          # noqa: E402
import passage_template as pt        # noqa: E402
import refrain as rf                   # noqa: E402
import template as tp                  # noqa: E402


class Check:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []

    def ok(self, name: str, cond: bool, detail: str = "") -> None:
        self.results.append((name, cond, detail))

    def report(self) -> int:
        n_ok = sum(1 for _, c, _ in self.results if c)
        print("=" * 72)
        print("PASSAGE TEMPLATE — integration / plumbing validation")
        print("=" * 72)
        for name, cond, detail in self.results:
            tag = "PASS" if cond else "FAIL"
            line = f"  [{tag}] {name}"
            if detail and not cond:
                line += f"  ({detail})"
            elif detail and cond:
                line += f"  ({detail})"
            print(line)
        print("-" * 72)
        print(f"  {n_ok}/{len(self.results)} checks passed")
        return 0 if n_ok == len(self.results) else 1


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def main() -> int:
    c = Check()
    cor = corpus_mod.load()
    M = [list(x) for x in cor.ciphertexts]
    N = cor.N

    # --- module wiring ---
    c.ok("noita_eye_core.passage_template importable",
         hasattr(pt, "discover_targets") and hasattr(pt, "run_paranoia_audit"))
    c.ok("selftest registered in aggregate gate",
         "passage_template" in open(CORE / "selftest.py").read())

    # --- discover plumbing ---
    targets = pt.discover_targets(M, labels=cor.labels, include_refrain=True)
    refrain_t = next((t for t in targets if t.source == "refrain"), None)
    c.ok("discover_targets returns refrain-4x",
         refrain_t is not None and len(refrain_t.instances) == 4,
         f"{len(targets)} targets total")
    c.ok("refrain instances match DEFAULT_INSTANCES",
         refrain_t is not None and sorted(refrain_t.instances) == sorted(rf.DEFAULT_INSTANCES))

    extract_ts = [t for t in targets if t.source == "extract"]
    c.ok("discover finds chain_extract targets",
         len(extract_ts) >= 1, f"{len(extract_ts)} extract target(s)")

    # --- analyze / extend expected behavior (refrain) ---
    assert refrain_t is not None
    ana = pt.analyze_target(M, refrain_t, N, max_extra=12)
    c.ok("refrain max consistent L == 22",
         ana.max_L == 22, f"got max_L={ana.max_L}")
    c.ok("refrain dof == 2",
         ana.max_template is not None and ana.max_template.dof == 2,
         f"dof={ana.max_template.dof if ana.max_template else None}")
    c.ok("refrain has 3 forced-SAME groups",
         ana.max_template is not None and len(ana.max_template.same_groups) == 3,
         str(ana.max_template.same_groups if ana.max_template else None))
    c.ok("refrain free position is [7]",
         ana.max_template is not None and ana.max_template.free_positions == [7])

    # --- collision constraints vs refrain_attack ---
    cols = pt.collision_constraints(M, refrain_t.instances, ana.max_L, N)
    seg = M[refrain_t.instances[0][0]][refrain_t.instances[0][1]:
                                         refrain_t.instances[0][1] + ana.max_L]
    first: dict[int, int] = {}
    ra_pairs: list[tuple[int, int]] = []
    for i, v in enumerate(seg):
        v = int(v)
        if v in first:
            ra_pairs.append((first[v], i))
        else:
            first[v] = i
    ra_line = pt.format_collision_line([(i, j, (j - i) % N) for i, j in ra_pairs])
    pt_line = pt.format_collision_line(cols)
    c.ok("collision line matches refrain_attack format",
         ra_line == pt_line, ra_line[:60])

    # --- GF cross-check on refrain ---
    assert ana.max_template is not None
    gf_checks = pt.verify_collisions_vs_template(
        M, refrain_t.instances, ana.max_template, N)
    c.ok("verify_collisions_vs_template all pass on refrain",
         gf_checks and all(ok for _, ok in gf_checks),
         f"{sum(1 for _, ok in gf_checks if ok)}/{len(gf_checks)}")

    ext_checks = pt.verify_extend_consistent(
        M, refrain_t.instances, refrain_t.base_length, N, max_extra=12)
    c.ok("verify_extend_consistent all pass on refrain",
         ext_checks and all(ok for _, ok in ext_checks))

    # --- L=23 must contradict for refrain ---
    t23 = tp.extract(M, refrain_t.instances, 23, N)
    c.ok("refrain L=23 template contradicts",
         not t23.consistent)

    # --- shared_structure target that fails progressive (expected) ---
    ss_bad = next((t for t in targets if t.name.startswith("passage-12-6")), None)
    if ss_bad is not None:
        bad_ana = pt.analyze_target(M, ss_bad, N, max_extra=5)
        c.ok("passage-12-6 inconsistent -> max_L=0 (expected)",
             bad_ana.max_L == 0 and bad_ana.max_template is None,
             f"max_L={bad_ana.max_L}")

    # --- stage 6 crib plumbing ---
    v = pt.validate_phrase(refrain_t, "x" * 22, M, N, "abcdefghijklmnopqrstuvwxyz",
                           n_null=50)
    c.ok("validate_phrase runs on refrain",
         v is not None)
    c.ok("garbage phrase rejected (no corpus extend)",
         v is not None and not (v.value_consistent and v.extends_corpus))

    # --- paranoia audit ---
    audit = pt.run_paranoia_audit(M, cor.labels, N)
    c.ok("run_paranoia_audit all pass",
         audit and all(ok for _, ok in audit),
         f"{sum(1 for _, ok in audit if ok)}/{len(audit)}")

    # --- CLI plumbing ---
    rc, out = _run([sys.executable, str(HERE / "passage_template.py"), "--audit"],
                   ROOT)
    c.ok("CLI eyewitness/passage_template.py --audit exit 0",
         rc == 0 and "audit checks passed" in out,
         f"rc={rc}")

    rc, out = _run([sys.executable, str(HERE / "passage_template.py"),
                    "--top", "3", "--html"],
                   ROOT)
    c.ok("CLI --html exit 0",
         rc == 0, f"rc={rc}")
    report_path = REPORT / "passage_template_report.md"
    c.ok("report/passage_template_report.md written",
         report_path.is_file() and "refrain-4x" in report_path.read_text())

    rc, out = _run([sys.executable, str(EYECRACK / "passage_template.py"), "--audit"],
                   ROOT)
    c.ok("CLI eyecrack/passage_template.py wrapper exit 0",
         rc == 0, f"rc={rc}")

    rc, out = _run([sys.executable, str(CORE / "passage_template.py")], ROOT)
    c.ok("CLI noita_eye_core/passage_template.py selftest exit 0",
         rc == 0 and "100/100" in out, f"rc={rc}")

    # --- eyes.py menu wiring ---
    eyes_txt = (ROOT / "eyes.py").read_text()
    c.ok("eyes.py menu lists passage_template --html",
         "passage_template.py" in eyes_txt and "--html" in eyes_txt)
    c.ok("eyes.py menu lists passage_template --audit",
         "passage_template.py" in eyes_txt and "--audit" in eyes_txt)

    # --- aggregate gate includes module ---
    rc, out = _run([sys.executable, str(CORE / "selftest.py")], ROOT)
    c.ok("aggregate selftest exit 0",
         rc == 0 and "ALL GREEN" in out, f"rc={rc}")
    c.ok("aggregate selftest includes passage_template OK",
         "[OK  ] passage_template" in out)

    return c.report()


if __name__ == "__main__":
    sys.exit(main())
