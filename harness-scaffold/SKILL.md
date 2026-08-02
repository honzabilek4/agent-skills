---
name: harness-scaffold
description: Initialize new repos with Harness Engineering principles — the 5 subsystems, Loop Engineering, Maker/Checker, and Ratchet patterns that make any project agent-ready, regardless of tech stack. Use this skill whenever creating a new project repo, bootstrapping a codebase for autonomous agents, setting up CI/CD guardrails, or applying the Repo as System of Record pattern.
version: 4.0.0
hermes_category: autonomous-ai-agents
---

# Harness Scaffold — Initialize Agent-Ready Repositories

Apply the Harness Engineering principles from [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/). These principles are technology-agnostic and work for Python, Rust, TypeScript, Go, or any stack.

## The Core Premise

**Model capability ≠ execution reliability.** The same model (Opus 4.5) with the same prompt ("build a 2D retro game editor") went from broken features ($9, 20 min) to fully playable ($200, 6 hours) with nothing changed except the harness. When things fail, fix the harness before swapping the model.

A harness is everything outside the model weights. It establishes a closed-loop working system: the agent acts, the environment feeds back results, verification gates completion, and state carries forward between sessions.

---

## The Eight Principles

### 1. The Harness Determines Reliability

**Why:** Agents fail in predictable ways — vague requirements, implicit conventions not written down, incomplete environments, no verification commands, cross-session state loss. Every failure maps to a harness defect. Nine times out of ten, "the model isn't good enough" is a harness problem.

A harness has five subsystems. They are capabilities the repo provides, not files:

| Subsystem | What it means | The agent's experience |
|---|---|---|
| **Instruction** | Explicit rules, constraints, conventions | "I know what to do and what NOT to do" |
| **Tools** | Ability to act (CLI, git, file access) | "I can run commands, read/write files, commit" |
| **Environment** | Reproducible setup from cold clone | "I can get running in one command" |
| **State** | Cross-session memory | "I know what was done before me and what's next" |
| **Feedback / Verification** | Executable proof of correctness | "I know whether I actually succeeded" |

**To apply:** After scaffold, ask: does the repo provide each of these five? Score each 1–5. The lowest-scoring subsystem is your bottleneck.

### 2. The Repo Is the System of Record

**Why:** An agent has exactly three sources of input — system prompts, file contents, and tool output. Your Slack history, Jira tickets, Confluence pages, and that decision you hashed out over coffee don't exist to the agent. If it's not in the repo, it's not real.

**The fresh-session test:** A brand-new agent session (zero prior context) must answer these five questions by reading the repo alone:

1. What is this project?
2. How is it organized?
3. How do I run it?
4. How do I verify it?
5. What was just done, and what's next?

If it can't answer any of these, the harness has a blank spot — and every new session will guess (and burn context, and get it wrong) in that spot.

**Progressive disclosure:** The entry document is a directory, not an encyclopedia. Keep it at 50–200 lines. Reference deeper files; the agent loads them on demand. A 600-line instruction file guarantees "lost in the middle" — critical rules buried at line 300 get ignored. Signal-to-noise ratio matters more than total coverage.

### 3. State Must Survive Sessions

**Why:** Context windows are finite. Even with 1M-token windows, complex tasks exhaust them. When context runs low, agents exhibit "context anxiety" — rushing to finish, skipping verification, choosing simpler solutions. Information produced during a session (why option A over B, which approach was tried and abandoned) is lost unless written down.

**State persistence:** Before every session ends, the agent writes down critical information so the next "shift" can pick up without re-discovering. This is non-negotiable. "I'll update it later" means it never happens.

**Separate initialization from implementation.** The first agent session on a new project should establish the environment, verify the baseline, and write the startup readiness checklist. Only then does feature work begin. Mixing initialization and implementation cuts completion rates — OpenAI's experiments showed 31% higher rates with a dedicated init phase. The time invested in init is recovered within 3–4 sessions.

**Use ACID principles for agent state:** Atomic commits (all or nothing, `git stash` on failure), Consistency (verify after every operation), Isolation (one agent per branch or progress file), Durability (critical knowledge lives in git-tracked files, not session memory).

### 4. Scope Must Be Constrained

