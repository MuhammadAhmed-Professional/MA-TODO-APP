---
id: 0005
title: MEDIUM Priority Terminology Standardization
stage: spec
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-console-todo-app
branch: 001-console-todo-app
user: muhammadahmed
command: Follow-up remediation
labels: ["terminology", "consistency", "documentation"]
links:
  spec: specs/001-console-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-console-todo-app/spec.md
  - specs/001-console-todo-app/plan.md
tests:
  - None (documentation changes only)
---

## Prompt

User requested: "2" (referring to option 2 from previous message: "Address MEDIUM priority issues - Standardize terminology across docs now?")

Context: After completing HIGH priority remediation (PHR 0004), the user requested to address remaining MEDIUM priority issues:
- A7: Terminology drift - "Status indicator" vs "Status formatting"
- A8: Delete operation return behavior unclear
- A9: Screen clear behavior after operations undefined
- A12: "Mark as Complete" vs "toggle_complete" naming inconsistency

## Response snapshot

Addressed all 4 remaining MEDIUM priority issues through terminology standardization and clarifying documentation:

**Issue A7 - Status Indicator Terminology:**
- Updated plan.md:380 from "status formatting" to "status indicator formatting"
- Standardized on "status indicator" across all documents (spec already used this term consistently)

**Issue A8 - Delete Operation Behavior:**
- Added clarification to spec.md Implementation Notes
- Documented that delete returns void/None after confirmation
- Confirmation communicated via success message display only

**Issue A9 - Screen Management:**
- Added clarification to spec.md Implementation Notes
- Documented that screen clearing is NOT required for FR-011 compliance
- Specified that menu displays via standard output, users scroll terminal history
- Noted screen clearing as optional enhancement for Phase 1

**Issue A12 - "Mark as Complete" Terminology:**
- Added comprehensive explanation to spec.md Implementation Notes
- Clarified intentional dual terminology:
  - User-facing: "Mark as Complete" (menu, user stories)
  - Implementation: "toggle completion status" (FR-006, functions)
- Explained rationale: user language emphasizes primary use case, technical language describes bidirectional behavior

All changes made to Implementation Notes section (spec.md:171-183), maintaining spec as implementation-agnostic while documenting necessary clarifications.

## Outcome

- ✅ Impact: Resolved all 4 remaining MEDIUM priority issues. Terminology now consistent across spec.md, plan.md, and tasks.md.
- 🧪 Tests: No test changes required (terminology and documentation only)
- 📁 Files: Modified 2 files (spec.md +12 lines, plan.md +1 line)
- 🔁 Next prompts: Continue with implementation (Task T011 - storage layer). Only 3 LOW priority issues remain (minor style/wording improvements that can be addressed during final review).
- 🧠 Reflection: The Implementation Notes section has proven invaluable for documenting cross-cutting decisions, terminology choices, and behavioral clarifications without polluting functional requirements. This pattern (user-facing language in FRs, technical clarifications in Implementation Notes) maintains spec readability while providing necessary implementation guidance.

## Evaluation notes (flywheel)

- Failure modes observed: None - straightforward documentation updates
- Graders run and results (PASS/FAIL): PASS - All MEDIUM priority issues resolved
- Prompt variant (if applicable): N/A (remediation task)
- Next experiment (smallest change to try): Monitor during implementation whether the dual terminology ("Mark as Complete" user-facing, "toggle" implementation) causes any confusion in function naming or UI messaging. If issues arise, may need to add cross-references between user stories and implementation functions.
