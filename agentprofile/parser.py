"""YAML parsing for AgentProfile files."""

from __future__ import annotations

from pathlib import Path

import yaml

from agentprofile.models import AgentProfile


def load_profile(path: str | Path) -> AgentProfile:
    """Load an AgentProfile from a profile.yaml file."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    return AgentProfile(**data)


def loads_profile(yaml_str: str) -> AgentProfile:
    """Load an AgentProfile from a YAML string."""
    data = yaml.safe_load(yaml_str) or {}
    return AgentProfile(**data)


def dumps_profile(profile: AgentProfile) -> str:
    """Serialize an AgentProfile to YAML string."""
    return yaml.dump(
        profile.model_dump(exclude_none=True, exclude_defaults=True),
        default_flow_style=False,
        sort_keys=False,
    )
