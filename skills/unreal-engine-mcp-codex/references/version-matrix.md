# Version and Schema Drift

Unreal MCP is experimental in Unreal Engine 5.8. Treat engine patch changes and MCP schema changes as operational risk, especially before live-editor mutations.

## Tested Matrix

| Component | Expected value | Notes |
|---|---|---|
| Unreal Engine | 5.8+ | Use the official `ModelContextProtocol` plugin bundled with UE 5.8 or newer. |
| Transport | Streamable HTTP | Default endpoint is `http://127.0.0.1:8000/mcp`. |
| Tool discovery | Tool-search mode | Prefer `list_toolsets`, `describe_toolset`, and `call_tool`. |
| Codex config | TOML | Project example is `.codex/config.toml.example`; live config may be user-level or project-level. |

## Read-Only Probe Workflow

1. Read the engine version and project root.
2. Verify whether `ModelContextProtocol` is enabled in the `.uproject`.
3. Probe the local MCP endpoint.
4. Use `list_toolsets` when MCP tools are available.
5. Confirm the meta-tools required for tool-search mode exist.
6. Describe one small canonical toolset and normalize the returned schema.
7. Compare the schema with the expected shape for this skill version.
8. Warn on drift. Stop before mutations if the engine major/minor or schema shape is unknown.

## Required Meta-Tools

- `list_toolsets`
- `describe_toolset`
- `call_tool`

If the server exposes all tools eagerly instead of the meta-tools, use the native tool schemas directly, but preserve serialized calls and strict result inspection.

## Drift Policy

- Patch-level engine updates can continue after a read-only probe passes.
- Unknown toolset names require `describe_toolset` before any domain call.
- Missing or incompatible meta-tools mean the agent must not pretend MCP is connected.
- Unknown major schema drift blocks mutations until the user updates the skill, pins the engine, or explicitly approves a one-off manual workflow.

## Probe Helpers

- Windows: `scripts/check_unreal_mcp.ps1`
- Cross-platform/CI: `scripts/check_unreal_mcp.py`

Both helpers are read-only and should return structured JSON so CI and agents can reason about the result without scraping prose.
