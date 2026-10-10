# bd-62ow live use — standalone fact-or-fiction against this repo (2026-10-10)

Dispatch: fresh general-purpose subagent on the session model; skill read from the working tree by path; Focus: none; no bd writes. Run cost: 354,556 subagent tokens, 78 tool uses, 1,816 s (~30 min).

Return line (verbatim):

```
CRITIQUE: 6 findings (1 problem, 5 incidental) — report: <scratchpad>/fact-or-fiction-2026-10-10/report.md
```

Report file (verbatim):

# fact-or-fiction critic — hyperpowers plugin (/Users/abugosh/g/hyperpowers), standalone, focus: none (hotspots decide) — 2026-10-10

## Targets

Declared intent read: docs/arch/adr/adr-001.md, adr-002.md, adr-003.md (all accepted). No architecture model (`docs/arch/*.c4` absent).

Change evidence: `Analyzed 408 commits (excluded 6 bulk, 0 generated-only, 0 manifest-only); dropped as ritual: .beads/issues.jsonl (tracker export, 355), .claude-plugin/plugin.json (version field, 57), .beads/.migration-hint-ts (22), .beads/interactions.jsonl (8), .claude/agent-memory/*/MEMORY.md (agent memory, 4+3)`. 402 kept commits — above the warn threshold. Window: last 6 months to HEAD 2026-10-06; the working tree (uncommitted fact-or-fiction addition and its edits) is read as it stands.

Hotspots ranked by change count x size (lines / words). The top 20 non-ritual files carry 63% of 591 file-changes; change is spread thin, so the read list covers the pipeline spine plus its single-source files.

| # | File | Changes (6 mo) | Lines / words | Read |
|---|------|----------------|---------------|------|
| 1 | CLAUDE.md | 35 | 378 / 4031 | read closely |
| 2 | skills/executing-plans/SKILL.md | 32 | 525 / 5427 | read closely |
| 3 | skills/brainstorming/SKILL.md | 32 | 513 / 4731 | read closely |
| 4 | README.md | 29 | 229 / 2233 | read closely |
| 5 | skills/peek/SKILL.md | 28 | 262 / 5684 | read closely |
| 6 | skills/common-patterns/loop-interfaces.md | 21 | 166 / 1382 | read closely |
| 7 | skills/sre-task-refinement/SKILL.md | 20 | 761 / 5534 | read closely |
| 8 | skills/common-patterns/pipeline-constants.md | 16 | 231 / 1888 | read closely |
| 9 | skills/writing-plans/SKILL.md | 15 | 506 / 2897 | read closely |
| 10 | agents/peek.md | 15 | 290 / 5364 | read closely |
| 11 | skills/managing-bd-tasks/SKILL.md | 15 | 688 / 3132 | not read — bd mechanics recipes; its change rides bd CLI changes, not the pipeline's design |
| 12 | skills/using-hyper/SKILL.md | 14 | 109 / 1088 | read closely |
| 13 | skills/opt/SKILL.md | 14 | 279 / 5194 | read closely |
| 14 | agents/reviewer.md | 14 | 259 / 2695 | read closely |
| 15 | skills/intuition/SKILL.md | 13 | 904 / 7913 | read closely |
| 16 | skills/analyzing-test-effectiveness/SKILL.md | 13 | 569 / 3596 | not read — off the pipeline spine; time spent on the shared vocabulary files instead |
| 17 | skills/preordain/SKILL.md | 11 | 295 / 2160 | not read — same reason |
| 18 | skills/common-patterns/forge-detection.md | 11 | 426 / 4032 | read closely |
| 19 | skills/common-patterns/common-rationalizations.md | 11 | 155 / 1786 | not read — catalog; rows are earned per observation and change by accretion |
| 20 | agents/executor.md | 11 | 107 / 1266 | read closely |
| — | agents/code-reviewer.md, skills/common-patterns/spec-templates.md | 7, 6 | small | read closely (the Stage-2 and spec contracts the spine cites) |
| — | skills/review-implementation, finishing-a-development-branch, consider, ponder, hooks/, docs/ledgers/ | <=9 | — | not read — below the hotspot line |

## Working Findings

### W1. Each rule is stored once as a definition and many times as copies that carry its values

**Braid:** a rule's value (a round cap, a model tier, a verdict word, a rigidity level, a qualifier-line name) is braided with every summary that orients a reader to it. The summaries are CLAUDE.md, README's skill/command/agent lists, using-hyper's routing and rigidity lists, command and frontmatter descriptions, sibling skills' handoff texts, and inside each skill its quick-reference table, critical rules, rationalizations, verification checklist, and integration "Flow". Every one of those is a place; a change to the value has to replace old information in each.

