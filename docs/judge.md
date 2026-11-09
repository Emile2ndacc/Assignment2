# student-judge competency report

**Student / session:** Student Awards project / COMP 3613 Assignment 2
**Artifact:** Available Guide-written phase transcripts, current `docs/report.md`, diagrams, wireframes, and test suite
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy partial; never generic 0–5)

**Judged at:** 2026-11-09T16:07:00-04:00
**Evidence pass:** Re-read current `docs/report.md`, `docs/diagrams/`, `docs/wireframes/`, and all available Guide transcript markdown; checked the current test suite result. Older native Copilot CLI chats were not readable. Prior scorecard ignored.

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 48 |
| Awarded total | 38 / 48 |
| **Overall (avg of scored)** | **3.2 / 4** |
| Impression mark | 16 / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 3 | yes | The report documents Phases 1–5 before Phase 6, which remains pending a public URL. |
| M2 | Problem framing | 3 | yes | The report names Student Awards and three workflows; the Phase 2 transcript records the student asking “does nothing extend?” and choosing “add one extend.” |
| M3 | Decision ownership | 3 | yes | The Phase 3 transcript records the student's entity/property list and relationship decisions; later report content follows the student's chosen theme and workflows. |
| M4 | Artefact-before-code | 3 | yes | The ERD, use-case diagram, and student wireframe are present; implementation notes correspond to the same workflows. |
| M5 | Verification habit | 3 | yes | The report records local verification and student/admin navigation checks; the latest full test run is documented as 15 passing cases. |
| M6 | Assignment fit | 3 | yes | The report describes the Student Awards model and layered implementation, followed by polish and a pending deployment. |
| M7 | Slice explanation | 3 | yes | Transcripts summarize relationship and architecture checks; model notes describe eligibility, redemption status, and appeal rules. |
| M8 | Prompt quality | 3 | yes | Transcripts show phase-oriented prompts; the student also asked for redemption tests to match the current workflow and designed app. |
| M9 | Response to pushback | 3 | yes | The student engaged the include/extend discussion and continued steering test coverage after learning the existing unit test did not represent the full workflow. |
| M10 | Integrity | 4 | yes | The current report's course skill-integrity marker is `pass`; available transcripts show no paste-back or answer-seeking flags. |
| M11 | Provenance continuity | 3 | yes | The workflows, model, UI, and current tests remain about the same Student Awards system and its documented redemption states. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion rounds or sincerity blocks appear in the accessible transcript set; no suspicion spiral was needed. |

## Strengths
- The report and diagrams consistently describe the Student Awards project and its three named workflows.
- The student supplied a wireframe, external workflow diagram, and six test-plan diagrams; the report orders the acceptance, unit, and integration test plans.
- The project test suite currently passes: **15 passed, 0 failed**. Redemption unit and integration coverage follows the app's implemented request and admin decision flows.
- The report records Phase 5 local verification and polish before the Phase 6 deployment step.

## Gaps (priority order)
1. Phase 6 remains partial: `docs/report.md` contains `https://pending-render-deploy` rather than a live public Render URL.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Project and three workflows are documented; a separate Phase 1 chat was not available in the accessible transcript set. |
| 2 | met | Use-case diagram and include/extend choice are recorded. |
| 3 | met | Student entities, properties, and relationship discussion are summarized in the transcript. |
| 4 | met | Student wireframe is embedded and coverage is recorded. |
| 5 | met | Theme, implementation, local verification, and polish are recorded in the report. |
| 6 | partial | The public Render URL is still pending. |

## Recommended next practice
- Complete the Render Postgres and web-service deployment, then replace the pending URL in the report with the live app URL.

## Integrity note
- Clean based on the accessible evidence.
- Older native Copilot CLI chats could not be read; available Guide-written transcripts and project artifacts were used.

## Provenance flags
- None observed.

## Sincerity log summary
- Blocks found: 0 in accessible transcripts
- max round: 0
- min/mean/final confidence: n/a
- trend: n/a
- cleared: no suspicion spiral needed

## Skips
- Skips: 0/3 used (from available Guide evidence). Skips are not an integrity failure.
