from __future__ import annotations

import argparse

from _unreal_runner_common import fail, find_uproject, print_json, resolve_engine_batch, run_logged, unique_run_dir, windows_batch_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an Unreal BuildCookRun smoke cook without opening editor windows.")
    parser.add_argument("--project", "-p", default=".", help=".uproject file or directory.")
    parser.add_argument("--engine-root", help="Unreal Engine root. Defaults to UE_ENGINE_ROOT.")
    parser.add_argument("--platform", default="Win64")
    parser.add_argument("--configuration", default="Development")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--run-id")
    parser.add_argument("--archive-dir", help="Archive output directory. Defaults under Saved/AgentRuns.")
    parser.add_argument("--extra-arg", action="append", default=[])
    args = parser.parse_args()

    try:
        project = find_uproject(args.project)
        run_uat = resolve_engine_batch(args.engine_root, ("Engine", "Build", "BatchFiles", "RunUAT.bat"))
        run_dir = unique_run_dir(project, "cook", args.run_id)
        log_path = run_dir / "cook.log"
        archive_dir = args.archive_dir or str(run_dir / "archive")
        uat_args = [
            "BuildCookRun",
            f"-project={project}",
            "-noP4",
            f"-platform={args.platform}",
            f"-clientconfig={args.configuration}",
            "-cook",
            "-stage",
            "-pak",
            "-archive",
            f"-archivedirectory={archive_dir}",
            "-unattended",
            "-utf8output",
        ]
        uat_args.extend(args.extra_arg)
        command = windows_batch_command(run_uat, uat_args)
        result = run_logged(command, log_path, args.timeout, cwd=project.parent)
    except Exception as exc:
        fail(str(exc))

    success = not result["timed_out"] and result["exit_code"] == 0
    print_json({"success": success, "project": str(project), "archive_dir": archive_dir, "run_dir": str(run_dir), **result}, 0 if success else 1)


if __name__ == "__main__":
    raise SystemExit(main())
