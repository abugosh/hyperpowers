---
name: using-hyper
description: Use when starting any conversation - establishes mandatory workflows for finding and using skills
---

<EXTREMELY_IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST read the skill.

**IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.**

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY_IMPORTANT>

<skill_overview>
Skills are proven workflows; if one exists for your task, using it is mandatory, not optional. The routing table below is the catalog — route every task through it.
</skill_overview>

<rigidity_level>
HIGH FREEDOM - The meta-process (check for skills, use Skill tool, announce usage) is rigid, but each individual skill defines its own rigidity level.
</rigidity_level>

<hard_gates>
## Before responding to ANY user message — no exceptions

1. ☐ Find the task's shape in the routing table below
2. ☐ If any row matches (even 1% chance) → you MUST use the Skill tool to load the skill
3. ☐ Announce it: "I'm using [skill] to [purpose]"
4. ☐ Follow the skill exactly as written
5. ☐ Skill has a checklist? You MUST track every item in the repo's tracker — bd when beads is present, TodoWrite otherwise. Mental tracking = skipped steps. Every time.

**Responding without completing this checklist = automatic failure.**

**Always load skills with the Skill tool — NEVER from memory.** Skills evolve; you need the current version, and the load confirms to the user that you are following it.
</hard_gates>

<routing_table>
## Routing Table — task shape → skill chain

| Task shape | Route |
|------------|-------|
| Exploring an idea; goal not yet clear | hyperpowers:consider → routes onward when ready |
| Build / create / add / implement anything | hyperpowers:brainstorming → hyperpowers:executing-plans → hyperpowers:review-implementation → hyperpowers:finishing-a-development-branch |
| Large initiative (sizing gate in `skills/common-patterns/pipeline-constants.md` fires) | hyperpowers:preordain → hyperpowers:brainstorming per leaf epic |
| Phase docs in a planning repo (multiservice) | hyperpowers:portent (draft / check) |
| Bug report or test failure | hyperpowers:debugging-with-tools → hyperpowers:fixing-bugs |
| Error deep in execution, unclear origin | hyperpowers:root-cause-tracing |
| Writing implementation code (inside any flow) | hyperpowers:test-driven-development + hyperpowers:testing-anti-patterns |
| Refactoring existing code | hyperpowers:refactoring-diagnosis → hyperpowers:refactoring-design → hyperpowers:refactoring-safely |
| bd tasks exist without complete specs | hyperpowers:writing-plans |
| bd surgery: split, merge, re-dep, archive | hyperpowers:managing-bd-tasks |
| Running tests / validations / commits | hyperpowers:test-runner agent (keeps verbose output out of context) |
| About to claim done / fixed / passing | hyperpowers:verification-before-completion |
| Structural friction; architecture unease | hyperpowers:intuition |
| Architecture model (.c4) create/update/review | hyperpowers:ponder |
| Auditing test quality | hyperpowers:analyzing-test-effectiveness |
| 3+ independent failures to investigate | hyperpowers:dispatching-parallel-agents |
| Creating or editing skills | hyperpowers:writing-skills |
| Creating Claude Code hooks | hyperpowers:building-hooks |

A matching row is a mandate, not a suggestion: you MUST load and follow that chain. If several rows match, chain them in the order shown.
</routing_table>

<session_start_duties>
## At session start (beads repos)

- Run `bd ready` / `bd list --status=in_progress` before starting new work. If an epic sits in_progress with no commits or bd updates for days, surface it to the user first — stalled lanes are acceptable only when the stall is visible on return.
- In multi-service work, shared plan documents (typically in a planning repo) may sit ABOVE bd: they carry cross-service requirements and contracts while bd remains the per-repo execution tracker. Both layers are legitimate at their own level — brainstorming can ingest a plan-doc slice, and per-repo learnings flow back up as plan-impact notices (`skills/common-patterns/loop-interfaces.md`). When no plan docs exist, nothing asks for them.
</session_start_duties>

<instructions_vs_workflows>
## User instructions describe WHAT, not HOW

"Add X" / "Fix Y" / "Refactor Z" state the GOAL. They are never permission to skip the routed workflow — you MUST route them through the table like everything else.

Red flags that you are rationalizing: "instruction was specific", "seems simple", "workflow is overkill". Workflows matter MORE when instructions are specific — clear requirements are the perfect input for the structured path, and skipping process on "easy" tasks is how they become hard problems.

The full excuse catalog lives in `skills/common-patterns/common-rationalizations.md` (see its Skill Routing Shortcuts) — any excuse you catch yourself making means STOP and use the skill. The classics: "This is just a simple question" (questions are tasks — check the table), "I remember this skill" (skills evolve — load it), "I'll just do this one thing first" (check BEFORE doing anything).
</instructions_vs_workflows>

<understanding_rigidity>
## Rigidity

- LOW FREEDOM (follow exactly): test-driven-development, verification-before-completion, executing-plans
- HIGH FREEDOM (adapt principles): consider, brainstorming, managing-bd-tasks, sre-task-refinement

Each skill declares its own `<rigidity_level>` — check it.
</understanding_rigidity>

<verification_checklist>
Before completing ANY task:

- [ ] Routed the task through the table before starting
- [ ] Loaded matching skills via the Skill tool (not memory) and announced them
- [ ] Followed each skill as written; checklist items tracked in the repo's tracker
- [ ] Verification-before-completion run before any "done" claim

Can't check all boxes? You skipped critical steps. Review and fix.
</verification_checklist>

<integration>
**This skill calls:** ALL other skills (meta-skill — the routing table above is the catalog).

**This skill is called by:** session start (injected every session) and before every task.
</integration>
