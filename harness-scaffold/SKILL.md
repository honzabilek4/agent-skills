---
name: harness-scaffold
description: Initialize new repos with Harness Engineering principles. Use whenever creating a new project repo, bootstrapping a codebase for autonomous agents, or setting up CI/CD guardrails. This skill handles repo INFRASTRUCTURE only — process discipline (design, TDD, debugging, code review, plan execution) is delegated to superpowers skills. Scaffold the harness FIRST, before entering the superpowers pipeline.
version: 5.0.0
hermes_category: autonomous-ai-agents
---

# Harness Scaffold — Initialize Agent-Ready Repositories

Apply the Harness Engineering principles from [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/). These principles are technology-agnostic and work for Python, Rust, TypeScript, Go, or any stack.

**Model capability ≠ execution reliability.** When things fail, fix the harness before swapping the model.

A harness is everything outside the model weights. It establishes a closed-loop working system: the agent acts, the environment feeds back results, verification gates completion, and state carries forward between sessions.

## How This Fits with Superpowers

Harness-scaffold and superpowers cover different layers. They do not overlap — one provides infrastructure, the other provides process discipline:

| Layer | Responsibility | Skill |
|---|---|---|
| **Repo infrastructure** | AGENTS.md, PROGRESS.md, feature queues, decision logs, verification commands, Maker/Checker architecture | **harness-scaffold** |
| **Design gate** | Brainstorming, spec writing, user approval before code | `superpowers:brainstorming` |
| **Implementation planning** | Task decomposition, file structure, TDD steps | `superpowers:writing-plans` |
| **TDD workflow** | RED-GREEN-REFACTOR per task | `superpowers:test-driven-development` |
| **Root-cause debugging** | 4-phase systematic debugging before fixing | `superpowers:systematic-debugging` |
| **Code review** | Subagent review, severity classification, fix loops | `superpowers:requesting-code-review` |
| **Task execution** | Subagent-driven or inline plan execution | `superpowers:subagent-driven-development` / `superpowers:executing-plans` |
| **Branch finishing** | Verification, cleanup, PR creation | `superpowers:finishing-a-development-branch` |

**Integration sequence for a new project:**

1. **harness-scaffold** → Create the repo, AGENTS.md, PROGRESS.md, verification command, feature queue. Commit as the FIRST commit.
2. **superpowers:brainstorming** → Explore context, ask questions, present design, get approval, write spec to `docs/superpowers/specs/`.
3. **superpowers:writing-plans** → Decompose spec into implementation tasks with exact file paths and TDD steps. Write to `docs/superpowers/plans/`.
4. **superpowers:subagent-driven-development** (preferred) or **superpowers:executing-plans** → Execute tasks.
5. **superpowers:finishing-a-development-branch** → Final verification, cleanup, PR.

**For an existing repo**, run the harness health check first (see below). If the repo passes, skip to brainstorming. If it fails, fix the harness gaps before starting feature work.

---

## The Five Subsystems

A harness has five subsystems. They are capabilities the repo provides, not files:

| Subsystem | What it means | The agent's experience |
|---|---|---|
| **Instruction** | Explicit rules, constraints, conventions | "I know what to do and what NOT to do" |
| **Tools** | Ability to act (CLI, git, file access) | "I can run commands, read/write files, commit" |
| **Environment** | Reproducible setup from cold clone | "I can get running in one command" |
| **State** | Cross-session memory | "I know what was done before me and what's next" |
| **Feedback / Verification** | Executable proof of correctness | "I know whether I actually succeeded" |

After scaffold, score each 1–5. The lowest-scoring subsystem is your bottleneck.

## Core Principles (Infrastructure-Only)

### 1. The Repo Is the System of Record

An agent has exactly three sources of input — system prompts, file contents, and tool output. If it's not in the repo, it's not real.

**The fresh-session test:** A brand-new agent session (zero prior context) must answer these five questions by reading the repo alone:

1. What is this project?
2. How is it organized?
3. How do I run it?
4. How do I verify it?
5. What was just done, and what's next?

**Progressive disclosure:** The entry document (`AGENTS.md`) is a directory, not an encyclopedia. Keep it 50–200 lines. Reference deeper files; the agent loads them on demand. Signal-to-noise ratio matters more than total coverage.

### 2. State Must Survive Sessions

Context windows are finite. Information produced during a session (why option A over B, which approach was tried and abandoned) is lost unless written down.

**ACID principles for agent state:** Atomic commits, Consistency (verify after every operation), Isolation (one agent per branch), Durability (critical knowledge lives in git-tracked files, not session memory).

**Separate initialization from implementation.** The first agent session on a new project establishes the environment, verifies the baseline, and writes the startup readiness checklist. Only then does feature work begin.

### 3. Scope Must Be Constrained

**Feature lists are harness machinery**, not project management. Every item must have:
- **What** to build — behavior, not implementation
- **How to verify** — an executable command, not "looks good"
- **Status** — `not_started` → `in_progress` → `done` or `blocked`

**Hard rule:** Only ONE feature `in_progress` at a time. The feature list is the scope enforcement mechanism.

### 4. Verification Must Be External (Maker/Checker)

The entity that writes the code cannot be the entity that grades it. Local `task check` is pre-flight; CI running in a clean environment is the independent checker. If CI fails, the work is not done, regardless of what passed locally.

**Definition of Done:** tests pass, lint is clean, state is updated, the work is committed, and the repo is clean. "It looked right" is not verification.

