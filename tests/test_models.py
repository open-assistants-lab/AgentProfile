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
    assert profile.provider is None
    assert profile.output_schema is None


def test_full_profile():
    profile = AgentProfile(
        name="coder",
        description="Coding agent",
        model="anthropic:claude-sonnet-4-20250514",
        tools=["files_read", "files_write", "shell_execute"],
        system_prompt="You are a coder.",
        skills=["file-management"],
        tags=["coding", "production"],
        handoff_instructions="Coder has finished the task.",
        provider="provider.json",
        output_schema="output-schema.json",
    )
    assert profile.provider == "provider.json"
    assert profile.output_schema == "output-schema.json"


def test_provider_options_excluded_from_dump():
    profile = AgentProfile(
        name="test",
        description="x",
        model="ollama:llama3.2",
        tools=[],
        system_prompt="x",
    )
    profile.provider_options = {"anthropic": {"thinking": {"type": "enabled"}}}
    dumped = profile.model_dump()
    assert "provider_options" not in dumped  # excluded
    assert dumped["name"] == "test"


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


def test_version_accepts_bumped():
    profile = AgentProfile(
        version=2,
        name="test",
        description="x",
        model="openai:gpt-4o",
        tools=[],
        system_prompt="x",
    )
    assert profile.version == 2


def test_version_rejects_zero():
    with pytest.raises(ValueError):
        AgentProfile(
            version=0,
            name="test",
            description="x",
            model="openai:gpt-4o",
            tools=[],
            system_prompt="x",
        )


def test_version_defaults_to_one():
    profile = AgentProfile(
        name="test",
        description="x",
        model="openai:gpt-4o",
        tools=[],
        system_prompt="x",
    )
    assert profile.version == 1


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
