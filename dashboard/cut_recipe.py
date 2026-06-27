"""Cut-recipe API for the workbench — range cuts, phrase viability, alphabet tools."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "noita_eye_core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import alphabet_cut as ac  # noqa: E402

# Tool argv fragments that accept --alphabet (or benefit from EYES_ALPHABET).
_ALPHABET_TOOL_MARKERS = (
    "order_solve.py",
    "refrain_attack.py",
    "ngram_solve.py",
    "refrain_sweep.py",
    "crib_fit.py",
    "deck_sweep.py",
)

PRESETS = {
    "god": {
        "title": "GOD cuts",
        "specs": list(ac.GOD_CUT_SPECS),
        "promote_god": True,
    },
    "az": {
        "title": "Standard A–Z (no cuts)",
        "specs": [],
        "promote_god": False,
    },
    "god-raw": {
        "title": "GOD cuts (no promotion)",
        "specs": list(ac.GOD_CUT_SPECS),
        "promote_god": False,
    },
}


def is_alphabet_dependent_tool(argv: Sequence[str]) -> bool:
    joined = " ".join(argv)
    return any(m in joined for m in _ALPHABET_TOOL_MARKERS)


def alphabet_tools_payload(tools: Sequence[dict]) -> List[dict]:
    """Filter annotated tool dicts to alphabet-dependent entries."""
    out = []
    for t in tools:
        argv = t.get("argv") or []
        if is_alphabet_dependent_tool(argv):
            out.append({
                "id": t["id"],
                "title": t["title"],
                "group": t.get("group", ""),
                "command": t.get("command", ""),
                "duration": t.get("duration", "medium"),
            })
    return out


def evaluate(body: dict) -> dict:
    """Build recipe from JSON body (cuts, phrase, variant, presets)."""
    preset_id = body.get("preset")
    if preset_id:
        if preset_id not in PRESETS:
            return {"ok": False, "error": f"unknown preset {preset_id!r}"}
        p = PRESETS[preset_id]
        specs = list(p["specs"])
        promote_god = bool(p.get("promote_god"))
        promote = None
    else:
        specs = body.get("cuts") or body.get("specs") or list(ac.GOD_CUT_SPECS)
        if isinstance(specs, str):
            specs = [s.strip() for s in specs.replace(",", " ").split() if s.strip()]
        promote_god = bool(body.get("promote_god"))
        promote = body.get("promote")

    phrase = str(body.get("phrase", "")).strip()
    variant = body.get("variant", "both")
    lower_mode = body.get("lower_mode", "mirror")
    wiki_crib = body.get("wiki_crib", True)
    wiki_mode = body.get("wiki_mode", "symbol")

    try:
        recipe = ac.build_recipe(
            specs,
            promote_god=promote_god,
            promote=promote,
            variant=variant,
            lower_mode=lower_mode,
            wiki_crib=wiki_crib,
            wiki_mode=wiki_mode,
            phrase=phrase,
        )
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    if not recipe.get("ok"):
        return recipe

    # Pick best deck for tool runs from phrase recommendation.
    best_variant = "52"
    if phrase and recipe.get("phrase"):
        best_variant = recipe["phrase"].get("recommended_variant") or "52"
    elif variant in ("26", "52"):
        best_variant = variant

    recipe["selected_variant"] = best_variant
    sel = recipe.get("variants", {}).get(best_variant, {})
    recipe["selected_deck"] = sel.get("deck", "")
    return recipe


def snapshot_presets() -> dict:
    """Embedded defaults for static HTML."""
    rows = {}
    for pid, meta in PRESETS.items():
        r = evaluate({"preset": pid, "phrase": "Eyes", "variant": "both"})
        rows[pid] = {
            "title": meta["title"],
            "upper26": r.get("upper26", ""),
            "phrase": r.get("phrase"),
        }
    return {
        "presets": PRESETS,
        "default_cuts": list(ac.GOD_CUT_SPECS),
        "examples": rows,
    }


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []
    out.append(("god preset evaluates", evaluate({"preset": "god", "phrase": "god"})["ok"]))
    eyes = evaluate({"preset": "god", "phrase": "Eyes"})
    out.append(("Eyes on 52 viable", eyes.get("phrase", {}).get("v52", {}).get("viable")))
    out.append(("Eyes on 26 not viable", not eyes.get("phrase", {}).get("v26", {}).get("viable")))
    out.append(("selected_deck len 83", len(eyes.get("selected_deck", "")) == 83))
    out.append(("is_alphabet_dependent order_solve",
                is_alphabet_dependent_tool(["order_solve.py", "foo"])))
    out.append(("snapshot_presets has god", "god" in snapshot_presets()["examples"]))
    return out
