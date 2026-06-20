from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def resolve_directory(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    return path if path.is_dir() else path.parent


def test_unreal_root(directory: Path) -> bool:
    if list(directory.glob("*.uproject")):
        return True
    return any((directory / marker).is_file() for marker in ("GenerateProjectFiles.bat", "GenerateProjectFiles.sh", "GenerateProjectFiles.command"))


def find_unreal_root(start: Path) -> Path | None:
    current: Path | None = start
    while current is not None:
        if test_unreal_root(current):
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def plugin_state(project_file: Path) -> dict[str, object]:
    try:
        data = json.loads(project_file.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"path": str(project_file), "present": False, "enabled": False, "error": str(exc)}

    plugin = None
    for item in data.get("Plugins", []):
        if item.get("Name") == "ModelContextProtocol":
            plugin = item
            break
    return {
        "path": str(project_file),
        "present": plugin is not None,
        "enabled": bool(plugin.get("Enabled")) if plugin else False,
    }


def editor_settings(project_root: Path) -> list[dict[str, object]]:
    settings_root = project_root / "Saved" / "Config"
    if not settings_root.exists():
        return []

    states: list[dict[str, object]] = []
    for file_path in settings_root.rglob("EditorPerProjectUserSettings.ini"):
        text = file_path.read_text(encoding="utf-8", errors="replace")
        states.append(
            {
                "path": str(file_path),
                "hasModelContextProtocolSection": "[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]" in text,
                "autoStart": "bAutoStartServer=True" in text,
                "toolSearch": "bEnableToolSearch=True" in text,
            }
        )
    return states


def test_endpoint(url: str, timeout_sec: float) -> dict[str, object]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            return {"reachable": True, "statusCode": response.status, "reason": response.reason}
    except urllib.error.HTTPError as exc:
        return {"reachable": True, "statusCode": exc.code, "reason": exc.reason}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Unreal MCP project and endpoint probe.")
    parser.add_argument("--path", default=".", help="Project file or directory to inspect.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--url-path", default="/mcp")
    parser.add_argument("--skip-http", action="store_true")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    start = resolve_directory(args.path)
    root = find_unreal_root(start)
    endpoint_path = args.url_path if args.url_path.startswith("/") else f"/{args.url_path}"
    endpoint = f"http://127.0.0.1:{args.port}{endpoint_path}"

    if root is None:
        print(json.dumps({"startDirectory": str(start), "projectRoot": None, "endpoint": endpoint, "advice": ["No Unreal project root found walking upward from the supplied path."]}, indent=2))
        return 2

    project_files = sorted(root.glob("*.uproject"))
    plugin_states = [plugin_state(path) for path in project_files]
    codex_config = root / ".codex" / "config.toml"
    mcp_json = root / ".mcp.json"
    http_state = None if args.skip_http else test_endpoint(endpoint, args.timeout)

    advice: list[str] = []
    if not project_files:
        advice.append("No .uproject file found at the detected root; this may be an Unreal source tree.")
    if project_files and not any(item.get("enabled") for item in plugin_states):
        advice.append("Enable ModelContextProtocol in the .uproject or through Edit > Plugins.")
    if not codex_config.exists():
        advice.append("No project .codex/config.toml found at the detected root.")
    if http_state and not http_state.get("reachable"):
        advice.append("MCP endpoint was not reachable. Launch Unreal Editor and run ModelContextProtocol.StartServer.")

    print(
        json.dumps(
            {
                "startDirectory": str(start),
                "projectRoot": str(root),
                "projectType": "engine-source-or-monorepo" if (root / "Engine").is_dir() else "game-or-installed-engine-project",
                "uprojectFiles": [str(path) for path in project_files],
                "modelContextProtocol": plugin_states,
                "codexConfig": {"path": str(codex_config), "exists": codex_config.exists()},
                "mcpJson": {"path": str(mcp_json), "exists": mcp_json.exists()},
                "editorSettings": editor_settings(root),
                "endpoint": endpoint,
                "http": http_state,
                "advice": advice,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