**Cost (change counts):**
- 43 of the 279 commits in the last 6 months that touched a non-ritual file have a subject naming a copy-sync (sweep, align, stale, wire, consistency, restate, agree, contradict). A few of the "wire" subjects are design work, so read 43 as an upper bound.
- CLAUDE.md is the most-changed file (35); README 29; 22 commits touch both. All 8 epic commits since the move to one commit per epic (d5377d4 v3.39.0 through 4f35057 v3.46.0) edited CLAUDE.md, and 6 of 8 edited README.
- Inside skills: across the six largest skills, 57 of 139 commits edited checklist items alongside the process text (peek 13/28, executing-plans 16/32, brainstorming 12/32, sre-task-refinement 7/20, opt 5/14, intuition 4/13). Peek's quick-reference rows were edited in 13 of the 27 commits after the file was created; 66362b5's subject opens "row 7 phase-B qualifier restored", a summary row edited alongside the paragraph it summarizes.
- The uncommitted fact-or-fiction addition edits CLAUDE.md (2 hunks), README (2 lists), using-hyper's routing table, and commands/intuition.md beyond the skill itself.

**Copies that have already drifted (the cost when a sync is missed):**
- `skills/using-hyper/SKILL.md:88` lists executing-plans under "LOW FREEDOM (follow exactly)"; `skills/executing-plans/SKILL.md:11` says "MEDIUM FREEDOM" and has since e75e436 (2026-04-01). The using-hyper line dates from bf93ceb (2026-07-06), and using-hyper is injected into every session.
- `CLAUDE.md:99` lists the agents directory without peek; `agents/peek.md` exists and CLAUDE.md's own Agent System section (item 8) describes it.
- `skills/intuition/SKILL.md:757` (Rule 9) and the Pass 7-9 formats (`:363`, `:404`, `:463`) still carry "Analysis Pass:"; the report format at `:560` replaced it with "Found by:".

**Values copied out of their declared home:** "Sonnet by default" at `CLAUDE.md:154`, `:166`, `:204`, `README.md:22`, `:86`, `:178`, `commands/execute-plan.md:7`. The round cap "2" appears five times in `skills/executing-plans/SKILL.md` (`:25`, `:194`, `:368`, `:482`, `:492`) and at `README.md:22`, `CLAUDE.md:166`, `:204`, while `skills/common-patterns/pipeline-constants.md:64-66` calls itself the "Single source for this constant". `skills/writing-plans/SKILL.md` cites pipeline-constants.md 11 times, and several of those citations say not to restate it.

**Problem or incidental:** incidental. The need behind the summaries is real: a cold reader (a GitHub visitor, a session improving the plugin, an agent deep in a long skill) needs orientation, and an agent needs a pre-return checklist. Neither needs the copy to carry the value. Orientation needs a name, a role, and a pointer; a checklist can check the decision ("round cap respected, `pipeline-constants.md`") without the number. The user's own memory already treats these summaries as untrusted ("pointers aren't contracts").

**ADR context:** ADR-001 (T8) accepted CLAUDE.md and README restating pipeline semantics, pending post-rework change rates, with the trigger "the next /intuition audit run after meaningful non-rework history has accumulated". Since it was accepted (054f546, 2026-07-07), 232 commits have landed and 18 of them edited CLAUDE.md. The non-rework history the deferral waited for now exists, and the co-change it accepted has continued at about the same rate: 17 CLAUDE.md edits in the window's 11 weeks before the ADR (from 2026-04-19), 18 in the 13 weeks after. The ADR names an /intuition run as the re-examination point; this critique is not that run, but the counts above are the evidence that run would read.

**Simpler shape:** summaries carry names, roles, and pointers, never values. CLAUDE.md's Agent System and Core Workflows say what each piece is for and where its contract lives. README lists each skill with its frontmatter description. A skill's quick-reference table names its steps. Checklists check decisions by reference. using-hyper drops its rigidity list, since its own next line ("Each skill declares its own `<rigidity_level>` — check it") already does the job.

**Lean:** do it. Start with CLAUDE.md and README, which every epic commit pays for, and with using-hyper's rigidity list, which is wrong today and loaded every session. Keep each skill's critical rules as the one deliberate restatement: the user's memory records that the hard rules are load-bearing at the point of use. Strip values from everything else. It trades away the at-a-glance mechanics a cold reader gets from CLAUDE.md today; a reader who wants them opens the skill, which the user's memory already tells them to do.

**Evidence:** files and lines above; the counts come from the change-history recipe and from `git log --format=%s` over the same 6-month window.

### W2. The shared contract files carry their consumers' procedures and rosters, so a change in one consumer edits the shared file

**Braid:** a shared definition (severity tiers, a verdict vocabulary, a template) braided with knowledge of who uses it and how each user bends it. The shared file becomes the place where every consumer's special case lives.

