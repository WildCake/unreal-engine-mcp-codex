# Unreal Agent Skills

Read this when creating, updating, or reviewing Unreal Agent Skills registered inside a UE project or plugin. These are not Codex skills. They are editor-discoverable instruction bundles loaded through Unreal MCP.

## Purpose

Use Unreal Agent Skills for project-specific or plugin-specific knowledge that the agent cannot discover from tool schemas alone:

- Naming conventions.
- Required content paths.
- Multi-step workflows.
- Local safety rules.
- Canonical validation paths.

Do not put generic Unreal facts into an Agent Skill.

## Before Creating One

1. Use `AgentSkillToolset.ListSkills` to see existing skills.
2. Load likely matches with `AgentSkillToolset.GetSkills`.
3. If an existing skill covers the task, update it instead of creating a duplicate.
4. Choose the storage path:
   - Python class for plugin-owned, version-controlled guidance.
   - UAsset skill for project-specific guidance stored in Content.

## Content Rules

Each skill has:

- Description: one or two sentences that clearly say when it applies.
- Instructions: concise operational guidance.

Good Agent Skills are:

- Novel: they add project knowledge, not generic engine docs.
- Durable: they avoid brittle tool names and implementation details unless necessary.
- Agnostic: they do not mention a specific assistant harness.
- Short: they preserve context for the actual task.

## Python Skill Pattern

Use a Python `unreal.AgentSkill` subclass when the skill belongs to a code plugin.

Key requirements:

- Decorate with the project/plugin's `agent_skill` helper.
- Put skill files in the plugin Python package's `skills/` folder unless local conventions differ.
- Import each skill from that folder's `__init__.py`.
- Ensure the plugin's Unreal Python init imports the skills package.
- Reload the plugin package before verification.

## UAsset Skill Pattern

Use `AgentSkillToolset` when the skill is project content:

1. List existing skills.
2. Create or update the skill in a stable folder such as `/Game/Skills/`.
3. Use PascalCase asset names.
4. Verify by loading it through `GetSkills`.

## Review Checklist

- The description alone lets an agent decide whether to load it.
- The instructions teach something not discoverable from the live tools.
- The content does not duplicate this Codex skill.
- The skill is short enough to be worth loading.
- The final saved asset or Python class is visible through `AgentSkillToolset`.
