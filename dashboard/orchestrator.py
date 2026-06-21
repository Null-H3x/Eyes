"""Job orchestrator — run EYES tools as subprocess jobs with saved stdout."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from dashboard import DATA_DIR, JOBS_DIR, ROOT, STATE_PATH
from dashboard.registry import Tool, load_tools, tool_by_id
from dashboard.workflows import PRESETS, preset_by_id

ISO = lambda: datetime.now(timezone.utc).isoformat()


def _venv_python() -> Path:
    if platform.system() == "Windows":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def have_venv() -> bool:
    return _venv_python().is_file()


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

    def to_dict(self) -> dict:
        return asdict(self)


class Orchestrator:
    def __init__(self):
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._running: Dict[str, subprocess.Popen] = {}
        self._load_state()

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

    def _job_dir(self, job_id: str) -> Path:
        d = JOBS_DIR / job_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _write_job(self, rec: JobRecord) -> None:
        p = self._job_dir(rec.id) / "status.json"
        p.write_text(json.dumps(rec.to_dict(), indent=2), encoding="utf-8")

    def _read_job(self, job_id: str) -> Optional[JobRecord]:
        p = JOBS_DIR / job_id / "status.json"
        if not p.is_file():
            return None
        d = json.loads(p.read_text(encoding="utf-8"))
        return JobRecord(**d)

    def _push_recent(self, job_id: str, limit: int = 40) -> None:
        ids = [j for j in self.state.get("recent_job_ids", []) if j != job_id]
        ids.insert(0, job_id)
        self.state["recent_job_ids"] = ids[:limit]

    # ------------------------------------------------------------------
    # Job execution
    # ------------------------------------------------------------------

    def start_tool(
        self,
        tool_id: str,
        *,
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
            if self.state.get("active_job_id"):
                active = self._read_job(self.state["active_job_id"])
                if active and active.status == "running":
                    raise RuntimeError(
                        f"Job {self.state['active_job_id']} still running — wait or cancel.")

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

    def _run_job(self, rec: JobRecord, tool: Tool) -> None:
        jdir = self._job_dir(rec.id)
        stdout_path = jdir / "stdout.log"
        stderr_path = jdir / "stderr.log"
        py = str(_venv_python())
        cwd = str(ROOT / tool.cwd)

        rec.status = "running"
        self._write_job(rec)

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        try:
            with stdout_path.open("w", encoding="utf-8", errors="replace") as out, \
                 stderr_path.open("w", encoding="utf-8", errors="replace") as err:
                out.write(f"$ {py} {' '.join(tool.argv)}   (in {tool.cwd})\n\n")
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
        if rec and rec.status == "running":
            rec.status = "cancelled"
            rec.finished_at = ISO()
            rec.exit_code = -1
            self._write_job(rec)
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
        rec = self._read_job(job_id)
        return rec.to_dict() if rec else None

    def get_stdout(self, job_id: str, tail: int = 0) -> str:
        p = JOBS_DIR / job_id / "stdout.log"
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace")
        if tail > 0:
            lines = text.splitlines()
            text = "\n".join(lines[-tail:])
        return text

    def get_stderr(self, job_id: str, tail: int = 0) -> str:
        p = JOBS_DIR / job_id / "stderr.log"
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

    def _workflow_state(self, workflow_id: str) -> dict:
        wf = self.state.setdefault("workflows", {})
        if workflow_id not in wf:
            preset = preset_by_id()[workflow_id]
            wf[workflow_id] = {
                "id": workflow_id,
                "title": preset.title,
                "description": preset.description,
                "current_step": 0,
                "status": "idle",          # idle | running | completed | failed
                "steps": [
                    {"tool_id": tid, "status": "pending", "job_id": None, "exit_code": None}
                    for tid in preset.steps
                ],
                "started_at": None,
                "updated_at": ISO(),
                "last_job_id": None,
            }
            self._save_state()
        return wf[workflow_id]

    def get_workflow(self, workflow_id: str) -> dict:
        if workflow_id not in preset_by_id():
            raise KeyError(workflow_id)
        return self._workflow_state(workflow_id)

    def list_workflows(self) -> List[dict]:
        return [self.get_workflow(p.id) for p in PRESETS]

    def reset_workflow(self, workflow_id: str) -> dict:
        wf = self.state.setdefault("workflows", {})
        wf.pop(workflow_id, None)
        self._save_state()
        return self.get_workflow(workflow_id)

    def run_workflow_step(self, workflow_id: str) -> dict:
        preset = preset_by_id()[workflow_id]
        wstate = self._workflow_state(workflow_id)

        if self.state.get("active_job_id"):
            active = self._read_job(self.state["active_job_id"])
            if active and active.status == "running":
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
            workflow_id=workflow_id,
            workflow_step=idx,
        )
        step["job_id"] = rec.id
        wstate["last_job_id"] = rec.id
        self._save_state()
        return wstate

    def run_workflow_auto(self, workflow_id: str) -> None:
        """Background thread: run all pending steps sequentially."""
        def worker():
            wstate = self.get_workflow(workflow_id)
            while wstate["current_step"] < len(wstate["steps"]):
                if self.state.get("active_job_id"):
                    time.sleep(0.5)
                    continue
                try:
                    wstate = self.run_workflow_step(workflow_id)
                except RuntimeError:
                    time.sleep(1)
                    continue
                jid = wstate.get("last_job_id")
                while True:
                    rec = self._read_job(jid) if jid else None
                    if rec and rec.status in ("completed", "failed", "cancelled"):
                        break
                    time.sleep(0.5)
                wstate = self.get_workflow(workflow_id)
                if wstate["steps"][wstate["current_step"] - 1]["status"] == "failed":
                    break
            self.get_workflow(workflow_id)

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
        if rec.exit_code == 0:
            wf["current_step"] = idx + 1
            if wf["current_step"] >= len(wf["steps"]):
                wf["status"] = "completed"
            else:
                wf["status"] = "idle"
        else:
            wf["status"] = "failed"
        self._save_state()


# Module-level singleton for the server process
_ORCH: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    global _ORCH
    if _ORCH is None:
        _ORCH = Orchestrator()
    return _ORCH
