"""Tests for AgentProfile YAML parser."""

import tempfile
from pathlib import Path

from agentprofile.parser import load_profile, loads_profile, dumps_profile


def test_loads_profile_minimal():
    yaml_str = """
name: test-agent
description: A test agent
model: openai:gpt-4o
tools:
  - time_get
system_prompt: You are a test agent.
"""
    profile = loads_profile(yaml_str)
    assert profile.name == "test-agent"
    assert profile.tools == ["time_get"]


def test_load_profile_from_file():
    yaml_str = """
name: file-agent
description: Loaded from file
model: ollama:llama3.2
tools:
  - files_read
system_prompt: Read files.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_str)
        f.flush()
        profile = load_profile(f.name)
        Path(f.name).unlink()

    assert profile.name == "file-agent"
    assert profile.model == "ollama:llama3.2"


def test_dumps_profile_roundtrip():
    yaml_str = """
name: roundtrip
description: Roundtrip test
model: openai:gpt-4o
tools:
  - time_get
system_prompt: Test.
tags:
  - test
"""
    profile = loads_profile(yaml_str)
    dumped = dumps_profile(profile)
    reloaded = loads_profile(dumped)
    assert reloaded.name == profile.name
    assert reloaded.tools == profile.tools
    assert reloaded.tags == profile.tags
