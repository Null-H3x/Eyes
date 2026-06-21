"""Workbench dataset store — import, plant, and activate custom corpora.

Supports eye-puzzle-like datasets that may lack the Noita universal header
(66, 5).  The built-in Noita corpus remains the default; imported or planted
datasets become the *active* corpus for cipher validation and (via
``EYES_CORPUS_PATH``) subprocess tool runs.
"""
from __future__ import annotations

import json
import re
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from dashboard import DATA_DIR, ROOT
from dashboard.import_parse import parse_import_content

DATASETS_DIR = DATA_DIR / "datasets"
ACTIVE_PATH = DATA_DIR / "active_dataset.json"
BUILTIN_ID = "noita-eye-corpus"
_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$")


@dataclass
class Dataset:
    id: str
    name: str
    source: str                       # builtin | imported | planted
    deck_size: int
    labels: List[str]
    ciphertexts: List[List[int]]
    created_at: str = ""
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def N(self) -> int:
        return self.deck_size

    @property
    def lengths(self) -> List[int]:
        return [len(ct) for ct in self.ciphertexts]

    @property
    def num_messages(self) -> int:
        return len(self.ciphertexts)

    def to_corpus_json(self) -> dict:
        return {
            "_comment": self.notes or f"Workbench dataset {self.name}",
            "_source": self.source,
            "deck_size": self.deck_size,
            "num_messages": self.num_messages,
            "message_labels": self.labels,
            "message_lengths": self.lengths,
            "ciphertexts": self.ciphertexts,
            **({"metadata": self.metadata} if self.metadata else {}),
        }

    def to_dict(self, *, include_messages: bool = True) -> dict:
        d = asdict(self)
        if not include_messages:
            d.pop("ciphertexts", None)
            d["lengths"] = self.lengths
            d["num_messages"] = self.num_messages
        return d


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _assert_safe_id(dataset_id: str) -> None:
    if dataset_id == BUILTIN_ID:
        return
    if not _SAFE_ID.match(dataset_id):
        raise ValueError(f"invalid dataset id: {dataset_id!r}")


def _dataset_json_path(dataset_id: str) -> Path:
    _assert_safe_id(dataset_id)
    path = (DATASETS_DIR / f"{dataset_id}.json").resolve()
    try:
        path.relative_to(DATASETS_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"invalid dataset id: {dataset_id!r}") from exc
    return path


def _validate_dataset(ds: Dataset) -> None:
    if ds.deck_size < 2:
        raise ValueError("deck_size must be >= 2")
    if not ds.ciphertexts:
        raise ValueError("dataset must contain at least one message")
    if len(ds.labels) != len(ds.ciphertexts):
        raise ValueError("label count must match message count")
    for i, ct in enumerate(ds.ciphertexts):
        if not ct:
            raise ValueError(f"message {i}: empty ciphertext")
        for v in ct:
            if not (0 <= v < ds.deck_size):
                raise ValueError(
                    f"message {i}: value {v} outside [0, {ds.deck_size})")


def load_builtin() -> Dataset:
    sys_path = ROOT / "noita_eye_core"
    import sys
    if str(sys_path) not in sys.path:
        sys.path.insert(0, str(sys_path))
    import corpus as corpus_mod
    c = corpus_mod.load()
    return Dataset(
        id=BUILTIN_ID,
        name="Noita Eye Corpus (9 messages)",
        source="builtin",
        deck_size=c.N,
        labels=list(c.labels),
        ciphertexts=[list(ct) for ct in c.ciphertexts],
        created_at="",
        notes="Original 9-message corpus with universal header CT[1]=66, CT[2]=5.",
        metadata={"builtin": True, "has_noita_header": True},
    )


def _save_dataset(ds: Dataset) -> Path:
    _ensure_dirs()
    _assert_safe_id(ds.id)
    _validate_dataset(ds)
    path = _dataset_json_path(ds.id)
    path.write_text(json.dumps(ds.to_corpus_json(), indent=2), encoding="utf-8")
    meta_path = DATASETS_DIR / f"{ds.id}.meta.json"
    meta_path.write_text(json.dumps(ds.to_dict(include_messages=False), indent=2),
                        encoding="utf-8")
    return path


