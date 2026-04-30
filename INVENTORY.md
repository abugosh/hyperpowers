# Hyperpowers Plugin Inventory

**Last Updated:** 2026-02-14
**Version:** 2.10.0
**Current Branch:** main

Complete inventory of all skills, commands, agents, hooks, and configuration in the hyperpowers plugin.

---

## 1. PLUGIN METADATA

**Location:** `/Users/abugosh/g/hyperpowers/.claude-plugin/plugin.json`

```json
{
  "name": "hyperpowers",
  "description": "Fork of withzombies/hyperpowers: strong guidance for Claude Code as a software development assistant",
  "version": "2.10.0",
  "author": { "name": "Alex Bugosh" },
  "homepage": "https://github.com/abugosh/hyperpowers",
  "repository": "https://github.com/abugosh/hyperpowers",
  "license": "MIT",
  "keywords": ["skills", "tdd", "debugging", "collaboration", "best-practices", "workflows"]
}
```

---

## 2. SKILLS (20 Total)

All skills located in `/Users/abugosh/g/hyperpowers/skills/*/SKILL.md`

### Feature Development Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **brainstorming** | Interactive design refinement using Socratic method - refines rough ideas into bd epics with immutable requirements | HIGH FREEDOM | Workflow |
| **writing-plans** | Expand bd tasks with detailed implementation steps - adds exact file paths, complete code, verification commands assuming zero context | MEDIUM FREEDOM | Workflow |
| **executing-plans** | Execute bd tasks iteratively - executes one task, reviews learnings, creates/refines next task, then STOPS for user review | LOW FREEDOM | Workflow |
| **review-implementation** | Verify implementation against bd spec, all success criteria met, anti-patterns avoided | LOW FREEDOM | Workflow |
| **finishing-a-development-branch** | Close bd epic, present integration options (merge/MR/keep/discard), executes choice | LOW FREEDOM | Workflow |
| **sre-task-refinement** | Refine subtasks with Google Fellow SRE scrutiny ensuring corner cases and requirements understood; verify no placeholder text | LOW FREEDOM | Workflow |

### Bug Fixing & Debugging Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **debugging-with-tools** | Systematic debugging using debuggers, internet research, and agents to find root cause before fixing | MEDIUM FREEDOM | Process |
| **root-cause-tracing** | Trace bugs backward through call stack to find original trigger, not just symptom | MEDIUM FREEDOM | Process |
| **fixing-bugs** | Complete workflow: reproduce, track in bd, debug systematically, write test, fix, verify, close | LOW FREEDOM | Process |

### Refactoring & Maintenance Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **refactoring-safely** | Test-preserving transformations in small steps, running tests between each change | MEDIUM FREEDOM | Process |

### Quality & Testing Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **test-driven-development** | Enforce RED-GREEN-REFACTOR cycle - write tests first, watch fail, implement minimal code | LOW FREEDOM (Rigid) | Process |
| **testing-anti-patterns** | Prevent common testing mistakes - 3 Iron Laws: never test mocks, never add test-only methods, never mock without understanding | LOW FREEDOM (Rigid) | Process |
| **verification-before-completion** | Require running verification commands with evidence - no shortcuts, no "should work" | LOW FREEDOM (Rigid) | Process |
| **analyzing-test-effectiveness** | Audit test quality with Google Fellow SRE scrutiny - identifies tautological tests, coverage gaming, weak assertions, missing corner cases | MEDIUM FREEDOM | Workflow |

### Task & Project Management Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **managing-bd-tasks** | Advanced bd operations - splitting tasks, merging duplicates, changing dependencies, archiving epics, querying metrics | HIGH FREEDOM | Workflow |

### Collaboration & Process Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **dispatching-parallel-agents** | Dispatch multiple agents to investigate 3+ independent failures concurrently | MEDIUM FREEDOM | Workflow |
| **using-hyper** | Establishes mandatory workflows for finding and using skills - MUST check for skills, MUST use Skill tool, announce usage | HIGH FREEDOM (Meta) | Process |
| **writing-skills** | Apply TDD to documentation - write failing test scenario, watch fail, write skill, watch pass, refactor | LOW FREEDOM (Rigid) | Workflow |

