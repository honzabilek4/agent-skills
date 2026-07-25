---
name: harness-scaffold
description: Initialize new repos with Harness Engineering principles — the 5 subsystems, Loop Engineering, Maker/Checker, and Ratchet patterns that make any project agent-ready, regardless of tech stack. Use this skill whenever creating a new project repo, bootstrapping a codebase for autonomous agents, setting up CI/CD guardrails, or applying the Repo as System of Record pattern.
version: 2.0.0
---

# Harness Scaffold — Initialize Agent-Ready Repositories

When starting any new project that AI agents will work on, apply the Harness Engineering principles from [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/). These principles are technology-agnostic — they work for Python, Rust, TypeScript, Go, or any stack.

## The Core Premise

**Model capability ≠ execution reliability.** A capable AI model fails when its environment (the "harness") doesn't tell it what's expected, how to verify work, or where things stand. The harness is everything *outside* the model's weights. Your job is to build it.

## The 5 Subsystems of a Harness

Every agent-ready project needs these five things. They are not files — they are *capabilities* the repo must provide:

| Subsystem | What it means | How the agent experiences it |
|---|---|---|
| **Instruction** | Explicit rules, constraints, conventions | "I know what to do and what NOT to do" |
| **Tools** | Ability to act (CLI, git, file access) | "I can run commands, read/write files, commit" |
| **Environment** | Reproducible setup (deps, config) | "I can get running from a cold clone" |
| **State** | Cross-session memory | "I know what was done before me and what's next" |
| **Feedback / Verification** | Executable proof of correctness | "I know whether I actually succeeded" |

When scaffolding a new project, ask: **does the repo provide each of these five?**

## The Repo is the System of Record

An AI agent starts every session with amnesia. If a rule, convention, or decision isn't written down in the repository, **it does not exist to the agent.** Implicit conventions, Slack messages, Jira tickets, and your mental model are invisible.

**The test:** A brand-new agent session (fresh context, no prior chat) must be able to answer these questions by reading the repo alone:
1. What is this project?
2. How is it organized?
3. How do I run it?
4. How do I verify it?
5. What was just done, and what's next?

If it can't answer any of these, the harness has a gap.

## Scaffolding by Project Type

Not every project needs the full machinery. Match the harness to the project:

| Project type | What to scaffold |
|---|---|
| **Multi-agent codebase** (production, > 20 files, multiple contributors) | Full harness: entry doc, progress tracking, feature queue, decision log, architecture constraints |
| **Single-person tool** (CLI, dashboard, < 20 files) | Light harness: entry doc + progress tracking only |
| **Research / experiments** (hypothesis-driven, data pipeline) | Research harness: entry doc + research log, no feature queue |
| **Throwaway spike** | Nothing beyond a README that says what it does |

## The Entry Document

Whatever you call it (`AGENTS.md`, `README.md`, `CLAUDE.md`), the project must have ONE file that answers those five questions. It should include:

- **Project description** — one paragraph on what and why
- **Directory map** — what lives where, in one sentence per directory
- **Setup & run commands** — the exact commands to go from cold clone to running
- **Verification command** — how to prove the project is working correctly
- **Rules and constraints** — things the agent must and must not do in this project

## Progress Tracking (State Subsystem)

The agent needs to know where things stand. The mechanism depends on project scale:

- **Markdown file** (`PROGRESS.md`) — simplest, works for any project. Tracks last commit, what was completed, what's in progress, known issues, and ordered next steps. Update before every handoff.
- **Task board** (Kanban, GitHub Issues) — for projects with multiple parallel workstreams. Each task needs an executable verification criterion.
- **Database / structured log** — for automated pipelines and ratchet loops.

**The rule:** before ending a session, the agent MUST update state. "I'll update it later" means it never happens.

## Feature Queue (for codebase projects)

When the project has multiple features to build, maintain a machine-readable queue. Every item must have:
- **What** to build (behavior, not implementation)
- **How to verify** it's done (an executable command, not "looks good")
- **Current state** (not started → active → done | blocked)

**Hard rule:** Only ONE feature active at a time. No scope creep. Finish and verify before starting the next.

## Decision Log

Record *why* architectural choices were made. Agents don't retain intermediate reasoning across sessions — without a log, they will redundantly re-evaluate or reverse past decisions. One line per decision: date, what was chosen, why, and what alternatives were considered.

## Loop Engineering: Moving Outside the Loop

Once a single agent run is reliable, the next step is making *continuous* runs autonomous:

- **Inside the loop:** You review work, decide the next step, type a prompt. You are the engine.
- **Outside the loop:** You design a system that triggers the agent, gives it the next task, verifies its output, and saves state. Your job shifts from "prompting" to "designing."

This means: cron jobs, webhook triggers, orchestrator scripts, automated verification gates.

## Maker / Checker Separation

A generative model is its own output's best defense attorney. If the same agent that wrote the code also verifies it, it will almost always pass itself.

For critical work, split into two roles:
- **Maker:** Builds, writes, implements.
- **Checker:** Independently verifies against the criteria. Rejects if evidence is missing.

This can be a separate agent call, a different model, or an automated script — the key is independence.

## The Ratchet Loop

State only moves forward. The pattern:
1. Agent attempts a task.
2. Independent verification runs.
3. If it passes → state is saved, advance to next.
4. If it fails → state is rolled back, failure is logged, retry or escalate.

The system ratchets upward in quality without human intervention on every cycle.

## Scaffolding Procedure (When Starting a New Project)

1. **Determine the level** — full, light, or research harness.
2. **Create the entry document** — answer the 5 questions. The first draft can be rough.
3. **Choose a state mechanism** — `PROGRESS.md` is the simplest default.
4. **Set up environment** — whatever `setup && check` means in this stack. Make it a single command.
5. **Define the verification command** — what proves the project works? Make it executable.
6. **Write down the rules** — what must and must not happen. Be explicit.
7. **Run the fresh-session test** — can a brand-new agent clone, setup, verify, and understand next steps from the repo alone?
8. **Commit** — the harness itself should be the first commit.

## Harness Health Check (For Existing Repos)

1. Can a fresh agent run the setup command and the verification command from a cold clone?
2. Does a single entry document answer the five questions?
3. Is the progress/state file current, or is it stale?
4. Are there debug prints, temp files, commented-out dead code? Remove them.
5. Does the verification command actually prove correctness, or just check syntax?
6. Is the decision log up to date, or are there undocumented architectural choices?
