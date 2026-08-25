# SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md

## Назначение
Этот документ описывает регрессионный набор v0.2.

## Что входит
- environment bootstrap self-check for the current Python-first bundle contract
- baseline fixtures
- human normalization fixtures
- pattern decomposition fixtures
- runtime fixtures
- state fixtures
- batch runtime/state corpus checks
- SVG renderer checks
- hardening-specific human/runtime/state checks
- inspector frontend workflow/module smoke checks
- inspector HTTP static/API/runtime smoke checks
- inspector frontend/server API route parity checks
- inspector frontend/HTTP-test API route coverage parity checks
- inspector frontend DOM id parity checks (`app.js` -> `index.html`)
- inspector downstream autofill/export wiring checks
- inspector localhost HTTP e2e scenario checks
- inspector localhost HTTP project-operations e2e checks
- inspector localhost HTTP lifecycle/direct-import e2e checks
- inspector localhost HTTP graph/session editor e2e checks

## Дополнительная browser verification
Вне unified suite теперь есть отдельный opt-in runner:

```bash
python run_inspector_browser_ui_checks.py
```

Он не входит в обычный hardening прогон по умолчанию, потому что требует реального headless browser / browser subprocess execution.
Но он полезен для живой проверки того, что inspector:
- реально открывается в браузере c корректным default profile/guidance;
- действительно выполняет `analyze -> add current session to project`;
- действительно проходит `branch -> release point -> snapshot export`;
- заранее блокирует очевидный `core`/`exec` profile mismatch для human-shorthand input;
- показывает live snapshot/package guidance по загруженному JSON;
- заранее различает snapshot package vs standalone outcome package прямо в UI;
- подтягивает restore/import/reconcile names из package metadata и не затирает ручные правки;
- подтягивает downstream commit/export names в snapshot/package/portable-merge flows и не мешает ручному override там, где он нужен;
- показывает live standalone/local package summary cards после export, а не заставляет ориентироваться только по сырому JSON;
- действительно проходит `local outcome package preview -> resolve -> commit/promote`;
- после local outcome commit сразу обновляет portable merge selectors живым committed outcome;
- действительно проходит сквозной `standalone package -> local outcome package -> portable merge` browser click-path;
- действительно проходит cross-project `snapshot reconcile -> standalone package -> local outcome package -> portable merge` browser click-path;
- сохраняет screenshot artifacts для визуальной сверки.

## Unified runner
```bash
python run_v0_2_hardening_suite.py
```

Current note: the unified non-browser runner now executes `run_environment_bootstrap_checks.py` before the rest of the regression suite. This keeps the bootstrap contract visible without making browser UI checks mandatory.

## Что он проверяет
- текущий environment/bootstrap contract: required project files, Python executable/version, dependency manifest presence, and optional Playwright availability as a warning-only browser signal;
- старые гарантии не сломались;
- новые grammar aliases нормально нормализуются;
- runtime correctly handles extended cases;
- state model rejects deferred branches;
- SVG layer остаётся совместимым после hardening;
- inspector module wiring не расползается после UI refactor;
- inspector server реально раздаёт modular frontend assets, а не только `index.html` и legacy shell;
- ключевые inspector `POST` routes живы на реальном localhost handler path, включая portable merge compare / resolve / commit.
- frontend `postJson("/api/...")` references не расходятся с реальным server route table.
- frontend `postJson("/api/...")` references не могут остаться без хотя бы одного inspector HTTP smoke/e2e runner.
- frontend `document.getElementById("...")` references не могут разъехаться с реально отрисованным inspector DOM.
- package-guidance shell для snapshot/standalone/local package inputs не может тихо исчезнуть из inspector markup/module wiring.
- metadata-driven autofill для snapshot/package flows не может тихо исчезнуть из workflow wiring.
- downstream autofill/export bindings для snapshot reconcile, standalone package, local outcome package и portable merge не могут тихо исчезнуть из workflow wiring.
- current standalone/local package summary cards не могут тихо исчезнуть из inspector markup/helper/workflow wiring.
- local outcome package commit/promote controls не могут тихо исчезнуть из inspector workflow wiring.
- standalone-commit -> local-outcome-export handoff не может тихо сломаться из-за отсутствующего summary layer: selector flow теперь имеет fallback на `currentProject` commit state.
- snapshot-reconcile -> portable-merge browser scenario не может тихо исчезнуть из opt-in runner: smoke-suite теперь держит отдельную wiring-проверку на этот click-path.
- основные multi-step inspector flows доходят до финального commit/promote через live HTTP scenario runner.
- core project operations тоже проходят live HTTP chain: branch creation, merge commit branch targeting, rebase, cherry-pick, squash и reset.
- lifecycle/import flows тоже проходят live HTTP chain: switch session, partial snapshot import, direct reconcile, direct standalone package import, direct local outcome import и compare-routes для promoted outcomes.
- graph/session editor flows тоже проходят live HTTP chain: analyze, text-to-graph, analyze-graph, export-session-text, export-session-graph и import-session.
