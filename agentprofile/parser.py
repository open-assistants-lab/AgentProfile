"""PROFILE.md parsing for AgentProfile files.

Parses frontmatter (YAML) + body (Markdown) following the Agentskills.io
SKILL.md convention. Auto-loads companion files (provider.json, output-schema.json)
when referenced by frontmatter pointers.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from agentprofile.models import AgentProfile


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split PROFILE.md into (frontmatter dict, body text).

    Frontmatter is between --- delimiters at the start of the file.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        # No frontmatter — treat whole file as body, metadata is empty
        return {}, text.strip()

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        # No closing --- — treat whole file as body
        return {}, text.strip()

    frontmatter_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:]).strip()

    data = yaml.safe_load(frontmatter_text) or {}
    return data, body


def _load_companion_file(base_dir: Path, filename: str | None) -> dict | None:
    """Load a JSON companion file from the same directory."""
    if not filename:
        return None
    path = base_dir / filename
    if not path.exists():
        return None
    return json.loads(path.read_text())


def load_profile(path: str | Path) -> AgentProfile:
    """Load an AgentProfile from a PROFILE.md file.

    Auto-loads companion files (provider.json, output-schema.json) when
    referenced by frontmatter pointers.
    """
    path = Path(path)
    base_dir = path.parent

    text = path.read_text()
    frontmatter, body = _parse_frontmatter(text)

    # Body becomes system_prompt if not overridden in frontmatter
    if body and "system_prompt" not in frontmatter:
        frontmatter["system_prompt"] = body

    profile = AgentProfile(**frontmatter)

    # Load companion files
    profile.provider_options = _load_companion_file(base_dir, profile.provider) or {}
    output_schema = _load_companion_file(base_dir, profile.output_schema)
    profile.output_schema_def = output_schema

    return profile


def loads_profile(md_text: str, base_dir: str | Path | None = None) -> AgentProfile:
    """Load AgentProfile from PROFILE.md text. Companion files require base_dir."""
    frontmatter, body = _parse_frontmatter(md_text)
    if body and "system_prompt" not in frontmatter:
        frontmatter["system_prompt"] = body

    profile = AgentProfile(**frontmatter)

    if base_dir is not None:
        base = Path(base_dir)
        profile.provider_options = _load_companion_file(base, profile.provider) or {}
        output_schema = _load_companion_file(base, profile.output_schema)
        profile.output_schema_def = output_schema

    return profile


def dumps_profile(profile: AgentProfile) -> str:
    """Serialize an AgentProfile to PROFILE.md format."""
    frontmatter = profile.model_dump(
        exclude={"system_prompt", "provider_options", "output_schema_def"},
        exclude_none=True,
        exclude_defaults=True,
    )

    # Remove fields that are already pointers
    frontmatter.pop("provider", None)
    frontmatter.pop("output_schema", None)

    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

    lines = ["---", yaml_str.strip(), "---", "", profile.system_prompt.strip()]
    return "\n".join(lines) + "\n"
