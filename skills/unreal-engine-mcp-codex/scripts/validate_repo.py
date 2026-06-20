from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None


SKILL_NAME = "unreal-engine-mcp-codex"
REQUIRED_SKILL_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/triggers.md",
    "references/version-matrix.md",
    "references/setup-codex.md",
    "references/live-editor-workflow.md",
    "references/operations.md",
    "references/toolset-authoring.md",
    "references/unreal-agent-skills.md",
    "references/security.md",
    "references/upstream.md",
    "scripts/check_unreal_mcp.ps1",
    "scripts/check_unreal_mcp.py",
    "scripts/run_unreal_automation.py",
    "scripts/run_unreal_python.py",
    "scripts/build_unreal.py",
    "scripts/cook_unreal.py",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def parse_frontmatter(skill_md: Path, errors: list[str]) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    require(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter.", errors)
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        errors.append("SKILL.md frontmatter is not closed.")
        return {}
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_skill(skill_dir: Path, errors: list[str]) -> None:
    for relative in REQUIRED_SKILL_FILES:
        require((skill_dir / relative).is_file(), f"Missing skill file: {relative}", errors)

    frontmatter = parse_frontmatter(skill_dir / "SKILL.md", errors)
    description = frontmatter.get("description", "")
    require(frontmatter.get("name") == SKILL_NAME, "SKILL.md frontmatter name mismatch.", errors)
    require(80 <= len(description) <= 300, f"SKILL.md description length should be concise, got {len(description)}.", errors)
    require("BP_" not in description and "UCLASS" not in description, "Trigger aliases must stay out of frontmatter description.", errors)

    openai_yaml = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
    require("dependencies:" in openai_yaml, "agents/openai.yaml must declare dependencies.", errors)
    require('value: "unreal-mcp"' in openai_yaml, "agents/openai.yaml must depend on unreal-mcp.", errors)
    require("$unreal-engine-mcp-codex" in openai_yaml, "agents/openai.yaml default_prompt must mention the skill name.", errors)


def validate_plugin(root: Path, errors: list[str]) -> None:
    manifest_path = root / ".codex-plugin" / "plugin.json"
    require(manifest_path.is_file(), "Missing .codex-plugin/plugin.json.", errors)
    if not manifest_path.is_file():
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("name") == SKILL_NAME, "plugin.json name mismatch.", errors)
    require(re.match(r"^\d+\.\d+\.\d+$", manifest.get("version", "")) is not None, "plugin.json version must be strict semver.", errors)
    require(manifest.get("skills") == "./skills/", "plugin.json skills path must be ./skills/.", errors)
    require(manifest.get("author", {}).get("name") == "WildCake", "plugin.json author.name mismatch.", errors)
    interface = manifest.get("interface", {})
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"):
        require(key in interface, f"plugin.json interface.{key} is required.", errors)


def validate_config(root: Path, errors: list[str]) -> None:
    path = root / ".codex" / "config.toml.example"
    require(path.is_file(), "Missing .codex/config.toml.example.", errors)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    require("[mcp_servers.unreal-mcp]" in text, "config example must include unreal-mcp server.", errors)
    require("default_tools_approval_mode = \"prompt\"" in text, "config example must keep MCP mutation approval prompted.", errors)
    if tomllib is not None and path.is_file():
        tomllib.loads(text)


def validate_python(skill_dir: Path, errors: list[str]) -> None:
    for script in sorted((skill_dir / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Python compile failed for {script.name}: {exc.msg}")


def main() -> int:
    root = repo_root()
    skill_dir = root / "skills" / SKILL_NAME
    errors: list[str] = []
    validate_skill(skill_dir, errors)
    validate_plugin(root, errors)
    validate_config(root, errors)
    validate_python(skill_dir, errors)

    result = {
        "success": not errors,
        "repo": str(root),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