- **Severity Anchor** (`skills/common-patterns/pipeline-constants.md:68-159`) names its consumers and their exemptions in their own process terms: peek's aims table ("the aims table row reads `missing`", `:91-94`), peek's synthesizing lead and Stance (`:131-132`), a pointer into `agents/peek.md` Shared Rule 3 (`:89`), opt's receiving-side exemption (`:151-156`), the in-epic judges' "no Critical tier" paragraph (`:138-149`), and peek's draft-comment follow-up split (`:153-156`). The Peek Fix Carve-out beside it (`:161-187`) also carries opt's Tier-1 reuse (`:166-169`).
- **Verdict Contracts** (`skills/common-patterns/loop-interfaces.md:74-166`) carries derivation procedure, not just vocabulary: how peek's synthesis derives its verdict (`:126-135`), the rule for when peek's Path is `rework` (`:136-148`), and which opt dispositions the lead may propose (`:149-161`).
- **Consumer rosters inside definitions:** `skills/common-patterns/prose-style.md:154-156` (12 named consumers), `skills/common-patterns/forge-detection.md:12` and `:328-330`, `skills/common-patterns/spec-templates.md:4-5`, `skills/common-patterns/change-history.md:4-5`, and `skills/common-patterns/report-file-contract.md:37-39` ("cite this file from its agent or skill and from every dispatch site").

**Cost (change counts):**
- pipeline-constants.md: every one of its 10 commits since 2026-08-26 edited the Severity Anchor or the Carve-out beside it, driven by peek (15a6425, 7bdcb0c, b7bfa37, ec661a4, ff58f4e, f7b4d96), by opt (b3a7b33, subject: "Severity Anchor and Peek Fix Carve-out acknowledge opt as second consumer"), and by the in-epic judges (49aa42c, fe2bf2c, 4a15aec).
- loop-interfaces.md: 9 of its 21 commits register or re-scope peek or opt vocabulary. Two of them only keep the file's description of itself true after a consumer arrived: 1f4c943 drops "(lead ↔ agent)" from the heading, and 9add6cc updates the intro's count of vocabularies. Two more, 52c0154 and 5440129, re-wrap the same peek-derivation sentence back and forth because a grep anchor elsewhere depends on its line breaks.
- Rosters drift: `spec-templates.md:4-5` names four consumers, but eleven files cite it, including `agents/reviewer.md:97`, `skills/executing-plans/SKILL.md`, `skills/analyzing-test-effectiveness/SKILL.md:139`, and `skills/managing-bd-tasks/SKILL.md:54`. The uncommitted change edits `prose-style.md:156` and `forge-detection.md:329` only to add fact-or-fiction to their rosters.

**Problem or incidental:** incidental. The domain has a real shared core: three tiers, the two qualifier lines (`Hits:`, `Maintainer cost:`), the `Contract:` opener, and verdict words that parse sites must match exactly. The per-consumer clauses are each consumer's own process, and they move at that consumer's rate. A roster is a fact `grep -rl` computes; stored as text, it goes stale.

**Simpler shape:** the shared file states the value in terms of the finding, never in terms of a consumer's step: the tier definitions, what fills each line, and the verdict words with their parse rule. Each consumer states its own use. Peek's skill says a `missing` aim becomes a delivery-class Critical and how synthesis files it. Opt's skill says severity weights triage. The in-epic judges say they have no Critical tier. Peek's skill owns its verdict and Path derivation. Rosters are deleted; `grep -rl <file> skills agents` is the roster.

**Lean:** do it, for the Severity Anchor and the Verdict Contracts first, because that is where the cost lands. It trades away one place to read every consumer's severity semantics side by side. It also drops the roster's job of reminding an editor whom to update; grep does that job better, as the spec-templates roster, missing four consumers, shows. W3 below is the other half: the anchor speaks each consumer's dialect partly because the record it grades has a different shape at every consumer.

**Evidence:** lines above; commit lists from `git log -- <file>` over the 6-month window; each commit's hunk headers confirm the section it edited.

### W3. One noun, the review finding, has a different record shape at every surface that produces one

**Braid:** what a finding *is* (where, what is claimed, the evidence, its class, the one qualifier line that justifies it, its tier) is braided with each producer's template. No surface shares a record; each re-specifies the same core fields in its own order and under its own names.

- Peek lens finding: a 13-field multi-line record, written out three times verbatim in one file (`agents/peek.md:131-147` CODE, `:189-204` ARCHITECTURE, `:248-262` DELIVERY), with the same field-presence sentence three times (`:149`, `:206`, `:265`) and the same Questions template three times (`:151-161`, `:208-217`, `:267-277`).
- Stage-2 concern: one line, `[class] <file>:<line> — <Contract:|Hits:|Maintainer cost:> what and why` (`skills/common-patterns/loop-interfaces.md:98-103`, restated at `agents/code-reviewer.md:33`).
- End-of-epic gap: `[class] [what] — Contract:|Hits:|Maintainer cost: … — Evidence: [file:line]` (`agents/reviewer.md:145`). It carries the same fields as the Stage-2 line, in a different order, with the location moved into Evidence.
- Opt finding record: `F<n> | thread | reviewer / claim / location / class / severity` (`skills/opt/SKILL.md:80-86`).
- Intuition tension: two shapes inside one file. The Pass 7-9 formats use "Analysis Pass:" and "Pull A/B" (`skills/intuition/SKILL.md:361-369`, `:401-415`); the report format uses "Found by:" and "Pull 1/2" (`:558-567`).

