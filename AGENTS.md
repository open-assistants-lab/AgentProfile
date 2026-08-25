# AGENTS.md

Guidance for coding agents working in this repository.

## What this is

**agentprofile** is a small PyPI package (`pypi.org/project/agentprofile`) providing a portable agent definition format: a `PROFILE.md` file (YAML frontmatter + Markdown body) parsed into a validated Pydantic model. The body of the file doubles as the agent's system prompt, following the SKILL.md convention.

Current state: library only — no CLI, no format converters. Version lives in two places (keep in sync): `pyproject.toml` and `agentprofile/__init__.py::__version__`. Latest published release: 0.2.1.

PyPI metadata lives in `pyproject.toml`: `readme = "README.md"` renders the README on pypi.org; `license`, keywords, classifiers, and `[project.urls]` are all set — keep them current when the format evolves.

See `STRATEGY.md` for product-direction context (it predates the PyPI release; its "no PyPI package / no README" claims are outdated).

## Layout

```
agentprofile/
  __init__.py    # public exports: AgentProfile, load_profile, loads_profile, dumps_profile
  models.py      # pydantic.AgentProfile model + validation (~49 lines)
  parser.py      # frontmatter split, companion-file loading, serialize (~113 lines)
tests/
  test_models.py
  test_parser.py
STRATEGY.md     # product strategy doc (historical)
LICENSE         # MIT
```

## Commands

```bash
uv sync                # set up .venv (deps + dev group)
uv run pytest          # run tests (pytest via dev dependency-group)
uv run pytest -k name  # filter tests
```

No linter/formatter config exists yet; match existing style (stdlib + pydantic idioms, module-level private helpers prefixed `_`, docstrings on all public functions).

## Invariants — do not break

These behaviors are load-bearing and covered by tests:

1. **Body → system_prompt fallback.** If the file has a Markdown body and frontmatter does not contain `system_prompt`, the body becomes `system_prompt`. A frontmatter `system_prompt` key overrides the body.
2. **Name validation.** `name` must match `^[a-zA-Z0-9_-]+$`, length 1–64. `version` must be ≥ 1.
3. **Lenient extras.** Model uses `extra="ignore"` — unknown frontmatter keys must be dropped silently, never raise.
4. **Serialization exclusions.** `dumps_profile()` excludes `system_prompt` (rendered as body), `provider_options` / `output_schema_def` (loaded, not stored), pointer fields `provider` / `output_schema`, plus nulls and defaults. Changing this changes every user's diff surface.
5. **Companion files are optional.** Missing `provider` / `output_schema` files resolve to `{}` / `None`, not errors. `loads_profile()` only resolves companions when `base_dir` is provided.

## Gotchas

- `dumps_profile(loads_profile(md))` is **not** byte-identical to arbitrary input: defaults, unknown keys, and explicit pointer lines are normalized away. Don't "fix" tests asserting this normalization.
- `_parse_frontmatter` treats a file with no leading/closing `---` as pure body (empty metadata). Edge cases: unclosed delimiter, empty frontmatter (`yaml.safe_load` returns `None` → `{}`).
- Requires Python `>=3.11,<3.14`; uses PEP 604 unions (`str | None`) at runtime under `from __future__ import annotations`.
- Dependencies are pinned loose ranges: `pydantic>=2,<3`, `pyyaml>=6,<7`. Don't add dependencies without strong justification — the value proposition is being tiny.

## Release checklist

1. Bump version in **both** `pyproject.toml` and `agentprofile/__init__.py`
2. Update README if the format/API changed (it renders directly on PyPI)
3. `uv run pytest` green
4. `rm -rf dist && uv build` → artifacts in `dist/`
5. Upload: `uv publish --token "$PYPI_TOKEN"` — the token is in `.env` as `PYPI_TOKEN=` (never commit `.env`; keep it in `.gitignore`)
6. Tag the release in git

PyPI cannot reuse a version number — always bump before re-uploading.
