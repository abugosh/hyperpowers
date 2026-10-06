---
name: writing-skills
description: Use when creating or editing skills, agent prompts, or common patterns - evidence-first author-editor method; the lead reads the recorded observation, authors the text for the agent that will read it, runs an editor pass, records a ledger, and hands the diff to the user
---

<skill_overview>
A skill edit starts from a recorded observation and ends as a diff the user edits; the lead authors the text itself, and subagents are tools for three narrow jobs, never the engine.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM - The sequence (evidence, sites, author, editor pass, ledger, hand-off) is fixed and the evidence rule has no exceptions; how you write within it is judgment.
</rigidity_level>

<quick_reference>
| Step | Action | Ledger line |
|------|--------|-------------|
| 1 Evidence | Find the recorded observation; quote it verbatim | Evidence |
| 2 Sites | Read the current text of every file the change touches; find the rule's one home | Edits by file |
| 3 Author | Write the text for the agent that will load this file with nothing else | (the diff) |
| 4 Editor pass | Your own pass for single source, contradictions, cuts; optional fresh-agent pass | Editor pass |
| 5 Behavior check | One live use or one cheap fixture, only when a rule's behavior is genuinely uncertain | Spot check |
| 6 Hand-off | Ledger in bd notes; diff to the user; commit on their word; close-out | Version |

**The rule:** NO EDIT WITHOUT A RECORDED OBSERVATION.
</quick_reference>

<when_to_use>
Any prose an agent reads at runtime: `skills/*/SKILL.md`, `agents/*.md`, `skills/common-patterns/*.md`, a command file, a hook's injected text.

**Create a skill when:**
- The technique was not obvious to you and you would reach for it again across projects
- The pattern applies broadly, not to one project

