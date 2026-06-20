from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


def as_path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def find_uproject(start: str | os.PathLike[str]) -> Path:
    path = as_path(start)
    if path.is_file() and path.suffix.lower() == ".uproject":
        return path

    directory = path if path.is_dir() else path.parent
    current: Path | None = directory
    while current is not None:
        projects = sorted(current.glob("*.uproject"))
        if len(projects) == 1:
            return projects[0].resolve()
        if len(projects) > 1:
            raise RuntimeError(f"Multiple .uproject files found in {current}; pass --project explicitly.")
        if current.parent == current:
            break
        current = current.parent

    raise RuntimeError(f"No .uproject found walking upward from {directory}.")


def unique_run_dir(project: Path, kind: str, run_id: str | None = None) -> Path:
    safe_run_id = run_id or f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    root = project.parent / "Saved" / "AgentRuns" / f"{kind}-{safe_run_id}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def resolve_engine_root(engine_root: str | None = None) -> Path:
    value = engine_root or os.environ.get("UE_ENGINE_ROOT")
    if not value:
        raise RuntimeError("Pass --engine-root or set UE_ENGINE_ROOT.")

    root = as_path(value)
    if not (root / "Engine").exists() and (root / "Build").exists():
        root = root.parent
    if not (root / "Engine").is_dir():
        raise RuntimeError(f"Engine root does not contain Engine/: {root}")
    return root


def resolve_editor_cmd(editor_cmd: str | None = None, engine_root: str | None = None) -> Path:
    value = editor_cmd or os.environ.get("UE_EDITOR_CMD")
    if value:
        path = as_path(value)
        if not path.is_file():
            raise RuntimeError(f"UnrealEditor-Cmd not found: {path}")
        return path

    root = resolve_engine_root(engine_root)
    candidates = [
        root / "Engine" / "Binaries" / "Win64" / "UnrealEditor-Cmd.exe",
        root / "Engine" / "Binaries" / "Mac" / "UnrealEditor-Cmd",
        root / "Engine" / "Binaries" / "Linux" / "UnrealEditor-Cmd",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise RuntimeError("UnrealEditor-Cmd not found. Pass --editor-cmd or set UE_EDITOR_CMD.")


def resolve_engine_batch(engine_root: str | None, relative_parts: Sequence[str]) -> Path:
    root = resolve_engine_root(engine_root)
    path = root.joinpath(*relative_parts)
    if not path.is_file():
        raise RuntimeError(f"Required Unreal script not found: {path}")
    return path.resolve()


def windows_batch_command(batch_file: Path, args: Sequence[str]) -> list[str]:
    if os.name == "nt":
        return ["cmd.exe", "/d", "/c", str(batch_file), *args]
    return [str(batch_file), *args]


def process_creation_flags() -> int:
    if os.name != "nt":
        return 0
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def preexec_fn():
    if os.name == "nt":
        return None
    return os.setsid


def terminate_process_tree(process: subprocess.Popen[object]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        time.sleep(2)
        if process.poll() is None:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError:
        return


def run_logged(command: Sequence[str], log_path: Path, timeout_sec: int, cwd: Path | None = None) -> dict[str, object]:
    started = time.monotonic()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd) if cwd else None,
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            shell=False,
            creationflags=process_creation_flags(),
            preexec_fn=preexec_fn(),
            text=True,
        )
        timed_out = False
        try:
            exit_code = process.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_process_tree(process)
            exit_code = process.poll()
            if exit_code is None:
                exit_code = -9
            log.write(f"\nTimed out after {timeout_sec} seconds.\n")

    return {
        "command": list(command),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_sec": round(time.monotonic() - started, 3),
        "log": str(log_path),
    }


def print_json(data: dict[str, object], exit_code: int) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))
    raise SystemExit(exit_code)


def fail(message: str, exit_code: int = 2) -> None:
    print_json({"success": False, "error": message}, exit_code)


def extend_args(base: list[str], extras: Iterable[str] | None) -> list[str]:
    if extras:
        base.extend(extras)
    return base
