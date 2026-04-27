# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

Hyperpowers is a Claude Code plugin that provides structured workflows, best practices, and specialized agents for software development. It's a plugin system that adds skills (reusable workflows), slash commands (quick access to workflows), specialized agents (domain-specific task handlers), and hooks (automatic behaviors).

Inspired by [obra/superpowers](https://github.com/obra/superpowers).

## CRITICAL: Understanding User Requests in This Repository

**This is a plugin development project.** Your task is to improve the plugin (skills, hooks, agents, commands), NOT to debug the user's other projects.

### Common Pattern: Examples from Other Sessions

The user will frequently describe issues like:
- "Claude did X in another session and it was wrong"
- "I got this error: [some error from another project]"
- "Claude truncated the bd task and that caused problems"
- "Claude edited .git/hooks/pre-commit with sed"

**CRITICAL - These are NOT problems for you to investigate or debug.**

### What These Examples Actually Mean

When the user describes an issue from another session, they are:
1. **Providing evidence** of a pattern where Claude behaves incorrectly
2. **Requesting plugin improvements** to prevent that pattern
3. **NOT asking you** to fix those specific historical errors

### The Correct Response Pattern

**Bad response (trying to fix the other session):**
```
Let me investigate that error. Can you show me the file where the truncation occurred?
Let me check the bd task that was created. What was the full command?
```

**Good response (improving the plugin):**
```
This is a pattern we can prevent with a hook. Let me create a PostToolUse hook
that blocks bd commands containing truncation markers.
```

### Translation Guide

| What user says | What they actually want |
|----------------|------------------------|
| "Claude truncated the bd task" | Create hook to block bd truncation |
| "Claude edited pre-commit with sed" | Create hook to block pre-commit modifications |
| "The test-runner agent didn't activate" | Improve skill-rules.json triggers |
| "Claude ignored the skill" | Improve skill description or add hook |
| "This caused incomplete implementation" | Add blocking hook to prevent pattern |

### Your Goal in This Repository

**Always:** Improve the plugin to prevent bad patterns
**Never:** Try to investigate or fix issues from other sessions

You cannot access other sessions. You cannot fix past problems. You CAN prevent those problems from happening again by improving skills, hooks, agents, and commands in THIS repository.

### Examples of Correct Responses

**User:** "Claude edited .git/hooks/pre-commit with `sed -i` to work around an error"

**Correct response:**
- Create PreToolUse hook blocking Edit/Write to pre-commit
- Create PostToolUse hook blocking Bash commands modifying pre-commit
- Update HOOKS.md with documentation

**User:** "The bd task had '[Remaining steps truncated]' which caused incomplete implementation"

**Correct response:**
- Create PostToolUse hook blocking bd create/update with truncation markers
- Add regex patterns for all truncation variations
- Test hook with sample commands

**User:** "Claude ran `./scripts/docker-test.sh` with 700+ lines of output and didn't suggest test-runner agent"

**Correct response:**
- Add test script patterns to skill-rules.json
- Add keywords like "npm test", "pytest", test runner names
- Test activation with sample prompts

## Plugin Structure

The repository is organized as follows:

- **skills/** - Reusable workflow definitions (each in its own directory with SKILL.md)
- **commands/** - Slash command definitions that invoke skills
- **agents/** - Specialized agent prompts (executor, reviewer, code-reviewer, codebase-investigator, internet-researcher, test-runner, ponder)
- **hooks/** - Automatic behaviors triggered by events
- **.claude-plugin/** - Plugin metadata (plugin.json)

## Key Architecture Concepts

### Skills System

Skills are detailed workflow instructions stored in `skills/*/SKILL.md`. Each skill follows a specific pattern:

1. **Frontmatter** - YAML metadata (name, description)
2. **Overview** - Core principle and context
3. **The Process** - Step-by-step workflow with exact commands
4. **Common Rationalizations** - Mistakes to avoid
5. **Red Flags** - Anti-patterns to prevent
6. **Integration** - How this skill calls/is called by others

**Critical distinction:**
- Some skills are **rigid processes** (TDD, verification) - follow exactly, no adaptation
- Some skills are **flexible patterns** (architecture, naming) - adapt principles to context
- The skill itself tells you which type it is

### Skill Invocation Pattern

Skills are invoked through slash commands that expand to prompts. The flow is:

1. User types `/hyperpowers:write-plan`
2. Command file (`commands/write-plan.md`) expands with instruction: "Use the writing-plans skill exactly as written"
3. Claude uses the Skill tool to load `skills/writing-plans/SKILL.md`
4. Claude follows the skill's detailed instructions

### bd Integration

Many skills integrate with `bd` (a task management tool). The workflows expect:

- **Epics** - High-level features/initiatives (created by writing-plans)
- **Tasks** - Specific implementation steps (created by writing-plans, executed by executor agent via executing-plans)
- **Dependencies** - Task relationships (blocking, parent-child)
- **Status tracking** - Open, in-progress, done, ready

Common bd commands:
```bash
bd list --type epic --status open       # Find open epics
bd ready                                 # Show ready tasks
bd show bd-1                            # Show task details
bd dep tree bd-1                        # Show task tree
bd status bd-3 --status in-progress     # Update task status
```

### Agent System

Specialized agents run in separate contexts to handle specific tasks:

1. **executor** (subagent) - Implements a single bd task with TDD discipline. Uses native TaskCreate/TaskUpdate for TDD sub-step tracking. Dispatched fresh per task by executing-plans; writes project memory before returning so the next executor has cross-task learnings. Returns structured output (completion report, escalation, or checkpoint) to the lead.
2. **reviewer** (subagent) - Verifies implementation against bd epic spec with Google Fellow SRE scrutiny. Returns APPROVED or GAPS FOUND verdict. Dispatched as one-shot subagent.
3. **test-runner** (uses Haiku) - Runs tests/hooks/commits, returns only summary + failures to keep context clean
4. **code-reviewer** - Reviews implementations against plans and coding standards
5. **codebase-investigator** - Explores codebase state and patterns when planning/designing
6. **internet-researcher** - Researches APIs, libraries, docs when planning/designing
7. **ponder** (subagent) - Creates, updates, and reviews LikeC4 architecture models. Single owner of all .c4 file operations. Dispatched by the ponder skill in update, bootstrap, or review mode.

**Critical pattern:** Agents keep verbose output (test results, formatting diffs) in their own context, returning only essential info to the main conversation.

**Delegation pattern:** The executing-plans skill uses blocking subagent dispatch — the lead (main context) dispatches a fresh executor subagent per task via the Agent tool (without team_name), which blocks the lead until the executor returns. The executor has a bounded single-task lifetime (preventing context exhaustion), writes learnings to project memory before returning, and the next executor reads that memory on startup. The lead holds the epic context and validates proposals; cross-task learnings are preserved via project memory rather than a single long-running context.

### Common Patterns Location

To avoid duplication, common elements are centralized in `skills/common-patterns/`:

- `bd-commands.md` - Standard bd command examples
- `common-anti-patterns.md` - Anti-patterns to avoid
- `common-rationalizations.md` - Excuses that signal failure

Skills reference these rather than duplicating content.

## Core Workflows

### Exploration (Pre-Brainstorm)

When the goal isn't yet clear — exploring whether to build something, clarifying problem framing, or thinking through an idea before committing:

1. **Consider** (`/hyperpowers:consider`) - Lightweight Socratic thinking partner. One question at a time, optional research agents on-demand, routes to /brainstorm (commit-to-build) or /intuition (structural friction) when ready. Clean exit valid if no commitment made.

### Feature Development (Greenfield)

Complete workflow from idea to PR:

1. **Brainstorming** (`/hyperpowers:brainstorm`) - Primary entry point when ready to build. Socratic questioning to refine requirements, research codebase/external docs, produce bd epic with immutable requirements
2. **SRE Task Refinement** (optional) - Uses Opus 4.1 to identify corner cases
3. **Writing Plans** (`/hyperpowers:write-plan`) - Creates detailed bd epic with tasks
4. **Executing Plans** (`/hyperpowers:execute-plan`) - Lead orchestrates executor subagent who implements tasks with TDD; lead validates proposals against epic
5. **Review Implementation** (`/hyperpowers:review-implementation`) - Verifies against spec
6. **Finishing Branch** - Creates PR, handles cleanup

### Architecture (Empirical, Brand-based)

Architecture uses Brand's empirical approach — observe actual change rates through git history rather than predicting forces upfront:

1. **Brainstorm** (`/hyperpowers:brainstorm`) - Primary entry point for new work. Includes Architecture Impact Check (5 structural questions) and design-time friction detection that routes to /intuition when structural uncertainty arises
2. **Build** - Implement the feature (executing-plans)
3. **Intuition** (`/hyperpowers:intuition`) - Intermittent diagnostic. Runs 9 structured analysis passes to find tensions (complection, coupling, dependency direction, rate-of-change mismatches, workaround cascades, mechanism bypass). Resolution protocol guides per-tension decisions (accept via ADR, resolve via ADR + ticket, brainstorm for complex cases, investigate for deeper evidence)
4. **Ponder** (`/hyperpowers:ponder`) - Architecture model ownership. Dispatches ponder subagent for all .c4 file operations (update, bootstrap, review). Called by review-implementation (architecture checklist) and Intuition (model bootstrapping)

The architecture model (LikeC4 `.c4` files in `docs/arch/`) represents current codebase reality. ADR trail IS the architectural strategy.

### Test-Driven Development

Required for most implementation work:

1. Write test first (RED phase)
2. Watch test fail (verifies test actually tests something)
3. Write minimal code to pass (GREEN phase)
4. Refactor while keeping tests green
5. Commit

The `test-driven-development` skill enforces this rigorously.

### Bug Fixing & Debugging

Complete workflow for fixing bugs systematically:

1. **Create bd Bug Issue** - Track the bug with reproduction steps
2. **Debugging with Tools** - Use debuggers, internet-researcher, codebase-investigator to find root cause
3. **Write Failing Test** (RED phase) - Reproduce the bug in a test
4. **Implement Fix** (GREEN phase) - Minimal fix addressing root cause
5. **Verify** - Run full test suite via test-runner agent, check for regressions
6. **Close bd Issue** - Document fix and close

**Key Skills:**
- `debugging-with-tools` - Systematic investigation using debuggers, internet research, and agents
- `root-cause-tracing` - Trace backward through call stack to find original trigger
- `fixing-bugs` - Complete workflow from bug discovery to closure

**Critical:** Always use debugger and internet-researcher BEFORE attempting fixes. Never fix symptoms.

### Verification Pattern

Before claiming any work is complete:

1. Run verification commands (tests, lints, builds)
2. Capture output as evidence
3. Only claim success if verification passes
4. Use test-runner agent to avoid context pollution

The `verification-before-completion` skill makes this mandatory.

## Development Commands

This is a plugin repository with no build system - it's pure markdown files. There are no tests, linters, or build commands.

### Testing Skills

When creating or modifying skills, use the `writing-skills` skill which applies TDD to documentation:

1. Test skill with subagents BEFORE writing final version
2. Iterate until the skill is bulletproof against rationalization
3. Document what failure modes you tested

### Publishing

The plugin is published to the Claude Code marketplace:

```bash
# In the marketplace system (not in this repo)
claude-code plugins install hyperpowers@abugosh
```

Version is tracked in `.claude-plugin/plugin.json`.

## Philosophy and Principles

From the using-hyper skill and README:

1. **Incremental progress over big bangs** - Small changes that compile and pass tests
2. **Learning from existing code** - Study patterns before implementing
3. **Explicit workflows over implicit assumptions** - Make the process visible
4. **Verification before completion** - Evidence over assertions
5. **Test-driven when possible** - Red, green, refactor

### Mandatory Workflows

The `using-hyper` skill establishes these non-negotiable rules:

- **Check for relevant skills before ANY task** - If a skill exists for it, use it
- **Use Skill tool before announcing** - Load the actual skill file, don't rely on memory
- **Create TodoWrite todos for checklists** - Track progress explicitly
- **Follow brainstorming before coding** - Design first, code second
- **Use verification-before-completion** - Never claim success without evidence

## Common Pitfalls

From `using-hyper` - watch for these rationalizations:

- "This is just a simple question" → Wrong. Check for skills.
- "I can check git/files quickly" → Wrong. Files lack context. Check for skills.
- "Let me gather information first" → Wrong. Skills tell you HOW to gather.
- "This doesn't need a formal skill" → Wrong. If skill exists, use it.
- "I remember this skill" → Wrong. Skills evolve. Run current version.
- "The skill is overkill" → Wrong. Skills exist because simple things become complex.

## Current Limitations

From RECOMMENDATIONS.md:

**Currently covered:**
- ✅ Greenfield feature development (idea → design → implementation → PR)
- ✅ Bug fixing and debugging workflows (systematic investigation, root cause tracing)
- ✅ Refactoring workflows (test-preserving transformations)
- ✅ Advanced task management (splitting, merging, dependencies, metrics)
- ✅ Quality culture (TDD, verification, SRE review)
- ✅ Clean bd integration

**Missing (see RECOMMENDATIONS.md for details):**
- ❌ Incident response
- ❌ Code review response (receiving reviews)
- ❌ Merge conflict resolution
- ❌ Documentation workflows

Priority: Continue adding collaboration workflows (code review response, incidents).

## File Naming Conventions

- Skills: `skills/<skill-name>/SKILL.md` (frontmatter + content)
- Commands: `commands/<command-name>.md` (frontmatter + brief invocation)
- Agents: `agents/<agent-name>.md` (frontmatter + detailed prompt)
- Common patterns: `skills/common-patterns/<pattern-name>.md`

## Important Notes

- This plugin is loaded automatically when installed; there's no runtime execution
- Skills are documentation that Claude reads at runtime, not executable code
- Changes to skill files take effect immediately in new conversations
- The test-runner agent uses Haiku model for cost efficiency
- The sre-task-refinement skill uses Opus 4.1 for deep analysis
- Most other operations use the default model (Sonnet)
- **Always bump the version** in `.claude-plugin/plugin.json` before the final push of any change that modifies files in `skills/`, `agents/`, `commands/`, `hooks/`, `CLAUDE.md`, or `README.md`. Patch bump (x.y.Z) for fixes, minor bump (x.Y.0) for features/rewrites.

## Contributing Guidelines

From writing-skills skill:

1. Test skills with subagents before finalizing
2. Iterate until bulletproof against rationalization
3. Follow the skill structure pattern (Overview, Process, Rationalizations, Red Flags, Integration)
4. Reference common-patterns instead of duplicating content
5. Be explicit about whether skill is rigid (must follow exactly) or flexible (adapt principles)