The names drift with the shapes: Defect / claim / what; Location / location / `<file>:<line>`.

**Cost (change counts):** 31 commits in the 6-month window changed lines carrying the finding's fields (`Hits:`, `Maintainer cost:`, `Contract:`, the class tags; `git log -G`). Bringing the in-epic judges under one bar (49aa42c, bd-1hm5) rewrote `agents/code-reviewer.md` (62 lines), `agents/reviewer.md` (318), and `agents/test-effectiveness-analyst.md` (218), plus loop-interfaces, pipeline-constants, and executing-plans. Adding the two qualifier lines (bd-3ahi) took ff58f4e (the anchor), 5393d04 (the peek agent's three copies), e13f540 and 9580af0 (peek's re-check), and then f7b4d96 ("one definition of filled") to reconcile what "filled" meant across them. The Severity Anchor has to say "its line opens `Contract:`" for one surface and "carries a `Critical class:` line" for another (`pipeline-constants.md:103-104`, `:139-141`), because it has no common record to talk about.

**Problem or incidental:** mostly incidental. Some difference between surfaces is the domain's. Stage 2 is one line so the lead's context does not fill with review bodies (`loop-interfaces.md:106-107`). Opt carries thread and reviewer because it answers threads. Peek carries Scope and Prior review because it weighs earlier review. Those are *extra fields*, not different shapes. Re-specifying the shared core at every site, in different orders and names, is the solution's addition.

**Simpler shape:** one finding record, defined once beside the Severity Anchor as named fields: location, claim, evidence, class, exactly one qualifier line, and tier where the surface has tiers. Each surface lists the extra fields it adds (peek: scope, prior review, trigger and consequence, direction; opt: thread, reviewer). Stage 2's line and the reviewer's gap entry become renderings of that record ("these fields, this order, one line"). `agents/peek.md` states its record once for all three lenses and says which extras each lens fills.

**Lean:** do the `agents/peek.md` part now: three verbatim copies of one template in one file is the cheapest win. Define the shared record the next time the Severity Anchor is touched, and let W2's rewrite speak in its fields. It trades away templates that each read standalone; today a lens or judge sees exactly what to write without a lookup. Stage 2's terseness also has to be kept on purpose, as a rendering rule, rather than falling out of its own template.

**Evidence:** lines above; the `git show --stat` sizes for 49aa42c; the bd-3ahi commit subjects.

### W4. Peek's severity re-check is ten special cases braided into one 391-word paragraph

**Braid:** the review's tier-calibration rules (condition, move, marker) are braided into one prose paragraph with their ordering and their exemptions, so an edit to any one rule is an edit inside all of them. `skills/peek/SKILL.md:127` holds, in one paragraph:
1. a Critical missing Trigger/Consequence drops to Important or Suggestion, by its line, with two markers;
2. a `[convention]` Critical takes the same two-stage drop, with two more markers;
3. an Important with no filled line drops to Suggestion;
4. a Suggestion that asks for no change moves to Questions or `Dropped:`;
5. a previously-reviewed finding without `Prior review:` moves to Questions;
6. a missing Scope defaults to delta;
7. a missing Class is assigned by the lead;
8. an aims-table `missing` row with no Critical becomes a lead-added Critical;
9. an undeclared reshape with no Critical becomes a lead-added Critical;
10. an aim finding above its row is corrected to the row.

The same paragraph also states the ordering (dedup first), the never-fill rule, and the lead-added exemption.

**Cost (change counts):** that one line was edited by 7 commits since 2026-07-24 (`git log -L127,127`): b317610, 8d92d07, dd2c606, 6ab4fc3, e13f540, 9580af0, f7b4d96. Three of them came in a single day of bd-3ahi, and 9580af0's subject ("name Trigger and Consequence in the lead-added rule") is a fix to one clause that lives mid-paragraph. Peek SKILL.md is the fifth-most-changed file (28) and carries 5684 words on 262 lines, so its lines are long; this one is the densest.

**Problem or incidental:** the rules are the domain's: calibrating severity against a published bar is real work. The shape is incidental. Most of the ten are instances of three principles, written out case by case:
- a finding lands at the highest tier whose required lines it fills, and a `[convention]` finding is never Critical (rules 1-3);
- what the aims table or the Stance requires and no lens filed, the lead files, and an aim finding never exceeds its row (rules 8-10);
- what asks no change or lacks its justification becomes a question (rules 4-5).
The rest are defaults (rules 6-7).

**Simpler shape:** the three principles stated once, then a closed table of moves and markers (condition | move | marker), so the markers stay exact and reviewable. The reason clauses ("so a Suggestion never rises above what its evidence supports") become one line under the table.

**Lean:** do it the next time Step 6 changes. It trades away the case-by-case spelling of the two-stage Critical drop, which today leaves the lead no room to read the principle differently in a corner case; the marker table carries that weight instead. This is the user's own principles-over-contingency-taxonomies move (the Step 7 trim, 2847687), applied to Step 6.

**Evidence:** `skills/peek/SKILL.md:127`; `wc -w` on that line; the commit list from `git log -L`.

### W5. The execution loop's escalation counts live only in the lead's context, and the model flag doubles as the record that a rung was spent

**Braid:** state and time braided into a place. The lead's escalation ladder counts events across a long session: BLOCKED returns per task and across tasks (`skills/executing-plans/SKILL.md:278-280`), capability fix rounds per task (`:194`), end-of-epic gap rounds (`:368`), whether the promotion rung was used (`:194`, `:261`), and each task's base commit (`:87-91`). None of these counts is written down as it happens. The only durable record is a gate-state block, written at gates (`skills/common-patterns/loop-interfaces.md:11-13`), plus a few prose notes (auto-promotion, retags, convention lead-fixes: `:191`, `:193`, `:194`, `:261`). The resume path reads open tasks and the latest gate-state (`:37`, `:70`) and recovers no count. Gap-round report files live in the session scratchpad (`:341`, `:345`), which the user's memory records does not survive between sessions.

Separately, "not already promoted" (`:194`, `:261`) reads the spec's `Executor: opus` line, which is the model choice. A task the planner promoted at spec time (`skills/common-patterns/pipeline-constants.md:192-193`) therefore enters the loop with its rung already counted as spent, and its first BLOCKED goes straight to the threshold count. "Which model" and "which rungs were used" are two facts stored as one.

**Cost (change counts):** latent, not observed. executing-plans is the second-most-changed file (32), and the counting rules took their own commits: 7ceffdf ("clarify BLOCKED counting rule"), c1a78a4 (round caps), 5994809 (round-cap escalation trigger), 5f160f2 (the closure path after CONCERNS). I found no recorded failure where a count was lost. The cost arrives the first time a long epic compacts the lead's context or resumes in a fresh session mid-ladder, which the user's four-lane operating mode makes ordinary.

**Problem or incidental:** problem. An executor that drifts and blocks needs bounded retries and a ladder, and ADR-003 records that the guard cluster is the interface's specification. The counts are the domain's. Keeping them only in context is the incidental part, so the lean contains rather than removes.

**Simpler shape:** each rung is an appended fact in the task's bd notes, in the same plain prose the loop already writes (`BLOCKED 1`, `capability round 2`, `promoted: lead, after BLOCKED`). Counts are derived by reading the notes, never held. "Promoted by the planner" and "the lead spent its rung" become two different notes.

**Lean:** do it the next time executing-plans changes. It is a few more `bd update --notes` lines per task. It trades away a small amount of bd note volume, which the user's memory caps at about 40KB per epic, for a ladder that survives compaction and resume. ADR-002's plain-prose bus is the right carrier, unchanged.

**Evidence:** lines above; commit subjects from `git log -- skills/executing-plans/SKILL.md`.

### W6. Two shared files are named and scoped for what they used to hold, and return lines have two homes

**Braid:** a file's name and opening sentence (what a reader looks for) braided with what it accreted. Separately, one kind of fact (a subagent's return-line format) is split across two homes by an incidental property.

