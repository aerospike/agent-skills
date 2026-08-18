# Published Aerospike skills

This directory holds the **published** Aerospike agent rules — one file you can add to any AI assistant. Content is built automatically from [`skills/`](../skills/) when changes merge to `init`.

| File | Purpose |
|------|---------|
| [`SKILLS.md`](SKILLS.md) | **Download this** — getting-started, application development, and data-modeling rules in one file |

## Quick install

**Raw file URL (use `init` or a release tag):**

```
https://raw.githubusercontent.com/aerospike/agent-skills/init/compiled-skills/SKILLS.md
```

1. Download [`SKILLS.md`](SKILLS.md) (or use the raw URL above).
2. Add it to your agent's **always-on context** (project rules, system prompt, knowledge base, or repo instructions).
3. See [`AGENTS.md`](../AGENTS.md) for a short overview.

## By tool

| Tool | What to do |
|------|------------|
| **Cursor** | Copy `compiled-skills/SKILLS.md` into a project rule (e.g. `.cursor/rules/aerospike.mdc`) or reference the raw URL in a rule. |
| **GitHub Copilot** | This repo's [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) already points at `SKILLS.md`. |
| **Claude Code / similar** | Add `compiled-skills/SKILLS.md` to project instructions, or start from [`CLAUDE.md`](../CLAUDE.md). |
| **ChatGPT / other chats** | Upload `SKILLS.md` to a project knowledge set, or paste the raw URL when working on Aerospike. |

For more install options, see the [repository README](../README.md#using-with-ai-assistants).
