# Unreal Engine MCP for Codex

Codex skill for driving Unreal Engine 5.8+ through Epic's official `ModelContextProtocol` Unreal MCP server.

This repository packages a Codex skill that helps an agent:

- Configure Unreal Engine 5.8+ `ModelContextProtocol` for Codex.
- Connect Codex to the local streamable HTTP MCP endpoint.
- Inspect and mutate a live Unreal Editor project safely.
- Use Unreal MCP tool-search mode correctly: `list_toolsets`, `describe_toolset`, `call_tool`.
- Troubleshoot missing toolsets, stale registry state, port conflicts, and editor hangs.
- Author new Unreal `ToolsetRegistry` toolsets.
- Create and review Unreal Agent Skills inside a UE project or plugin.

## Install

Copy `skills/unreal-engine-mcp-codex` into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\unreal-engine-mcp-codex "$env:USERPROFILE\.codex\skills\unreal-engine-mcp-codex"
```

Then start a new Codex session and use:

```text
Use $unreal-engine-mcp-codex to connect this Unreal project to Codex through official UE MCP.
```

## Unreal Setup Summary

In Unreal Editor 5.8+:

1. Enable the `Unreal MCP` / `ModelContextProtocol` plugin.
2. Start the server:

```text
ModelContextProtocol.StartServer
```

3. Generate Codex config:

```text
ModelContextProtocol.GenerateClientConfig Codex
```

Or add the streamable HTTP server manually:

```powershell
codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp
```

The skill contains detailed setup and troubleshooting under `skills/unreal-engine-mcp-codex/references/`.

## Included Files

- `SKILL.md`: Core trigger and runtime workflow.
- `references/setup-codex.md`: UE MCP and Codex TOML setup.
- `references/live-editor-workflow.md`: Safe live editor operation pattern.
- `references/operations.md`: Console commands and troubleshooting.
- `references/toolset-authoring.md`: ToolsetRegistry authoring guide.
- `references/unreal-agent-skills.md`: Unreal Agent Skill authoring guide.
- `references/security.md`: Recovery and security posture.
- `scripts/check_unreal_mcp.ps1`: Windows probe for project/config/endpoint state.

## Upstream

Adapted for Codex from:

- Epic Games' Unreal Engine Skills for Claude Code plugin: https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin
- Unreal MCP documentation: https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor
- OpenAI Codex MCP documentation: https://developers.openai.com/codex/mcp

This repository is not affiliated with Epic Games or OpenAI. Epic's original MIT notice is preserved in `skills/unreal-engine-mcp-codex/LICENSE-EPIC-MIT.txt`.

## License

MIT. See `LICENSE`.
