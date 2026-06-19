# Toolset Authoring

Read this when adding or extending Unreal Engine tools exposed through `ToolsetRegistry` and Unreal MCP.

## Before Writing Code

Answer these in order:

1. Does an existing tool already do it? If the editor is running, inspect toolsets first. If not, search source for existing Toolsets and read nearby headers or Python modules.
2. Is the requested operation really domain-specific, or should it belong in a broader owner such as asset, object, level, actor, or material tooling?
3. Does the domain already have a toolset? Extend that owner instead of creating a parallel toolset.
4. Is this project-specific or plugin-worthy? Keep project-only behavior in the project/plugin that owns it.
5. Can Python do it cleanly? Prefer Python for iteration when the Unreal Python stubs expose the needed API. Use C++ when reflection, editor internals, performance, or missing Python coverage requires it.

If neither Python nor C++ exposes the needed engine capability cleanly, stop and say so. Do not add fragile workaround layers.

## API Design Rules

- One tool should have one responsibility.
- Use real typed parameters and return values. Do not pass JSON strings for structured data.
- Return data on success; raise errors on failure.
- Keep names stable, descriptive, and consistent with neighboring toolsets.
- Reuse generic tools such as object property get/set instead of duplicating them.
- Provide CRUD symmetry when it makes sense.
- Prefer structured result types over prose.
- Document only non-obvious meaning, units, ranges, and empty/null semantics.

## C++ Pattern

- Derive the toolset class from `UToolsetDefinition`.
- Keep one toolset class per header/source pair.
- Expose AI-callable operations as `static` methods with `UFUNCTION(meta = (AICallable))`.
- Omit `AICallable` from private helpers.
- Use reflected `USTRUCT` return types for structured data.
- Register/unregister the toolset in the module lifecycle or match the local plugin pattern.
- Use `UToolCallAsyncResult` subclasses for long-running work such as screenshots or waiting for editor state changes.
- Raise Unreal script errors for invalid input or unmet preconditions.

After adding a new reflected declaration, restart the editor. Live Coding can update bodies, but new UFUNCTION schemas may not appear until restart.

## Python Pattern

- Decorate the class with `@unreal.uclass()`.
- Inherit from `unreal.ToolsetDefinition`.
- Decorate each exposed function with `@toolset_registry.tool_call` and `@staticmethod`.
- Use standard Python type annotations such as `list[str]` and `dict[str, str]`.
- Put private helpers at the end with `_` prefixes and no tool decorator.
- Register the toolset class from the plugin's Python init path.
- Raise Python exceptions for tool failure.

If `Intermediate/PythonStub/unreal.py` is missing, ask the user to enable Python Developer Mode in Unreal Project Settings and restart the editor.

## Testing

Every new tool needs coverage for:

- At least one success path.
- Each error/raise path.
- Serialization shape when the return type is non-trivial.

Preferred live-editor loop:

1. Compile C++ with the Live Coding toolset if C++ changed.
2. Reload the Python package if Python changed.
3. Use `AutomationTestToolset.DiscoverTests`.
4. Use `ListTests` with a narrow filter.
5. Run the exact test path(s).
6. Poll status and retrieve results.

Command-line fallback:

```text
UnrealEditor-Cmd.exe <Project>.uproject -ExecCmds="Automation RunTests <Filter>;quit" -Unattended -NullRHI
```

Use the filter convention already present in the plugin.

## Review Pass

Before handoff, reread the toolset as an API:

- No duplicate behavior already available elsewhere.
- No JSON-in-string parameters.
- No result wrappers used only to smuggle errors.
- No comments that restate signatures.
- Tests cover every precondition failure.
- Tool schemas are visible after `ModelContextProtocol.RefreshTools` or editor restart.