**Why:** Agents overreach (creeping into unrelated code) and under-finish (shipping incomplete work). Both stem from the same root: there's no machine-readable boundary around the task.

**Feature lists are harness machinery**, not project management. Every item must have three properties:
- **What** to build — behavior, not implementation
- **How to verify** — an executable command, not "looks good"
- **Status** — `not_started` → `in_progress` → `done` or `blocked`

**Hard rule:** Only ONE feature `in_progress` at a time. No scope creep. Finish and verify before starting the next. The feature list is the scope enforcement mechanism — the agent reads it at session start, picks the highest-priority unfinished item, and works on nothing else.

### 5. Verification Must Be External

**Why:** A generative model is its own output's best defense attorney. If the same agent that wrote the code also judges it, it will almost always pass itself. Agents declare victory when they *feel* done — not when they *are* done.

**The verification gap** — the proportion of times the agent claims completion but independent tests fail — is the most common failure mode in agent workflows.

**Maker/Checker separation:** The entity that writes the code cannot be the entity that grades it. For everything: local `task check` is a pre-flight, not the final verdict. CI running in a clean environment is the independent checker. Treat CI failures as authoritative — if CI fails, the work is not done, regardless of what passed locally.

**Definition of Done** must be explicit and verifiable by command. "It looked right" is not verification. Every task completes only when: tests pass, lint is clean, state is updated, the work is committed, and the repo is clean.

**Only full-pipeline runs count.** Unit tests miss component boundary defects — interface mismatches, state propagation errors, resource lifecycle issues. The agent must run the end-to-end verification (`make check`), not just unit tests. When an agent knows its work will be validated by end-to-end tests, its coding behavior shifts: it considers component interactions, respects architectural boundaries, and handles error paths.

### 6. Runtime Must Be Observable

**Why:** Without observability, retries become blind wandering. The agent can't distinguish "correct" from "looks correct." Evaluation becomes mysticism — the same output gets different judgments from different evaluators. When the agent doesn't know why something failed, its retry direction is random.

Observability operates on two layers, both essential:

- **Runtime observability:** System-level signals — logs, traces, health checks. Answers "what did the system do."
- **Process observability:** Harness decision artifacts — sprint contracts (what will change, what won't, verification standards), evaluator rubrics (evidence-based scoring), task traces (decision-path records). Answers "why should this change be accepted."

**Agents can't solve observability themselves** — they don't know what they don't know, log formats drift across sessions, and process observability requires harness-level support. Build signal collection into the harness, not the agent's prompts.

### 7. Sessions Must End Clean

**Why:** Entropy growth is the default state. Lehman's laws: systems undergoing continuous change grow more complex unless actively managed. Every session introduces changes; without cleanup at exit, technical debt accumulates exponentially.

A project developed with agents for 12 weeks without cleanup:
- Week 1: build 100%, tests 100%, startup 5 min
- Week 4: build 95%, tests 92%, startup 15 min
- Week 8: build 82%, tests 78%, startup 35 min
- Week 12: build 68%, tests 61%, startup 60+ min

**Five clean-state conditions** at session end:
1. Build passes
2. All tests pass (including pre-existing ones — the session must not break existing functionality)
3. Progress recorded in machine-readable artifacts (what's done, what's in progress, what's next)
4. No stale artifacts — no debug logs, temp files, commented-out dead code, TODO markers
5. Standard startup path works — the next session can begin without manual intervention

**"Clean up later" means never clean up.** The next agent session doesn't know what you left behind. It'll spend significant time inferring which code is intentional and which is temporary — then start new work on top of the chaos.

### 8. The Agent Must Drive Itself

**Why:** Everything in principles 1–7 assumes you're at the keyboard, typing instructions one at a time. Loop engineering moves you outside the loop — the agent decides when to start, when to retry, and when to stop.

**The /goal pattern** has three parts: a goal (what the end state looks like), a verification method, and a stopping condition. The maker/checker split is what makes autonomous stopping safe — the entity writing code can't judge whether it's done.

**Four loop types**, increasingly autonomous:
| Type | Trigger | Stop condition | Best for |
|---|---|---|---|
| Turn-based | You type each prompt | Agent thinks it's done | Small tasks, exploration |
| Goal-based | You give a goal and walk away | Independent evaluator confirms done | Complex tasks with clear completion criteria |
| Time-based | Scheduled interval | You stop it, or it exits on completion | Polling, periodic checks, recurring work |
| Event-driven | External event (PR, CI failure, new issue) | After handling event or hitting retry limit | Reactive workflows, CI/CD integration |

**Technical debt is a high-interest loan.** OpenAI's five-month Codex experiment taught them: agents copy patterns already in the repo, even inconsistent ones. Encode golden rules into the repository, establish periodic automated cleanup workflows, and capture human taste once — then enforce it continuously. Pay down debt in small increments; the cumulative cleanup cost is always lower than one massive payoff event.

---

## Scaffolding Procedure

1. **Determine the level.** Not every project needs the full machinery.
   - **Multi-agent codebase** (production, > 20 files, multiple contributors) → Full harness: entry doc, progress tracking, feature queue, decision log, architecture constraints
   - **Single-person tool** (CLI, dashboard, < 20 files) → Light harness: entry doc + progress tracking
   - **Research / experiments** → Entry doc + research log, no feature queue
   - **Throwaway spike** → A README that says what it does

2. **Create the entry document** (`AGENTS.md`, `CLAUDE.md`, or `README.md`). 50–200 lines. Must include:
   - Project description (one paragraph), directory map, setup/run commands, verification command, gotchas
   - **Startup Workflow** — exact steps the agent follows at session start: confirm directory, read state files, install deps, review git log, verify baseline passes
   - **Working Rules** — one task at a time, no premature completion claims, scope discipline, prefer repo artifacts over chat summaries, respect architecture constraints
   - **Architecture Constraints** — module boundaries, import rules, what depends on what, firewall rules (for full harness)
   - **Definition of Done** — the checklist: tests pass, lint clean, state updated, committed, repo clean. "It looked right" is not verification.
   - **Maker / Checker** — local verification is a pre-flight; CI is the independent checker. If CI fails, the work is not done.
   - **Ratchet Loop** — the failure protocol: stop on red, log the failure, fix the root cause, re-verify. Never advance state past a failing check.
   - **End Of Session** — the closing ritual: run full check, update state, record decisions, commit, leave repo clean.

3. **Choose a state mechanism.** `PROGRESS.md` is the simplest default — tracks completed, in-progress, known issues, and ordered next steps. For multi-agent projects, also track last verified commit.

4. **Create a feature queue** (for full harness). Every future feature gets: what (behavior), how to verify (executable command), status. Only ONE `in_progress` at a time. Verification criteria are written before implementation starts.

5. **Set up the environment.** Whatever `setup && check` means in this stack — make it a single command. Use `pyproject.toml` / `package.json` / `Cargo.toml` to lock deps, `.python-version` / `.nvmrc` / `rust-toolchain.toml` for runtime versions.

6. **Define the verification command.** Must prove correctness — not just check syntax. Pytest with behavioral tests, `cargo test`, `npm test` with integration suites. Make it executable: one command that runs the full pipeline.

7. **Write architecture constraints.** For full harness: module boundaries, import direction rules, firewall rules (e.g., "Risk Manager cannot be bypassed"). Prefer "MUST / MUST NOT" language.

8. **Create the decision log.** Every architectural choice gets: date, what was chosen, why, what alternatives were considered. Without this, every new session redundantly re-evaluates past decisions.

9. **Run the fresh-session test.** Spawn a brand-new agent. Give it only the repo. Ask the five questions. If it can't answer all of them, fix the harness and retest.

10. **Run the ratchet test.** Deliberately break a test. Verify the agent stops on red, logs the failure, and refuses to advance state. If the agent claims completion despite a red pipeline, the ratchet is not enforced.

11. **Commit.** The harness itself is the first commit. It is the foundation everything else builds on.

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
8. Is the decision log up to date? Any undocumented architectural choices?
9. Ratchet test: break something, then verify the agent refuses to advance state.
10. Five clean-state conditions at last session end: build green, tests green, progress recorded, no stale artifacts, startup path works?

**Harness rots like code does.** Audit regularly. As model capabilities improve, remove components that are no longer necessary — a constraint essential today may be overhead in three months.
