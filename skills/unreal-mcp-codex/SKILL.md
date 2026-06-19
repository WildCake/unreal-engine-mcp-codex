---
name: unreal-mcp-codex
description: "Use this skill for Unreal Engine 5.8+ work through the official Unreal MCP ModelContextProtocol server from Codex. Trigger when the user wants Codex to connect to, inspect, or mutate a live Unreal Editor project; configure UE MCP for Codex; troubleshoot missing Unreal MCP tools; spawn, move, duplicate, inspect, or delete actors; create or edit Blueprints, Widgets, Materials, Niagara, Sequencer, Control Rig, State Tree, Behavior Tree, GAS, meshes, assets, levels, or automation tests; run Live Coding through the editor; author new ToolsetRegistry toolsets; or create Unreal Agent Skills. Treat UE signals as triggers even without the word Unreal: .uproject, Content Browser, Outliner, PlayerStart, UCLASS, UPROPERTY, UFUNCTION, UObject, Slate, UHT, BP_, WBP_, M_, MI_, NS_, CR_, SK_, SM_, ABP_. Skip for Unity, Godot, non-UE blueprint usage, or conceptual Unreal docs questions that do not need project/editor action."
---

# Unreal MCP Codex

Use the official Unreal Engine 5.8+ `ModelContextProtocol` plugin as the primary bridge between Codex and a live Unreal Editor. Prefer the built-in UE MCP server over older community bridge plugins unless the user explicitly asks for a different server.

## Operating Contract

1. Confirm the task is about a real Unreal project or live editor state. If the task is only conceptual, answer normally and do not force MCP setup.
2. If an Unreal MCP server is already available in this Codex session, use it. If `tool_search` is available, search for `unreal mcp`, `list_toolsets`, `describe_toolset`, or `call_tool` before assuming it is missing.
3. Use UE MCP tool-search mode by default. Discover with `list_toolsets`, inspect the relevant schema with `describe_toolset`, then dispatch through `call_tool`.
4. Serialize every live-editor MCP call. Unreal executes tool calls on the game thread; parallel calls can hang, collide, or corrupt editor state.
5. Save before risky edits and save after successful edits. Treat multi-asset, Blueprint, compile, and content-browser operations as destructive until proven otherwise.
6. Read every MCP result. Some editor operations report failure in returned status fields instead of transport errors.
7. If the MCP meta-tools are unavailable, do not pretend to be connected. Follow `references/setup-codex.md` or ask the user to launch Unreal Editor and start `ModelContextProtocol`.

## Workflow Router

- First-time Codex connection, `.uproject` plugin enablement, auto-start, or TOML config: read `references/setup-codex.md`.
- Live editor changes or inspection through MCP: read `references/live-editor-workflow.md`.
- Missing tools, stale registry, port collision, hangs, PIE problems, or connection failures: read `references/operations.md`.
- Authoring or extending a UE MCP toolset: read `references/toolset-authoring.md`.
- Creating or editing Unreal Agent Skills inside a UE project or plugin: read `references/unreal-agent-skills.md`.
- Bulk edits, untrusted machines, `execute_tool_script`, approvals, or remote exposure questions: read `references/security.md`.
- Attribution, upstream provenance, and source links: read `references/upstream.md`.

## Project Discovery

Find the Unreal project root before editing config or advising launch paths:

- A game project root normally contains one or more `.uproject` files.
- An engine source tree root normally contains `GenerateProjectFiles.bat`, `.sh`, or `.command`.
- Do not treat a bare `Engine` directory as a reliable root marker; source trees contain nested `Engine` module paths.
- For installed/launcher engine projects, generated MCP config belongs next to the `.uproject`.
- For source builds with an `Engine/` directory at the workspace root, generated MCP config can belong at the workspace root, not beside an individual `.uproject`.

Use `scripts/check_unreal_mcp.ps1` on Windows when you need a deterministic probe of project markers, `.uproject` plugin state, Codex config files, per-user editor settings, and the local MCP endpoint.

## Live MCP Call Pattern

When callable Unreal MCP tools exist:

1. Call `list_toolsets` unless the required toolset is obvious.
2. Call `describe_toolset` for the likely toolset before invoking any domain tool.
3. Call `call_tool` with `toolset_name`, `tool_name`, and an `arguments` object that matches the schema exactly.
4. Inspect the result for explicit success, failure, warnings, generated asset paths, compile status, or log excerpts.
5. Stop on ambiguous failure. Do not stack speculative fixes into the editor.

If the server exposes all tools eagerly instead of tool-search meta-tools, use the advertised schemas directly, but still serialize calls and verify every result.

## Built-In Project Skills

Unreal projects can register Agent Skills inside the editor. At the start of unfamiliar project work, check for project skills through `AgentSkillToolset`:

1. Use `call_tool` on `AgentSkillToolset.ListSkills`.
2. If a skill description matches the user's task, load it with `AgentSkillToolset.GetSkills`.
3. Follow project skill instructions over this generic skill when they conflict.

## Codex-Specific Notes

- Codex MCP config is TOML, not Claude `.mcp.json`.
- Prefer the UE console command `ModelContextProtocol.GenerateClientConfig Codex` when the editor is running.
- If Codex config already exists, the UE writer may refuse to overwrite it. Merge the Unreal entry manually instead of deleting unrelated config.
- Codex can also add the streamable HTTP server with `codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp`.
- Restart or reconnect Codex after changing MCP configuration so the server tools are exposed in the session.

## Hard Stops

Stop and ask for editor/project action when:

- Unreal Editor is not running and the task requires live editor state.
- `ModelContextProtocol` is not enabled and you cannot safely edit the `.uproject`.
- C++ or shader compilation is in progress and no compile/wait tool is available.
- Play-in-Editor is active and the requested editor-only operation behaves inconsistently.
- The user asks to expose the MCP server beyond loopback without an explicit security decision.

## Source Posture

This skill is adapted for Codex from Epic Games' public Unreal Engine skills for Claude Code and the official UE 5.8 Unreal MCP documentation. Keep changes aligned with official Epic and OpenAI docs when behavior changes.
