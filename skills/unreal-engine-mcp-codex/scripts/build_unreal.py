from __future__ import annotations

import argparse

from _unreal_runner_common import fail, find_uproject, print_json, resolve_engine_batch, run_logged, unique_run_dir, windows_batch_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Unreal project target through UBT without opening editor windows.")
    parser.add_argument("--project", "-p", default=".", help=".uproject file or directory.")
    parser.add_argument("--engine-root", help="Unreal Engine root. Defaults to UE_ENGINE_ROOT.")
    parser.add_argument("--target", help="Target name. Defaults to the .uproject stem.")
    parser.add_argument("--platform", default="Win64")
    parser.add_argument("--configuration", default="Development")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--run-id")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--extra-arg", action="append", default=[])
    args = parser.parse_args()

    try:
        project = find_uproject(args.project)
        target = args.target or project.stem
        build_script = resolve_engine_batch(args.engine_root, ("Engine", "Build", "BatchFiles", "Build.bat"))
        run_dir = unique_run_dir(project, "build", args.run_id)
        log_path = run_dir / "build.log"
        ubt_args = [
            target,
            args.platform,
            args.configuration,
            f"-Project={project}",
            "-WaitMutex",
            "-NoHotReloadFromIDE",
        ]
        if args.clean:
            ubt_args.append("-Clean")
        ubt_args.extend(args.extra_arg)
        command = windows_batch_command(build_script, ubt_args)
        result = run_logged(command, log_path, args.timeout, cwd=project.parent)
    except Exception as exc:
        fail(str(exc))

    success = not result["timed_out"] and result["exit_code"] == 0
    print_json({"success": success, "project": str(project), "target": target, "run_dir": str(run_dir), **result}, 0 if success else 1)


if __name__ == "__main__":
    raise SystemExit(main())