### Infrastructure & Customization Skills

| Skill | Description | Rigidity | Type |
|-------|-------------|----------|------|
| **building-hooks** | Create Claude Code hooks - covers progressive enhancement from observe → automate → enforce | MEDIUM FREEDOM | Workflow |
| **skills-auto-activation** | Solve skills not activating through better descriptions, CLAUDE.md references, or custom hook system | HIGH FREEDOM | Workflow |

### Common Patterns (Shared References)

Centralized patterns in `/Users/abugosh/g/hyperpowers/skills/common-patterns/`:

- **bd-commands.md** - Standard bd command examples
- **common-anti-patterns.md** - Anti-patterns to avoid
- **common-rationalizations.md** - Excuses that signal failure

---

## 3. COMMANDS (6 Total)

All commands located in `/Users/abugosh/g/hyperpowers/commands/*.md`

| Command | Description | Invokes Skill |
|---------|-------------|---------------|
| `/hyperpowers:brainstorm` | Interactive design refinement using Socratic method | brainstorming |
| `/hyperpowers:write-plan` | Create detailed implementation plan with bite-sized tasks | writing-plans |
| `/hyperpowers:execute-plan` | Execute plan in batches with review checkpoints | executing-plans |
| `/hyperpowers:review-implementation` | Review implementation was faithfully executed | review-implementation |
| `/hyperpowers:finish-branch` | Close epic and integrate branch after manual validation complete | finishing-a-development-branch |
| `/hyperpowers:analyze-tests` | Audit test quality - identify tautological tests, coverage gaming, missing corner cases | analyzing-test-effectiveness |

---

## 4. AGENTS (5 Total)

All agents located in `/Users/abugosh/g/hyperpowers/agents/*.md`

### Investigation & Review Agents

| Agent | Purpose | Model | Memory | Special Permissions |
|-------|---------|-------|--------|-------------------|
| **code-reviewer** | Review completed project steps against original plan and coding standards | sonnet | project | Uses testing-anti-patterns skill |
| **codebase-investigator** | Understand codebase state, find existing patterns, verify design assumptions | haiku | project | plan_mode_required |
| **internet-researcher** | Research APIs, libraries, docs, current best practices | haiku | user | — |
| **test-effectiveness-analyst** | Analyze test effectiveness with Google Fellow SRE scrutiny - identifies tautological tests, weak assertions, missing corner cases | sonnet | project | — |

### Execution Agent

| Agent | Purpose | Model | Memory | Special Permissions |
|-------|---------|-------|--------|-------------------|
| **test-runner** | Run tests/validations/commits without context pollution - returns only summary + failures | haiku | — | dontAsk; Edit & Write disallowed |

---

## 5. HOOKS SYSTEM

**Location:** `/Users/abugosh/g/hyperpowers/hooks/`

### Hook Configuration

**hooks.json** - Defines all active hooks:

| Hook Type | Event | Hooks Registered |
|-----------|-------|------------------|
| **SessionStart** | Startup/resume/clear/compact | session-start.sh |
| **PreToolUse** | Read/Grep → block-beads-direct-read.py |
| | Edit/Write → 01-block-pre-commit-edits.py |
| **UserPromptSubmit** | 10-skill-activator.js |
| **PostToolUse** | Edit/Write → 01-track-edits.sh |
| | Bash → 02-block-bd-truncation.py, 03-block-pre-commit-bash.py, 04-block-pre-existing-checks.py |
| **Stop** | 10-gentle-reminders.sh |

### Hook Scripts

**Pre-Tool Hooks:**
- `01-block-pre-commit-edits.py` - Block Direct Edit/Write to .git/hooks/pre-commit

