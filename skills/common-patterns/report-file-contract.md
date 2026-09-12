# Report File Contract

Single source for how a dispatched subagent hands a multi-section report back
to the lead that dispatched it. Consumers cite this file; none restates it.

A report composed in the final message is the failure this contract removes:
the return arrives truncated, or the subagent stalls composing it, and the lead
holds nothing — every re-dispatch starts from zero. Under this contract the
report is on disk section by section while the subagent works, the final
message is one line, and a re-dispatch resumes from what the file already
holds.

## When it applies

Any dispatch whose return has section headings is a report and travels by
file. Today that is:

| Dispatch | Terminal section | Return line |
|----------|------------------|-------------|
| peek RECON (`agents/peek.md`) | `### Coverage` | `RECON: <N> aims, <M> surprises, rung <R> — report: <path>` |
| peek lens — CODE, ARCHITECTURE, DELIVERY (`agents/peek.md`) | `### Coverage` | `LENS <MODE>: <C> Critical, <I> Important, <S> Suggestions, <Q> questions — report: <path>` |
| end-of-epic reviewer (`agents/reviewer.md`) | `## Implementation Review:` | `REVIEW VERDICT: <APPROVED\|GAPS FOUND> — <N> gaps — report: <path>` |
| SRE batch reviewer (`skills/sre-task-refinement/SKILL.md`) | `### Batch Verdict` | `SRE VERDICT: <APPROVE\|NEEDS REVISION\|REJECT> — report: <path> — <N> specs updated` |
| intuition analyst (`skills/intuition/SKILL.md`, Steps 0-3) | `### Audit Outcome` | `TENSION REPORT: <N> tensions, <D> drift — report: <path>` |
| test-effectiveness analyst (`agents/test-effectiveness-analyst.md`) | `## Executive Summary` (written last, from the sections above it) | `TEST AUDIT: <N> tests — RED <r>, YELLOW <y>, GREEN <g>, <c> corner cases — report: <path>` |

The return lines that carry a verdict word are registered in
`loop-interfaces.md` (Verdict Contracts); the others are return lines, not
verdicts, and introduce no verdict vocabulary. Counts on a return line are
what the file holds — a lead reads them as a pointer, never as the finding.

Short returns stay inline: the executor's one-liner, the Stage-2
code-reviewer's verdict line plus concern lines, the test-runner's summary,
and the prose summaries of codebase-investigator and internet-researcher.
Adding a dispatch to the table above is a contract change: name its terminal
section and its return line here, then cite this file from its agent or
skill and from every dispatch site.

## Lead side — dispatching

- Supply an absolute path in the lead's session scratchpad, one file per
  dispatch, under a directory named for the run:
  `<scratchpad>/<flow>-<id>/<mode-or-role>.md`. Members of a parallel
  fan-out never share a file.
- The dispatch prompt carries the line `Report path: <path>` and cites this
  file. A dispatch under this contract with no path is an error the agent
  returns, not a gap it improvises around.
- Every member of a parallel fan-out whose return is a report returns
  under this contract — parallel inline reports are the truncation-and-stall
  pattern this file removes.

## Agent side — writing

1. **Create the file before the first section.** Its first line names the
   dispatch (mode or role, target, date). An existing file at the path means
   this is a re-dispatch: read it, keep every complete section, and continue
   from the first section the contract's order says is missing — never
   restart, never write a section twice.
2. **Append each section as it completes,** in the contract's section order.
   Never hold the report for one final write: a stall after section three of
   seven must leave three complete sections on disk.
3. **End with the terminal section** named in the table above. It is the
   section whose presence proves the report complete; a section the contract
   allows after it (intuition's Architect Questions) follows it.
4. **Verify before returning:** `grep -c '<terminal section>' <path>` must
   return at least 1. If it does not, finish the file. Never fall back to
   returning the report in chat — a file write that failed is fixed, not
   worked around, and a report in the final message is the contract
   violation this file exists to prevent.
5. **Final message is exactly the one return line** from the table — no
   preamble, no summary, no excerpt of the report. Everything the lead needs
   beyond the line is in the file.

## Lead side — receiving

A return is **compliant** when the final message parses as its return line,
the file at the path exists, the terminal section is present, and — where
a verdict rides the line — the line's verdict word matches the file's.
Anything else is non-compliant, including a complete report delivered in
chat with no file behind it: the chat text is not read into synthesis, not
parsed for a verdict, not pasted anywhere.

On a non-compliant return:

1. Read the file as it stands — partial sections are evidence, not waste.
2. Re-dispatch **once**: a fresh subagent, the same prompt, the same path.
   The agent resumes per the writing rules above. In a fan-out, re-dispatch
   only the non-compliant member, alone; compliant members' files stand.
3. On a second non-compliant return: stop, persist a gate-state to the
   epic's bd notes where an epic exists (`loop-interfaces.md`), and escalate
   to the user with whatever the file holds. A stalled report is never
   silently dropped and never replaced by the lead's own reading.

This counter is channel failure only. It is separate from any quality loop
the flow runs on the report's content (NEEDS REVISION rounds, gap rounds);
a non-compliant return never counts against those caps.

The lead reads the file on demand and presents what the flow says to
present. It does not read every report wholesale into its own context: the
return line and the sections the next step needs are the read.
