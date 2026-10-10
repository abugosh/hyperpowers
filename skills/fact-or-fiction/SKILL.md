---
name: fact-or-fiction
description: Use when a design feels more complicated than it should, when you want Rich Hickey's lens on a codebase (simple vs easy, what is complected, values vs places, information vs mechanism, incidental complexity, one language of the system), or as intuition's second read before resolving tensions - an opinionated critique that reads the code where change is frequent, ranks findings by what the complexity costs, and says what it would do
---

<skill_overview>
An opinionated design critique through Hickey's lens: it reads what the code means — its data shapes, names, and nouns — where change is most frequent, says which complexity is incidental, ranks it by what it costs, and leans; the architect decides.
</skill_overview>

<rigidity_level>
HIGH FREEDOM — The lens is a set of principles applied with judgment; there are no passes and no checklist of smells. Fixed: the dispatch, the report shape, the voice rules, and the pick-list exit.
</rigidity_level>

<quick_reference>
| Step | Who | Action | Deliverable |
|------|-----|--------|-------------|
| Dispatch | Lead | Fresh subagent; focus, or intuition's report when chained | One return line |
| 1 Prepare | Critic | Start the report file; read declared intent (ADRs, model) | File started |
| 2 Target | Critic | Hotspots from change history, or intuition's evidence when chained | Read list |
| 3 Read and judge | Critic | Close reading with the lens; each finding written as it completes | Findings on disk |
| 4 Assemble | Critic | The read, findings ordered by cost, Critique Outcome | Report complete |
| 5 Present and pick | Lead | Present verbatim; route the findings the architect picks | Issues or handoffs |

**This is not intuition.** Intuition reads structure from outside — the dependency graph, request paths, change rates — and presents both pulls of every tension without a preference. This skill reads the design's ideas and takes a side. Each runs alone; chained, this one gives intuition's tensions a lean before the architect resolves them.
</quick_reference>

<when_to_use>
- The design feels heavier than the problem it solves
- You want a Hickey review of a codebase or one area of it
- After an epic lands, to see what it cost the design
- From intuition's Step 4, as a second read on its tensions

**Don't use for:**
- Neutral structural evidence (coupling, dependency direction, change-rate mismatch) — use hyperpowers:intuition
- Reviewing a colleague's branch — use hyperpowers:peek
- Diagnosing a known refactor target — use hyperpowers:refactoring-diagnosis
</when_to_use>

<the_process>

## Dispatch — the critique runs in a subagent

The lead does not read the code. Close reading fills a context; dispatch a fresh blocking subagent and keep the lead's context for presenting and routing.

Do not pass a model override: the critique is judgment and inherits the session model. The lead checks the return per the receiving rules in `skills/common-patterns/report-file-contract.md`, then runs Step 5.

**If you are reading this as the dispatched critic:** Steps 1-4 are yours. Do not use AskUserQuestion; do not run Step 5. The final message is the one `CRITIQUE:` line, never the report.

### Standalone

```
Agent tool:
  subagent_type: "general-purpose"
  prompt: |
    Load the skill hyperpowers:fact-or-fiction with the Skill tool and
    execute Steps 1-4 as the dispatched critic.
    Focus: <verbatim, or "none — hotspots decide">
    Intuition report: none (standalone)
    Working directory: <pwd>
    Report path: <scratchpad>/fact-or-fiction-<date>/report.md
    Write the critique to the report path per
    skills/common-patterns/report-file-contract.md and return exactly one
    line: CRITIQUE: <N> findings (<P> problem, <I> incidental) — report: <path>
    Do NOT run Step 5.
```

### Chained from intuition