**Only full-pipeline runs count.** Unit tests miss component boundary defects. The verification command must run the end-to-end pipeline.

### 5. Sessions Must End Clean

Entropy growth is the default. Every session introduces changes; without cleanup at exit, technical debt accumulates exponentially.

**Five clean-state conditions** at session end:
1. Build passes
2. All tests pass (including pre-existing ones)
3. Progress recorded in machine-readable artifacts
4. No stale artifacts — no debug logs, temp files, commented-out dead code, TODO markers
5. Standard startup path works

### 6. The Agent Must Drive Itself (Loop Engineering)

Four loop types, increasingly autonomous:

| Type | Trigger | Stop condition |
|---|---|---|
| Turn-based | You type each prompt | Agent thinks it's done |
| Goal-based | You give a goal and walk away | Independent evaluator confirms done |
| Time-based | Scheduled interval | You stop it, or it exits on completion |
| Event-driven | External event (PR, CI failure, new issue) | After handling event or hitting retry limit |

### 7. Runtime Must Be Observable

Two layers, both essential:
- **Runtime observability:** System-level signals — logs, traces, health checks. Answers "what did the system do."
- **Process observability:** Harness decision artifacts — sprint contracts, evaluator rubrics, task traces. Answers "why should this change be accepted."

Build signal collection into the harness, not the agent's prompts.

### 8. The Ratchet Loop

The failure protocol: stop on red, log the failure, fix the root cause, re-verify. Never advance state past a failing check. This is harness-enforced, not agent-discretionary — the verification command gates all progress.

---

## Scaffolding Procedure

1. **Determine the level:**
   - **Multi-agent codebase** (production, > 20 files, multiple contributors) → Full harness: entry doc, progress tracking, feature queue, decision log, architecture constraints
   - **Single-person tool** (CLI, dashboard, < 20 files) → Light harness: entry doc + progress tracking
   - **Research / experiments** → Entry doc + research log, no feature queue
   - **Throwaway spike** → A README that says what it does

2. **Create the entry document** (`AGENTS.md`). 50–200 lines. Must include:
   - Project description (one paragraph), directory map, setup/run commands, verification command, gotchas
   - **Startup Workflow** — exact steps the agent follows at session start: confirm directory, read state files, install deps, review git log, verify baseline passes
   - **Working Rules** — one task at a time, no premature completion claims, scope discipline, prefer repo artifacts over chat summaries
   - **Architecture Constraints** — module boundaries, import rules, what depends on what, firewall rules (for full harness)
   - **Definition of Done** — the checklist: tests pass, lint clean, state updated, committed, repo clean
   - **Maker / Checker** — local verification is pre-flight; CI is the independent checker
   - **Ratchet Loop** — the failure protocol: stop on red, log the failure, fix the root cause, re-verify
   - **End Of Session** — the closing ritual: run full check, update state, record decisions, commit, leave repo clean
   - **Superpowers integration** — include a line stating: "Process discipline (brainstorming, TDD, debugging, code review, plan execution) follows the superpowers skills loaded in your session."

3. **Choose a state mechanism.** `PROGRESS.md` is the default — tracks completed, in-progress, known issues, and ordered next steps. For multi-agent projects, also track last verified commit.

4. **Create a feature queue** (for full harness). Every future feature gets: what (behavior), how to verify (executable command), status. Only ONE `in_progress` at a time.

5. **Set up the environment.** Make setup a single command: `just setup` or equivalent. Use `pyproject.toml` / `package.json` / `Cargo.toml` to lock deps, `.python-version` / `.nvmrc` / `rust-toolchain.toml` for runtime versions.

6. **Define the verification command.** Must prove correctness — not just check syntax. One command that runs the full pipeline (tests, lint, type check).

7. **Write architecture constraints.** For full harness: module boundaries, import direction rules, firewall rules. Prefer "MUST / MUST NOT" language.

8. **Create the decision log.** Every architectural choice gets: date, what was chosen, why, what alternatives were considered. Without this, every new session redundantly re-evaluates past decisions.

9. **Run the fresh-session test.** Spawn a brand-new agent. Give it only the repo. Ask the five questions. Fix the harness and retest until it passes.

10. **Run the ratchet test.** Deliberately break a test. Verify the agent stops on red, logs the failure, and refuses to advance state.

11. **Commit.** The harness itself is the first commit — the foundation everything else builds on.

12. **Hand off to superpowers.** After the harness is committed, invoke `superpowers:brainstorming` to begin the design phase.

---

## Harness Health Check

For existing repos, run these checks:

1. Can a fresh agent run setup and verification from a cold clone?
2. Does the entry document answer the five fresh-session questions?
3. Are all mandatory sections present: Startup Workflow, Working Rules, Architecture Constraints, Definition of Done, Maker/Checker, Ratchet Loop, End Of Session?
4. Is the state file current, or stale?
5. Is the feature queue populated with verification criteria per item, and only one active?
6. Are there debug prints, temp files, commented-out dead code? Remove them.
7. Does the verification command prove correctness, or just check syntax?
8. Is the decision log up to date?
9. Ratchet test: break something, then verify the agent refuses to advance state.
10. Five clean-state conditions at last session end: build green, tests green, progress recorded, no stale artifacts, startup path works?

**If the harness fails any check, fix it before starting feature work.** A broken harness guarantees wasted sessions. Use `superpowers:systematic-debugging` if the failure's root cause isn't obvious.

**Harness rots like code does.** Audit regularly. As model capabilities improve, remove components no longer necessary — a constraint essential today may be overhead in three months.
