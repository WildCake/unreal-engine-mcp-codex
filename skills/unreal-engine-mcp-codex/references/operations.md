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
