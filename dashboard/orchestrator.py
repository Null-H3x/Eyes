"""Job orchestrator — run EYES tools as subprocess jobs with saved stdout."""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dashboard import DATA_DIR, JOBS_DIR, ROOT, STATE_PATH
from dashboard.registry import Tool, load_tools, tool_by_id
from dashboard.workflows import PRESETS, preset_by_id

ISO = lambda: datetime.now(timezone.utc).isoformat()

_JOB_ID = re.compile(r"^\d{8}-\d{6}-[a-f0-9]{8}$")
_ACTIVE_JOB_STATUSES = frozenset({"queued", "running"})


def _venv_python() -> Path:
    if platform.system() == "Windows":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def have_venv() -> bool:
    return _venv_python().is_file()


def _assert_safe_job_id(job_id: str) -> None:
    if not _JOB_ID.match(job_id):
        raise ValueError(f"invalid job id: {job_id!r}")


def _job_log_path(job_id: str, name: str) -> Path:
    _assert_safe_job_id(job_id)
    path = (JOBS_DIR / job_id / name).resolve()
    try:
        path.relative_to(JOBS_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"invalid job id: {job_id!r}") from exc
    return path


@dataclass
class JobRecord:
    id: str
    tool_id: str
    title: str
    group: str
    cwd: str
    argv: List[str]
    command: str
    status: str                     # queued | running | completed | failed | cancelled
    exit_code: Optional[int] = None
    started_at: str = ""
    finished_at: Optional[str] = None
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    workflow_id: Optional[str] = None
    workflow_step: Optional[int] = None
    duration_hint: str = "medium"
    error: Optional[str] = None
    dataset_id: Optional[str] = None
    dataset_name: Optional[str] = None
    corpus_path: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class Orchestrator:
    def __init__(self):
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._running: Dict[str, subprocess.Popen] = {}
        self._wf_auto_running: set[str] = set()
        self._load_state()
        self._reconcile_on_startup()

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def _load_state(self) -> None:
        if STATE_PATH.is_file():
            try:
                self.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.state = self._default_state()
        else:
            self.state = self._default_state()

    def _default_state(self) -> dict:
        return {
            "version": 1,
            "updated_at": ISO(),
            "active_job_id": None,
            "workflows": {},
            "recent_job_ids": [],
        }

    def _save_state(self) -> None:
        self.state["updated_at"] = ISO()
        STATE_PATH.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def _reconcile_on_startup(self) -> None:
        """Clear zombie locks left by a crashed server mid-job."""
        changed = False
        jid = self.state.get("active_job_id")
        if jid:
            try:
                _assert_safe_job_id(jid)
            except ValueError:
                self.state["active_job_id"] = None
                changed = True
                jid = None
        if jid:
            rec = self._read_job(jid)
            if not rec or rec.status in _ACTIVE_JOB_STATUSES:
                if rec and rec.status in _ACTIVE_JOB_STATUSES:
                    rec.status = "failed"
                    rec.error = rec.error or "interrupted (server restarted)"
                    rec.finished_at = ISO()
                    rec.exit_code = rec.exit_code if rec.exit_code is not None else -1
                    self._write_job(rec)
                    self._reconcile_workflow_step(rec)
                self.state["active_job_id"] = None
                changed = True
        for wf in self.state.get("workflows", {}).values():
            if wf.get("status") == "running":
                wf["status"] = "failed"
                wf["updated_at"] = ISO()
                changed = True
            for step in wf.get("steps", []):
                if step.get("status") == "running":
                    step["status"] = "failed"
                    changed = True
        if changed:
            self._save_state()

    def _reconcile_workflow_step(self, rec: JobRecord) -> None:
        if rec.workflow_id is None or rec.workflow_step is None:
            return
        wf = self.state.get("workflows", {}).get(rec.workflow_id)
        if not wf:
            return
        idx = rec.workflow_step
        if 0 <= idx < len(wf.get("steps", [])):
            step = wf["steps"][idx]
            step["status"] = "failed"
            step["exit_code"] = rec.exit_code
            step["job_id"] = rec.id
            wf["status"] = "failed"
            wf["updated_at"] = ISO()

    def _job_dir(self, job_id: str) -> Path:
        _assert_safe_job_id(job_id)
        d = JOBS_DIR / job_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _write_job(self, rec: JobRecord) -> None:
        p = self._job_dir(rec.id) / "status.json"
        p.write_text(json.dumps(rec.to_dict(), indent=2), encoding="utf-8")

    def _read_job(self, job_id: str) -> Optional[JobRecord]:
        try:
            _assert_safe_job_id(job_id)
        except ValueError:
            return None
        p = JOBS_DIR / job_id / "status.json"
        if not p.is_file():
            return None
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        if not isinstance(raw, dict):
            return None
        known = {f.name for f in fields(JobRecord)}
        data = {k: raw[k] for k in raw if k in known}
        try:
            return JobRecord(**data)
        except TypeError:
            return None

    def _push_recent(self, job_id: str, limit: int = 40) -> None:
        ids = [j for j in self.state.get("recent_job_ids", []) if j != job_id]
        ids.insert(0, job_id)
        self.state["recent_job_ids"] = ids[:limit]

    def _active_job_blocks(self) -> Optional[str]:
        jid = self.state.get("active_job_id")
        if not jid:
            return None
        rec = self._read_job(jid)
        if rec and rec.status in _ACTIVE_JOB_STATUSES:
            return jid
        if rec is None:
            self.state["active_job_id"] = None
            self._save_state()
        return None

    # ------------------------------------------------------------------
    # Job execution
    # ------------------------------------------------------------------

    def start_tool(
        self,
        tool_id: str,
        *,
        dataset_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        workflow_step: Optional[int] = None,
        wait: bool = False,
    ) -> JobRecord:
        tools = tool_by_id()
        if tool_id not in tools:
            raise KeyError(f"unknown tool_id: {tool_id}")
        tool = tools[tool_id]
        if not have_venv():
            raise RuntimeError("No .venv — run Setup (python3 full-installer.py) first.")

        with self._lock:
            blocking = self._active_job_blocks()
            if blocking:
                raise RuntimeError(
                    f"Job {blocking} still active — wait or cancel.")

            job_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
            rec = JobRecord(
                id=job_id,
                tool_id=tool.id,
                title=tool.title,
                group=tool.group,
                cwd=tool.cwd,
                argv=list(tool.argv),
                command=tool.command,
                status="queued",
                started_at=ISO(),
                workflow_id=workflow_id,
                workflow_step=workflow_step,
                duration_hint=tool.duration,
                dataset_id=dataset_id,
            )
            self._write_job(rec)
            self._push_recent(job_id)
            self.state["active_job_id"] = job_id
            self._save_state()

        thread = threading.Thread(
            target=self._run_job,
            args=(rec, tool),
            daemon=True,
            name=f"job-{job_id}",
        )
        thread.start()
        if wait:
            thread.join()
            return self._read_job(job_id) or rec
        return rec

    def _corpus_env(self, dataset_id: Optional[str] = None) -> tuple:
        from dashboard.dataset_store import prepare_tool_run

        path, ds = prepare_tool_run(dataset_id)
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["EYES_CORPUS_PATH"] = str(path)
        env["EYES_DATASET_ID"] = ds.id
        return env, str(path), ds.id, ds.name

    def _run_job(self, rec: JobRecord, tool: Tool) -> None:
        jdir = self._job_dir(rec.id)
        stdout_path = jdir / "stdout.log"
        stderr_path = jdir / "stderr.log"
        py = str(_venv_python())
        cwd = str(ROOT / tool.cwd)

        rec.status = "running"
        self._write_job(rec)

        try:
            env, corpus_path, ds_id, ds_name = self._corpus_env(rec.dataset_id)
            rec.corpus_path = corpus_path
            rec.dataset_id = ds_id
            rec.dataset_name = ds_name
            self._write_job(rec)

            with stdout_path.open("w", encoding="utf-8", errors="replace") as out, \
                 stderr_path.open("w", encoding="utf-8", errors="replace") as err:
                out.write(f"$ {py} {' '.join(tool.argv)}   (in {tool.cwd})\n")
                out.write(f"# dataset: {ds_name} ({ds_id})\n")
                out.write(f"# corpus:  {corpus_path}\n")
                out.write(f"# EYES_CORPUS_PATH={corpus_path}\n\n")
                out.flush()
                proc = subprocess.Popen(
                    [py, *tool.argv],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    env=env,
                )
                with self._lock:
                    self._running[rec.id] = proc

                def pump(stream, dest, attr):
                    nonlocal rec
                    for line in iter(stream.readline, ""):
                        dest.write(line)
                        dest.flush()
                        with self._lock:
                            rec = self._read_job(rec.id) or rec
                            if attr == "stdout":
                                rec.stdout_bytes = stdout_path.stat().st_size
                            else:
                                rec.stderr_bytes = stderr_path.stat().st_size
                            self._write_job(rec)
                    stream.close()

                t_out = threading.Thread(target=pump, args=(proc.stdout, out, "stdout"))
                t_err = threading.Thread(target=pump, args=(proc.stderr, err, "stderr"))
                t_out.start()
                t_err.start()
                rc = proc.wait()
                t_out.join()
                t_err.join()

            rec = self._read_job(rec.id) or rec
            rec.exit_code = rc
            rec.status = "completed" if rc == 0 else "failed"
            rec.finished_at = ISO()
            rec.stdout_bytes = stdout_path.stat().st_size if stdout_path.is_file() else 0
            rec.stderr_bytes = stderr_path.stat().st_size if stderr_path.is_file() else 0
        except Exception as e:
            rec = self._read_job(rec.id) or rec
            rec.status = "failed"
            rec.error = str(e)
            rec.finished_at = ISO()
            if rec.exit_code is None:
                rec.exit_code = -1
        finally:
            with self._lock:
                self._running.pop(rec.id, None)
                if self.state.get("active_job_id") == rec.id:
                    self.state["active_job_id"] = None
            self._write_job(rec)
            self._save_state()
            if rec.workflow_id is not None and rec.workflow_step is not None:
                self._on_workflow_step_done(rec)

    def cancel_active(self) -> Optional[JobRecord]:
        with self._lock:
            jid = self.state.get("active_job_id")
            if not jid:
                return None
            proc = self._running.get(jid)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        rec = self._read_job(jid)
        if rec and rec.status in _ACTIVE_JOB_STATUSES:
            rec.status = "cancelled"
            rec.finished_at = ISO()
            rec.exit_code = -1
            self._write_job(rec)
            self._reconcile_workflow_step(rec)
            self.state["active_job_id"] = None
            self._save_state()
        return rec

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_jobs(self, limit: int = 40) -> List[dict]:
        out = []
        for jid in self.state.get("recent_job_ids", [])[:limit]:
            rec = self._read_job(jid)
            if rec:
                out.append(rec.to_dict())
        return out

    def get_job(self, job_id: str) -> Optional[dict]:
        _assert_safe_job_id(job_id)
        rec = self._read_job(job_id)
        return rec.to_dict() if rec else None

    def get_stdout(self, job_id: str, tail: int = 0) -> str:
        p = _job_log_path(job_id, "stdout.log")
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace")
        if tail > 0:
            lines = text.splitlines()
            text = "\n".join(lines[-tail:])
        return text

    def get_stderr(self, job_id: str, tail: int = 0) -> str:
        p = _job_log_path(job_id, "stderr.log")
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace")
        if tail > 0:
            lines = text.splitlines()
            text = "\n".join(lines[-tail:])
        return text

    def snapshot(self) -> dict:
        return {
            "have_venv": have_venv(),
            "active_job_id": self.state.get("active_job_id"),
            "updated_at": self.state.get("updated_at"),
            "workflows": self.state.get("workflows", {}),
            "recent_jobs": self.list_jobs(20),
            "tools_count": len(load_tools()),
            "presets_count": len(PRESETS),
        }

    # ------------------------------------------------------------------
    # Workflow automation
    # ------------------------------------------------------------------

    def _sync_workflow_with_preset(self, wstate: dict, preset) -> None:
        """Keep persisted step metadata aligned with current preset tool IDs."""
        steps = wstate.get("steps", [])
        preset_steps = list(preset.steps)
        if len(steps) != len(preset_steps):
            preserved = []
            for i, tid in enumerate(preset_steps):
                old = steps[i] if i < len(steps) else {}
                preserved.append({
                    "tool_id": tid,
                    "status": old.get("status", "pending"),
                    "job_id": old.get("job_id"),
                    "exit_code": old.get("exit_code"),
                })
            wstate["steps"] = preserved
            wstate["current_step"] = min(wstate.get("current_step", 0), len(preset_steps))
            wstate["title"] = preset.title
            wstate["description"] = preset.description
            wstate["tags"] = list(preset.tags)
            wstate["updated_at"] = ISO()
            self._save_state()
            return
        changed = False
        for i, tid in enumerate(preset_steps):
            if steps[i].get("tool_id") != tid:
                steps[i]["tool_id"] = tid
                changed = True
        if wstate.get("title") != preset.title:
            wstate["title"] = preset.title
            changed = True
        if wstate.get("description") != preset.description:
            wstate["description"] = preset.description
            changed = True
        if list(wstate.get("tags") or []) != list(preset.tags):
            wstate["tags"] = list(preset.tags)
            changed = True
        if changed:
            wstate["updated_at"] = ISO()
            self._save_state()

    def _workflow_state(self, workflow_id: str) -> dict:
        wf = self.state.setdefault("workflows", {})
        preset = preset_by_id()[workflow_id]
        if workflow_id not in wf:
            wf[workflow_id] = {
                "id": workflow_id,
                "title": preset.title,
                "description": preset.description,
                "tags": list(preset.tags),
                "current_step": 0,
                "status": "idle",          # idle | running | completed | failed
                "steps": [
                    {"tool_id": tid, "status": "pending", "job_id": None, "exit_code": None}
                    for tid in preset.steps
                ],
                "started_at": None,
                "updated_at": ISO(),
                "last_job_id": None,
                "continue_on_fail": True,
            }
            self._save_state()
        else:
            self._sync_workflow_with_preset(wf[workflow_id], preset)
            if "continue_on_fail" not in wf[workflow_id]:
                wf[workflow_id]["continue_on_fail"] = True
                self._save_state()
        return wf[workflow_id]

    def _apply_workflow_options(
        self,
        wstate: dict,
        *,
        dataset_id: Optional[str] = None,
        continue_on_fail: Optional[bool] = None,
    ) -> None:
        if dataset_id:
            wstate["dataset_id"] = dataset_id
        if continue_on_fail is not None:
            wstate["continue_on_fail"] = bool(continue_on_fail)
        if dataset_id is not None or continue_on_fail is not None:
            self._save_state()

    def get_workflow(self, workflow_id: str) -> dict:
        if workflow_id not in preset_by_id():
            raise KeyError(workflow_id)
        return self._workflow_state(workflow_id)

    def list_workflows(self) -> List[dict]:
        return [self.get_workflow(p.id) for p in PRESETS]

    def reset_workflow(self, workflow_id: str) -> dict:
        wf = self.state.setdefault("workflows", {})
        wf.pop(workflow_id, None)
        self._wf_auto_running.discard(workflow_id)
        self._save_state()
        return self._workflow_state(workflow_id)

    def run_workflow_step(
        self,
        workflow_id: str,
        *,
        dataset_id: Optional[str] = None,
        continue_on_fail: Optional[bool] = None,
    ) -> dict:
        preset = preset_by_id()[workflow_id]
        wstate = self._workflow_state(workflow_id)
        self._apply_workflow_options(
            wstate, dataset_id=dataset_id, continue_on_fail=continue_on_fail)

        blocking = self._active_job_blocks()
        if blocking:
            raise RuntimeError("Another job is running.")

        idx = wstate["current_step"]
        if idx >= len(preset.steps):
            wstate["status"] = "completed"
            wstate["updated_at"] = ISO()
            self._save_state()
            return wstate

        if wstate["status"] == "idle" and idx == 0:
            wstate["started_at"] = ISO()

        tool_id = preset.steps[idx]
        wstate["status"] = "running"
        wstate["updated_at"] = ISO()
        step = wstate["steps"][idx]
        step["status"] = "running"
        self._save_state()

        rec = self.start_tool(
            tool_id,
            dataset_id=wstate.get("dataset_id"),
            workflow_id=workflow_id,
            workflow_step=idx,
        )
        step["job_id"] = rec.id
        wstate["last_job_id"] = rec.id
        self._save_state()
        return wstate

    def run_workflow_auto(
        self,
        workflow_id: str,
        *,
        dataset_id: Optional[str] = None,
        continue_on_fail: Optional[bool] = None,
    ) -> None:
        """Background thread: run all pending steps sequentially."""
        with self._lock:
            if workflow_id in self._wf_auto_running:
                return
            self._wf_auto_running.add(workflow_id)
        wstate = self._workflow_state(workflow_id)
        self._apply_workflow_options(
            wstate, dataset_id=dataset_id, continue_on_fail=continue_on_fail)

        def worker():
            try:
                wstate = self.get_workflow(workflow_id)
                ds_id = wstate.get("dataset_id")
                while wstate["current_step"] < len(wstate["steps"]):
                    if self._active_job_blocks():
                        time.sleep(0.5)
                        continue
                    try:
                        wstate = self.run_workflow_step(workflow_id, dataset_id=ds_id)
                    except RuntimeError:
                        time.sleep(1)
                        continue
                    jid = wstate.get("last_job_id")
                    waited = 0
                    while True:
                        rec = self._read_job(jid) if jid else None
                        if rec and rec.status in ("completed", "failed", "cancelled"):
                            break
                        waited += 1
                        if waited > 7200:
                            break
                        time.sleep(0.5)
                    wstate = self.get_workflow(workflow_id)
                    # Step failure advances when continue_on_fail is enabled.
                self.get_workflow(workflow_id)
            finally:
                with self._lock:
                    self._wf_auto_running.discard(workflow_id)

        threading.Thread(target=worker, daemon=True, name=f"wf-{workflow_id}").start()

    def _on_workflow_step_done(self, rec: JobRecord) -> None:
        wf = self.state.get("workflows", {}).get(rec.workflow_id or "")
        if not wf:
            return
        idx = rec.workflow_step
        if idx is None or idx >= len(wf["steps"]):
            return
        step = wf["steps"][idx]
        step["status"] = "completed" if rec.exit_code == 0 else "failed"
        step["exit_code"] = rec.exit_code
        step["job_id"] = rec.id
        wf["updated_at"] = ISO()
        continue_on_fail = wf.get("continue_on_fail", True)
        if rec.exit_code == 0:
            wf["current_step"] = idx + 1
            if wf["current_step"] >= len(wf["steps"]):
                failed = sum(1 for s in wf["steps"] if s["status"] == "failed")
                wf["status"] = "completed_with_failures" if failed else "completed"
            else:
                wf["status"] = "idle"
        elif continue_on_fail:
            wf["current_step"] = idx + 1
            if wf["current_step"] >= len(wf["steps"]):
                wf["status"] = "completed_with_failures"
            else:
                wf["status"] = "idle"
        else:
            wf["status"] = "failed"
        self._save_state()


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    out.append(("job id regex accepts canonical", _JOB_ID.match("20260621-220235-490f1abe") is not None))
    out.append(("job id regex rejects traversal", _JOB_ID.match("../etc") is None))
    try:
        _assert_safe_job_id("20260621-220235-490f1abe")
        ok = True
    except ValueError:
        ok = False
    out.append(("assert_safe_job_id accepts canonical", ok))
    try:
        _assert_safe_job_id("../../etc")
        ok = False
    except ValueError:
        ok = True
    out.append(("assert_safe_job_id rejects traversal", ok))
    orch = Orchestrator()
    out.append(("orchestrator reconciles startup", orch.state.get("active_job_id") is None))
    rec = orch._read_job("not-a-job")
    out.append(("_read_job rejects bad id", rec is None))

    # continue-on-failure advances workflow past failed steps
    orch.state["workflows"] = {
        "quick-validate": {
            "id": "quick-validate",
            "title": "Quick Validate",
            "description": "",
            "current_step": 0,
            "status": "running",
            "continue_on_fail": True,
            "steps": [
                {"tool_id": "a", "status": "running", "job_id": "j1", "exit_code": None},
                {"tool_id": "b", "status": "pending", "job_id": None, "exit_code": None},
            ],
            "started_at": ISO(),
            "updated_at": ISO(),
            "last_job_id": "j1",
        }
    }
    orch._on_workflow_step_done(JobRecord(
        id="j1", tool_id="a", title="t", group="g", cwd=".", argv=[], command="",
        status="failed", exit_code=1, workflow_id="quick-validate", workflow_step=0,
    ))
    wf = orch.state["workflows"]["quick-validate"]
    out.append(("continue_on_fail advances step", wf["current_step"] == 1))
    out.append(("failed step marked", wf["steps"][0]["status"] == "failed"))
    out.append(("workflow stays idle for next step", wf["status"] == "idle"))

    return out


# Module-level singleton for the server process
_ORCH: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    global _ORCH
    if _ORCH is None:
        _ORCH = Orchestrator()
    return _ORCH


if __name__ == "__main__":
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} orchestrator checks passed")
    sys.exit(0 if n == len(results) else 1)
