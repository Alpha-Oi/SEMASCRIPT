# Source Architecture Map

This map is based on folder structure, filenames, and safe metadata. It does not claim runtime behavior unless explicitly marked as confirmed from project files/structure.

## Main Source Directories

- Confirmed from file structure: `tooling/` contains Python backend/tooling, parser/runtime/state/project modules, fixture generators, corpus fixtures, and smoke/regression runners.
- Confirmed from file structure: `inspector/` contains the browser UI shell and modular workflow controllers in JavaScript plus HTML/CSS.
- Confirmed from file structure: `docs/` contains SEMASCRIPT specs, current status, roadmap, hardening notes, and feature documents.
- Confirmed from file structure: `tooling/corpus/` and `tooling/fixtures/` contain JSON/TXT/SVG examples and test evidence for parser/runtime/state/project behavior.

## Likely Entry Points

- Confirmed from file structure: `tooling/inspector_server.py` is the backend/server entry named by `AGENTS.md`.
- Confirmed from file structure: `inspector/index.html` and `inspector/app.js` are the browser inspector shell/entry surface.
- Confirmed from file structure: `tooling/run_v0_2_hardening_suite.py` is the broad non-browser verification entry named by `AGENTS.md`.
- Inference from naming: `tooling/parse_to_ast.py`, `tooling/validate_cli.py`, `tooling/normalize_cli.py`, and `tooling/execute_runtime.py` are CLI-style entry points for parser/validator/normalizer/runtime flows.

## Likely Core Modules

- Inference from naming: `tooling/semascript_parser.py`, `tooling/semascript_ast.py`, and `tooling/semascript_validator.py` define grammar/parser/AST/validation core.
- Inference from naming: `tooling/state_model.py`, `tooling/session_model.py`, and `tooling/project_model.py` define state/session/project model contracts.
- Inference from naming: `tooling/exec_runtime.py`, `tooling/execute_runtime.py`, and `tooling/execute_with_state.py` define runtime execution behavior.
- Inference from naming: `tooling/session_diff.py`, `tooling/session_merge.py`, and `tooling/session_conflict_resolution.py` define cross-session compare/merge/conflict logic.

## Likely UI/API/Runtime Modules

- Confirmed from file structure: `inspector/*workflow.js` files split UI workflows by feature area.
- Inference from naming: `tooling/inspector_service.py` provides service-layer behavior used by `tooling/inspector_server.py`.
- Inference from naming: `tooling/run_inspector_http*_checks.py` and `tooling/run_inspector_browser_ui_checks.py` verify HTTP and browser UI integration boundaries.
- Inference from naming: `inspector/inspector-package-guidance.js`, `inspector/reconcile-commit-package-workflow.js`, `inspector/local-outcome-set-package-workflow.js`, and `inspector/portable-merge-workstation.js` are package/reconcile/merge UI flow modules.

## Likely Data / Memory / State Modules

- Inference from naming: `tooling/project_snapshot*.py`, `tooling/project_branching.py`, `tooling/project_rebase.py`, `tooling/project_reset.py`, `tooling/project_tags.py`, `tooling/workspace_navigation.py`, and `tooling/workspace_timeline.py` model workspace history, lineage, restore, and release-point state.
- Confirmed from file structure: `tooling/corpus/*.json` includes sample project indexes, session states, package artifacts, merge results, and validation reports.
- Unknown / needs focused evidence: whether any runtime data persistence exists outside the included JSON corpus and project model APIs.

## Likely Integration Boundaries

- Inference from naming: browser UI calls backend/API through `inspector_server.py`/`inspector_service.py` and modular inspector workflow files.
- Inference from naming: SEMASCRIPT parser/runtime/state modules could be adapted as a DSL/state engine boundary for a GPTMEAi-like orchestration system.
- Unknown / needs focused evidence: no direct GPTMEAi adapter/interface is visible from filenames in this repository snapshot.
- Unknown / needs focused evidence: external services, credentials, databases, or deployment surfaces are not evidenced by safe config files in this pack.

## Likely Generated / No-Edit Zones

- Confirmed from file structure and exclusion rules: `__pycache__/`, `tooling/browser_ui_artifacts/`, and `_gptmaios_analysis_pack/` are generated/output zones excluded from tree/source bundles.
- Inference from naming: `tooling/_generate_*.py` scripts generate corpus fixtures; generated fixture outputs under `tooling/corpus/` should be treated as evidence artifacts unless a later task confirms they are authoritative source of truth.

## Files That Probably Need Focused Review Later

- `tooling/inspector_server.py` — backend/API entry and route boundary.
- `tooling/inspector_service.py` — service bridge between UI/API and core modules.
- `tooling/semascript_parser.py`, `tooling/semascript_ast.py`, `tooling/semascript_validator.py` — language core.
- `tooling/exec_runtime.py`, `tooling/state_model.py`, `tooling/session_model.py`, `tooling/project_model.py` — runtime/state/session/project semantics.
- `tooling/project_snapshot*.py`, `tooling/project_local_outcome_set_package*.py` — snapshot/package/reconcile integration surface.
- `inspector/app.js`, `inspector/index.html`, and `inspector/*workflow.js` — UI/API contract and user workflow evidence.
