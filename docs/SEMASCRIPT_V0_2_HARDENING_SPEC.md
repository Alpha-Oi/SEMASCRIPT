# SEMASCRIPT_V0_2_HARDENING_SPEC.md

## Назначение
Этот документ фиксирует **v0.2 hardening** как следующий приоритетный слой после SVG renderer.

## Почему hardening выше редактора
Редактор / visual inspector полезен, но он должен опираться на уже устойчивую grammar/runtime/state систему.
Поэтому сначала усиливается:
- grammar coverage
- runtime coverage
- state coverage
- regression suite
- batch hardening corpus

## Что добавлено в v0.2 hardening
- расширенные human grammar aliases:
  - `A gives B resource`
  - `A transfers resource to B`
  - `A returns resource to B`
  - `resource decreases`
  - `system grows`
  - `system stabilizes`
  - `state:stable(...)`
  - `state:unstable(...)`
  - `state:open(...)`
  - `state:closed(...)`
- state-layer rejection для `branch_set`:
  - `S_BRANCH_DEFERRED`
- hardening fixtures для:
  - human normalization
  - runtime
  - state model
- expanded hardening corpus
- unified `run_v0_2_hardening_suite.py`
- inspector regression layer:
  - frontend workflow/module wiring smoke
  - HTTP static/API/runtime smoke for inspector server
  - frontend/server API route parity check
  - frontend/HTTP-test API route coverage parity check
  - frontend DOM id parity check (`app.js` vs `index.html`)
- live localhost HTTP e2e scenario runner
- live localhost HTTP project-operations e2e runner
- live localhost HTTP lifecycle/direct-import e2e runner
- live localhost HTTP graph/session editor e2e runner
- opt-in browser UI runner for live inspector click-path verification

## Главный эффект
Этот шаг не добавляет красивый интерфейс.
Он снижает хрупкость системы и подготавливает её к следующему UI/inspector слою без накопления скрытых расхождений.

В текущем состоянии hardening уже защищает не только grammar/runtime/state, но и базовую живучесть inspector shell:
- modular frontend bundles реально подключены;
- inspector HTTP layer отдает актуальные `.js`/`.css` ассеты;
- inspector HTTP layer принимает и возвращает ожидаемые payload-ы по ключевым `POST` маршрутам;
- inspector frontend route references синхронизированы с live server handlers;
- inspector frontend route references дополнительно синхронизированы с реальным HTTP smoke/e2e coverage;
- inspector DOM contract дополнительно синхронизирован между `app.js` и `index.html`, так что workflow controls труднее потерять при frontend refactor;
- основные inspector workflows проходят до финального outcome/merge commit через отдельный e2e scenario runner;
- branch-aware project operations дополнительно проходят через отдельный HTTP e2e runner, так что merge/rebase/cherry-pick/squash/reset меньше зависят от ручной проверки;
- direct lifecycle/import actions inspector-а тоже отдельно прогоняются по live HTTP path, так что `switch/import/reconcile/compare` меньше зависят от ручного кликанья;
- graph/session editor surface тоже отдельно прогоняется по live HTTP path, так что базовый `analyze/graph/session export-import` слой не остаётся только на smoke;
- inspector refactor труднее случайно сломать одним пропущенным route или script include.
- package-heavy inspector flows тоже стали менее хрупкими на самом UI-слое: snapshot/package inputs теперь показывают live summaries и type-mismatch guidance до server roundtrip.
- metadata-heavy inspector flows тоже стали удобнее: restore/import/reconcile names теперь можно получить из загруженного package JSON без ручного повторного набора.
- downstream-heavy inspector flows тоже стали удобнее: commit/export names теперь можно получить из live reconcile/package/merge results без лишнего ручного повторного набора.
- exported-package-heavy flows тоже стали понятнее: standalone/local package handoff теперь можно читать через structured summary cards, а не только через raw JSON payloads.

Отдельно от unified suite теперь существует browser-level verification runner.
Он не является частью стандартного hardening запуска из-за зависимости от живого browser execution, но закрывает следующий уровень уверенности:
- видимость реально восстановленных sidebar panels;
- корректный default profile / profile guidance прямо в live UI;
- живой frontend state update после `analyze`;
- живой UI path для `add current session`, `create branch`, `create release point`, `create snapshot export`.
- obvious profile/input mismatch теперь можно проверять как отдельный browser-led preflight path, а не только как backend parse failure.
- snapshot/package JSON guidance и cross-panel package-type mismatch теперь тоже можно проверять как отдельный browser-led UI path.
- metadata-driven autofill и сохранение manual overrides для restore/import/reconcile names теперь тоже можно проверять как отдельный browser-led UI path.
- downstream commit/export autofill и сохранение manual overrides для snapshot/package steps теперь тоже можно проверять как отдельный browser-led UI path.
- current standalone/local package summary cards после export теперь тоже можно проверять как отдельный browser-led UI path.
- local outcome package resolution -> commit/promote теперь тоже можно проверять как отдельный browser-led UI path.
- handoff из local outcome commit в portable merge selectors теперь можно проверять прямо в live UI, а не только через HTTP e2e.
- standalone package import -> local outcome export/import/commit -> portable merge теперь тоже можно проверять как один связный browser-led pipeline.
- snapshot reconcile -> standalone package export -> target project import -> local outcome -> portable merge теперь тоже можно проверять как один связный cross-project browser-led pipeline.
