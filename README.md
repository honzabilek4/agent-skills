# Agent Skills — Canonical Source

Shared skills repository following the [Agent Skills open standard](https://agentskills.io). One source of truth, consumed by multiple AI coding agents via symlinks.

## Commands

```bash
just              # list all commands
just validate     # check all skills against skill-creator standard
just precommit    # validate + symlink checks (run before committing)
just wire-all     # wire all skills to all agents
just wire <name>  # wire a single skill
just list         # show current wiring state
just eval-list <skill>     # list evals for a skill
just eval-show <skill> <id> # show one eval in detail
just commit "msg" # precommit checks + git add + commit
```

## Format

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```
skill-name/
├── SKILL.md          # Required: name + description in frontmatter, then markdown instructions
├── scripts/          # Optional: executable scripts the agent can run
├── references/       # Optional: reference docs loaded on demand
├── assets/           # Optional: templates, images, etc.
├── agents/           # Optional: subagent instructions (skill-creator convention)
├── eval-viewer/      # Optional: eval viewer assets
└── evals/            # Optional: test prompts (evals.json)
```

## Skills

| Skill | Description | Evals |
|-------|-------------|-------|
| [skill-creator](skill-creator/SKILL.md) | Create, test, and optimize AI agent skills. Use when creating, editing, or benchmarking skills. | — |
| [software-design-principles](software-design-principles/SKILL.md) | Design principles & red flags (Ousterhout's "A Philosophy of Software Design"). Use when writing, reviewing, or refactoring code. | [3 evals](software-design-principles/evals/evals.json) |
| [harness-scaffold](harness-scaffold/SKILL.md) | Initialize agent-ready repos with Harness Engineering principles. Use when bootstrapping a new project or auditing an existing one. | [3 evals](harness-scaffold/evals/evals.json) |

## Validation

Every skill is validated against the skill-creator standard on commit:

```bash
just precommit
```

Runs 10 checks per skill: frontmatter validity, kebab-case naming, pushy descriptions, body length, standard directory structure, symlink integrity, dangling references, and more. See `scripts/validate-all-skills.py`.

## Evals

Each skill can have test prompts in `evals/evals.json`. Evals are **agent-in-the-loop** — the CLI orchestrates, the agent session executes.

### Step by step

**1. Print the eval prompts (dry-run)**

```bash
just eval harness-scaffold
```

This prints each prompt and shows where to save output. Nothing executes yet.

**2. Agent executes each eval**

Copy one of the printed prompts into the agent session and ask it to execute. Two approaches:

*Inline (faster, shares context):*
```
Run eval 1 for harness-scaffold: "I'm starting a new Python CLI tool called
'ship' that deploys Docker containers to a VPS..." Save your analysis to
harness-scaffold-workspace/eval-1/output.md
```

*Subagent (isolated, cleaner):*
```
Load the harness-scaffold skill and run eval 1 via delegate_task. Save the
output to harness-scaffold-workspace/eval-1/output.md
```

The agent does the work, then saves the result to the path shown by step 1.

**3. Generate the report**

```bash
just eval-report harness-scaffold
```

Reads all `output.md` files and produces `harness-scaffold-workspace/RESULTS.md`.

### Concrete example

```bash
# In CLI:
$ just eval harness-scaffold
# Prints:
#   ## Eval 1
#   **Prompt:** I'm starting a new Python CLI tool called 'ship'...
#   **Save output to:** harness-scaffold-workspace/eval-1/output.md

# In the agent session (this chat):
> "Run eval 1 for harness-scaffold: scaffold a Python CLI called ship.
>   Save your analysis to harness-scaffold-workspace/eval-1/output.md"

# Agent scaffolds the project, writes output.md

# Back in CLI:
$ just eval-report harness-scaffold
# → harness-scaffold-workspace/RESULTS.md
```

### Why agent-in-the-loop?

The eval prompts test whether the skill actually changes agent behavior. A plain API call can't replicate the agent's tool access, skill loading, or context injection. The agent session IS the test harness — just like sandbox mode for human QA.

### Available commands

```bash
just eval <skill>              # dry-run: print eval prompts
just eval-one <skill> <id>     # show one eval prompt in detail
just eval-report <skill>       # generate RESULTS.md from completed runs
just eval-list <skill>         # list all evals with previews
just eval-show <skill> <id>    # show one eval's prompt + expected output
```

## Architecture

```
~/Projects/agent-skills/          ← THIS REPO (source of truth)
├── skill-creator/
├── software-design-principles/
├── harness-scaffold/
├── scripts/                      ← repo tooling (validate, wire, evals)
├── AGENTS.md                     ← injected into every agent's context
└── justfile                      ← self-documenting commands

~/.agents/skills/                 ← Agent Skills standard hub (global tier)
├── skill-creator/ → ../../Projects/agent-skills/skill-creator/
├── software-design-principles/ → ../../Projects/agent-skills/software-design-principles/
└── harness-scaffold/ → ../../Projects/agent-skills/harness-scaffold/

~/.hermes/skills/<cat>/<name>/SKILL.md   ← file symlink
~/.claude/skills/<name>/SKILL.md         ← real dir + file symlink
~/.codex/skills/<name>/SKILL.md          ← real dir + file symlink
~/.gemini/skills/<name>/SKILL.md         ← real dir + file symlink
~/.pi/agent/skills/<name>/SKILL.md       ← real dir + file symlink
```

## Adding a New Skill

```bash
# 1. Create the skill directory
mkdir -p ~/Projects/agent-skills/my-skill
cat > ~/Projects/agent-skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does and when to use it — be "pushy" with trigger contexts.
---
# My Skill
...
EOF

# 2. Validate
just validate

# 3. Wire it to all agents
just wire my-skill --hermes-category general

# 4. Add evals (optional)
mkdir my-skill/evals
# Create evals/evals.json with test prompts

# 5. Update this README — add to the Skills table

# 6. Commit
just commit "Add my-skill"
```

Or use `./scripts/wire-skill.sh --all --hermes-category <cat>` to re-wire everything.

See `./scripts/wire-skill.sh --help` for all options (`--list`, `--unwire`, `--dry-run`).

### Agent Discovery Paths Reference

| Agent | Path | Symlink Strategy |
|-------|------|-----------------|
| **Hermes** | `~/.hermes/skills/<cat>/<name>/SKILL.md` | File symlink |
| **Claude Code** | `~/.claude/skills/<name>/SKILL.md` | Real dir + file symlink |
| **Codex** | `~/.codex/skills/<name>/SKILL.md` | Real dir + file symlink |
| **Gemini CLI** | `~/.gemini/skills/<name>/SKILL.md` | Real dir + file symlink |
| **Pi** | `~/.pi/agent/skills/<name>/SKILL.md` | Real dir + file symlink |
| **OpenCode** | `~/.claude/skills/` or `~/.agents/skills/` | Auto-covered |
| **Standard hub** | `~/.agents/skills/<name>/` | Directory symlink |

### Known Limitations

- **Codex CLI**: [Doesn't follow symlinked `.agents/skills/` directories](https://github.com/openai/codex/issues/11314). Workaround: use `~/.codex/skills/` with a real directory + symlinked `SKILL.md` inside.
- **Gemini CLI**: [Doesn't follow symlinked skill directories](https://github.com/google-gemini/gemini-cli/issues/16247). Workaround: use `~/.gemini/skills/` with a real directory + symlinked `SKILL.md` inside.

## Adding a New Consumer Agent

1. Find the agent's skill discovery path (check their docs or `agentskills.io`)
2. Create the appropriate symlink following the pattern above
3. If they have a directory-symlink bug, use the "real dir + file symlink" pattern
4. Add to the table in this README
5. Add the agent to `scripts/wire-skill.sh` AGENTS array
6. Commit

## Why Not Just Copy?

Symlinks mean a single edit propagates instantly to all agents. No sync scripts, no stale copies, no drift.
