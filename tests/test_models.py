"""Tests for AgentProfile Pydantic model."""

import pytest
from agentprofile.models import AgentProfile


def test_minimal_valid_profile():
    profile = AgentProfile(
        name="researcher",
        description="Research agent",
        model="openai:gpt-4o",
        tools=["web_search"],
        system_prompt="You are a researcher.",
    )
    assert profile.name == "researcher"
    assert profile.version == 1
    assert profile.skills == []
    assert profile.tags == []
    assert profile.provider_options == {}
    assert profile.handoff_instructions is None


def test_full_profile():
    profile = AgentProfile(
        name="coder",
        description="Coding agent",
        model="anthropic:claude-sonnet-4-20250514",
        tools=["files_read", "files_write", "shell_execute"],
        system_prompt="You are a coder.",
        skills=["file-management"],
        tags=["coding", "production"],
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        provider_options={"anthropic": {"thinking": {"type": "enabled", "budget_tokens": 4000}}},
        handoff_instructions="Coder has finished the task.",
    )
    assert "anthropic" in profile.provider_options


def test_name_rejects_special_chars():
    with pytest.raises(ValueError):
        AgentProfile(
            name="bad name",
            description="x",
            model="openai:gpt-4o",
            tools=[],
            system_prompt="x",
        )


def test_name_rejects_too_long():
    with pytest.raises(ValueError):
        AgentProfile(
            name="a" * 65,
            description="x",
            model="openai:gpt-4o",
            tools=[],
            system_prompt="x",
        )


def test_version_rejects_unknown():
    with pytest.raises(ValueError):
        AgentProfile(
            version=2,
            name="test",
            description="x",
            model="openai:gpt-4o",
            tools=[],
            system_prompt="x",
        )


def test_extra_fields_ignored():
    profile = AgentProfile(
        name="test",
        description="x",
        model="openai:gpt-4o",
        tools=[],
        system_prompt="x",
        unknown_field="should be ignored",
    )
    assert not hasattr(profile, "unknown_field")