**Never create for:**
- One-off solutions
- Standard practices documented well elsewhere
- Project-specific conventions (those go in the project's CLAUDE.md)

**Edit when an observation shows:**
- An agent doing the wrong thing with the current text in front of it
- A loophole an agent took, in its own words
- Two files that say different things about one rule
</when_to_use>

<the_process>
## 1. Evidence

An observation is something that happened and was written down: a user report, a failing artifact (an MR, a transcript, an insights report), a ledger or bd-notes line, a reviewer's or agent's return. Quote it verbatim into the ledger. Paraphrase invites lenient reading.

"Agents might..." is a hypothesis. Record it as a question for the user and make no edit.

An edit that adds text names the failure class the text now guards against. An edit that removes text names the observation that showed the text was dead weight; for a guard on an agent interface, that observation is an A/B probe (`resources/testing-methodology.md`, A/B Method), the only path `docs/arch/adr/adr-003.md` sanctions.

## 2. Read the sites

Read the current text of every file the change touches, by path from the working tree. Then find the rule's one home:

- A rule several skills follow lives in one shared patterns file (in this repo, under `skills/common-patterns/`; the repo's CLAUDE.md says which file takes what).
- A rule one skill follows lives in that skill.
- Every other site cites the home by path. Nothing restates.

Grep the rule's key phrase across `skills/`, `agents/`, `CLAUDE.md`, and `README.md`. Every hit is either the home or a citation, or it is the drift you are fixing.

## 3. Author

Write for one reader: the agent that loads this file with nothing else in front of it. Ask of each sentence:

- Given only this file, what would the agent do at this step?
- Which sentence changes nothing the agent does?
- Which rule is a contingency the agent could derive from a stated principle?
- What is stated twice?

A principle beats a contingency list. An unconditional rule beats a branch for a rare edge; the user handles the edge. A wrong sentence is cut, never qualified (`skills/common-patterns/prose-style.md`). The common rationalizations and anti-patterns an edit invites go in `skills/common-patterns/common-rationalizations.md` and `common-anti-patterns.md`, each row earned by an observation.

The skill structure rules below apply to new files and to any section you rewrite.

## 4. Editor pass

Your own pass, before anyone else reads it:

- **Single source.** Re-run the grep from step 2 against the working tree. Every hit is the home or cites it.
- **Contradictions.** Read each file that cites the sentence you changed. A citation that now says something the home does not is a contradiction to fix in the citing file.
- **Cuts.** Apply the four reader questions to your own text once more.

Optional fresh-agent pass, when the change is large or you have been in the file too long to read it cold: dispatch a fresh general-purpose agent on the session model with the file paths and the four reader questions. It reads the files from the working tree and returns line edits and cuts, never severity findings. Apply or decline each one; the ledger records the declines with a one-line reason.

## 5. Behavior check, only when uncertain

Most edits need none: you can say from reading what the agent will do. When you cannot, run one live use (the real dispatch with real inputs and no bd writes) or one cheap fixture. At most one per changed behavior.

- Read the working tree by path. The installed plugin copy that the Skill tool loads is stale on a branch.
- A pass proves the text renders the behavior once. It does not prove a field rate.
- Failures seen in long sessions (self-review leniency, stale-reference following, gate paraphrasing) rarely reproduce in a short clean fixture. The fix for those is mechanism, not more prose (`resources/testing-methodology.md`).

Record the agent's return verbatim: in the ledger when short, in a `docs/ledgers/` file when long. Scratchpad files do not survive the session.

## 6. Ledger, hand-off, close-out

Write the ledger to the owning bd issue's notes before handing over:

```
LEDGER (<date>): Evidence — <verbatim observation and where it is recorded>.
Baseline — none run (author-editor) | <the live use or fixture, one line>.
Edits by file — <file>: <what changed>; ...
Editor pass — own pass clean | <fresh-agent pass: N edits returned, M applied, declines one line each>.
Spot check — <result> | none needed.
Version — <old> -> <new>.
```

Hand the diff to the user. They edit; you do not commit until they say so. Their approval of the diff is the gate for an author-editor build. On their word: commit, merge or push as they direct, `bd close` with a reason naming the approval, and the bd sync commit. `hyperpowers:finishing-a-development-branch` is not the close-out for these builds; its gate is the end-of-epic reviewer, which did not run.

The loop stays human-routed. Ledgers inform the author; nothing edits skills autonomously.
</the_process>

<skill_structure>
**Frontmatter:** only `name` and `description`, 1024 characters together. Name uses letters, numbers, and hyphens. Description starts with "Use when", is in the third person, and carries the triggers an agent would search for: symptoms, error strings, tool names.

```yaml
# ❌ Too abstract, first person
description: I can help with async tests when they're flaky

# ✅ Triggers, problem, what the skill does
description: Use when tests have race conditions or pass/fail inconsistently - replaces arbitrary timeouts with condition polling
```

**Sections, in XML tags:** `skill_overview` (one sentence), `rigidity_level` (LOW, MEDIUM, or HIGH FREEDOM and what that means), `quick_reference` (a scannable table), `the_process`, `examples` (two or three `<example>` blocks showing a failure mode and its correction), `critical_rules`, `verification_checklist`, `integration`, `resources`.

**Length:** no word budget. Every sentence passes the four reader questions or goes. Heavy reference (an API surface, a long method) moves to a `resources/` file linked from the skill.

**Cross-references:** by `hyperpowers:<skill>` name or by repo path. Never `@` links; they force-load the file.
</skill_structure>

<examples>
<example>
<scenario>An edit from a hypothesis</scenario>

<code>
# Lead, mid-session:
"Executors probably skip the Verification section when the spec is long.
I'll add a MUST line to executor.md."
</code>

<why_it_fails>
- Nothing happened. No executor was seen skipping anything.
- The MUST line costs every future executor a sentence to guard a failure nobody recorded.
- If the failure is real, the first observation would also say which spec shape triggers it, and the fix would target that.
</why_it_fails>

<correction>
Record the hypothesis as a question in the gate-state's Needs-you section. Make no edit. When an executor return or a Stage-2 finding shows the skip, quote it and edit then.
</correction>
</example>

<example>
<scenario>A subagent loop in place of authoring</scenario>

<code>
# Lead, with the observation in hand:
"I'll have a Sonnet agent run the pressure scenario without the new
paragraph, then with it, and keep iterating until it complies."
</code>

<why_it_fails>
- The observation was a long-session failure; the short fixture passed before the edit too, so GREEN proves rendering, not the fix.
- Rounds of a weaker reader shape the prose toward that reader's rationalizations instead of toward the principle.
- bd-3ahi spent about 1.2M subagent tokens this way; a lead-direct trim of the same step from 3119 to 970 words kept every capability.
</why_it_fails>

<correction>
Author the paragraph for the agent that will read it. Run your editor pass. If, after reading, you genuinely cannot say what the agent will do, run one live use and record its return verbatim.
</correction>
</example>

<example>
<scenario>Qualifying a wrong sentence</scenario>

<code>
# Existing rule:
"Stage 2 runs a full code-quality review after every task."
# Observation: 26 Sonnet per-task reviews blocked nothing behavioral.
# Proposed edit:
"Stage 2 runs a full code-quality review after every task, except that on
simple tasks it may be abbreviated when the lead judges the risk low."
</code>

<why_it_fails>
- The sentence the observation falsified is still there, now with a branch hanging off it.
- The branch asks the lead for a judgment call the observation already settled.
</why_it_fails>

<correction>
Cut and replace: "Stage 2 is an outcome check: spec-match, the tests the spec names, and the lead's questions. Full code quality runs on `Review: full` tasks." One unconditional rule, the flag carrying the exception.
</correction>
</example>
</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **No edit without a recorded observation, quoted verbatim** → a hypothesis is a question for the user, not an edit
2. **The lead authors** → subagents have three jobs: the fresh-agent editor pass, one live use or fixture when behavior is genuinely uncertain, the A/B probe when removing a guard
3. **One home per rule** → every other site cites by path; nothing restates
4. **Cut, never extend** → a sentence an observation falsified is removed, not qualified
5. **The user is the editor and the gate** → the diff is handed over; commit only on their word

## Common Excuses

The excuses this method invites are catalogued in `skills/common-patterns/common-rationalizations.md` (Skill Authoring Shortcuts). All of them mean: **STOP. Find the observation, or author the text yourself.**
</critical_rules>

<verification_checklist>
Before handing over the diff:

- [ ] Ledger's Evidence line quotes a recorded observation and names where it is recorded
- [ ] Every file the change touches was read from the working tree before editing
- [ ] The rule has one home; the grep for its key phrase shows only the home and citations
- [ ] Each sentence passed the four reader questions
- [ ] Nothing was qualified where it should have been cut
- [ ] New skill or rewritten section follows the structure rules (frontmatter, description format, sections)
- [ ] Behavior check run only where behavior was genuinely uncertain, at most once per changed behavior, return recorded verbatim
- [ ] Ledger written to the owning bd issue's notes with all six lines
- [ ] Diff handed to the user; no commit without their word

**Can't check all boxes?** Return to the step that fails.
</verification_checklist>

<integration>
**This skill requires:**
- `skills/common-patterns/prose-style.md` (cut-never-extend, cite-never-restate, the reader)
- Agent tool, for the three subagent jobs only

**This skill is called by:**
- `hyperpowers:using-hyper` routing row "Creating or editing skills"
- `hyperpowers:brainstorming` Step 6b, when the epic's artifacts are prose
- Anyone editing a skill, agent prompt, or common pattern

**Agents used:**
- general-purpose on the session model, for the fresh-agent editor pass and for live uses
</integration>

<resources>
- [Behavior checks and the A/B method](resources/testing-methodology.md) - when a fixture is warranted by skill type; bulletproofing as authoring guidance; the A/B re-baselining method for removing guards
- [Anthropic best practices](anthropic-best-practices.md) - official skill authoring guidance
- [Persuasion principles](persuasion-principles.md) - why counters to rationalization work
- [Graphviz conventions](graphviz-conventions.dot) - flowchart style rules

**When stuck:**
- No observation but the text feels wrong → write the question in the gate-state and ask the user
- Cannot tell what the agent will do → one live use, working tree by path, return recorded verbatim
- The edit touches a rule in several files → find the home first; the other files become citations
- The fresh-agent pass returned severity findings → it was dispatched wrong; re-dispatch asking for line edits and cuts
</resources>
