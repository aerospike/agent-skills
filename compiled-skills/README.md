# Published Aerospike skills

This directory holds the **published** Aerospike agent rules — one file you can add to any AI assistant. Content is built from [`skills/`](../skills/); CI fails any pull request whose compiled output is stale, so this file always matches the source skills on `main`.

| File | Purpose |
|------|---------|
| [`SKILLS.md`](SKILLS.md) | **Download this** — getting-started, application development, and data-modeling rules in one file |

## Quick install

**Raw file URL (use `main` or a release tag):**

```
https://raw.githubusercontent.com/aerospike/agent-skills/main/compiled-skills/SKILLS.md
```

1. Download [`SKILLS.md`](SKILLS.md) (or use the raw URL above).
2. Add it to your agent's **always-on context** (project rules, system prompt, knowledge base, or repo instructions).
3. See [`AGENTS.md`](../AGENTS.md) for a short overview.

**Prefer the full skill folders?** With the [`skills` CLI](https://skills.sh):

```bash
npx skills add aerospike/agent-skills
```

## By tool

| Tool | What to do |
|------|------------|
| **Cursor** | Copy `compiled-skills/SKILLS.md` into a project rule (e.g. `.cursor/rules/aerospike.mdc`) or reference the raw URL in a rule. |
| **GitHub Copilot** | This repo's [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) already points at `SKILLS.md`. |
| **Claude Code / similar** | Add `compiled-skills/SKILLS.md` to project instructions, or start from [`CLAUDE.md`](../CLAUDE.md). |
| **ChatGPT / other chats** | Upload `SKILLS.md` to a project knowledge set, or paste the raw URL when working on Aerospike. |

For more install options, see the [repository README](../README.md#using-with-ai-assistants).