Intuition's lead dispatches the same block with `Intuition report: <path to intuition's report>`, `Focus:` set to intuition's prose focus verbatim, and `Report path: <scratchpad>/intuition-<date>/critique.md` — the intuition run's own directory. The audit's tensions replace the hotspot targeting; the close reading is unchanged.

---

## Step 1 — Prepare

Start the report file per the contract (`skills/common-patterns/report-file-contract.md`, Agent side).

Read declared intent: ADRs (`docs/arch/adr/*.md`) and the architecture model if one exists (`docs/arch/*.c4`, read as files). They tell you what the design meant to be. A choice an accepted ADR covers is still a full finding, with the ADR named as context: an ADR records a decision, not that the design is simple.

Chained: read intuition's report — its tensions, its change-rate data, its module summary.

## Step 2 — Target

**Standalone:** run the history-depth check and the counting in `skills/common-patterns/change-history.md`, per file. A hotspot is "complicated code that you have to work with often" (Tornhill): read first where the most-changed files are also the largest. A focus narrows the area; hotspots still rank within it. Below change-history's skip threshold, read by focus or by structure — entry points, the largest modules — and say the ranking has no change evidence behind it; below its warn threshold, carry its warning into the Change evidence line.

**Chained:** intuition's tensions are your targeting, in place of hotspots. Its change rates are per module and present only when its rate-of-change pass ran; for a finding's per-file cost, run the count — it takes under a second. Read the modules each tension names, then the most-changed modules no tension covers — that is where what the structure cannot show tends to live.

Read the hotspots that account for most of the change. Append the read list under `## Targets` before Step 3, marking each entry read closely or not read; the coverage line in Step 4 is built from it and makes the critique honest about its reach.

## Step 3 — Read and judge

Read the code yourself — data shapes, signatures, names, the nouns of the domain. Do not hand the reading to codebase-investigator: the reading is the judgment, and a summary loses it.

Ask of what you read:

1. **Simple or easy?** Simple is "one fold/braid… objective"; easy is "near, at hand… relative" (Simple Made Easy). Where did the code reach for the familiar thing and pay for it with a braid?
2. **What is braided?** Name the strands. The Complexity Toolkit (Resources) is the vocabulary.
3. **Values or places?** Where does new information replace old? Where is identity used where a value would do? (Are We There Yet?; The Value of Values)
4. **Information or mechanism?** Is data visible as data — maps, records, self-describing formats — or wrapped in a bespoke class or API per noun? (The Value of Values; Effective Programs, "weak support for information")
5. **Problem or incidental?** "Incidental is Latin for your fault" (Simple Made Easy). Which complexity is the domain's, and which did the solution add? When it is the domain's, say so: the finding stays in the list, ranked by cost, and its lean says how to contain it, not how to remove it.
6. **One language?** "Precision in naming == precision in thinking" (Design in Practice). One word per concept, names the domain would recognize, terms that drifted from what they first meant.

And one probe: could you move this subsystem out of process, onto another thread, into another language, without changing much? (Simplicity Matters)

**Cost** is how tangled times how often changes pay for it. A braid in a file untouched for a year costs little; the same braid on the hottest path costs every change that crosses it.

Append each finding under `## Working Findings` as it completes, carrying: the braid, what it costs (the change counts), problem or incidental, the simpler shape, your lean and what it trades away, and the evidence (file:line). Chained, also write a lean for each of intuition's tensions: which pull you would take and why, with evidence.

## Step 4 — Assemble

Append the critique, written per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader).

```
## Critique: <system, or the focus area>

*One critic's read through Hickey's lens: opinions with evidence. The architect decides.*

**The read:** <2-4 sentences — how simple the system is, and where it pays most>

### On the tensions                      (chained runs only)
- <tension name>: <the pull I'd take> — <why, with evidence>

### Findings, ordered by cost            (chained runs: "What the structure can't show")
#### 1. <the braid, in system terms>
**Costs:** <how often changes pay for it>
**Problem or incidental:** <which, and why>
**Simpler shape:** <the decomplected version, sketched>
**Lean:** <what I'd do, and what it trades away>
**Evidence:** <file:line; change counts>

### Critique Outcome
**Findings:** <N> (<P> problem, <I> incidental)
**Read closely:** <files or modules>
**Not read:** <what was left, and why>
**Change evidence:** <the filtering line from change-history.md, or "none — insufficient history">
```

**The voice.** State an opinion as evidence plus a lean: "these braid pricing and persistence; 9 of the last 12 changes to pricing touched the store; I'd pass the store a value." Tone follows the Human-Facing Prose Baseline (`skills/common-patterns/prose-style.md`). When "easy" was the better trade for this codebase, say that too. Intuition's neutrality rules — both pulls equal, no ranking, the recommendation self-check — do not apply here: the voice is the deliverable.

Before returning, scan the critique for the baseline's grading words and rewrite any you find into their evidence, then verify the terminal section per the contract.

## Step 5 — Present and pick (lead)

Present the `## Critique` section verbatim.

**Standalone:** ask which findings the architect wants to act on. For each pick, the architect chooses the route:
- **Forge issue** — draft the title and body from the finding (the braid, its cost, the simpler shape, the evidence), show them, and file on approval per `skills/common-patterns/forge-detection.md` (Issues).
- **hyperpowers:brainstorming** — when acting on it is a design change; hand the finding over as context.
- **hyperpowers:refactoring-diagnosis** — when it is a code-level refactor target.

Findings not picked end with the session.

**Chained:** intuition's Step 4 runs the sequence (`skills/intuition/SKILL.md`, Step 4).

</the_process>

<examples>
<example>
<scenario>Opinion with no evidence behind it</scenario>

<code>
#### 1. The event layer is overengineered
**Lean:** This is a mess; rip it out and call the handlers directly.
</code>

<why_it_fails>
- No braid is named, so the architect cannot see what is tangled with what.
- No cost: nothing says how often a change pays for it.
- "A mess" grades the work; it carries no fact the architect can check.
</why_it_fails>

<correction>
#### 1. Event payloads carry the emitter's objects, not values
**Costs:** 14 of the last 20 changes to billing also touched `events/` (6 months).
**Problem or incidental:** Incidental — subscribers only read three fields.
**Simpler shape:** Emit a plain record of those fields; subscribers stop importing billing's types.
**Lean:** Do it. It trades one mapping function for the import edge from every subscriber into billing.
**Evidence:** `events/bus.ts:40` passes `Invoice`; `notify/handler.ts:12`, `ledger/sync.ts:31` read `.id`, `.total`, `.dueDate` only.
</correction>
</example>

<example>
<scenario>A critique that will not take a side</scenario>

<code>
#### 2. Session state lives in a shared registry
**Lean:** Keeping the registry gives one lookup point; replacing it with
passed values gives independence. Both have merit depending on growth.
</code>

<why_it_fails>
- Two pulls stated equally is intuition's format; the architect already has it.
- The critic was dispatched for a lean, and this one hands the judgment back unmade.
</why_it_fails>

<correction>
**Lean:** Pass the session as a value. Every test of the auth flow seeds the registry first (`test/auth/*.ts`, 11 files), and the two readers outside auth only need the user id. It trades the single lookup point for one extra parameter on four functions.
</correction>
</example>

<example>
<scenario>Ranking by how tangled the code looks instead of by cost</scenario>

<code>
#### 1. The legacy report generator braids formatting, querying, and paging
(file last changed 14 months ago)
#### 2. Checkout recomputes tax inside the cart's mutation methods
(changed 31 times in 6 months)
</code>

<why_it_fails>
- The report generator is the worse tangle and the cheaper one: nobody pays for it.
- Cost is tangle times change; the checkout braid is paid on every one of 31 changes.
</why_it_fails>

<correction>
Order checkout first. Keep the report generator, last, with its cost stated plainly — "untouched for 14 months; costs nothing until someone changes it" — so the architect sees it is known and cheap.
</correction>
</example>
</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **Every claim carries evidence** — file:line for what the code does, change counts for what it costs (or "no change history" when Step 2 found none). An opinion without evidence is cut.
2. **Every finding leans** — say what you would do and what it trades away.
3. **Order by cost** — how tangled times how often changes pay for it.
4. **Read the code yourself** — no codebase-investigator for the close reading.
5. **Concede problem complexity** — the domain's complexity is named as such; its lean contains it rather than removes it.
6. **Report by file** — `skills/common-patterns/report-file-contract.md`; the final message is the one `CRITIQUE:` line.

## Common Excuses

All of these mean: **STOP. Reread the rules.**

- "This module is obviously bad; the evidence is overkill" (rule 1: the architect cannot check "obviously")
- "Both options have merit" (rule 2: the neutral read is intuition's; you were asked for a side)
- "I'll have the investigator summarize the hotspots" (rule 4: a summary drops the data shapes and names you are judging)
</critical_rules>

<verification_checklist>
Before returning (critic):
- [ ] Declared intent read (ADRs, model if present); ADR-covered choices reported as full findings with the ADR as context
- [ ] Targeting from change history (standalone) or intuition's report (chained); coverage line says what was and was not read
- [ ] Every finding carries the braid, its cost, problem or incidental, the simpler shape, a lean, and file:line evidence
- [ ] Findings ordered by cost; chained runs carry a lean for every tension
- [ ] Grading-word scan done; top layer free of pass and step labels
- [ ] `### Critique Outcome` present; final message is the one `CRITIQUE:` line

Before finishing (lead):
- [ ] Return checked per the report-file contract; critique presented verbatim
- [ ] Pick-list offered (standalone), or after intuition's last tension (chained); forge issues shown before filing
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:brainstorming or hyperpowers:refactoring-diagnosis (Step 5, for findings the architect picks)

**This skill is called by:**
- User (via /hyperpowers:fact-or-fiction, with an optional focus)
- hyperpowers:intuition (Step 4, on the architect's yes — the chained run)

**Agents used:**
- general-purpose (the critic), on the session model
- NO codebase-investigator (the reading is the judgment)

**Artifacts produced:**
- The critique (scratchpad, presented, not persisted)
- Forge issues (Step 5, on approval)
</integration>

<resources>
**Shared patterns:**
- [Change history](../common-patterns/change-history.md) — history depth, noise filtering, churn counting
- [Report file contract](../common-patterns/report-file-contract.md)
- [Prose style](../common-patterns/prose-style.md) — the Audience Contract and the grading-word baseline
- [Forge detection and issues](../common-patterns/forge-detection.md)

**Hickey's talks (what each gives the lens):**
- Simple Made Easy (Strange Loop, 2011) — simple vs easy, complect, the Complexity Toolkit, "incidental"
- Are We There Yet? (JVM Language Summit, 2009) — value, identity, state, time
- The Value of Values (JaxConf, 2012) — place-oriented programming: "new information replaces old"; facts are values
- Effective Programs (Clojure/Conj, 2017) — the problems of programming by cost: domain complexity and misconception first, then place-oriented programming, weak support for information, brittleness and coupling
- The Language of the System (Clojure/Conj, 2012) — systems speak in protocols and formats; "functional programming in the small only to build object-oriented programming in the large"
- Simplicity Matters (RailsConf, 2012) — the move-your-subsystem litmus
- Design in Practice (Clojure/conj, 2023) — naming precision; one glossary, used uniformly

**The Complexity Toolkit** (Simple Made Easy — construct: what it complects):
State: everything that touches it · Objects: state, identity, value · Methods: function and state, namespaces · Syntax: meaning, order · Inheritance: types · Switch/matching: multiple who/what pairs · Variables: value, time · Imperative loops, fold: what/how · Actors: what/who · ORM: OMG · Conditionals: why, rest of program

**Simpler constructs** (same talk — complexity: simplicity):
State, objects: values · Methods: functions, namespaces · Variables: managed refs · Inheritance, switch, matching: polymorphism à la carte · Syntax: data · Imperative loops, fold: set functions · Actors: queues · ORM: declarative data manipulation · Conditionals: rules · Inconsistency: consistency

**Terms:** Hickey's word is "incidental", set against problem complexity; "essential/accidental" is Brooks's (No Silver Bullet), carried by Moseley and Marks (Out of the Tar Pit). Hotspots are Adam Tornhill's (Your Code as a Crime Scene, 2015).
</resources>
