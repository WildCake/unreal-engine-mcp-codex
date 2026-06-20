# Unreal Engine MCP for Codex

Codex skill for driving Unreal Engine 5.8+ through Epic's official `ModelContextProtocol` Unreal MCP server.

This repository packages a Codex plugin and skill that helps an agent:

- Configure Unreal Engine 5.8+ `ModelContextProtocol` for Codex.
- Connect Codex to the local streamable HTTP MCP endpoint.
- Inspect and mutate a live Unreal Editor project safely.
- Use Unreal MCP tool-search mode correctly: `list_toolsets`, `describe_toolset`, `call_tool`.
- Troubleshoot missing toolsets, stale registry state, port conflicts, and editor hangs.
- Author new Unreal `ToolsetRegistry` toolsets.
- Create and review Unreal Agent Skills inside a UE project or plugin.

## Install

### Plugin install

Install this repository as a Codex plugin when your Codex surface supports local or GitHub plugin sources. The plugin manifest lives at:

```text
.codex-plugin/plugin.json
```

The plugin declares the `unreal-mcp` dependency in `skills/unreal-engine-mcp-codex/agents/openai.yaml` and includes a project-scoped config example at `.codex/config.toml.example`.

### Raw skill install

For surfaces that only support raw skills, copy `skills/unreal-engine-mcp-codex` into your Codex skills directory:

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

## Headless Runners

The skill prefers unattended command-line execution for build, test, validation, and cook work that does not need live editor state:

```powershell
python .\skills\unreal-engine-mcp-codex\scripts\check_unreal_mcp.py --path .
python .\skills\unreal-engine-mcp-codex\scripts\run_unreal_automation.py --project . --editor-cmd "C:\Path\To\UnrealEditor-Cmd.exe" --tests Project
python .\skills\unreal-engine-mcp-codex\scripts\run_unreal_python.py --project . --editor-cmd "C:\Path\To\UnrealEditor-Cmd.exe" --script .\Scripts\validate_content.py
python .\skills\unreal-engine-mcp-codex\scripts\build_unreal.py --project . --engine-root "C:\Program Files\Epic Games\UE_5.8"
python .\skills\unreal-engine-mcp-codex\scripts\cook_unreal.py --project . --engine-root "C:\Program Files\Epic Games\UE_5.8"
```

Every runner writes logs and a JSON summary. Project runners place output under `Saved/AgentRuns/<kind>-<run-id>` and use hidden/background process flags on Windows.

## Included Files

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `.codex/config.toml.example`: Project-scoped Codex MCP config example.
- `SKILL.md`: Core trigger and runtime workflow.
- `agents/openai.yaml`: UI metadata and `unreal-mcp` dependency.
- `references/triggers.md`: Broad Unreal aliases kept out of the frontmatter description.
- `references/setup-codex.md`: UE MCP and Codex TOML setup.
- `references/live-editor-workflow.md`: Safe live editor operation pattern.
- `references/operations.md`: Console commands and troubleshooting.
- `references/version-matrix.md`: UE MCP version and schema drift policy.
- `references/toolset-authoring.md`: ToolsetRegistry authoring guide.
- `references/unreal-agent-skills.md`: Unreal Agent Skill authoring guide.
- `references/security.md`: Recovery and security posture.
- `scripts/check_unreal_mcp.ps1`: Windows probe for project/config/endpoint state.
- `scripts/check_unreal_mcp.py`: Cross-platform/CI JSON probe.
- `scripts/run_unreal_automation.py`: Headless Automation Tests runner.
- `scripts/run_unreal_python.py`: Headless Unreal Python commandlet runner.
- `scripts/build_unreal.py`: Background UBT build helper.
- `scripts/cook_unreal.py`: Background BuildCookRun smoke cook helper.

## Upstream

Adapted for Codex from:

- Epic Games' Unreal Engine Skills for Claude Code plugin: https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin
- Unreal MCP documentation: https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor
- OpenAI Codex MCP documentation: https://developers.openai.com/codex/mcp

This repository is not affiliated with Epic Games or OpenAI. Epic's original MIT notice is preserved in `skills/unreal-engine-mcp-codex/LICENSE-EPIC-MIT.txt`.

## License

MIT. See `LICENSE`.
