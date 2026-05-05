# Timeline Plan (Project Bootstrap -> v2.0)

Date range: 2021-01-04 - 2022-12-30
Target commits: ~320
Target issues: ~70
Target PRs: ~85

This plan maps product work into seven phases across 2021-2022.

PHASE_A - Project Bootstrap (2021-01-04 - 2021-02-14)
- Repository setup, dependency pinning, Django config, and initial docs
- Early scaffolding in `microfinance/` and top-level templates

PHASE_B - Core Data Layer (2021-02-15 - 2021-04-11)
- Models, forms, admin hooks, and initial migrations
- Loosely coupled app wiring for loans and savings

PHASE_C - Business Logic Core (2021-04-12 - 2021-08-29)
- Validation rules, posting logic, reports, and tests
- QA starts filing bugs once workflows become usable

PHASE_D - API / UI Layer (2021-08-30 - 2021-11-28)
- Views, routing, templates, and export screens
- More review back-and-forth as the UI gets exercised by branches

PHASE_E - Stabilization (2021-11-29 - 2022-03-27)
- Bug fixes, regression tests, and cleanup
- Release prep for v1.1 and v1.2

PHASE_F - Feature Expansion (2022-03-28 - 2022-08-28)
- Reporting refinements, search filters, and automation
- Branch managers start asking for more convenience features

PHASE_G - Hardening (2022-08-29 - 2022-12-30)
- Performance, docs, and final verification passes
- Merge discipline gets stricter before the release cut