- `skills/common-patterns/pipeline-constants.md:3-5` describes itself as "workflow sizing, classification, and executor routing", but 120 of its 231 lines (`:68-187`) are the severity policy and peek's fix authority. A reader looking for the review bar would not open a file called "constants".
- `skills/common-patterns/loop-interfaces.md:3-7` describes itself as the artifacts between a session and its governor and between a session and a planning layer. Its largest and most-changed section, Verdict Contracts (`:74-166`), is mostly subagent→lead and skill→user vocabularies.
- Return lines: `report-file-contract.md:18-26` registers every report-by-file return line, and `loop-interfaces.md` registers the verdict-bearing ones again. The reviewer line is verbatim in both (`loop-interfaces.md:110`, `report-file-contract.md:22`), and so is the SRE line (`:122`, `:23`). Each file states the split rule (`report-file-contract.md:28-31`, `loop-interfaces.md:163-166`). The split is by whether the line carries a verdict word, a property that decides how a lead *parses* the line, not where its format should live.

**Cost (change counts):** low. When the reviewer's return line moved to by-file delivery (2327663), both files changed: report-file-contract +100, loop-interfaces 24 lines. 2 of report-file-contract's 3 commits co-changed loop-interfaces. The names cost reading, not edits, and a rename would touch 22 files with 100 citations (pipeline-constants) and 20 files (loop-interfaces).

