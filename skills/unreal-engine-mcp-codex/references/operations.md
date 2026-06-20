# Operations and Troubleshooting

Read this when Unreal MCP is unavailable, toolsets are missing, calls hang, or endpoint/config behavior is unclear.

## Unreal Console Commands

Run from the Unreal Editor console.

| Command | Purpose |
|---|---|
| `ModelContextProtocol.StartServer [port]` | Start the MCP server, optionally overriding the port. |
| `ModelContextProtocol.StopServer` | Stop the server and close sessions. |
| `ModelContextProtocol.RefreshTools` | Re-poll registered tool providers after enabling plugins or reloading toolsets. |
| `ModelContextProtocol.GenerateClientConfig <client>` | Write client config for `ClaudeCode`, `Cursor`, `VSCode`, `Gemini`, `Codex`, or `All`. |

## Settings

Per-user editor settings section:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
ServerPortNumber=8000
ServerUrlPath=/mcp
bEnableToolSearch=True
```

Tool-search mode is the default and preferred mode. In that mode `tools/list` returns only the discovery/dispatch meta-tools rather than every toolset tool.

## Symptom Matrix

| Symptom | Likely cause | Action |
|---|---|---|
| No `unreal-mcp` server in Codex | Codex config missing, project config not trusted, or Codex was not restarted | Run `codex mcp list`, inspect `.codex/config.toml`, consider user-level config, reconnect Codex. |
| Endpoint not reachable | Editor not running, plugin disabled, server not started, or wrong port | Launch editor, enable plugin, run `ModelContextProtocol.StartServer`, check Output Log. |
| Port bind failure | Another local service owns the port | Start with another port, update `ServerPortNumber`, regenerate/merge Codex config. |
| Only meta-tools are visible | Normal tool-search mode | Use `list_toolsets`, `describe_toolset`, `call_tool`. Do not expect every domain tool in the native tool list. |
| Expected domain toolset is missing | Plugin disabled or registry cache stale | Enable the related UE plugin if required, restart if needed, run `ModelContextProtocol.RefreshTools`. |
| Tool call hangs | Editor is compiling, loading, in modal UI, or receiving overlapping calls | Wait, avoid parallel calls, check compilation/PIE state, restart server if needed. |
| Blueprint/material/widget operation returns odd data | PIE/editor mode mismatch or compile failed | Stop PIE, inspect returned status/logs, compile again only after identifying the failing path. |
| New C++ tool does not appear | Reflection schema did not reload | Restart editor after adding reflected declarations. |

## Local Probe

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\skills\unreal-engine-mcp-codex\scripts\check_unreal_mcp.ps1 -Path . -Port 8000 -UrlPath /mcp
```

Use `-SkipHttp` if the editor is not running and you only need project/config inspection.

Cross-platform or CI:

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\check_unreal_mcp.py --path . --port 8000 --url-path /mcp
```

Use `--skip-http` when only project/config inspection is required.

## Headless Runner Scripts

Use these scripts when the task has a command-line path. They write logs and JSON summaries under `Saved/AgentRuns` and avoid opening the full editor UI.

### Automation Tests

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\run_unreal_automation.py `
  --project . `
  --editor-cmd "C:\Path\To\UnrealEditor-Cmd.exe" `
  --tests Project
```

Use `--no-null-rhi` only when the test needs rendering. Add extra Unreal flags with repeated `--extra-arg`.

### Python Validation Commandlet

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\run_unreal_python.py `
  --project . `
  --editor-cmd "C:\Path\To\UnrealEditor-Cmd.exe" `
  --script .\Scripts\validate_content.py
```

### Build

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\build_unreal.py `
  --project . `
  --engine-root "C:\Program Files\Epic Games\UE_5.8" `
  --target MyProjectEditor `
  --configuration Development
```

### Cook Smoke

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\cook_unreal.py `
  --project . `
  --engine-root "C:\Program Files\Epic Games\UE_5.8" `
  --platform Win64
```

Do not launch the full editor only to run build, validation, automation, or cook steps. Use live MCP only after a command-line step proves the project is in a sane state or when the task needs editor state.

## Debugging

- Check Unreal Output Log for `LogModelContextProtocol`.
- Increase log verbosity from the console when needed:

```text
Log LogModelContextProtocol Verbose
```

- Use the official MCP Inspector for protocol-level debugging:

```text
npx @modelcontextprotocol/inspector
```

Point it at:

```text
http://127.0.0.1:8000/mcp
```

Use Streamable HTTP transport.
