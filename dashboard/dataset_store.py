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
from dashboard.cipher_validate import GLYPHS, parse_values

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


def active_corpus_path() -> Path:
    """Path passed to tools via EYES_CORPUS_PATH for subprocess runs."""
    ds = get_active()
    if ds.id == BUILTIN_ID:
        return ROOT / "noita_eye_core" / "corpus.json"
    _ensure_dirs()
    out = DATA_DIR / "active_corpus.json"
    out.write_text(json.dumps(ds.to_corpus_json(), indent=2), encoding="utf-8")
    return out


def _parse_glyph_line(line: str, *, N: int) -> List[int]:
    vals: List[int] = []
    for ch in line:
        if ch.isspace():
            continue
        if ch in GLYPHS:
            vals.append(GLYPHS.index(ch))
        elif ch.isdigit():
            vals.append(int(ch))
        else:
            raise ValueError(f"cannot parse glyph {ch!r} (not in alphabet)")
    for v in vals:
        if not (0 <= v < N):
            raise ValueError(f"glyph value {v} outside [0, {N})")
    return vals


def _parse_message_line(line: str, *, N: int, fmt: str) -> List[int]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    if fmt == "glyphs":
        return _parse_glyph_line(line, N=N)
    if fmt == "json_array":
        arr = json.loads(line)
        vals = [int(v) for v in arr]
        for v in vals:
            if not (0 <= v < N):
                raise ValueError(f"value {v} outside [0, {N})")
        return vals
    return parse_values(line, N=N, strict=True)


def _detect_import_format(content: str) -> str:
    if content.startswith("{"):
        return "corpus_json"
    sample_lines = [
        ln.strip() for ln in content.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ][:5]
    if not sample_lines:
        return "lines"
    glyphish = 0
    for ln in sample_lines:
        body = ln.split(":", 1)[-1].strip() if ":" in ln and not ln[0].isdigit() else ln
        if body and not body[0].isdigit() and any(ch in GLYPHS for ch in body):
            glyphish += 1
    if glyphish >= max(1, len(sample_lines) // 2):
        return "glyphs"
    return "lines"


def parse_import(
    content: str,
    *,
    fmt: str = "auto",
    name: str = "Imported dataset",
    deck_size: int = 83,
    labels: Optional[Sequence[str]] = None,
) -> Dataset:
    """Import ciphertext from JSON, lines of decimals, or glyph strings."""
    content = content.strip()
    if not content:
        raise ValueError("empty import")
    if deck_size < 2 or deck_size > 256:
        raise ValueError("deck_size must be in [2, 256]")

    if fmt == "auto":
        fmt = _detect_import_format(content)

    messages: List[List[int]] = []
    lbls: List[str] = []

    if fmt == "corpus_json":
        raw = json.loads(content)
        N = int(raw.get("deck_size", deck_size))
        if N < 2 or N > 256:
            raise ValueError("deck_size must be in [2, 256]")
        if "ciphertexts" not in raw:
            raise ValueError("corpus JSON missing ciphertexts")
        messages = [list(int(v) for v in ct) for ct in raw["ciphertexts"]]
        lbls = [str(x) for x in raw.get("message_labels", [])]
        if not lbls:
            lbls = [f"Message {i + 1}" for i in range(len(messages))]
        ds_id = str(uuid.uuid4())[:12]
        ds = Dataset(
            id=f"import-{ds_id}",
            name=name,
            source="imported",
            deck_size=N,
            labels=lbls,
            ciphertexts=messages,
            created_at=_now(),
            notes=f"Imported as corpus JSON ({len(messages)} messages)",
        )
        _validate_dataset(ds)
        return ds

    msg_num = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line and not line[0].isdigit() and fmt != "glyphs":
            label, rest = line.split(":", 1)
            lbls.append(label.strip())
            vals = _parse_message_line(rest, N=deck_size, fmt=fmt)
        else:
            lbls.append(
                labels[msg_num] if labels and msg_num < len(labels)
                else f"Message {msg_num + 1}")
            vals = _parse_message_line(line, N=deck_size, fmt=fmt)
        if vals:
            messages.append(vals)
            msg_num += 1

    if not messages:
        raise ValueError("no messages parsed from import")

    ds_id = str(uuid.uuid4())[:12]
    ds = Dataset(
        id=f"import-{ds_id}",
        name=name,
        source="imported",
        deck_size=deck_size,
        labels=lbls[:len(messages)],
        ciphertexts=messages,
        created_at=_now(),
        notes=f"Imported {len(messages)} message(s), format={fmt}",
        metadata={"import_format": fmt},
    )
    if len(ds.labels) < len(messages):
        ds.labels.extend(
            f"Message {i + 1}" for i in range(len(ds.labels), len(messages)))
    _validate_dataset(ds)
    return ds


def import_and_save(
    content: str,
    *,
    fmt: str = "auto",
    name: str = "Imported dataset",
    deck_size: int = 83,
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
        parse_import("999 1000", fmt="lines", deck_size=83)
        out.append(("strict import rejects OOR decimals", False))
    except ValueError:
        out.append(("strict import rejects OOR decimals", True))

    imp = parse_import("# comment\nA: 1 2 3\n4 5 6", fmt="lines", deck_size=83)
    out.append(("import labels with comment line", imp.labels[0] == "A"))

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

    planted = parse_import("10 20 30", fmt="lines", deck_size=83)
    out.append(("parse single-line import", len(planted.ciphertexts[0]) == 3))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} dataset_store checks passed")
    sys.exit(0 if n == len(results) else 1)
