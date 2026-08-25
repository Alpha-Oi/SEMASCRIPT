# SEMASCRIPT All-in-One Bundle v0.2 — Portable Local Outcome Package Three-Way Merge Commit / Promote

Этот рабочий bundle продолжает кумулятивную цепочку `SEMASCRIPT_All_In_One_v0_2_*`.

Текущее состояние закрывает полный portable-local three-way merge workflow:
- baseline / three-way merge preview;
- manual conflict resolution;
- commit / promote resolved merge outcome.

## Быстрый self-check

Если нужно быстро понять, что bundle живой, сначала запусти:

```bash
python tooling/run_v0_2_hardening_suite.py
python tooling/run_inspector_browser_ui_checks.py
Set-Location .\tooling
python -c "import inspector_server; print('IMPORT_OK')"
```

Что это даёт:
- `run_v0_2_hardening_suite.py` проверяет основной regression-контур без браузера;
- `run_inspector_browser_ui_checks.py` проверяет живой inspector UI end-to-end;
- `import inspector_server` подтверждает, что HTTP shell поднимается без import-level поломки.

Если browser-check падает в ограниченной среде на запуске Playwright/subprocess, это может быть проблемой sandbox, а не самого проекта. В нормальном разрешённом окружении он должен проходить зелёно.

## Environment bootstrap and verification

Current bootstrap/verification contract is documented in `docs\SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md`.

At this point the bundle does not define an official dependency manifest. Do not assume a `pip install -r requirements.txt`, `pyproject.toml`, or npm workflow unless a separate bounded task creates that contract.

Verification levels:
- environment bootstrap self-check: `python tooling/run_environment_bootstrap_checks.py`
- non-browser hardening: `python tooling/run_v0_2_hardening_suite.py` (includes the environment bootstrap self-check)
- opt-in browser UI checks: `python tooling/run_inspector_browser_ui_checks.py`
- import check:
  ```powershell
  Set-Location .\tooling
  python -c "import inspector_server; print('IMPORT_OK')"
  ```

Browser UI checks may require the Playwright Python package plus a usable browser execution environment.

Актуальные ориентиры:
- agent notes: `AGENTS.md`
- environment/bootstrap contract: `docs\SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md`
- status pack: `docs/SEMASCRIPT_PROJECT_STATUS_PACK_v0.2.md`
- feature doc: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1.md`
