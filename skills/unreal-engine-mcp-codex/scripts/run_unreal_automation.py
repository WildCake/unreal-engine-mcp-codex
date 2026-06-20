from __future__ import annotations

import argparse
from pathlib import Path

from _unreal_runner_common import fail, find_uproject, print_json, resolve_editor_cmd, run_logged, unique_run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Unreal Automation Tests through UnrealEditor-Cmd without opening editor windows.")
    parser.add_argument("--project", "-p", default=".", help=".uproject file or directory.")
    parser.add_argument("--editor-cmd", help="Path to UnrealEditor-Cmd.exe. Defaults to UE_EDITOR_CMD or --engine-root discovery.")
    parser.add_argument("--engine-root", help="Unreal Engine root used to discover UnrealEditor-Cmd.")
    parser.add_argument("--tests", default="Project", help="Automation test filter, for example Rookwall or Project.")
    parser.add_argument("--automation-command", default="Automation RunTests", help="Automation console command prefix.")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--run-id")
    parser.add_argument("--no-null-rhi", action="store_true", help="Disable -NullRHI when rendering is required.")
    parser.add_argument("--extra-arg", action="append", default=[])
    args = parser.parse_args()

    try:
        project = find_uproject(args.project)
        editor_cmd = resolve_editor_cmd(args.editor_cmd, args.engine_root)
        run_dir = unique_run_dir(project, "automation", args.run_id)
        log_path = run_dir / "automation.log"
        report_path = run_dir / "report"
        command = [
            str(editor_cmd),
            str(project),
            "-Unattended",
            "-NoSplash",
            "-NoSound",
            "-stdout",
            "-FullStdOutLogOutput",
            f"-ExecCmds={args.automation_command} {args.tests};Quit",
            f"-TestExit=Automation Test Queue Empty",
            f"-ReportExportPath={report_path}",
            f"-log={log_path}",
        ]
        if not args.no_null_rhi:
            command.insert(6, "-NullRHI")
        command.extend(args.extra_arg)
        result = run_logged(command, log_path, args.timeout, cwd=project.parent)
    except Exception as exc:
        fail(str(exc))

    success = not result["timed_out"] and result["exit_code"] == 0
    print_json({"success": success, "project": str(project), "run_dir": str(run_dir), "report": str(report_path), **result}, 0 if success else 1)


if __name__ == "__main__":
    raise SystemExit(main())
