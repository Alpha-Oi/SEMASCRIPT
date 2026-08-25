# AGENTS.md

## Scope
These instructions apply to the extracted working bundle at `SEMASCRIPT_current_bundle`.

## Project Shape
- `inspector/` — browser UI, modular workflow controllers, styles, static shell.
- `tooling/` — Python backend, HTTP server, smoke/e2e/browser verification runners.
- `docs/` — status pack, hardening spec, feature docs.

## What This Project Is
SEMASCRIPT is currently centered on:
- session/text/graph analysis;
- project workspace operations (branches, tags, snapshots, lineage);
- snapshot reconcile;
- standalone outcome package flow;
- local outcome package flow;
- portable local three-way merge flow;
- inspector UI that drives those workflows end-to-end.

## First Checks
Run these before claiming the project is healthy:

```bash
python tooling/run_v0_2_hardening_suite.py
python tooling/run_inspector_browser_ui_checks.py
python -c "import inspector_server; print('IMPORT_OK')"
```

Notes:
- `run_v0_2_hardening_suite.py` is the main non-browser regression entrypoint.
- `run_inspector_browser_ui_checks.py` is the live UI/self-hosted browser check. In restricted environments it may need subprocess/browser permission outside the sandbox.
- `inspector_server` import checks should run from `tooling/`, for example:

```powershell
Set-Location .\tooling
python -c "import inspector_server; print('IMPORT_OK')"
```

## Editing Rules
- Prefer changing the dedicated workflow module in `inspector/` instead of growing `inspector/app.js`.
- When adding or renaming inspector controls, keep `inspector/index.html` and `inspector/app.js` DOM ids aligned.
- When adding frontend `postJson("/api/...")` calls, keep server route coverage and smoke/e2e parity intact.
- When changing package/reconcile/merge UX, update both smoke checks and browser UI checks.
- When the verified baseline changes, update `docs/SEMASCRIPT_PROJECT_STATUS_PACK_v0.2.md`.

## Environment/bootstrap and report discipline

- Do not add or assume dependency manifests such as `pyproject.toml`, `requirements.txt`, `package.json`, `Pipfile`, `poetry.lock`, or `Dockerfile` unless a task explicitly scopes that bootstrap contract.
- Treat browser/UI verification through Playwright as optional and opt-in. It is not required for every docs-only or non-UI task.
- Use `tooling/run_v0_2_hardening_suite.py` as the broad non-browser verification entrypoint when runtime/workflow logic changes.
- Use this import verification when the server/import surface may be affected:

```powershell
Set-Location .\tooling
python -c "import inspector_server; print('IMPORT_OK')"
```

- Do not change `inspector/` or `tooling/` logic during docs-only tasks.
- Save SEMASCRIPT Codex reports as one flat Markdown report under `D:\Codex_Review_Reports\SEMASCRIPT\YYYY-MM-DD_HH-mm_task_CHATGPT_REVIEW_REPORT.md`.
- Do not create timestamped report folders, `_LATEST`, `COMMAND_LOG.txt`, ZIP files, report indexes, or auxiliary report files unless the user explicitly asks for them.

## Useful Anchors
- Backend entry: `tooling/inspector_server.py`
- Unified regression: `tooling/run_v0_2_hardening_suite.py`
- Browser verification: `tooling/run_inspector_browser_ui_checks.py`
- Environment/bootstrap contract: `docs/SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md`
- Current project status: `docs/SEMASCRIPT_PROJECT_STATUS_PACK_v0.2.md`
