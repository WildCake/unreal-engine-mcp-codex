# Live Editor Workflow

Read this before using a live Unreal MCP connection to inspect or mutate editor state.

## Default Flow

1. Identify whether the task is read-only, single-object mutation, multi-asset mutation, compile/test, or bulk scripting.
2. For unfamiliar projects, query project Agent Skills through `AgentSkillToolset` and follow relevant project instructions.
3. Discover toolsets with `list_toolsets`.
4. Describe the minimum relevant toolsets with `describe_toolset`.
5. Execute exactly one `call_tool` at a time.
6. Check the result before the next action.
7. Save changed assets through the appropriate asset/save tool, or tell the user what must be saved manually if no save tool is available.

## Read-Only First

Start with read-only operations when the state is unknown:

- List selected actors.
- Inspect current level/world.
- Find assets by path or prefix.
- Inspect a Blueprint, material, widget, sequence, mesh, or component before editing it.
- Check PIE/editor mode before asset operations.

## Mutation Rules

- Prefer the smallest owning toolset. Do not use broad Python execution for simple actor or asset operations.
- Never issue overlapping tool calls.
- Never assume a Blueprint, material, or widget compiled successfully until the returned status confirms it.
- For actor transforms, use structured transform fields exactly as the schema expects.
- For asset paths, preserve Unreal package path conventions such as `/Game/...`.
- For bulk changes, make a recovery point first: save, commit, shelve, duplicate assets, or confirm the user has a clean checkout.

## Compilation

If C++ or Live Coding is relevant:

1. Use the Live Coding toolset when available.
2. Wait for compile completion through the tool result.
3. Read compiler diagnostics from the returned payload.
4. Do not continue with editor mutations after a failed compile.

Adding a new `UFUNCTION` exposed to reflection usually requires an editor restart; Live Coding may update function bodies but not the reflected schema.

## Automation Tests

When running UE automation tests through MCP:

1. Discover tests first.
2. List tests with a narrow filter.
3. Run only the relevant test path(s).
4. Poll status.
5. Retrieve detailed results.

Do not use a broad test suite when a focused editor or toolset test proves the contract.

## Programmatic Scripts

Use script execution only when several tool calls need one atomic or batched editor-side operation. Before script execution:

- Prefer existing toolsets.
- Keep the script narrowly scoped.
- Avoid filesystem deletes or asset moves unless explicitly requested.
- Return structured data, not prose.
- Treat any exception as a stop condition.

## Completion Checklist

Before handing off:

- Changed assets are saved or explicitly called out as unsaved.
- Compile/test operations returned success or known failures are reported.
- Asset paths, actor names, and generated object names are listed.
- The user knows whether the editor must be restarted or Codex must reconnect.
