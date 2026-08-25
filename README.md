# AgentProfile

**Portable agent profile definition — schema and parser.**

AgentProfile defines a single `PROFILE.md` file that captures everything needed to instantiate an AI agent: identity metadata, model, tools, skills, system prompt, runtime limits, and pointers to companion config files. The format follows the [SKILL.md](https://agentskills.io) convention — YAML frontmatter for metadata, Markdown body for the system prompt.

## Installation

```bash
pip install agentprofile
```

Requires Python ≥ 3.11, < 3.14.

## Quick start

Create a `PROFILE.md`:

```markdown
---
name: research-assistant
description: Web research agent that summarizes findings with citations
model: gpt-4o-mini
tools:
  - web_search
tags:
  - research
---

You are a research assistant. Always cite sources with URLs.
Prefer primary sources. Be concise.
```

Load it:

```python
from agentprofile import load_profile

profile = load_profile("PROFILE.md")

profile.name            # "research-assistant"
profile.model           # "gpt-4o-mini"
profile.tools           # ["web_search"]
profile.system_prompt   # "You are a research assistant. Always cite sources..."
```

Round-trip back to `PROFILE.md`:

```python
from agentprofile import dumps_profile

md_text = dumps_profile(profile)
```

Or parse from a string (no file I/O):

```python
from agentprofile import loads_profile

profile = loads_profile(md_text)
```

## Format

A `PROFILE.md` has two parts:

1. **YAML frontmatter** (between `---` delimiters) — structured metadata
2. **Markdown body** — becomes the agent's `system_prompt` (unless overridden by a `system_prompt` key in frontmatter)

A file without frontmatter is treated entirely as the system prompt.

### Frontmatter fields

| Field | Type | Default | Description |
|---|---|---|---|
| `version` | int | `1` | Profile schema version |
| `name` | str | *required* | Agent name, 1–64 chars, `[a-zA-Z0-9_-]` only |
| `description` | str | `""` | Short human-readable description |
| `model` | str | `""` | Model identifier (e.g. `gpt-4o-mini`) |
| `tools` | list[str] | `[]` | Tool names available to the agent |
| `skills` | list[str] | `[]` | Skill references |
| `tags` | list[str] | `[]` | Free-form tags |
| `handoff_instructions` | str \| null | `null` | Instructions when handing off to another agent |
| `system_prompt` | str | *(body)* | System prompt; defaults to Markdown body |

### Runtime limits (harness-specific, optional)

| Field | Type | Default | Description |
|---|---|---|---|
| `max_llm_calls` | int | `50` | Maximum LLM invocations per run |
| `cost_limit_usd` | float | `1.0` | Spend cap per run |
| `timeout_seconds` | int | `300` | Wall-clock timeout per run |

### Companion files

Frontmatter can point to JSON files in the same directory as the profile; they are auto-loaded when the profile is loaded from disk:

| Pointer | Loads into | Purpose |
|---|---|---|
| `provider: provider.json` | `profile.provider_options` | Provider/model configuration |
| `output_schema: output-schema.json` | `profile.output_schema_def` | Structured output JSON Schema |

Companion contents are kept out of frontmatter serialization (`exclude=True`), so round-tripping a profile never leaks them into the `.md`.

```python
profile = load_profile("agents/research/PROFILE.md")
profile.provider_options   # dict from provider.json
profile.output_schema_def  # dict from output-schema.json
```

When using `loads_profile()` on raw text, pass `base_dir=` to enable companion loading.

## Behavior notes

- **Validation:** `name` must match `^[a-zA-Z0-9_-]+$` (1–64 chars); `version` must be ≥ 1.
- **Lenient parsing:** unknown frontmatter keys are ignored (`extra="ignore"`).
- **Serialization:** `dumps_profile()` omits defaults, nulls, `system_prompt` (moved to the body), and companion-file fields. Pointers (`provider`, `output_schema`) are also omitted since they reference sibling files.

## API

| Function | Description |
|---|---|
| `load_profile(path)` | Parse a `PROFILE.md` from disk, auto-loading companion files |
| `loads_profile(text, base_dir=None)` | Parse from string; optional `base_dir` for companions |
| `dumps_profile(profile)` | Serialize an `AgentProfile` back to `PROFILE.md` text |
| `AgentProfile` | Pydantic model — see field tables above |

## Development

```bash
uv sync            # install deps + dev group
uv run pytest      # run tests
```

## License

MIT — see [LICENSE](LICENSE).