def list_datasets() -> List[dict]:
    _ensure_dirs()
    out = [load_builtin().to_dict(include_messages=False)]
    seen = {BUILTIN_ID}
    for meta_path in sorted(DATASETS_DIR.glob("*.meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        ds_id = meta.get("id", "")
        if not ds_id or ds_id in seen:
            continue
        json_path = DATASETS_DIR / f"{ds_id}.json"
        if not json_path.is_file():
            continue
        seen.add(ds_id)
        out.append(meta)
    return out


def load_dataset(dataset_id: str) -> Dataset:
    if dataset_id == BUILTIN_ID:
        return load_builtin()
    path = _dataset_json_path(dataset_id)
    if not path.is_file():
        raise KeyError(f"dataset not found: {dataset_id}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    meta_path = DATASETS_DIR / f"{dataset_id}.meta.json"
    meta = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    deck_size = int(raw["deck_size"])
    labels = [str(x) for x in raw["message_labels"]]
    ciphertexts = [list(int(v) for v in ct) for ct in raw["ciphertexts"]]
    declared = raw.get("message_lengths")
    if declared is not None:
        declared = [int(x) for x in declared]
        actual = [len(ct) for ct in ciphertexts]
        if declared != actual:
            raise ValueError(
                f"message_lengths {declared} != actual lengths {actual}")
    ds = Dataset(
        id=dataset_id,
        name=meta.get("name", dataset_id),
        source=meta.get("source", "imported"),
        deck_size=deck_size,
        labels=labels,
        ciphertexts=ciphertexts,
        created_at=meta.get("created_at", ""),
        notes=meta.get("notes", raw.get("_comment", "")),
        metadata=meta.get("metadata", raw.get("metadata", {})),
    )
    _validate_dataset(ds)
    return ds


def _reset_active_builtin() -> None:
    _ensure_dirs()
    ACTIVE_PATH.write_text(json.dumps({
        "active_id": BUILTIN_ID,
        "updated_at": _now(),
        "reset_reason": "stale_or_invalid_active_id",
    }, indent=2), encoding="utf-8")


def get_active_id() -> str:
    _ensure_dirs()
    if not ACTIVE_PATH.is_file():
        return BUILTIN_ID
    try:
        data = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
        active_id = data.get("active_id", BUILTIN_ID)
    except json.JSONDecodeError:
        return BUILTIN_ID
    if active_id == BUILTIN_ID:
        return BUILTIN_ID
    try:
        _assert_safe_id(active_id)
        if not _dataset_json_path(active_id).is_file():
            _reset_active_builtin()
            return BUILTIN_ID
    except ValueError:
        _reset_active_builtin()
        return BUILTIN_ID
    return active_id


def set_active(dataset_id: str) -> Dataset:
    ds = load_dataset(dataset_id)
    _ensure_dirs()
    ACTIVE_PATH.write_text(json.dumps({
        "active_id": dataset_id,
        "updated_at": _now(),
    }, indent=2), encoding="utf-8")
    return ds


def get_active() -> Dataset:
    return load_dataset(get_active_id())


def corpus_path_for(dataset_id: Optional[str] = None) -> Path:
    """Materialize corpus JSON for tool runs (builtin path or active_corpus.json)."""
    ds = load_dataset(dataset_id) if dataset_id else get_active()
    if ds.id == BUILTIN_ID:
        return ROOT / "noita_eye_core" / "corpus.json"
    _ensure_dirs()
    out = DATA_DIR / "active_corpus.json"
    out.write_text(json.dumps(ds.to_corpus_json(), indent=2), encoding="utf-8")
    return out


def active_corpus_path() -> Path:
    """Path passed to tools via EYES_CORPUS_PATH for subprocess runs."""
    return corpus_path_for(get_active_id())


def prepare_tool_run(dataset_id: Optional[str] = None) -> Tuple[Path, Dataset]:
    """Resolve corpus path for a tool run; keep active id in sync when explicit."""
    ds_id = dataset_id or get_active_id()
    ds = load_dataset(ds_id)
    if ds_id != get_active_id():
        set_active(ds_id)
    return corpus_path_for(ds_id), ds


def _resolve_deck_size(raw) -> Optional[int]:
    """Return None for unknown/auto deck size."""
    if raw is None:
        return None
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in ("", "unknown", "auto", "?"):
            return None
        return int(s)
    if isinstance(raw, bool):
        return None
    v = int(raw)
    return None if v <= 0 else v


def parse_import(
    content: str,
    *,
    fmt: str = "auto",
    name: str = "Imported dataset",
    deck_size: Optional[int] = 83,
    labels: Optional[Sequence[str]] = None,
) -> Dataset:
    """Import ciphertext from any mix of numbers, glyphs, spacing, punctuation."""
    if fmt in ("lines", "glyphs"):
        fmt = "auto"
    unknown_n = deck_size is None
    inference = None
    resolved_n = deck_size if deck_size is not None else 83
    if unknown_n:
        from dashboard.deck_infer import infer_from_text
        inference = infer_from_text(content, fmt=fmt)
        resolved_n = inference["inferred_N"]
        parsed = parse_import_content(
            content, fmt=fmt, deck_size=resolved_n, labels=labels, strict=True)
    else:
        parsed = parse_import_content(
            content, fmt=fmt, deck_size=deck_size, labels=labels, strict=True)
        resolved_n = parsed.deck_size
    ds_id = str(uuid.uuid4())[:12]
    meta: Dict[str, Any] = {
        "import_format": parsed.detected_format,
        "import_diagnostics": {
            "per_message": parsed.per_message,
            "notes": parsed.notes,
        },
    }
    if inference:
        meta["deck_size_inferred"] = True
        meta["deck_inference"] = inference
        meta["import_diagnostics"]["deck_inference"] = inference
    ds = Dataset(
        id=f"import-{ds_id}",
        name=name,
        source="imported",
        deck_size=resolved_n,
        labels=list(parsed.labels),
        ciphertexts=[list(ct) for ct in parsed.messages],
        created_at=_now(),
        notes=(
            f"Imported {len(parsed.messages)} message(s), "
            f"N={resolved_n}" + (" (inferred)" if inference else "")
        ),
        metadata=meta,
    )
    _validate_dataset(ds)
    return ds


def preview_import(
    content: str,
    *,
    fmt: str = "auto",
    deck_size: Optional[int] = 83,
) -> dict:
    """Dry-run parse — returns diagnostics without saving."""
    if fmt in ("lines", "glyphs"):
        fmt = "auto"
    unknown_n = deck_size is None
    inference = None
    if unknown_n:
        from dashboard.deck_infer import infer_from_text
        inference = infer_from_text(content, fmt=fmt)
        resolved_n = inference["inferred_N"]
        parsed = parse_import_content(
            content, fmt=fmt, deck_size=resolved_n, strict=True)
    else:
        parsed = parse_import_content(
            content, fmt=fmt, deck_size=deck_size, strict=True)
    out = {
        "detected_format": parsed.detected_format,
        "num_messages": len(parsed.messages),
        "labels": parsed.labels,
        "lengths": [len(m) for m in parsed.messages],
        "per_message": parsed.per_message,
        "notes": list(parsed.notes),
        "deck_size_unknown": unknown_n,
        "preview_decimals": [
            " ".join(str(v) for v in m[:40]) + ("…" if len(m) > 40 else "")
            for m in parsed.messages
        ],
        "inferred_N": parsed.deck_size,
    }
    if inference:
        out["deck_inference"] = inference
        out["notes"].append(
            f"Inferred N={inference['inferred_N']} ({inference['confidence']} confidence)")
    return out


def import_and_save(
    content: str,
    *,
    fmt: str = "auto",
    name: str = "Imported dataset",
    deck_size: Optional[int] = 83,
    activate: bool = False,
) -> Dataset:
    ds = parse_import(content, fmt=fmt, name=name, deck_size=deck_size)
    _save_dataset(ds)
    if activate:
        set_active(ds.id)
    return ds


def save_planted(ds: Dataset, *, activate: bool = False) -> Dataset:
    if not ds.created_at:
        ds.created_at = _now()
    ds.source = "planted"
    _save_dataset(ds)
    if activate:
        set_active(ds.id)
    return ds


def selftest() -> List[Tuple[str, bool]]:
    import os
    import shutil
    import tempfile

    out: List[Tuple[str, bool]] = []
    builtin = load_builtin()
    out.append(("builtin loads 9 messages", builtin.num_messages == 9))

    try:
        load_dataset("../../../etc/passwd")
        out.append(("path traversal blocked", False))
    except (KeyError, ValueError):
        out.append(("path traversal blocked", True))

    try:
        parse_import("999 1000", fmt="auto", deck_size=83)
        out.append(("strict import rejects OOR decimals", False))
    except ValueError:
        out.append(("strict import rejects OOR decimals", True))

    imp = parse_import("# comment\nA: 1 2 3\n4 5 6", fmt="auto", deck_size=83)
    out.append(("import labels with comment line", imp.labels[0] == "A"))

    mixed = parse_import("10o66\no%5\n10665", fmt="auto", deck_size=83)
    out.append(("mixed import parses 3 messages", len(mixed.ciphertexts) == 3))
    from dashboard.cipher_validate import GLYPHS
    out.append(("mixed glued digits", mixed.ciphertexts[2] == [10, 66, 5]))
    out.append(("mixed glyphs", mixed.ciphertexts[1][0] == GLYPHS.index("o")))

    unk = parse_import("10 20 30\n40 50 60", fmt="auto", deck_size=None)
    out.append(("unknown N import infers deck", unk.deck_size >= 61))
    out.append(("unknown marks inferred metadata",
                  unk.metadata.get("deck_size_inferred") is True))

    orig_dir = DATA_DIR
    tmp = Path(tempfile.mkdtemp())
    try:
        globals()["DATA_DIR"] = tmp
        globals()["DATASETS_DIR"] = tmp / "datasets"
        globals()["ACTIVE_PATH"] = tmp / "active_dataset.json"
        _ensure_dirs()
        ACTIVE_PATH.write_text(json.dumps({"active_id": "import-deadbeef"}))
        out.append(("stale active falls back to builtin",
                    get_active_id() == BUILTIN_ID))
    finally:
        globals()["DATA_DIR"] = orig_dir
        globals()["DATASETS_DIR"] = orig_dir / "datasets"
        globals()["ACTIVE_PATH"] = orig_dir / "active_dataset.json"
        shutil.rmtree(tmp, ignore_errors=True)

    planted = parse_import("10 20 30", fmt="auto", deck_size=83)
    out.append(("parse single-line import", len(planted.ciphertexts[0]) == 3))

    saved = import_and_save(
        name="bridge-test",
        content="1 2 3\n4 5 6",
        fmt="auto",
        deck_size=83,
        activate=False,
    )
    p = corpus_path_for(saved.id)
    out.append(("corpus_path_for custom dataset", p.is_file()))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    out.append(("corpus_path_for round-trip", len(loaded["ciphertexts"]) == 2))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} dataset_store checks passed")
    sys.exit(0 if n == len(results) else 1)