**Post-Tool Hooks:**
- `01-track-edits.sh` - Track file edits during session to context/edit-log.txt
- `02-block-bd-truncation.py` - Detect and block bd commands with truncation markers
- `03-block-pre-commit-bash.py` - Block Bash commands modifying .git/hooks/pre-commit
- `04-block-pre-existing-checks.py` - Block commands modifying pre-existing checks

**User Prompt Hooks:**
- `10-skill-activator.js` - Analyze user prompt and suggest relevant skills from skill-rules.json

**Session Hooks:**
- `session-start.sh` - Initialize session context and setup

**Stop Hooks:**
- `10-gentle-reminders.sh` - Provide gentle reminders (TDD, verification, commits)

**Utilities:**
- `context-query.sh` - Query context from edit-log.txt
- `format-output.sh` - Format hook output
- `skill-matcher.sh` - Match skills against prompts
- `test-performance.sh` - Test hook performance

**Context:**
- `edit-log.txt` - Tracks file edits during session

### Skill Activation Rules

**skill-rules.json** - Defines auto-activation triggers for 20 skills + test-runner agent

Structure: Each skill/agent has `type`, `enforcement`, `priority`, and `promptTriggers` (keywords + regex patterns)

**Priority Levels:**
- **Critical** (must always suggest): test-driven-development, verification-before-completion, using-hyper
- **High** (suggest often): debugging-with-tools, fixing-bugs, brainstorming, writing-plans, executing-plans, review-implementation, test-runner
- **Medium** (suggest relevant): refactoring-safely, dispatching-parallel-agents, testing-anti-patterns, sre-task-refinement
- **Low** (suggest when specific): managing-bd-tasks, building-hooks, skills-auto-activation, writing-skills

---

## 6. DOCUMENTATION FILES

| File | Purpose | Type |
|------|---------|------|
| **README.md** | Plugin overview, features, usage, philosophy, installation | Project docs |
| **CLAUDE.md** | Instructions for Claude Code when working with this repository | Developer docs |
| **HOOKS.md** | Comprehensive hooks documentation, configuration, troubleshooting | Hook docs |
| **AGENTS.md** | Summary of available agents and when to use them | Agent docs |
| **INVENTORY.md** (this file) | Complete catalog of skills, commands, agents, hooks | Catalog |
| **BUG-brainstorming-skips-questions.md** | Issue tracking known bug in brainstorming skill | Issue tracking |
| **REWRITE_COMPLETE.md** | Notes on major rewrite completion | Development notes |

---

## 7. PROJECT STRUCTURE

```
/Users/abugosh/g/hyperpowers/
├── .claude-plugin/
│   └── plugin.json                    # Plugin metadata
├── skills/
│   ├── analyzing-test-effectiveness/
│   ├── brainstorming/
│   ├── building-hooks/
│   ├── debugging-with-tools/
│   ├── dispatching-parallel-agents/
│   ├── executing-plans/
│   ├── finishing-a-development-branch/
│   ├── fixing-bugs/
│   ├── managing-bd-tasks/
│   ├── refactoring-safely/
│   ├── review-implementation/
│   ├── root-cause-tracing/
│   ├── skills-auto-activation/
│   ├── sre-task-refinement/
│   ├── test-driven-development/
│   ├── testing-anti-patterns/
│   ├── using-hyper/
│   ├── verification-before-completion/
│   ├── writing-plans/
│   ├── writing-skills/
│   └── common-patterns/
│       ├── bd-commands.md
│       ├── common-anti-patterns.md
│       └── common-rationalizations.md
├── commands/
│   ├── analyze-tests.md
│   ├── brainstorm.md
│   ├── execute-plan.md
│   ├── finish-branch.md
│   ├── review-implementation.md
│   └── write-plan.md
├── agents/
│   ├── code-reviewer.md
│   ├── codebase-investigator.md
│   ├── internet-researcher.md
│   ├── test-effectiveness-analyst.md
│   └── test-runner.md
├── hooks/
│   ├── hooks.json
│   ├── skill-rules.json
│   ├── block-beads-direct-read.py
│   ├── session-start.sh
│   ├── context/
│   │   └── edit-log.txt
│   ├── pre-tool-use/
│   │   └── 01-block-pre-commit-edits.py
│   ├── post-tool-use/
│   │   ├── 01-track-edits.sh
│   │   ├── 02-block-bd-truncation.py
│   │   ├── 03-block-pre-commit-bash.py
│   │   └── 04-block-pre-existing-checks.py
│   ├── user-prompt-submit/
│   │   └── 10-skill-activator.js
│   ├── stop/
│   │   └── 10-gentle-reminders.sh
│   ├── utils/
│   │   ├── context-query.sh
│   │   ├── format-output.sh
│   │   ├── skill-matcher.sh
│   │   └── test-performance.sh
│   └── test/
│       └── integration-test.sh
├── README.md
├── CLAUDE.md
├── HOOKS.md
├── AGENTS.md
├── INVENTORY.md (this file)
├── BUG-brainstorming-skips-questions.md
└── REWRITE_COMPLETE.md
```

