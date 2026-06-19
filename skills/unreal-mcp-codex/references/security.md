# Security and Recovery

Read this before bulk edits, script execution, low-approval sessions, or non-loopback MCP exposure.

## Trust Boundary

The official Unreal MCP server is intended for local use. Loopback reduces exposure, but it is not an authentication boundary between processes on the same machine. Treat any connected agent as editor-privileged.

Do not expose the server outside localhost unless the user explicitly requests it after understanding the risk.

## Recovery Point

Before multi-asset or bulk editor work:

- Save the project.
- Prefer a clean VCS state, checkpoint commit, or shelved changes.
- Identify which assets/levels may be touched.
- Keep the first operation read-only when possible.

After success:

- Save changed assets.
- Report changed paths.
- Tell the user if an editor restart is required.

## Privileged Tools

Any tool that runs editor-side Python, changes assets, compiles C++, mutates Blueprints, or moves/deletes content can have broad effects.

Use the narrowest tool that owns the operation:

- Actor/level tool for actor transforms.
- Asset tool for save/find/move/duplicate.
- Blueprint tool for Blueprint graph work.
- Material tool for material graph or instance work.
- Automation test tool for tests.

Only use programmatic script execution for batched work that is too awkward or fragile as individual calls.

## Approval Modes

If Codex or another agent is running without approval prompts, reduce blast radius:

- Ask for narrow tasks.
- Avoid broad content queries followed by mutation.
- Do not run destructive filesystem commands through editor-side script execution.
- Prefer sandbox projects for experiments.

## Remote and Shared Machines

Avoid running Unreal MCP on:

- Shared workstations.
- Machines with untrusted local users.
- Exposed development VMs.
- Ports forwarded to other hosts.

If remote access is explicitly required, document the chosen bind address, port, auth/proxy posture, and why loopback is insufficient.
