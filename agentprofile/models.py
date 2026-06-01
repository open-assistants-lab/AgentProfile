"""Pydantic model for AgentProfile — portable agent definition."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


class AgentProfile(BaseModel):
    """Portable agent definition: frontmatter metadata + body as system_prompt.

    PROFILE.md format aligned with Agentskills.io SKILL.md conventions.
    """

    version: int = Field(default=1, ge=1, le=1)
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    tools: list[str] = Field(default_factory=list)
    system_prompt: str = Field(default="")
    skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    handoff_instructions: str | None = None

    # Pointers to companion files (same directory as PROFILE.md)
    provider: str | None = None
    output_schema: str | None = None

    # Loaded from companion files, not serialized to frontmatter
    provider_options: dict[str, Any] = Field(default_factory=dict, exclude=True)
    output_schema_def: dict[str, Any] | None = Field(default=None, exclude=True)

    model_config = {"extra": "ignore"}

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(f"Invalid name: {v!r}. Must match {_NAME_RE.pattern}")
        return v

    @field_validator("version")
    @classmethod
    def _validate_version(cls, v: int) -> int:
        if v != 1:
            raise ValueError(f"Unsupported version: {v}. Only version 1 is supported.")
        return v
