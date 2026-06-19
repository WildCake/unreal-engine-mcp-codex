# Codex Setup for Official Unreal MCP

Read this when a project is not yet wired to Codex through Unreal Engine 5.8+ `ModelContextProtocol`.

## Goal

Set up three things:

1. Enable the Unreal plugin `ModelContextProtocol`.
2. Start the editor MCP server consistently.
3. Configure Codex to connect to the streamable HTTP endpoint.

## 1. Confirm the Project Root

Walk upward from the current directory until you find:

- `*.uproject` for installed/launcher engine projects.
- `GenerateProjectFiles.bat`, `GenerateProjectFiles.sh`, or `GenerateProjectFiles.command` for engine source roots.

Do not use a bare `Engine` directory as the only root signal.

On Windows, run this skill's probe when uncertain:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\skills\unreal-engine-mcp-codex\scripts\check_unreal_mcp.ps1 -Path .
```

## 2. Enable `ModelContextProtocol`

Preferred path: ask the user to enable `Unreal MCP` in Edit > Plugins and restart the editor.

When editing the `.uproject` directly, confirm the exact `.uproject` path first, then ensure the `Plugins` array includes:

```json
{
  "Name": "ModelContextProtocol",
  "Enabled": true
}
```

If the plugin entry exists with `Enabled` false, flip only that value. Do not rewrite unrelated project metadata.

## 3. Start the MCP Server

Manual start from the Unreal Editor console:

```text
ModelContextProtocol.StartServer
```

Optional port override:

```text
ModelContextProtocol.StartServer 8000
```

Persistent auto-start lives in the per-user editor settings file under the project:

```text
<Project>/Saved/Config/<Platform>Editor/EditorPerProjectUserSettings.ini
```

Add or update:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
ServerPortNumber=8000
ServerUrlPath=/mcp
```

The default endpoint is:

```text
http://127.0.0.1:8000/mcp
```

Keep it loopback-only unless the user explicitly accepts the security risk.

## 4. Generate or Merge Codex Config

Preferred from the running editor:

```text
ModelContextProtocol.GenerateClientConfig Codex
```

Use `All` only when the user wants configs for multiple clients:

```text
ModelContextProtocol.GenerateClientConfig All
```

Codex config is TOML. The UE writer may refuse to overwrite an existing `.codex/config.toml`; if so, merge manually.

Project-scoped Codex config:

```toml
[mcp_servers.unreal-mcp]
url = "http://127.0.0.1:8000/mcp"
startup_timeout_sec = 10
tool_timeout_sec = 120
enabled = true
```

Equivalent CLI registration:

```powershell
codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp
```

Use project-local `.codex/config.toml` only for trusted projects. Use user-level `~/.codex/config.toml` if the local Codex surface does not load project MCP config reliably.

## 5. Verify

After Unreal Editor is running:

1. Check Output Log for `LogModelContextProtocol` startup/bind messages.
2. Restart or reconnect Codex.
3. In Codex, inspect active MCP servers with `/mcp` or `codex mcp list`.
4. Confirm Unreal exposes either:
   - Tool-search meta-tools: `list_toolsets`, `describe_toolset`, `call_tool`.
   - Or eagerly advertised Unreal tool schemas if tool-search mode is off.
5. Ask a read-only smoke question first, such as current selection or actor listing.

## First Safe Prompt

Use a read-only prompt before mutating content:

```text
Use $unreal-engine-mcp-codex to connect to Unreal MCP and list the available toolsets. Do not modify assets.
```
