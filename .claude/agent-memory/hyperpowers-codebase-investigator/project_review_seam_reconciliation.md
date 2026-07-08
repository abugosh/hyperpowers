---
name: project-review-seam-reconciliation
description: Design session (2026-07-07, v3.20.0) reconciling end-of-epic review seam — reviewer agent to become single review engine; review-implementation to shrink/retire
metadata:
  type: project
---

Design direction (2026-07-07, main @ v3.20.0): agents/reviewer.md becomes the single end-of-epic review engine; skills/review-implementation shrinks or retires.

**Why:** executing-plans section 6 already dispatches agents/reviewer.md directly and hands off to /finish-branch, while review-implementation/SKILL.md still claims to be the mainline step (integration section says "called by executing-plans Step 5" — stale) and finishing-a-development-branch lists review-implementation approval as a prerequisite. Two parallel review paths exist.

**How to apply:** Key facts found during investigation — (1) review-implementation's UNIQUE load-bearing content is Step 4 (manual-validation STOP, GAPS FOUND STOP, plan-impact notice at L619) and Step 5 (5-question architecture checklist → /ponder UPDATE dispatch); everything else duplicates agents/reviewer.md or is dead weight. (2) skills/review-implementation/resources/ does NOT exist — the three resource links at L1164-1169 are dead. (3) reviewer.md per-task extraction (Step 1, L48: goal/success criteria/implementation checklist/key considerations/anti-patterns) does not match two-tier spec-templates.md fields (Simple: Goal/Why/Changes/Verification; Medium: +Context/Implementation/Tests/Boundaries). (4) ADR-003's guard cluster covers per-task two-stage review, not the end-of-epic reviewer — no ADR contradiction. (5) ponder SKILL.md names review-implementation as caller at L47, L336, L376, L387-388; CLAUDE.md:210 too — these need updating if the checklist relocates.
