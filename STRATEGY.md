# AgentProfile Strategy

## The honest truth

AgentProfile is a 3-day-old, 169-line prototype with no README, no CLI, no PyPI package, no documentation, and no users. It competes in a space with:

- **Agent Format** (Snap-backed, v1.0, JSON Schema, multi-language SDKs, CLI, governance model, conformance program)
- **Agent Definition Language** (Ironstead Group, enterprise governance, patent-pending, IETF roadmap)
- **A2A Agent Cards** (Google, v1.0, de facto standard for inter-agent communication)
- **Oracle Agent Spec** (Oracle Labs, published at ACM CAIS 2026, PyAgentSpec SDK)
- **Open Agent Spec** (Prime Vector, v1.5, CLI runner, behavioral contracts)
- **SKILL.md** (Anthropic, 18K GitHub stars, same PROFILE.md pattern)

AgentProfile does not outperform any of these on any dimension. That's not a fixable problem — it's a structural one.

---

## The hard question

> **"Should this product exist?"**

The honest answer: **not as a competing standard.** The format-definition space is consolidating around Agent Format (general-purpose, Snap-backed) and ADL (enterprise governance, IETF-track). A third format from a single developer with no institutional backing will not gain adoption.

The PROFILE.md format alignment with SKILL.md is real, but SKILL.md itself is a skill format, not an agent format, and it already has 18K stars and Anthropic behind it. Adding "PROFILE.md for agents" to that ecosystem doesn't create a new standard — it creates confusion.

---

## Two options

### Option A: Kill it

Delete the repo. Put the 12-field schema into HybridDB or CoreMem as a metadata helper. The ground truth about "what is this agent" can be a Python dict or a YAML file in the agent's data directory — it doesn't need its own package, its own format, and its own branding.

**Time saved:** 0. You're done.
**Loss:** A few hours of work. That's it.

### Option B: Pivot to a bridge library

Don't compete on the format. Compete on **interoperability.** Build a Python library that converts between all the major formats:

```python
from agentprofile import convert

# Load any format, convert to any format
profile = convert.load("agent.agf.yaml")        # Agent Format
profile = convert.load("profile.json")            # ADL
profile = convert.load("PROFILE.md")              # Our format
profile = convert.load(".well-known/agent-card.json")  # A2A

# Convert between them
convert.to_agf(profile)    # -> .agf.yaml
convert.to_adl(profile)    # -> agent.adl.json
convert.to_a2a(profile)    # -> A2A Agent Card JSON
convert.to_profile_md(profile)  # -> PROFILE.md
```

This is actually useful because:
- No single standard will win — Agent Format for execution, ADL for governance, A2A for communication
- Anyone building agent infrastructure needs to handle multiple formats
- A Python native library with clean Pydantic models and bidirectional conversion saves real engineering time

**What this needs to win:**

1. Rename the package to something that signals "bridge" — `agent-spec-bridge`, `agent-format-convert`, something that says "I translate between formats" not "I am another format"
2. Ship bidirectional converters for at least Agent Format and A2A Agent Cards (these are the two most likely to matter)
3. Publish on PyPI with real documentation
4. Position as "the `jsonpickle` / `pandoc` for agent specs" — not trying to be a standard, just a utility

**Time to MVP:** 2-3 weeks for Agent Format and A2A converters.
**Risk:** This is a utility library, not a product. Hard to build a company or community around it.

---

## What I would do

If the goal is to ship products that matter for the Open Assistants stack:

**Kill AgentProfile as an independent product.** Move the schema into HybridDB as a helper class or into CoreMem as a metadata model. An agent's identity data (name, model, tools, system prompt) is a few fields — it belongs alongside the agent's data, not in its own package.

This frees time to ship the things that actually differentiate the stack:
- HybridDB MCP server + schema inference
- ConnectKit's agent-native meta-tools
- EA as the consumption layer

Those three products have genuine competitive moats. AgentProfile does not.

---

## If you keep it as a bridge library

| Priority | What | Why | Effort |
|----------|------|-----|--------|
| P0 | Rename to signal bridge, not format | "agent-spec-bridge" or similar | 10 min |
| P0 | Agent Format bidirectional converter | The most important standard | 1 week |
| P0 | A2A Agent Card bidirectional converter | Second most important | 1 week |
| P1 | ADL converter | Enterprise users | 1 week |
| P1 | CLI tool for format conversion | "agp convert file.yaml --to agf" | 1 week |
| P1 | PyPI publish + README | Without this, nobody uses it | 1 day |
| P2 | MCP server that serves agent specs | Agents discover profiles via MCP | 1 week |
| P3 | Open Agent Spec converter | Niche but growing | 1 week |

---

## Summary

| Option | Effort | Impact | Verdict |
|--------|--------|--------|---------|
| Kill it | 0 | Frees time for more important work | ✅ Smart |
| Keep as competing format | 2-3 weeks of polish | Zero adoption against Snap/Google/Oracle | ❌ Waste |
| Pivot to bridge library | 3-4 weeks | Genuinely useful utility, small but real impact | ⚠️ Plausible |

**Recommendation:** Kill it as an independent product. Move the schema into HybridDB or CoreMem as a metadata helper. Don't spend cycles building in a space where Snap, Google, Oracle, and Anthropic are already entrenched.