**Problem or incidental:** incidental.

**Simpler shape:** each return line's format lives once, in report-file-contract's table, which already has the column. loop-interfaces keeps what each verdict word means and the governor artifacts its opening sentence names. Both files' opening sentences say what they now hold.

**Lean:** fix the two opening sentences and drop the duplicated lines from loop-interfaces as part of W2's rewrite. Do not rename: 100 citations is a real cost for a name, and the opening sentence is what a reader reads first. Here the easy choice, keeping the names, is the better trade. It trades away seeing a verdict word and its exact line in one place; that becomes two lookups.

**Evidence:** lines above; `grep -rl` counts over `skills agents commands CLAUDE.md README.md`; `git show --stat 2327663`.

## Critique: the hyperpowers plugin (whole repository, targeted by change history)

*One critic's read through Hickey's lens: opinions with evidence. The architect decides.*

**The read:** The parts that carry information between agents are simple, and I would keep them as they are: a subagent hands back a file and one line, the task tracker (bd) holds plain prose a person can read (ADR-002), and forge commands live in one lookup file. The system pays where a rule is told more than once. Summaries and checklists copy a rule's values, the shared contract files carry each consumer's special cases, and a review finding has a different shape at every surface that produces one, so a large share of each change goes to keeping copies in agreement. Nearly all of that cost is in how the plugin describes itself, not in the workflows it runs.

### Findings, ordered by cost

#### 1. A rule's value is copied into every summary of it, so each change is paid once per copy

**Costs:** The repository's instructions file for sessions working on the plugin (CLAUDE.md) is the most-changed design file: 35 changes in 6 months, 22 of them together with README. All 8 epic commits since v3.39.0 edited CLAUDE.md, and 6 of the 8 edited README. Across the six largest skills, 57 of 139 commits edited checklist items alongside the process those items check. Up to 43 of 279 commit subjects name a copy-sync (sweep, align, stale, wire, consistency). Copies that missed a sync are wrong today. The routing skill injected at every session start (using-hyper) tells every session that the execution skill (executing-plans) is follow-exactly, while that skill calls itself medium freedom.
**Problem or incidental:** Incidental. Cold readers need orientation and agents need a pre-return checklist, but neither needs the copy to hold the value. A name, a role, and a pointer orient a reader; a checklist can check a decision by reference. ADR-001 accepted this restatement until non-rework history built up. That history now exists (232 commits since the ADR, 18 of them to CLAUDE.md), and the co-change the ADR accepted has gone on at about the same rate.
**Simpler shape:** Summaries carry names, roles, and pointers, never values: no model tiers, round caps, verdict words, or line names outside their home file. CLAUDE.md says what each piece is for and where its contract lives. README lists each skill by its own description. A skill's quick-reference table names its steps. A checklist checks decisions by reference. The routing skill drops its list of rigidity levels.
**Lean:** Do it. Start with CLAUDE.md and README, which every epic pays for, and with the routing skill's rigidity list, which is wrong now and loaded every session. Keep each skill's critical rules as the one deliberate restatement, since the hard rules matter most where the agent reads them. It trades away the mechanics a cold reader gets at a glance from CLAUDE.md today.
**Evidence:** `skills/using-hyper/SKILL.md:88` against `skills/executing-plans/SKILL.md:11` (MEDIUM since e75e436, 2026-04-01; the using-hyper line from bf93ceb, 2026-07-06). `CLAUDE.md:99` omits `agents/peek.md`. `skills/intuition/SKILL.md:757`, `:363`, `:404`, `:463` keep "Analysis Pass:" after `:560` moved to "Found by:". "Sonnet by default" appears at `CLAUDE.md:154`, `:166`, `:204`, `README.md:22`, `:86`, `:178`, `commands/execute-plan.md:7`. The round cap appears at `skills/executing-plans/SKILL.md:25`, `:194`, `:368`, `:482`, `:492`, against `skills/common-patterns/pipeline-constants.md:64-66` ("Single source for this constant"). Peek's quick-reference rows were edited in 13 of its 27 post-creation commits. The uncommitted fact-or-fiction addition edits CLAUDE.md, README (two lists), the routing table, and `commands/intuition.md`. ADR-001 (T8).

#### 2. The shared contract files carry each consumer's own procedure, so a change in one consumer edits the shared file

