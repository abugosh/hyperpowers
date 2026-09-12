# Common Rationalizations - STOP

These rationalizations appear across multiple contexts. When you catch yourself thinking any of these, STOP - you're about to violate a skill.

## Process Shortcuts

| Excuse | Reality |
|--------|---------|
| "This is simple, can skip the process" | Simple tasks done wrong become complex problems. |
| "Just this once" | No exceptions. Process exists because exceptions fail. |
| "I'm confident this will work" | Confidence ≠ evidence. Run the verification. |
| "I'm tired" | Exhaustion ≠ excuse for shortcuts. |
| "No time for proper approach" | Shortcuts cost more time in rework. |
| "Partner won't notice" | They will. Trust is earned through consistency. |
| "Different words so rule doesn't apply" | Spirit over letter. Intent matters. |

## Verification Shortcuts

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification command. |
| "Looks correct" | Run it and see the output. |
| "Tests probably pass" | Probably ≠ verified. Run them. |
| "Linter passed, must be fine" | Linter ≠ compiler ≠ tests. Run everything. |
| "Partial check is enough" | Partial proves nothing about the whole. |
| "Agent said success" | Agents lie/hallucinate. Verify independently. |
| "I'm confident this fixes it" | Confidence ≠ evidence. Run the verification. |

## Documentation Shortcuts

| Excuse | Reality |
|--------|---------|
| "File probably exists" | Use tools to verify. Don't assume. |
| "Design mentioned it, must be there" | Codebase changes. Verify current state. |
| "I can verify quickly myself" | Use investigator agents. Prevents hallucination. |
| "User can figure it out during execution" | Your job is exact instructions. No ambiguity. |

## Planning Shortcuts

| Excuse | Reality |
|--------|---------|
| "Can skip exploring alternatives" | Comparison reveals issues. Always propose 2-3. |
| "Partner knows what they want" | Questions reveal hidden constraints. Always ask. |
| "Whole design at once for efficiency" | Incremental validation catches problems early. |
| "Checklist is just suggestion" | Track every item in the repo's tracker (bd when beads is present, TodoWrite otherwise). |
| "Subtask can reference parent for details" | NO. Subtasks must be complete. NO placeholders, NO "see parent". |
| "I'll use placeholder and fill in later" | NO. Write actual content NOW. No meta-references like "[detailed above]". |
| "Design field is too long, use placeholder" | A placeholder is a missing spec. Write the content the task needs — and only that; length is not the goal. |
| "Should I continue to the next task?" | YES. You have a tracked plan. Execute it. Don't interrupt your own workflow. |
| "Let me ask user's preference for remaining tasks" | NO. The user gave you the work. Do it. Only ask at natural completion points. |
| "Should I stop here or keep going?" | Your tracker tells you. If tasks remain, continue. |
| "Spec is truncated but the gist is clear" | A truncated spec (e.g. "[Remaining steps truncated]") is a missing spec. Route through writing-plans. |

## Execution Shortcuts

| Excuse | Reality |
|--------|---------|
| "Task is already tracked, don't need step tracking" | Tasks have 4-8 implementation steps. Without substep tracking, steps 4-8 get skipped. |
| "Made progress on the task, can move on" | Progress ≠ complete. All substeps must finish. 2/6 steps = 33%, not done. |
| "Other tasks are waiting, should continue" | Current task incomplete = blocked. Finish all substeps first. |
| "Can finish remaining steps later" | Later never comes. Complete all substeps now before closing task. |

## Dispatch Shortcuts

| Excuse | Reality |
|--------|---------|
| "The report is short enough to return inline" | A report with section headings travels by file (`report-file-contract.md`). Short reports truncate too; the file costs nothing. |
| "The subagent put the whole report in chat, I'll use that" | A chat report is the truncation path. Read nothing from it; re-dispatch once with the same path so the agent resumes from the file. |
| "Re-dispatch fresh, the partial file is junk" | The partial file is the evidence a resume starts from. Same path, same prompt; the agent continues from the first missing section. |
| "The file write failed, returning inline is the fallback" | There is no fallback. Fix the write, then return the one line. |

## Quality Shortcuts

| Excuse | Reality |
|--------|---------|
| "Small gaps don't matter" | Spec is contract. All criteria must be met. |
| "Will fix in next MR" | This MR should complete this work. Fix now. |
| "Partner will review anyway" | You review first. Don't delegate your quality check. |
| "Good enough for now" | "Now" becomes "forever". Do it right. |

## Comment Shortcuts

| Excuse | Reality |
|--------|---------|
| "It's an invariant, so the policy allows it" | The policy allows the sentence that states it, not the paragraph that proves it. |
| "This clause is subtle, one sentence won't hurt" | Make the code say it. If you cannot name the wrong edit the comment prevents, there is no comment. |
| "The reviewer requires evidence for every claim" | Evidence goes in the test and the commit body. A comment that argues with a reviewer is noise even when true. |
| "Someone might 'simplify' this away, so I'll warn them" | A comment written for an imagined critic is noise. One sentence of hazard, or nothing. |
| "The reviewer said the comment was wrong, so I corrected it" | A wrong comment is cut or deleted, never extended. |
| "Every clause here has a hazard" | Then each gets one sentence. A hazard that needs a paragraph is an ADR. |
| "The policy is never numeric, so volume can't be a finding" | Shape is evidence. A comment longer than its code is presumed misplaced until each sentence passes. |
| "The spec explained it, so the code should too" | The spec is for the executor. Nothing in Why or Context is transcribed into comments. |

## TDD Shortcuts

| Excuse | Reality |
|--------|---------|
| "Test is obvious, can skip RED phase" | If you don't watch it fail, you don't know it works. |
| "Will adapt this code while writing test" | Delete it. Start fresh from the test. |
| "Can keep it as reference" | No. Delete means delete. |
| "Test is simple, don't need to run it" | Simple tests fail for subtle reasons. Run it. |
| "Tests after achieve the same goals" (deadline/authority pressure) | Tests-after prove nothing about intent. Test first, even shipping in 10 minutes. |
| "Deleting X hours of work is wasteful" | Sunk cost. Untested code is the waste. |

## Research Shortcuts

| Excuse | Reality |
|--------|---------|
| "I can research quickly myself" | Use agents. You'll hallucinate or waste context. |
| "Agent didn't find it first try, must not exist" | Be persistent. Refine query and try again. |
| "I know this codebase" | You don't know current state. Always verify. |
| "Obvious solution, skip research" | Codebase may have established pattern. Check first. |

## Skill Routing Shortcuts

| Excuse | Reality |
|--------|---------|
| "This is just a simple question" | Questions are tasks. Check the routing table. |
| "I can check git/files quickly" | Files lack context. Check for skills first. |
| "Let me gather information first" | Skills tell you HOW to gather. Check first. |
| "This doesn't need a formal skill" | If a skill exists, using it is mandatory. |
| "I remember this skill" | Skills evolve. Load the current version via the Skill tool. |
| "This doesn't count as a task" | Taking action = task. Check the routing table. |
| "The skill is overkill for this" | Skills exist because "simple" becomes complex. |
| "I'll just do this one thing first" | Check for skills BEFORE doing anything. |
| "Instruction was specific so I can skip the workflow" | Specific instructions = WHAT, not HOW. Route through the table. |

**All of these mean: STOP. Follow the requirements exactly.**

## Why This Matters

Rationalizations are how good processes fail:
1. Developer thinks "just this once"
2. Shortcut causes subtle bug
3. Bug found in production/MR
4. More time spent fixing than process would have cost
5. Trust damaged

**No shortcuts. Follow the process. Every time.**
