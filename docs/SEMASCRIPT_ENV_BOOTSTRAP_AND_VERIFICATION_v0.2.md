# SEMASCRIPT Environment Bootstrap and Verification v0.2

## 1. Scope

This document records the current bootstrap and verification contract for the extracted SEMASCRIPT v0.2 working bundle at `D:\SEMASCRIPT\SEMASCRIPT_current_bundle`.

It does not create a dependency manifest, virtual environment, package workflow, or release process.

## 2. Current environment status

### Evidence

- Standard dependency manifests are currently not found:
  - `pyproject.toml`
  - `requirements*.txt`
  - `package.json`
  - `Pipfile` / `poetry.lock`
  - `Dockerfile`
- The project is operated as a Python-first bundle under `tooling/`.
- The main browser UI check contains an explicit optional Playwright dependency signal: `playwright.sync_api`.
- The broad non-browser runner is `tooling/run_v0_2_hardening_suite.py`.
- The live browser runner is `tooling/run_inspector_browser_ui_checks.py`.

### Inference

- Core project verification expects a compatible Python interpreter and local project files.
- Browser UI verification is separate from the default non-browser regression path.
- Playwright is relevant to browser checks, not to every SEMASCRIPT task.

### Hypothesis

- A future bootstrap formalization task may define an official interpreter, manifest, and install flow.
- Browser UI checks may require both the Playwright Python package and browser binaries/environment.

## 3. What Codex tasks must not assume

- No official `requirements.txt` workflow unless created by a dedicated task.
- No official `pyproject.toml` workflow unless created by a dedicated task.
- No Node/NPM workflow unless created by a dedicated task.
- No official virtualenv path unless created by a dedicated task.
- No dependency installation or environment mutation unless explicitly scoped.

## 4. Verification levels

### Level 1 - docs-only verification

Use for documentation or contract changes.

Expected checks:
- changed files exist
- references are consistent
- no `inspector/` or `tooling/` code changed

### Level 1.5 - environment bootstrap self-check

Use before broader verification when a task needs to confirm the current bootstrap assumptions:

```powershell
python tooling/run_environment_bootstrap_checks.py
```

It checks:
- required SEMASCRIPT project files
- current Python executable and version
- whether standard dependency manifests are absent or unexpectedly present
- optional Playwright availability via `importlib.util.find_spec("playwright")`

It does not:
- install dependencies
- create a virtualenv
- create files
- start a server, UI, browser, or hardening suite
- import `playwright.sync_api`

Warnings mean the bootstrap contract may need attention, but they are not automatically failures. For example, missing Playwright is expected for non-browser tasks.

### Level 2 - non-browser regression

Use when runtime or workflow logic changes. This suite now includes the Level 1.5 environment bootstrap self-check before the other non-browser checks:

```powershell
python tooling/run_v0_2_hardening_suite.py
```

Missing Playwright should not break this non-browser suite. Playwright remains relevant to the opt-in browser UI checks.

### Level 3 - import verification

Use when the server/import surface may be affected:

```powershell
Set-Location .\tooling
python -c "import inspector_server; print('IMPORT_OK')"
```

### Level 4 - opt-in browser UI checks

Use only when browser execution is available and the task permits it:

```powershell
python tooling/run_inspector_browser_ui_checks.py
```

Browser checks may require the Playwright Python package plus browser binaries or a compatible browser execution environment.

## 5. Future bootstrap formalization slice

A separate bounded task can formalize bootstrap/dependencies. That task should:

- choose whether SEMASCRIPT needs `requirements.txt`, `pyproject.toml`, or another manifest
- define the supported Python interpreter range
- document how Playwright is installed only for browser verification
- prove the install path in a clean environment before updating project status
- avoid mixing bootstrap formalization with feature work or inspector refactors