**Costs:** All 10 commits since 2026-08-26 to the shared pipeline-values file (pipeline-constants.md) edited its severity section or the fix-authority section beside it. Six were driven by branch review (peek), one by review response (opt), and three by the per-task and end-of-epic reviewers. One commit's whole subject is "acknowledge opt as second consumer". 9 of 21 commits to the shared handoff-formats file (loop-interfaces.md) register or re-scope peek's or opt's vocabulary, and two of those only kept the file's description of itself current. Consumer lists stored inside definitions go stale: the spec-template file names 4 consumers, and 11 files cite it.
**Problem or incidental:** Incidental. The shared core is real: three tiers, two qualifier lines, a contract-miss opener, and verdict words that parse sites must match. Each consumer's clauses, though, move at that consumer's rate: peek's aims table and synthesis, opt's receiving side, the in-epic reviewers' missing top tier. A consumer list is a fact `grep -rl` computes.
**Simpler shape:** The shared file defines tiers, lines, and verdict words in terms of the finding, never in terms of a consumer's step. Each consumer states its own use and owns its own derivation; peek's verdict and Path rules move into peek. Consumer lists are deleted.
**Lean:** Do it, with the severity section and the verdict registry first. It trades away one place to read every consumer's severity semantics side by side. It also drops the consumer list's reminder of whom to update, which grep gives exactly.
**Evidence:** `skills/common-patterns/pipeline-constants.md:89`, `:91-94`, `:131-132`, `:138-149`, `:151-156`, `:166-169`. `skills/common-patterns/loop-interfaces.md:126-135`, `:136-148`, `:149-161`. Consumer lists at `skills/common-patterns/prose-style.md:154-156`, `forge-detection.md:12`, `:328-330`, `spec-templates.md:4-5`, `change-history.md:4-5`. Commits 15a6425, 7bdcb0c, b7bfa37, ec661a4, ff58f4e, f7b4d96, b3a7b33, 49aa42c, fe2bf2c, 4a15aec; 1f4c943 and 9add6cc (self-description); 52c0154 and 5440129 re-wrap the same peek sentence back and forth to keep a grep anchor intact.

#### 3. A review finding has a different record shape at every surface that produces one

**Costs:** 31 commits in 6 months changed lines carrying a finding's fields. Putting the per-task and end-of-epic reviewers under one bar (49aa42c) rewrote three agent templates (62, 318, and 218 lines). Adding the two qualifier lines to branch review took four commits, then a fifth ("one definition of filled") to reconcile what "filled" meant across surfaces. The branch-review agent writes the same 13-field template out three times.
**Problem or incidental:** Incidental, for the most part. Some differences are the domain's. The per-task review stays one line to keep the lead's context small, review response carries thread and reviewer, and branch review weighs earlier review. Those are extra fields, though. The shared core (location, claim, evidence, class, one qualifier line, tier) is re-specified at each site in a different order and under different names (Defect, claim, what).
**Simpler shape:** One finding record, defined once beside the severity section. Each surface lists the fields it adds. The one-line per-task form and the end-of-epic gap entry are renderings of it, and the branch-review agent states its record once for all three of its reviewers.
**Lean:** Collapse the three copies in the branch-review agent now. Define the shared record the next time the severity section changes, so that finding 2's rewrite has fields to talk about. It trades away templates that each read standalone, and the one-line form's terseness has to be kept as an explicit rendering rule.
**Evidence:** `agents/peek.md:131-147`, `:189-204`, `:248-262` (and `:149`, `:206`, `:265`). `skills/common-patterns/loop-interfaces.md:98-103`; `agents/code-reviewer.md:33`; `agents/reviewer.md:145`; `skills/opt/SKILL.md:80-86`; `skills/intuition/SKILL.md:361-369` against `:558-567`; `skills/common-patterns/pipeline-constants.md:103-104`, `:139-141`. Commits 49aa42c, ff58f4e, 5393d04 (the same two lines added three times), e13f540, 9580af0, f7b4d96.

#### 4. Branch review's severity re-check is ten special cases written as one paragraph

**Costs:** That paragraph (391 words, one line of the file) was edited by 7 commits since 2026-07-24. Three of those came on one day, and one was a fix to a single clause in the middle of the paragraph. Its skill file is the fifth-most-changed in the repository (28 changes).
**Problem or incidental:** Incidental in shape; the calibration rules themselves are the domain's. Most of the ten cases are three principles written out case by case. First, a finding lands at the highest tier whose required lines it fills, and a style-class finding is never top tier. Second, what the aims table or the structural stance requires and nobody filed, the lead files, never above its row. Third, a finding that asks for no change, or lacks its justification, becomes a question.
**Simpler shape:** The three principles stated once, then a closed table of condition, move, and marker.
**Lean:** Do it the next time that section changes. It is the same principles-over-cases move already made to the gate section that follows it (3119 → 972 words). It trades away the spelled-out two-step demotion paths; the marker table pins the outcomes instead.
**Evidence:** `skills/peek/SKILL.md:127`. `git log -L127,127` lists b317610, 8d92d07, dd2c606, 6ab4fc3, e13f540, 9580af0, f7b4d96. The earlier trim is 2847687.