---

## 8. KEY STATISTICS

- **Total Skills:** 20
- **Total Commands:** 6
- **Total Agents:** 5
- **Total Hooks:** 12 (post-use, pre-use, user-prompt, session, stop)
- **Skill Auto-Activation Rules:** 20 skills + 1 agent = 21 total
- **Hook Priority Distribution:**
  - Critical: 3
  - High: 7
  - Medium: 4
  - Low: 6

---

## 9. QUICK REFERENCE: WORKFLOW CHAINS

### Feature Development Chain
```
brainstorming → writing-plans → executing-plans → review-implementation → finishing-a-development-branch
```

### Bug Fixing Chain
```
fixing-bugs → (debugging-with-tools | root-cause-tracing) → test-driven-development → fixing-bugs implementation → verification-before-completion
```

### Test Quality Chain
```
analyzing-test-effectiveness → sre-task-refinement → executing-plans → verification-before-completion
```

### Refactoring Chain
```
refactoring-safely → test-driven-development → verification-before-completion
```

---

## 10. CRITICAL WORKFLOWS

**Mandatory (Cannot Skip):**
- using-hyper - Check for skills BEFORE any work
- test-driven-development - RED → GREEN → REFACTOR cycle
- verification-before-completion - Evidence before claims
- testing-anti-patterns - 3 Iron Laws strictly enforced

**Strongly Recommended (Follow Unless Justified):**
- brainstorming - Design before coding
- sre-task-refinement - Corner case analysis
- debugging-with-tools - Root cause before fixing
- review-implementation - Verify against spec

---

## 11. VERSION HISTORY

- **2.10.0** (current) - Reverted wave/team execution system; clean stable state
- **2.9.0** - Added execute-wave command (reverted in 2.10.0)
- **2.8.x** - Added team vs solo routing to using-hyper skill
- **2.7.x** - Upgraded agent definitions with new subagent features
- **2.6.x** - Added team-executing-plans skill (reverted in 2.10.0)

---

## 12. UNTRACKED FILES (As of 2026-02-14)

```
?? .beads/README.md
?? .beads/config.yaml
?? .beads/interactions.jsonl
?? .beads/metadata.json
?? .gitattributes
?? AGENTS.md
```

Note: AGENTS.md is being tracked but shows as untracked in initial git status.

---

## 13. KNOWN ISSUES

- **BUG-brainstorming-skips-questions.md** - Brainstorming skill may skip asking all planned questions in some scenarios

---

## 14. DESIGN NOTES FOR FUTURE EXTENSIONS

### Missing Workflows (from RECOMMENDATIONS.md)
- Incident response
- Code review response (receiving reviews)
- Merge conflict resolution
- Documentation workflows

### Current Focus Areas
- Stability and reliability of core workflows
- Hook system for automated quality checks
- Skill auto-activation through skill-rules.json
- Agent dispatch for parallel investigations

---

End of Inventory
