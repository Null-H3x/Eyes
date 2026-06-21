"""Workbench dataset store — import, plant, and activate custom corpora.

Supports eye-puzzle-like datasets that may lack the Noita universal header
(66, 5).  The built-in Noita corpus remains the default; imported or planted
datasets become the *active* corpus for cipher validation and (via
``EYES_CORPUS_PATH``) subprocess tool runs.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from dashboard import DATA_DIR, ROOT
from dashboard.cipher_validate import GLYPHS, parse_values

DATASETS_DIR = DATA_DIR / "datasets"
ACTIVE_PATH = DATA_DIR / "active_dataset.json"
BUILTIN_ID = "noita-eye-corpus"


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


def _validate_dataset(ds: Dataset) -> None:
    if len(ds.labels) != len(ds.ciphertexts):
        raise ValueError("label count must match message count")
    for i, ct in enumerate(ds.ciphertexts):
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
    _validate_dataset(ds)
    path = DATASETS_DIR / f"{ds.id}.json"
    path.write_text(json.dumps(ds.to_corpus_json(), indent=2), encoding="utf-8")
    meta_path = DATASETS_DIR / f"{ds.id}.meta.json"
    meta_path.write_text(json.dumps(ds.to_dict(include_messages=False), indent=2),
                        encoding="utf-8")
    return path


def list_datasets() -> List[dict]:
    _ensure_dirs()
    out = [load_builtin().to_dict(include_messages=False)]
    for meta_path in sorted(DATASETS_DIR.glob("*.meta.json")):
        try:
            out.append(json.loads(meta_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def load_dataset(dataset_id: str) -> Dataset:
    if dataset_id == BUILTIN_ID:
        return load_builtin()
    path = DATASETS_DIR / f"{dataset_id}.json"
    if not path.is_file():
        raise KeyError(f"dataset not found: {dataset_id}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    meta_path = DATASETS_DIR / f"{dataset_id}.meta.json"
    meta = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return Dataset(
        id=dataset_id,
        name=meta.get("name", dataset_id),
        source=meta.get("source", "imported"),
        deck_size=int(raw["deck_size"]),
        labels=[str(x) for x in raw["message_labels"]],
        ciphertexts=[list(int(v) for v in ct) for ct in raw["ciphertexts"]],
        created_at=meta.get("created_at", ""),
        notes=meta.get("notes", raw.get("_comment", "")),
        metadata=meta.get("metadata", raw.get("metadata", {})),
    )


def get_active_id() -> str:
    _ensure_dirs()
    if not ACTIVE_PATH.is_file():
        return BUILTIN_ID
    try:
        data = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
        return data.get("active_id", BUILTIN_ID)
    except json.JSONDecodeError:
        return BUILTIN_ID


def set_active(dataset_id: str) -> Dataset:
    load_dataset(dataset_id)  # validate exists
    _ensure_dirs()
    ACTIVE_PATH.write_text(json.dumps({
        "active_id": dataset_id,
        "updated_at": _now(),
    }, indent=2), encoding="utf-8")
    return load_dataset(dataset_id)


def get_active() -> Dataset:
    return load_dataset(get_active_id())


def active_corpus_path() -> Path:
    """Path passed to tools via EYES_CORPUS_PATH for subprocess runs."""
    ds = get_active()
    if ds.id == BUILTIN_ID:
        return ROOT / "noita_eye_core" / "corpus.json"
    out = DATA_DIR / "active_corpus.json"
    out.write_text(json.dumps(ds.to_corpus_json(), indent=2), encoding="utf-8")
    return out


def _parse_message_line(line: str, *, N: int, fmt: str) -> List[int]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    if fmt == "glyphs":
        return [GLYPHS.index(ch) if ch in GLYPHS else int(ch) % N
                for ch in line if not ch.isspace()]
    if fmt == "json_array":
        arr = json.loads(line)
        return [int(v) % N for v in arr]
    return parse_values(line, N=N)


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

    if fmt == "auto":
        if content.startswith("{"):
            fmt = "corpus_json"
        elif "\n" in content and all(
            len(ln.strip()) > 0 and not ln.strip()[0].isdigit()
            for ln in content.splitlines()[:3] if ln.strip() and not ln.strip().startswith("#")
        ):
            fmt = "glyphs"
        else:
            fmt = "lines"

    messages: List[List[int]] = []
    lbls: List[str] = []

    if fmt == "corpus_json":
        raw = json.loads(content)
        N = int(raw.get("deck_size", deck_size))
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

    for i, line in enumerate(content.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line and not line[0].isdigit() and fmt != "glyphs":
            label, rest = line.split(":", 1)
            lbls.append(label.strip())
            vals = _parse_message_line(rest, N=deck_size, fmt=fmt)
        else:
            lbls.append(
                labels[i] if labels and i < len(labels) else f"Message {len(messages) + 1}")
            vals = _parse_message_line(line, N=deck_size, fmt=fmt)
        if vals:
            messages.append(vals)

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
    ds.source = "planted"
    if not ds.created_at:
        ds.created_at = _now()
    _save_dataset(ds)
    if activate:
        set_active(ds.id)
    return ds