#### 5. The execution loop's escalation counts live only in the lead's memory, and the model flag doubles as the record of a used rung

**Costs:** Latent: no lost count is on record. The execution skill is the second-most-changed file (32), and its counting rules took their own commits (BLOCKED counting, round caps, the round-cap trigger, closure after concerns). The loop counts BLOCKED returns per task and across tasks, fix rounds, gap rounds, and promotion. None of those counts is written down as it happens, so a resumed session reads the open tasks and the last gate-state and recovers no count. A task the planner put on the stronger model enters the loop with its promotion rung already counted as used.
**Problem or incidental:** Problem. An executor that drifts and blocks needs bounded retries, and ADR-003 records the guard cluster as the specification of that interface. Holding the counts only in context is the incidental part, so the lean contains the complexity rather than removing it.
**Simpler shape:** Each rung is an appended prose note on the task (`BLOCKED 1`, `capability round 2`, `promoted: lead, after BLOCKED`), and the counts are derived from the notes. "The planner chose the model" and "the lead used the rung" become separate facts.
**Lean:** Do it the next time the execution skill changes. It trades a few more tracker note lines per task for a ladder that survives compaction and resume, on the plain-prose bus ADR-002 already chose.
**Evidence:** `skills/executing-plans/SKILL.md:37`, `:70`, `:87-91`, `:194`, `:261`, `:278-280`, `:341`, `:345`, `:368`; `skills/common-patterns/loop-interfaces.md:11-13`; `skills/common-patterns/pipeline-constants.md:192-193`. Commits 7ceffdf, c1a78a4, 5994809, 5f160f2.

#### 6. Two shared files are named for what they used to hold, and return-line formats have two homes

**Costs:** Low. The end-of-epic reviewer's and the plan reviewer's return lines are stated verbatim both in the report-delivery contract and in the handoff-formats file, and the one change to the reviewer's line (2327663) edited both. The pipeline-values file says it holds sizing, classification, and routing, but 120 of its 231 lines are review severity and fix authority. The handoff-formats file says it holds session-to-governor artifacts, but its largest section is agent-to-lead verdicts.
**Problem or incidental:** Incidental. Whether a return line carries a verdict word decides how the lead parses it, not where its format should live.
**Simpler shape:** Every return line's format lives once, in the report-delivery contract's table. The handoff-formats file keeps what each verdict word means, and both files' opening sentences say what they now hold.
**Lean:** Fix the two opening sentences and drop the duplicate lines as part of finding 2's rewrite. Do not rename either file: 22 and 20 files cite them, and the opening sentence is what a reader meets first. Keeping the names is the easier choice and here the better trade. It trades away seeing a verdict word and its exact line in one place.
**Evidence:** `skills/common-patterns/loop-interfaces.md:3-7`, `:110`, `:122`, `:163-166`; `skills/common-patterns/report-file-contract.md:22`, `:23`, `:28-31`; `skills/common-patterns/pipeline-constants.md:3-5`, `:68-187`. `git show --stat 2327663` shows report-file-contract +100 and loop-interfaces 24 lines. 22 files cite pipeline-constants.md (100 citations) and 20 cite loop-interfaces.md.

### Critique Outcome
**Findings:** 6 (1 problem, 5 incidental)
**Read closely:** CLAUDE.md; README.md; skills/executing-plans, brainstorming, peek, sre-task-refinement, writing-plans, using-hyper, opt, intuition (each SKILL.md); agents/peek.md, reviewer.md, executor.md, code-reviewer.md; skills/common-patterns/pipeline-constants.md, loop-interfaces.md, forge-detection.md, spec-templates.md, report-file-contract.md, prose-style.md, change-history.md; docs/arch/adr/adr-001.md through adr-003.md. No architecture model exists to read.
**Not read:** skills/managing-bd-tasks (15 changes; bd command mechanics that change with the tracker's CLI); skills/analyzing-test-effectiveness (13) and skills/preordain (11), which are off the main build pipeline; common-rationalizations.md (11), a catalog that grows one row at a time; skill examples files; everything at 9 changes or fewer (review-implementation, finishing-a-development-branch, consider, ponder, hooks/, docs/ledgers/). Findings 1 and 2 likely extend into the unread skills, but their checklists and consumer lists were not counted.
**Change evidence:** Analyzed 408 commits (excluded 6 bulk, 0 generated-only, 0 manifest-only); dropped as ritual: .beads/issues.jsonl, .claude-plugin/plugin.json, .beads/.migration-hint-ts, .beads/interactions.jsonl, .claude/agent-memory/*/MEMORY.md
