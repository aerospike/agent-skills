# Published Aerospike skill

This directory holds the **published** Aerospike agent skill — one file compiled from the three authoring folders under [`skills/`](../skills/). CI fails any pull request whose compiled output is stale, so this always matches the source skills on `main`.

| File | Purpose |
|------|---------|
| [`aerospike/SKILL.md`](aerospike/SKILL.md) | **Download this** — getting-started, application development, and data-modeling rules in one file, with frontmatter registries can validate |

## Quick install

**With the [`skills` CLI](https://skills.sh):**

```bash
npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike
```

**Raw file URL (use `main` or a release tag):**

```
https://raw.githubusercontent.com/aerospike/agent-skills/main/compiled-skills/aerospike/SKILL.md
```

1. Download [`aerospike/SKILL.md`](aerospike/SKILL.md) (or use the raw URL above).
2. Add it to your agent's **always-on context** (project rules, system prompt, knowledge base, or repo instructions), or drop the `aerospike/` folder into your agent's skills directory.
3. See [`AGENTS.md`](../AGENTS.md) for a short overview.

## By tool

| Tool | What to do |
|------|------------|
| **Claude Code** | `npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike -a claude-code`, which installs to `.claude/skills/aerospike/`. Or add the file to project instructions. |
| **Cursor** | `npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike -a cursor`, which installs to `.agents/skills/aerospike/` (globally, `~/.cursor/skills/`). Or copy the file into a project rule such as `.cursor/rules/aerospike.mdc`. |
| **Gemini CLI** | `npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike -a gemini-cli`, which installs to `.agents/skills/aerospike/` (globally, `~/.gemini/skills/`). |
| **GitHub Copilot** | This repo's [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) already points at the compiled skill. |
| **ChatGPT / other chats** | Upload `aerospike/SKILL.md` to a project knowledge set, or paste the raw URL when working on Aerospike. |

The three folders under [`skills/`](../skills/) are the authoring source for this file. They are not published or installed separately — edit there, then recompile. See [CONTRIBUTING.md](../CONTRIBUTING.md).

For more install options, see the [repository README](../README.md#using-with-ai-assistants).
