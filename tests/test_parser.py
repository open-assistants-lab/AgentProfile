"""Tests for AgentProfile PROFILE.md parser."""
import json
import tempfile

import pytest
from pathlib import Path

from agentprofile.parser import load_profile, loads_profile, dumps_profile


def test_loads_profile_minimal():
    md_text = """---
name: test-agent
description: A test agent
model: openai:gpt-4o
tools:
  - time_get
---

You are a test agent.
"""
    profile = loads_profile(md_text)
    assert profile.name == "test-agent"
    assert profile.tools == ["time_get"]
    assert profile.system_prompt == "You are a test agent."


def test_load_profile_from_file():
    md_text = """---
name: file-agent
description: Loaded from file
model: ollama:llama3.2
tools:
  - files_read
---

Read files from the filesystem.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md_text)
        f.flush()
        profile = load_profile(f.name)
        Path(f.name).unlink()

    assert profile.name == "file-agent"
    assert profile.model == "ollama:llama3.2"
    assert profile.system_prompt == "Read files from the filesystem."


def test_loads_profile_with_companion_files():
    md_text = """---
name: with-provider
description: Has provider config
model: openai:gpt-4o
tools:
  - time_get
provider: provider.json
output_schema: output-schema.json
---

Do things.
"""
    with tempfile.TemporaryDirectory() as d:
        profile_md = Path(d) / "PROFILE.md"
        profile_md.write_text(md_text)

        provider_json = Path(d) / "provider.json"
        provider_json.write_text(
            json.dumps({"anthropic": {"thinking": {"type": "enabled"}}})
        )

        output_json = Path(d) / "output-schema.json"
        output_json.write_text(
            json.dumps({"type": "object", "properties": {"result": {"type": "string"}}})
        )

        profile = load_profile(str(profile_md))

    assert profile.name == "with-provider"
    assert profile.provider_options == {"anthropic": {"thinking": {"type": "enabled"}}}
    assert profile.output_schema_def == {
        "type": "object",
        "properties": {"result": {"type": "string"}},
    }


def test_dumps_profile_roundtrip():
    md_text = """---
name: roundtrip
description: Roundtrip test
model: openai:gpt-4o
tools:
  - time_get
tags:
  - test
---

You are a test.
"""
    profile = loads_profile(md_text)
    dumped = dumps_profile(profile)
    reloaded = loads_profile(dumped)
    assert reloaded.name == profile.name
    assert reloaded.tools == profile.tools
    assert reloaded.tags == profile.tags
    assert reloaded.system_prompt.strip() == profile.system_prompt.strip()


def test_loads_profile_no_frontmatter():
    """Entire file is body — no frontmatter. Should fail validation."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        loads_profile("You are a helper.")


def test_loads_profile_system_prompt_in_frontmatter_overrides_body():
    """System prompt in frontmatter takes priority over body."""
    md_text = """---
name: explicit
description: Has explicit system_prompt
model: ollama:llama3.2
system_prompt: I am in frontmatter.
---

I am in the body.
"""
    profile = loads_profile(md_text)
    assert profile.system_prompt == "I am in frontmatter."
