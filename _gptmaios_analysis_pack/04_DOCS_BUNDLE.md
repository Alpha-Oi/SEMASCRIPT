# Documentation Bundle

Relevant README/docs/spec/current-state/roadmap/design content. Large files are truncated as noted.

## FILE: README.md
Path: `README.md`

Size: 2696 bytes

````markdown
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
````


## FILE: docs/README.md
Path: `docs/README.md`

Size: 7975 bytes

````markdown
# SEMASCRIPT Project Pack v0.1

Это complete baseline-пакет проекта SEMASCRIPT для сохранения, переноса и дальнейшей реализации.

## Состав
- `00_PROJECT_IDENTITY.md`
- `01_ARCHITECTURE_MAP.md`
- `02_CURRENT_STATUS.md`
- `03_ROADMAP.md`
- `04_SCOPE_V0_1.md`
- `SEMASCRIPT_0_SEMANTIC_BASELINE.md`
- `SEMASCRIPT_CORE_SPEC_v0.1.md`
- `SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`
- `SEMASCRIPT_PROFILE_MATRIX_v0.1.md`
- `SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md`
- `SEMASCRIPT_TESTPACK_v0.1.md`
- `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`
- `SEMASCRIPT_EXEC_PROFILE_v0.1.md`
- `SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`
- `SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md`
- `SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md`
- `SEMASCRIPT_MANIFEST_v0.1.md`

## Роль пакета
Этот pack нужен как baseline:
- для продолжения проекта без потери контекста;
- для handoff в новый чат или новому инженеру;
- для перехода от идей к спецификации, валидации и реализации.

## Следующий сильный шаг
Начать либо parser/validator MVP, либо расширение corpus и test fixtures.


## Expanded alignment
Starter corpus и test pack синхронизированы с текущим tooling MVP.

- `SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1.md` — описание Human normalizer MVP и его границ

- `SEMASCRIPT_GRAMMAR_EXPANSION_v0.1.md` — grammar expansion: list-scope + richer human scene forms

- `SEMASCRIPT_AST_INTEGRATION_PACK_v0.1.md` — AST integration layer for tooling
- `SEMASCRIPT_CORPUS_PIPELINE_v0.1.md` — batch normalization/validation pipeline for corpus

- `SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1.md` — первый operational decomposition layer для `SPR/GEN/PAL`

- `SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1.md` — restricted exec runtime semantics for v0.1

- `SEMASCRIPT_STATE_MODEL_v0.1.md` — execution state container and state transition rules

- `SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1.md` — batch runtime/state corpus pipeline and reporting

- `SEMASCRIPT_SVG_RENDERER_SPEC_v0.1.md` — SVG prototype renderer and layout rules

- `SEMASCRIPT_V0_2_HARDENING_SPEC.md` — priority rationale and hardening scope
- `SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md` — unified hardening regression suite

- `SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1.md` — local editor / visual inspector layer

- `SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1.md` — graph model + editable visual graph mode

- `SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1.md` — persisted project/session format and inspector import/export

- `SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1.md` — multi-session workspace and project index

- `SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1.md` — workspace navigation and dependency map between sessions

- `SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1.md` — workspace timeline and session evolution history

- `SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1.md` — cross-session compare and diff mode

- `SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1.md` — three-way session merge and conflict detection

- `SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md` — interactive conflict resolution and manual merge decisions

- `SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1.md` — merge commit and resolved session insertion into workspace

- `SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1.md` — branching and named merge lineage graph

- `SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1.md` — branch rebase and replay onto target lineage

- `SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1.md` — cherry-pick and selective session replay across branches

- `SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1.md` — squash/fold multiple sessions into one lineage commit

- `SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1.md` — reset / restore branch head to historical session or lineage point

- `SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1.md` — tag / release points over sessions and lineage states

- `SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1.md` — snapshot / immutable workspace state export by tag or release point

- `SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1.md` — snapshot import / workspace restore from immutable export

- `SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1.md` — snapshot diff / restore preview before apply

- `SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1.md` — partial snapshot restore / selective workspace state import

- `SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1.md` — snapshot merge / reconcile imported state with current workspace lineage

- `SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1.md` — snapshot conflict detection / reconcile preview before apply

- `SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1.md` — snapshot conflict resolution / manual reconcile decisions

- `SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1.md` — snapshot reconcile commit / promote resolved decisions into named resolution set or release lineage point

- `SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1.md` — resolution set diff / compare between promoted reconcile outcomes

- `SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1.md` — resolution set export/import as standalone promoted outcome package

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md` — standalone outcome package diff / compatibility check before import

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md` — standalone outcome package conflict resolution / manual import decisions

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1.md` — standalone outcome package commit / promote imported resolution into local named outcome set or release point

- `SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1.md` — local outcome set diff / compare between imported promoted resolutions

- `SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1.md` — local outcome set export / import as portable local promoted resolution package

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md` — portable local outcome package diff / compatibility check before import

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md` — portable local outcome package conflict resolution / manual import decisions

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1.md` — portable local outcome package commit / promote imported resolution

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1.md` — portable local outcome package diff / compare between committed imported outcomes

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1.md` — portable local outcome package export / import compare baseline or three-way merge

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md` — portable local outcome package three-way conflict resolution / manual merge decisions
````


## FILE: tooling/README.md
Path: `tooling/README.md`

Size: 2507 bytes

````markdown
# SEMASCRIPT Tooling MVP v0.1 — Grammar Expanded

Это расширенный parser/validator/normalizer bundle для SEMASCRIPT.

## Что уже умеет
- парсить канонические одиночные конструкции;
- парсить list-scope значения:
  ```text
  scp=[[NODE]; [NODE]]
  ```
- валидировать базовые Core правила;
- валидировать минимальный Exec subset;
- нормализовать стандартизированный Human shorthand в Core;
- прогонять expanded fixtures.

## Human normalizer grammar
Поддерживаемые wrappers:
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `state:bal(...)`
- `inv:zsum(...)`
- `inv:nzsum(...)`
- `time:lin(...)`
- `time:cyc(...)`
- `time:brn(...)`
- `time:rec(...)`
- `time:rev(...)`
- `time:atm(...)`

Поддерживаемые scene forms:
- `A -> B : resource`
- `human observes object`
- `human acts on system`
- `system creates resource`
- `system destroys resource`
- `form depends on code`
- `A equals B`
- `resource declines`
- `resource increases`
- `system becomes unstable`
- causal form: `scene1 => scene2`
- multi-scene list: `scene1; scene2`

## Ограничение
Это всё ещё deterministic shorthand normalizer, а не parser свободного естественного языка.

## Environment bootstrap self-check

Read-only check for the current SEMASCRIPT bootstrap contract:

```bash
python tooling/run_environment_bootstrap_checks.py
```

It checks required project files, current Python executable/version, absence or presence of standard dependency manifests, and optional Playwright availability. Missing Playwright is a warning, not a failure, for non-browser tasks.

The broad non-browser hardening suite now runs this self-check before the other checks:

```bash
python tooling/run_v0_2_hardening_suite.py
```

Browser UI checks remain opt-in and separate:

```bash
python tooling/run_inspector_browser_ui_checks.py
```

## Примеры запуска
Проверка Core:
```bash
python validate_cli.py sample_core.txt --mode core
```

Проверка Exec:
```bash
python validate_cli.py sample_exec.txt --mode exec
```

Прогон Core/Exec fixtures:
```bash
python run_fixture_validation.py
```

Прогон Human normalization fixtures:
```bash
python run_human_normalization_checks.py
```

Нормализация shorthand:
```bash
python normalize_cli.py human_sample.txt
```
````


## FILE: tooling/FIXTURE_INDEX.md
Path: `tooling/FIXTURE_INDEX.md`

Size: 1200 bytes

````markdown
# SEMASCRIPT_FIXTURE_INDEX_v0.1

## Назначение
Этот документ описывает fixture-набор для grammar-expanded tooling bundle.

## Наборы
- `core_positive.json` — 16 валидных Core-конструкций
- `core_negative.json` — 14 невалидных Core-конструкций
- `exec_positive.json` — 8 валидных Exec-конструкций
- `exec_negative.json` — 9 невалидных Exec-конструкций
- `human_normalization_positive.json` — 10 валидных Human shorthand cases
- `human_normalization_negative.json` — 5 невалидных Human shorthand cases

## Что добавлено в grammar expansion
- list-scope syntax:
  ```text
  scp=[[NODE]; [NODE]]
  ```
- более сложные scene shorthands для normalizer-а;
- causal scene form через `=>`;
- multiple scene blocks через `;`.

## Что покрыто
- `FRM:INV` с multi-scene scope
- `FRM:TIME` с multi-scene scope
- `PAT:PAL` со scope-list
- `creates`, `destroys`, `depends on`, `equals`
- `declines`, `becomes unstable/stable/open/closed/balanced`
- human shorthand normalization для multi-scene wrappers
````


## FILE: docs/00_PROJECT_IDENTITY.md
Path: `docs/00_PROJECT_IDENTITY.md`

Size: 2794 bytes

````markdown
# 00_PROJECT_IDENTITY

## Название
SEMASCRIPT

## Тип проекта
Нелинейная семасиографическая система записи смысла.

## Краткое определение
SEMASCRIPT — это проект языка / нотации / семантической системы, в которой запись строится не через фонетическую цепочку слов, а через смысловые узлы, отношения, пространственную композицию, режимы чтения и формальные слои семантики.

## Главная цель
Построить систему, которая позволяет:
- компактно записывать сложные структуры смысла;
- выражать не только содержание, но и форму организации содержания;
- поддерживать как человеческое чтение, так и строгое формальное представление;
- в перспективе иметь исполнимое подмножество.

## Что проект должен уметь
- кодировать сущности, процессы, состояния и отношения;
- кодировать причинность, условия, контекст, результат;
- поддерживать нелинейную композицию и радиально-иерархическое чтение;
- иметь каноническую линейную проекцию;
- иметь Human Mode и Exec Mode поверх общего Core;
- поддерживать temporal logic, pattern logic и invariant logic.

## Что проект не должен делать
- не превращаться в декоративный набор красивых символов;
- не зависеть от догадки читателя как основного механизма интерпретации;
- не подменять грамматику визуальной интуицией;
- не пытаться сразу стать универсальным языком для всего;
- не смешивать поэтическую многозначность и исполнимую строгость в одном неразделённом слое.

## Базовая формула проекта
Не слова → а смысловые узлы.

Не линейный порядок → а топология и область действия.

Не только описание → а структурная запись смысла.

Не один режим → а Core + Human + Exec.
````


## FILE: docs/01_ARCHITECTURE_MAP.md
Path: `docs/01_ARCHITECTURE_MAP.md`

Size: 2179 bytes

````markdown
# 01_ARCHITECTURE_MAP

## Общая схема
SEMASCRIPT состоит из трёх основных слоёв:
1. CORE SEMANTICS
2. HUMAN MODE
3. EXEC MODE

Над ними находятся расширяющие логические пакеты.
Под ними — визуальный и инструментальный слой.

## CORE SEMANTICS
Это source of truth для системы.

Состав:
- классы узлов;
- роли;
- правила фокуса;
- правила области действия;
- пространственная грамматика;
- каноническая линейная запись;
- вложенность;
- базовые правила валидации.

## HUMAN MODE
Это слой человеческой коммуникации.

Допустимо:
- сокращение;
- визуальная композиция;
- акцент;
- образность в допустимых границах;
- shorthand для паттернов.

Недопустимо:
- невосстанавливаемая двусмысленность;
- свободные декоративные знаки без маппинга в Core;
- скрытая логика, которую нельзя развернуть в каноническую форму.

## EXEC MODE
Это исполнимый слой.

Требует:
- явные типы;
- явные роли;
- явный scope;
- временную логику, если она влияет на поведение;
- инварианты, если они влияют на операцию;
- строгую валидацию.

## Расширяющие логические слои
### Pattern Logic
- SPR
- GEN
- PAL

### Temporal Logic
- LIN
- CYC
- BRN
- REC
- SIM
- REV
- ATM
- ECH

### Invariant Logic
- ZSUM
- NZSUM
- BAL

## Tooling слой
- parser
- validator
- converters
- human/core projection tools
- exec validation tools

## Главное правило
Core является единственным авторитетным семантическим контрактом между всеми режимами.
````


## FILE: docs/02_CURRENT_STATUS.md
Path: `docs/02_CURRENT_STATUS.md`

Size: 2384 bytes

````markdown
# 02_CURRENT_STATUS

## Статус проекта
SEMASCRIPT находится на стадии концептуально-архитектурной сборки с уже сформированным ядром идей и базовым направлением реализации.

## Что уже достигнуто
- проект осмыслен как нелинейная семасиографическая система;
- зафиксирован принцип “сначала семантическая архитектура, потом глифы”;
- собран базовый каркас Core;
- зафиксирована необходимость канонической линейной проекции;
- зафиксировано разделение на Core / Human / Exec;
- начат расширенный логический слой;
- введены `SPR`, `GEN`, `PAL`, `TIME:*`, `ZSUM`.

## Что уже понятно архитектурно
- нельзя начинать с финальных глифов;
- нельзя смешивать человеческую компрессию и машинную строгость;
- нельзя раздувать словарь до фиксации грамматики;
- нельзя считать символику работающей, пока она не проходит обратимость и тестирование.

## Что пока не завершено
- не реализован parser/validator MVP;
- не собран большой reference corpus;
- не сделаны SVG / glyph prototypes;
- не проведены executable experiments;
- не начат цикл v0.2 refinement.

## Главные риски текущего состояния
- слишком ранний переход к визуальной эстетике;
- попытка сделать сразу полный язык общения, язык программирования и онтологию;
- добавление новых паттернов без decomposition;
- отсутствие corpus-based проверки.

## Правильный фокус
1. baseline и спецификация;
2. тестируемость;
3. Human и Exec профили;
4. tooling MVP;
5. только потом визуальная экспансия.
````


## FILE: docs/03_ROADMAP.md
Path: `docs/03_ROADMAP.md`

Size: 1458 bytes

````markdown
# 03_ROADMAP

## Общая цель roadmap
Перевести SEMASCRIPT из концептуально сильной идеи в рабочую систему с проверяемым ядром, профилями, тестами и прототипами.

## Порядок фаз
### Phase 0 — Alignment / Freeze
- identity
- architecture map
- current status
- scope v0.1

### Phase 1 — Core Specification
- классы узлов
- роли
- focus rule
- scope rule
- canonical form
- базовая валидность

### Phase 2 — Pattern / Time / Invariant Pack
- `SPR`
- `GEN`
- `PAL`
- `TIME:*`
- `ZSUM / NZSUM / BAL`

### Phase 3 — Test Pack
- positive / negative cases
- error classes
- manual validation checklist

### Phase 4 — Human Profile
- сокращения
- omissions
- shorthand
- ambiguity limits
- Human → Core

### Phase 5 — Exec Profile
- executable grammar
- typing
- scope
- validation
- serialization

### Phase 6 — Tooling MVP
- parser
- validator
- converters

### Phase 7 — Glyph Architecture
- shape classes
- modifiers
- frame markers
- layout rules

### Phase 8 — Reference Corpus / Pilots
- corpus
- пилотные домены
- сравнение плотности и ясности

### Phase 9 — v1 Decision Gate
- стабилен ли Core
- читаем ли Human Mode
- валиден ли Exec Mode
- не ломает ли визуальный слой семантику
````


## FILE: docs/04_SCOPE_V0_1.md
Path: `docs/04_SCOPE_V0_1.md`

Size: 1673 bytes

````markdown
# 04_SCOPE_V0_1

## Назначение
Этот документ фиксирует границы версии SEMASCRIPT v0.1.

## Главная цель v0.1
Собрать первую рабочую архитектурную версию SEMASCRIPT как семантической системы с:
- формальным Core;
- базовым расширенным логическим слоем;
- черновыми Human и Exec профилями;
- тестовым пакетом;
- минимальным baseline проекта.

## Что входит в v0.1
- Core semantics baseline
- пространственная грамматика начального уровня
- Pattern logic v0 (`SPR`, `GEN`, `PAL`)
- Temporal logic v0 (`LIN`, `CYC`, `BRN`, `REC`, `REV`, `ATM`)
- Invariant logic v0 (`ZSUM`, `NZSUM`, `BAL`)
- Human Profile draft
- Exec Profile draft
- Test Pack v0.1
- Starter reference corpus

## Что не входит в v0.1
- финальный полный словарь языка;
- полный glyphset / финальный алфавит;
- production-ready язык программирования;
- полная универсальность доменов;
- полноценная IDE и шрифт;
- неограниченное добавление новых архетипов.

## Приоритеты внутри v0.1
1. Семантическая стабильность.
2. Обратимость.
3. Проверяемость.
4. Разделение профилей.
5. Контролируемое расширение логики.
6. Потом — визуальная экспансия.
````


## FILE: docs/SEMASCRIPT_0_SEMANTIC_BASELINE.md
Path: `docs/SEMASCRIPT_0_SEMANTIC_BASELINE.md`

Size: 2146 bytes

````markdown
# SEMASCRIPT_0_SEMANTIC_BASELINE

## Назначение
Этот документ фиксирует ранний смысловой baseline проекта как черновую нулевую спецификацию до детализации отдельных профилей.

## Базовая идея
SEMASCRIPT — это нелинейная система записи смысла, в которой:
- запись строится через смысловые узлы;
- чтение организуется топологически;
- композиция важнее линейной строки;
- значения должны быть разложимы и обратимы.

## Базовые классы
- Object / Entity
- Process
- State
- Relation
- Modifier
- Frame
- Index

## Базовые операторы роли
- субъект / агент
- объект
- причина
- следствие
- контекст
- результат
- зависимость
- модификация

## Пространственная логика
- центр = главное ядро
- север = условия / контекст / модальность / время
- запад = источник / агент / причина
- восток = цель / объект / выход
- юг = результат / следствие
- внутри = состав
- вокруг = модификаторы
- рамка = область действия

## Режим чтения
1. найти фокус
2. определить активную рамку
3. прочитать север
4. прочитать запад
5. прочитать восток
6. прочитать юг
7. раскрыть вложенность
8. собрать линейную проекцию

## Главные ранние принципы
- сначала semantic architecture, потом glyph design;
- сначала decomposition, потом compression;
- без canonical projection система не считается рабочей;
- без grammar pattern-forms превращаются в хаос.
````


## FILE: docs/SEMASCRIPT_AST_INTEGRATION_PACK_v0.1.md
Path: `docs/SEMASCRIPT_AST_INTEGRATION_PACK_v0.1.md`

Size: 873 bytes

````markdown
# SEMASCRIPT_AST_INTEGRATION_PACK_v0.1

## Назначение
Этот документ описывает слой интеграции между:
- parser/normalizer text forms
- AST schema
- validator pipeline

## Что добавлено
- `semascript_ast.py`
- `parse_to_ast.py`
- `serialize_ast.py`
- `validate_ast.py`

## Роль
Теперь parser и normalizer могут выдавать не только внутренние Python-структуры, но и канонический AST document JSON, согласованный с `SEMASCRIPT_AST_SCHEMA_v0.1`.

## Главный маршрут
```text
Human/Core/Exec text -> parse/normalize -> AST JSON -> validate -> report
```

## Важный эффект
Это снимает главный текущий разрыв между:
- спецификацией AST
- реальным tooling MVP
````


## FILE: docs/SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1.md
Path: `docs/SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1.md`

Size: 1551 bytes

````markdown
# SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1

## Назначение
Этот документ описывает **batch runtime/state corpus pipeline** для SEMASCRIPT v0.1.

Его задача:
- прогонять серию сценариев через runtime;
- прогонять те же сценарии через state model;
- собирать batch-отчёты;
- выявлять системные ошибки не по одному примеру, а по корпусу.

## Что добавлено
- `tooling/run_runtime_corpus.py`
- `tooling/run_state_corpus.py`
- `tooling/run_batch_runtime_state_corpus_checks.py`
- `tooling/corpus/runtime_state_corpus_manifest.json`
- sample runtime/state corpus reports

## Pipeline
1. взять `runtime_state_corpus_manifest.json`
2. для каждого entry:
   - прочитать `profile`
   - запустить runtime
   - при необходимости запустить state model с `initial_state`
3. собрать:
   - runtime batch report
   - state batch report
   - summary counts

## Форматы отчётов
### Runtime batch
- `accepted`
- `plan_length`
- `schedule`
- `invariant_law`
- `errors`
- `notes`

### State batch
- `accepted`
- `history_len`
- `dependency_count`
- `expansion_count`
- `action_count`
- `observation_count`
- `errors`

## Практический смысл
Этот слой переводит runtime/state execution из точечных smoke-тестов в **серийную корпусную проверку**.
````


## FILE: docs/SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1.md
Path: `docs/SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1.md`

Size: 1659 bytes

````markdown
# SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1

## Назначение
Этот документ описывает следующий слой после branching / named merge lineage graph:
**branch rebase / replay onto target lineage**.

## Что это даёт
Теперь workspace умеет:
- выбрать source branch;
- выбрать target branch;
- replay-ить commits source branch onto target lineage;
- создавать новые rebased session entries;
- обновлять head source branch;
- сохранять provenance rebase replay;
- отражать результат в lineage graph и timeline.

## Что добавлено
- `tooling/project_rebase.py`
- `/api/rebase-project-branch`
- rebase panel in inspector
- `run_branch_rebase_checks.py`
- sample rebased project / result / lineage graph JSON

## Rebase policy v0.1
Это **conservative replay rebase**, а не destructive history rewrite.

### Как работает
- source branch root не копируется;
- commits source branch после fork point replay-ятся как новые entries;
- первый replay commit получает parent = current head target branch;
- следующие replay commits строятся цепочкой поверх предыдущего replay;
- новые replay commits остаются в `source_branch_name`.

### Provenance
Каждый replay commit получает:
- `commit_kind = rebase_replay`
- `rebase_replay.source_branch_name`
- `rebase_replay.target_branch_name`
- `rebase_replay.original_session_id`
- `rebase_replay.replay_index`

## History event
- `branch_rebased`
````


## FILE: docs/SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1.md
Path: `docs/SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1.md`

Size: 1407 bytes

````markdown
# SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1

## Назначение
Этот документ описывает следующий слой после merge commit / resolved session insertion:
**branching / named merge lineage graph**.

## Что это даёт
Теперь workspace умеет:
- иметь named branches;
- создавать ветку от активной сессии;
- сохранять branch metadata у session entries;
- строить lineage graph с parent / merge-parent edges;
- показывать branch heads и lineage graph в inspector.

## Что добавлено
- `tooling/project_branching.py`
- branching-aware `project_model.py`
- create-branch API in inspector
- branch panel + lineage graph in inspector
- `run_branching_checks.py`
- sample branching project + lineage graph JSON

## Branch metadata
Каждая session entry теперь может нести:
```json
{
  "branching": {
    "branch_name": "main",
    "parent_session_ids": ["..."],
    "lineage_kind": "commit | merge_commit | root"
  }
}
```

## Lineage graph
Graph строится по:
- `branch_name`
- `parent_session_ids`
- `lineage_kind`

Типы ребер:
- `parent`
- `merge_parent`

## Merge commit integration
Merge commit теперь можно направить в named branch.
Committed session попадает в lineage graph как merge node.
````


## FILE: docs/SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1.md
Path: `docs/SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1.md`

Size: 1659 bytes

````markdown
# SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1

## Назначение
Этот документ описывает следующий слой после branch rebase / replay onto target lineage:
**cherry-pick / selective session replay across branches**.

## Что это даёт
Теперь workspace умеет:
- выбрать одну или несколько session entries;
- выбрать target branch;
- replay-ить выбранные sessions как новые commits в target branch;
- сохранять provenance cherry-pick;
- отражать результат в lineage graph и history.

## Что добавлено
- `tooling/project_cherrypick.py`
- `/api/cherry-pick-project-sessions`
- cherry-pick panel in inspector
- `run_cherry_pick_checks.py`
- sample cherry-picked project / result / lineage graph JSON

## Semantics v0.1
Это **selective replay**, а не перенос ссылки на исходный commit.

### Как работает
- выбранные `source_session_ids` replay-ятся в указанном порядке;
- первый cherry-pick commit получает parent = current head target branch;
- следующие cherry-pick commits строятся цепочкой поверх предыдущего cherry-pick;
- новые replay commits живут в `target_branch_name`.

## Provenance
Каждый replay commit получает:
- `commit_kind = cherry_pick`
- `cherry_pick.source_session_id`
- `cherry_pick.source_branch_name`
- `cherry_pick.target_branch_name`
- `cherry_pick.cherry_pick_index`

## History event
- `branch_cherry_picked`
````


## FILE: docs/SEMASCRIPT_CORE_SPEC_v0.1.md
Path: `docs/SEMASCRIPT_CORE_SPEC_v0.1.md`

Size: 3662 bytes

````markdown
# SEMASCRIPT_CORE_SPEC_v0.1

## Статус
Draft baseline specification

## Назначение
Этот документ фиксирует Core semantics baseline для SEMASCRIPT v0.1.

## Главный принцип
Core — это source of truth.

Любая запись SEMASCRIPT считается корректной только в той степени, в которой её можно:
1. разложить в Core;
2. прочитать по правилам Core;
3. проверить на валидность по правилам Core.

---

## 1. Модель Core
SEMASCRIPT Core описывает смысл как структурированную композицию узлов, ролей, областей действия и рамок.

## 2. Базовые единицы
- Node
- Construction
- Frame

## 3. Классы узлов
- `ENT`
- `PRC`
- `STA`
- `REL`
- `MOD`
- `FRM`
- `IDX`

## 4. Нормативные инварианты Core
- один фокус;
- каждый узел типизирован;
- у каждой связи есть роль;
- scope обязателен;
- каноническая форма обязательна;
- вложенность сильнее визуальной близости;
- графика вторична.

## 5. Семантические роли
- `agt`
- `obj`
- `src`
- `dst`
- `ctx`
- `res`
- `cau`
- `dep`
- `mod`
- `ins`
- `loc`
- `tim`
- `scp`

## 6. Фокус и центр конструкции
Чтение всегда начинается с фокуса.
У завершённой конструкции должен быть ровно один фокус.

## 7. Пространственная грамматика v0.1
- центр — фокус
- север — условия / контекст / модальность / время
- запад — источник / агент / причина
- восток — объект / цель / выход
- юг — результат / следствие
- внутри — состав
- вокруг — модификаторы
- рамка — область действия

## 8. Scope
Если scope неясен, Core-конструкция невалидна.

## 9. Вложенность
Вложенный блок читается как subordinate semantic unit.
Вложенность не должна разрушать главный фокус текущего уровня.

## 10. Каноническая линейная запись
```text
[CLASS:ROOT {modifiers} <role=value; role=value; ...>]
```

## 11. Модификаторы
Модификатор не существует сам по себе без target.

## 12. Рамки
Типовые рамки:
- `FRM:SCN`
- `FRM:TIME`
- `FRM:INV`
- `FRM:CND`
- `FRM:CTX`

## 13. Core и расширяющие слои
Поверх Core подключаются:
- Pattern Logic
- Temporal Logic
- Invariant Logic

## 14. Валидность конструкции
Конструкция валидна, если:
- есть один фокус;
- все узлы типизированы;
- роли указаны или однозначно восстановимы;
- scope понятен;
- каноническая форма собирается.

## 15. Error classes v0.1
- `C001` — missing focus
- `C002` — untyped node
- `C003` — ambiguous role
- `C004` — undefined scope
- `C005` — unattached modifier
- `C006` — invalid nesting
- `C007` — non-canonical construction
- `C008` — unresolved frame boundary
- `C009` — conflicting focus
- `C010` — unrecoverable ambiguity
````


## FILE: docs/SEMASCRIPT_CORPUS_PIPELINE_v0.1.md
Path: `docs/SEMASCRIPT_CORPUS_PIPELINE_v0.1.md`

Size: 867 bytes

````markdown
# SEMASCRIPT_CORPUS_PIPELINE_v0.1

## Назначение
Этот документ описывает batch pipeline для corpus обработки.

## Что добавлено
- `normalize_corpus.py`
- `validate_corpus.py`
- `corpus/corpus_manifest.json`
- sample normalized corpus JSON
- sample validation report JSON

## Pipeline
1. взять `corpus_manifest.json`
2. определить profile (`human/core/exec`)
3. если `human` — прогнать normalizer
4. построить AST document
5. прогнать validator
6. записать normalized corpus / validation report

## Выходные форматы
- `SEMASCRIPT_CORPUS_NORMALIZED_v0.1`
- `SEMASCRIPT_CORPUS_REPORT_v0.1`

## Практический смысл
Это переводит систему от одиночных fixtures к batch-проверке корпуса.
````


## FILE: docs/SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1.md
Path: `docs/SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1.md`

Size: 1438 bytes

````markdown
# SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1

## Назначение
Этот документ описывает следующий слой после workspace timeline / session evolution history:
**cross-session compare / diff mode**.

## Что это даёт
Теперь project workspace умеет не только:
- хранить и переключать сессии,
- строить dependency map,
- показывать timeline,

но и:
- сравнивать две выбранные сессии напрямую,
- видеть структурные и execution-различия,
- сравнивать сущности, inputs/outputs, runtime-операции и state metrics.

## Что добавлено
- `tooling/session_diff.py`
- `/api/compare-project-sessions` in inspector server
- compare panel in inspector UI
- `run_cross_session_compare_checks.py`
- sample compare sessions / project / diff JSON

## Что сравнивается v0.1
### Identity
- `profile`
- `source_mode`

### Structure
- `slinear`
- `decomposed_slinear`
- `entities`
- `inputs`
- `outputs`
- `state_nodes`

### Execution
- `runtime_accepted`
- `state_accepted`
- `runtime_ops`
- `dependency_count`
- `expansion_count`
- `action_count`
- `observation_count`
- `history_len`

## Граница v0.1
Это уже полезный engineering diff,
но ещё не semantic theorem prover и не three-way merge.
````


## FILE: docs/SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1.md
Path: `docs/SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1.md`

Size: 2171 bytes

````markdown
# SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1

## Назначение
Этот документ описывает **editable visual graph mode** как следующий приоритетный слой после inspector.

## Почему он выше session format
Сначала системе нужен полноценный графический режим редактирования:
- import text -> graph
- edit graph entities
- edit graph edges / roles
- set root entity
- re-run graph through AST / validation / runtime / state / SVG

Только после этого правильно делать persisted project/session format, потому что тогда уже есть что сохранять как рабочую визуальную сцену.

## Что добавлено
- `tooling/graph_model.py`
- `tooling/inspector_service.py` (graph bridge)
- `tooling/inspector_server.py` (graph API)
- `tooling/run_inspector_smoke_checks.py`
- `inspector/index.html`
- `inspector/app.js`
- `inspector/styles.css`

## Graph model
Введён локальный graph-format:
- `root_entity_id`
- `entities`
- `edges`

### Entity kinds
- `node`
- `list`
- `raw_token`
- `typed_literal`

### Node entity
Хранит:
- `class_name`
- `root`
- `modifiers`
- `x`
- `y`

### Edge
Хранит:
- `from_id`
- `to_id`
- `role`
- `order`

## Что умеет graph mode
- загрузить текст и превратить его в graph
- визуально перетаскивать entities
- редактировать selected entity
- создавать role-edges
- задавать root entity
- прогонять graph обратно через:
  - AST
  - validation
  - runtime
  - state
  - SVG preview

## Как запускать
```bash
python tooling/inspector_server.py --host 127.0.0.1 --port 8765
```

Открыть:
```text
http://127.0.0.1:8765
```

## Граница v0.1
Это editable graph mode, а не full graphical IDE.
Он уже делает inspector рабочим редактором, но ещё не даёт:
- session persistence
- collaborative editing
- undo/redo stack
- project workspace
````


## FILE: docs/SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1.md
Path: `docs/SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1.md`

Size: 1474 bytes

````markdown
# SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1

## Назначение
Этот документ описывает **editor / visual inspector** как следующий UI-слой SEMASCRIPT после v0.2 hardening.

## Почему сейчас
Теперь под ним уже есть устойчивый operational contour:
- Human normalizer
- AST
- validation
- pattern decomposition
- runtime
- state model
- batch corpus
- SVG renderer
- hardening regression suite

## Что делает inspector
Inspector объединяет в одном локальном интерфейсе:
1. source input
2. profile selection (`human/core/exec`)
3. optional decomposition
4. initial state JSON
5. normalized text / S-Linear
6. AST view
7. validation view
8. runtime view
9. state view
10. SVG preview

## Что добавлено
- `tooling/inspector_service.py`
- `tooling/inspector_server.py`
- `tooling/run_inspector_smoke_checks.py`
- `inspector/index.html`
- `inspector/app.js`
- `inspector/styles.css`

## Как запускать
```bash
python tooling/inspector_server.py --host 127.0.0.1 --port 8765
```

После этого открыть в браузере:
```text
http://127.0.0.1:8765
```

## Граница v0.1
Это local inspector, а не production multi-user IDE.
Он нужен для:
- engineering inspection,
- visual debugging,
- manual scenario analysis,
- UI validation поверх уже собранной системы.
````


## FILE: docs/SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md
Path: `docs/SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md`

Size: 4136 bytes

````markdown
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
````


## FILE: docs/SEMASCRIPT_EXEC_PROFILE_v0.1.md
Path: `docs/SEMASCRIPT_EXEC_PROFILE_v0.1.md`

Size: 5900 bytes

````markdown
# SEMASCRIPT_EXEC_PROFILE_v0.1

## Статус
Draft executable subset specification

## Назначение
Этот документ задаёт **Exec Mode** для SEMASCRIPT.

Его задача:
- выделить строгое исполнимое подмножество;
- потребовать явные типы, роли и scope;
- нормализовать переход Core → Exec;
- запретить исполнение через догадку;
- задать базовую validation discipline.

## Главный принцип
Не всякая Core-конструкция исполнима.  
Но всякая исполнимая конструкция обязана быть валидной Core-конструкцией.

---

## 1. Роль Exec Mode
Exec Mode нужен для:
- rule execution;
- deterministic transformation;
- state transition;
- declared action semantics;
- constrained machine interpretation.

Он не нужен для:
- свободной метафоры;
- недоопределённых сообщений;
- purely visual composition;
- implicit semantics.

---

## 2. Executable subset v0.1

### Supported classes
- `ENT`
- `PRC`
- `STA`
- `REL`
- `FRM:TIME`
- `FRM:INV`
- `MOD:NEG`

### Supported operational profiles
- transfer
- create
- destroy
- act
- observe
- change
- simple condition
- simple causal chain
- declared invariant
- declared time mode

### Not executable directly
- `PAT:SPR`
- `PAT:GEN`
- `PAT:PAL`

Они допустимы только после decomposition into executable semantics.

---

## 3. Exec requirements

### E1 — Explicit typing
Каждый значимый операнд должен иметь тип.

### E2 — Explicit roles
Все операционные роли должны быть указаны явно.

### E3 — Explicit scope
Scope не может восстанавливаться “по рисунку” или по интуиции.

### E4 — Temporal declaration if behaviorally relevant
Если время влияет на интерпретацию, нужен явный `FRM:TIME`.

### E5 — Invariant declaration if behaviorally relevant
Если закон сохранения влияет на выполнение, нужен явный `FRM:INV` или equivalent operational invariant.

### E6 — No unresolved referents
Нельзя исполнять конструкции с недоопределёнными ссылками.

---

## 4. Canonical Exec surface

В v0.1 допускается следующая нормальная surface-форма:

```text
[EXEC:OPERATION <
  role=value;
  role=value;
  ...
>]
```

### Examples
```text
[EXEC:TRANSFER <
  src=[ENT:A];
  dst=[ENT:B];
  obj=[ENT:RES]
>]
```

```text
[EXEC:ACT <
  agt=[ENT:HUM];
  obj=[ENT:SYS];
  time=[TIME:LIN]
>]
```

```text
[EXEC:CREATE <
  dst=[ENT:SYS];
  obj=[ENT:RES];
  invariant=[LAW:NZSUM]
>]
```

---

## 5. Core → Exec mapping rules

### Rule X1 — Processes map to operations
`PRC:*` Core forms may map to `EXEC:*` operations if complete enough.

### Rule X2 — Frames become execution constraints
`FRM:TIME` and `FRM:INV` do not disappear; they become execution constraints or execution modifiers.

### Rule X3 — Pattern layer must decompose first
Pattern macros do not map directly to executable operations.

### Rule X4 — Human omission is illegal in Exec
Everything required operationally must be explicit.

---

## 6. Minimal executable grammar

```text
EXEC_FORM :=
  [EXEC:OP <role=value; role=value; ...>]

value :=
  typed node
  | typed literal
  | execution constraint
  | nested executable block (limited)

typed node :=
  [ENT:...]
  | [STA:...]
  | [VAL:...]

execution constraint :=
  [TIME:LIN]
  [TIME:CYC]
  [LAW:ZSUM]
  [LAW:NZSUM]
```

---

## 7. Supported operations v0.1

### EXEC:TRANSFER
Required roles:
- `src`
- `dst`
- `obj`

Optional:
- `qty`
- `time`
- `invariant`

### EXEC:CREATE
Required:
- `dst`
- `obj`

Optional:
- `qty`
- `time`
- `invariant`

### EXEC:DESTROY
Required:
- `obj`

Optional:
- `ctx`
- `time`
- `invariant`

### EXEC:ACT
Required:
- `agt`

Optional:
- `obj`
- `ctx`
- `time`

### EXEC:OBSERVE
Required:
- `agt`
- `obj`

Optional:
- `time`

### EXEC:CHANGE
Required:
- `obj`

Optional:
- `res`
- `time`
- `ctx`

---

## 8. Validation errors

- `X001` — missing executable operation
- `X002` — missing required role
- `X003` — untyped executable operand
- `X004` — unresolved referent
- `X005` — undefined scope
- `X006` — unsupported pattern macro in exec
- `X007` — undeclared invariant
- `X008` — undeclared time constraint
- `X009` — human-only compression inside exec
- `X010` — non-deterministic interpretation

---

## 9. Examples

### Example E-1 — Valid transfer
```text
[EXEC:TRANSFER <
  src=[ENT:ACCOUNT_A];
  dst=[ENT:ACCOUNT_B];
  obj=[ENT:CREDIT];
  qty=[VAL:10];
  invariant=[LAW:ZSUM]
>]
```

### Example E-2 — Valid action
```text
[EXEC:ACT <
  agt=[ENT:HUM];
  obj=[ENT:SYS];
  time=[TIME:LIN]
>]
```

### Example E-3 — Invalid due to pattern
```text
[EXEC:SPR <core=[ENT:SEED]; res=[ENT:FORM]>]
```
**Expected:** invalid (`X006`)

### Example E-4 — Invalid due to missing role
```text
[EXEC:TRANSFER <dst=[ENT:B]; obj=[ENT:RES]>]
```
**Expected:** invalid (`X002`)

### Example E-5 — Invalid due to metaphor
```text
[EXEC:ACT <agt=[ENT:DESTINY]; obj=[ENT:BECOMING]>]
```
**Expected:** invalid unless these referents are formally defined entities

---

## 10. Criteria of readiness

Exec Profile v0.1 можно считать рабочим, если:
- есть минимальная executable grammar;
- есть набор supported operations;
- есть validation errors;
- есть понятный Core → Exec mapping;
- недоопределённые конструкции reliably reject instead of guessing.
````


## FILE: docs/SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1.md
Path: `docs/SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1.md`

Size: 4290 bytes

````markdown
# SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1

## Назначение
Этот документ задаёт **restricted exec runtime semantics** для SEMASCRIPT v0.1.

Его задача:
- определить, как `EXEC`-операции интерпретируются в runtime;
- определить действие `FRM:TIME` и `FRM:INV`;
- определить поведение multi-scene `scp`;
- определить, как decomposed pattern forms входят в runtime path;
- ввести deterministic rejection rules.

## Главный принцип
Runtime v0.1 не пытается исполнять “всё”.
Он исполняет только:
- supported `EXEC` operations;
- ограниченный набор Core-derived runtime forms;
- time/invariant constraints, которые заданы явно.

---

## 1. Runtime entry forms

Допустимые точки входа:
- top-level `EXEC:*`
- `FRM:TIME <scp=...>`
- `FRM:INV <scp=...>`
- `FRM:SCN <scp=...>`
- Core forms после decomposition:
  - `PRC:EXP`
  - `REL:DEP`
  - `REL:CAU`
  - `STA:*`

---

## 2. Supported EXEC operations

- `EXEC:TRANSFER`
- `EXEC:CREATE`
- `EXEC:DESTROY`
- `EXEC:ACT`
- `EXEC:OBSERVE`
- `EXEC:CHANGE`

Все остальные операции в runtime v0.1 считаются unsupported.

---

## 3. Time semantics

### `TIME:LIN`
- multi-scene `scp` исполняется как `sequential`

### `TIME:CYC`
- multi-scene `scp` трактуется как `cyclical`
- runtime plan помечается циклическим schedule

### `TIME:BRN`
- набор сцен трактуется как `branch_set`
- выбор ветви в v0.1 не делается автоматически
- runtime возвращает deferred branch semantics

### `TIME:REC`
- набор сцен трактуется как `recursive`

### `TIME:REV`
- требует обратимых операций
- `CREATE` и `DESTROY` под `REV` запрещены

### `TIME:ATM`
- не навязывает линейный temporal order
- используется для atemporal / dependency-like runtime plans

---

## 4. Invariant semantics

### `ZSUM`
Разрешает только redistributive operations.
В runtime v0.1:
- `TRANSFER` допустим
- `CREATE` запрещён
- `DESTROY` запрещён

### `NZSUM`
Используется для чистого роста / убыли.
В runtime v0.1:
- `CREATE` и `DESTROY` допустимы
- bare `TRANSFER` под `NZSUM` отвергается

### `BAL`
В runtime v0.1 не считается operational law.
Это postcondition-like concept, а не direct runtime invariant.
Поэтому direct execution under `BAL` отвергается.

---

## 5. Multi-scene scope

`scp=[[NODE]; [NODE]]` теперь трактуется как runtime scene-set.

В зависимости от `TIME`:
- `LIN` -> sequential list
- `CYC` -> cyclical list
- `BRN` -> branch set
- `REC` -> recursive set
- `ATM` -> atemporal set

Без `TIME`:
- multiple `scp` items трактуются как sequential list by default

---

## 6. Pattern decomposition in runtime

Runtime v0.1 не исполняет raw `PAT:*` напрямую.

Перед runtime:
- `PAT:SPR` -> `PRC:EXP`
- `PAT:GEN` -> `REL:DEP`
- `PAT:PAL` -> `FRM:SCN`

Это делает runtime path operationally tractable без PAT macros в critical execution path.

---

## 7. Deterministic rejection rules

Runtime обязан reject:
- unsupported `EXEC` operations
- missing required roles
- `ZSUM + CREATE/DESTROY`
- `NZSUM + bare TRANSFER`
- `BAL` как direct runtime law
- `REV + non-reversible op`
- undecomposed unsupported pattern
- unsupported frame root in runtime path

---

## 8. Current boundary

Runtime v0.1 — это:
- execution planner
- constrained semantics layer
- deterministic acceptance / rejection layer

Это ещё не:
- полноценный stateful virtual machine
- complete executor for all Core forms
- full branch selector
- final programming runtime

---

## 9. Следующий сильный шаг

После runtime semantics логично идти в:
1. state model / execution state container
2. batch runtime corpus
3. renderer / SVG prototypes
````


## FILE: docs/SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md
Path: `docs/SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`

Size: 5791 bytes

````markdown
# SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1

## Статус
Draft visual architecture

## Назначение
Этот документ задаёт начальную архитектуру глифов для SEMASCRIPT.

Его задача:
- построить визуальный слой без разрушения Core;
- стандартизировать shape classes;
- отделить класс формы от корня смысла;
- задать систему модификаторов;
- подготовить базу для SVG / шрифта / редактора.

## Главный принцип
Глиф — это surface-carrier смысла, а не самостоятельный источник семантики.

Визуальный слой вторичен по отношению к Core.

---

## 1. Layered glyph model

Каждый глиф в v0.1 должен рассматриваться как трёхслойный объект:
1. **Class shape**
2. **Semantic root**
3. **Operational markers**

---

## 2. Class shapes

### ENT
Базовая форма: круг / кругоподобная замкнутая фигура

### PRC
Базовая форма: треугольник / направленная острая форма

### STA
Базовая форма: квадрат / прямоугольная устойчивая форма

### REL
Базовая форма: ромб / узловой стык

### MOD
Базовая форма: дуга / малая приставка / надстройка

### FRM
Базовая форма: контейнер / рамка / охватывающий контур

### IDX
Базовая форма: точка / маркер / осевая отметка

---

## 3. Semantic root principle

Внутри class shape должен находиться root-pattern.

Root-pattern:
- не должен ломать читаемость class shape;
- должен быть различим на малом размере;
- должен быть пригоден для сериализации и повторения;
- не должен превращаться в декоративный шум.

---

## 4. Modifier system

### Suggested markers
- `NEG` — диагональный штрих / slash
- `INT` — усилительный дублирующий контур
- `PLR` — множественный маркер / повторная точка
- `UNC` — пунктирный контур
- `NEC` — утолщённый контур
- `POT` — полуконтур / открытая возможность
- `CND` — верхний условный маркер

### Rule
Модификатор не должен скрывать class identity.

---

## 5. Frame markers

### `FRM:TIME`
внешний временной контур или режимный header-marker

### `FRM:INV`
инвариантный замыкающий контур с law marker

### `FRM:CND`
условная рамка с северным заголовком

### `FRM:SCN`
общая сценическая рамка

---

## 6. Spatial composition rules

### Rule G1 — Focus first
Фокус визуально должен быть наиболее считываемым узлом.

### Rule G2 — Scope visibility
Scope должен быть видим не только логически, но и композиционно.

### Rule G3 — Nesting beats proximity
Вложенный блок должен выглядеть вложенным.

### Rule G4 — Modifier attachment must be clear
Должно быть ясно, к чему относится модификатор.

### Rule G5 — Frame boundaries must be readable
Рамка обязана показывать, что входит в её действие.

---

## 7. Visual priorities
1. class identity
2. focus readability
3. frame / scope readability
4. role-supporting layout
5. modifier clarity
6. root distinctiveness
7. aesthetic refinement

---

## 8. Early glyph families

### Core class family
- ENT base
- PRC base
- STA base
- REL base
- MOD base
- FRM base
- IDX base

### Minimal root family
16–32 базовых корня на черновом уровне.

### Modifier family
6–10 служебных маркеров.

### Frame family
4–6 базовых рамок.

---

## 9. Glyph validation checklist

Для каждого глифа проверить:
1. Читается ли его класс?
2. Видно ли отличие от соседних классов?
3. Не съедает ли root-pattern class shape?
4. Можно ли однозначно прицепить модификатор?
5. Можно ли уменьшить знак без потери различимости?
6. Можно ли сериализовать / переиспользовать знак?
7. Не создаёт ли графика скрытую неописанную семантику?

---

## 10. What v0.1 does not finalize
Этот документ не фиксирует:
- финальный художественный стиль;
- полный алфавит;
- готовый шрифт;
- редактор;
- финальную систему stroke-weight;
- финальный orthographic beauty layer.

---

## 11. Criteria of readiness
Glyph Architecture v0.1 можно считать собранной, если:
- shape classes стандартизированы;
- модификаторы разведены;
- рамки имеют понятную композиционную роль;
- есть baseline для SVG / font experiments;
- визуальный слой не противоречит Core semantics.
````


## FILE: docs/SEMASCRIPT_GRAMMAR_EXPANSION_v0.1.md
Path: `docs/SEMASCRIPT_GRAMMAR_EXPANSION_v0.1.md`

Size: 1918 bytes

````markdown
# SEMASCRIPT_GRAMMAR_EXPANSION_v0.1

## Назначение
Этот документ описывает расширение grammar слоя для parser/validator/normalizer.

## Что добавлено

### 1. List-scope syntax
Теперь parser поддерживает list-scope конструкции вида:
```text
[FRM:INV <law=ZSUM; scp=[[PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]; [PRC:TRF <src=[ENT:B]; dst=[ENT:C]; obj=[ENT:CREDIT]>]]>]
```

Это позволяет:
- задавать несколько сцен внутри `scp`;
- собирать multi-scene временные и инвариантные рамки;
- делать scope-list внутри pattern forms.

### 2. Expanded Human scene grammar
Human normalizer теперь поддерживает:
- transfer scene
- observe scene
- act-on scene
- create scene
- destroy scene
- dependency scene
- equality scene
- decline/increase states
- becomes-state transitions
- causal shorthand через `=>`
- multi-scene scope через `;`

### 3. MVP boundary
Расширение grammar не превращает систему в freeform natural-language parser.
Всё ещё поддерживается только стандартизированный shorthand.

## Архитектурный смысл
Это расширение важно, потому что:
- делает `scp` пригодным для реальных сценических блоков;
- усиливает Human → Core bridge;
- готовит систему к batch corpus normalization;
- приближает grammar к реальным use-case, а не только к toy examples.

## Что остаётся следующим шагом
- richer nested list semantics;
- batch normalizer for corpus files;
- parser support for broader literal/value types;
- deeper executable mapping for decomposed patterns.
````


## FILE: docs/SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md
Path: `docs/SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md`

Size: 6711 bytes

````markdown
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
````


## FILE: docs/SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1.md
Path: `docs/SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1.md`

Size: 1250 bytes

````markdown
# SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1

## Назначение
Этот документ описывает Human normalizer MVP и его grammar-expanded версию.

## Что он делает
Human normalizer:
1. принимает стандартизированный Human shorthand;
2. переводит его в Core form;
3. подаёт результат в parser/validator pipeline.

## Поддерживаемые wrappers
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `state:bal(...)`
- `inv:zsum(...)`
- `inv:nzsum(...)`
- `time:*`

## Поддерживаемые scene forms
- transfer
- observe
- act-on
- create
- destroy
- dependency
- equality
- decline / increase
- becomes-state
- causality via `=>`
- multi-scene via `;`

## Граница MVP
Это не parser свободного русского или английского текста.
Это deterministic shorthand normalizer.

## Практический смысл
Нормализатор уже позволяет:
- писать короткие Human forms;
- получать из них валидный Core;
- проверять их через tooling MVP;
- расширять corpus без ручной переписи каждого кейса.
````


## FILE: docs/SEMASCRIPT_HUMAN_PROFILE_v0.1.md
Path: `docs/SEMASCRIPT_HUMAN_PROFILE_v0.1.md`

Size: 7533 bytes

````markdown
# SEMASCRIPT_HUMAN_PROFILE_v0.1

## Статус
Draft communicative profile

## Назначение
Этот документ задаёт **Human Mode** для SEMASCRIPT.

Его задача:
- сделать язык пригодным для человеческого чтения и записи;
- разрешить контролируемую компрессию;
- определить допустимые сокращения;
- удержать границу между выразительностью и хаосом;
- обеспечить Human → Core проекцию.

## Главный принцип
Human Mode может быть компактнее Core, но не может вводить смысл, который нельзя восстановить в Core.

---

## 1. Роль Human Mode
Human Mode нужен для:
- быстрых сообщений;
- концептуальных записей;
- причинно-следственных схем;
- структурного общения;
- образовательных и проектных заметок;
- наглядной работы с pattern / time / invariant logic.

Он не предназначен для:
- окончательной семантической истины;
- замены Core;
- прямого исполнения.

---

## 2. Что Human Mode разрешает

### 2.1 Compression
Разрешено:
- сокращать повторяющиеся элементы;
- опускать очевидные типы;
- заменять канонические формы человекочитаемыми шаблонами;
- использовать стрелки, краткие маркеры, фокусные слова.

### 2.2 Recoverable omission
Разрешено опускать только то, что:
- восстанавливается из общего grammar;
- однозначно выводится из ближайшего контекста;
- не влияет на critical scope.

### 2.3 Emphasis
Разрешено:
- выделение фокуса;
- акцент;
- тематическое сжатие;
- маркировка важности;
- surface shorthand для уже стандартизированных паттернов.

### 2.4 Pattern shorthand
Разрешены shorthand-формы для:
- `SPR`
- `GEN`
- `PAL`
- `TIME:*`
- `ZSUM / NZSUM / BAL`

Но только если они стандартизированы и читаемы.

---

## 3. Что Human Mode запрещает

### 3.1 Unrecoverable ambiguity
Запрещено:
- писать так, что роль нельзя восстановить;
- смешивать несколько смыслов без markers;
- опираться только на интуитивную картинку.

### 3.2 Decorative-only glyphs
Нельзя использовать символ, если он:
- не маппится в Core;
- не имеет scope;
- не имеет понятной роли.

### 3.3 Human metaphor as Core fact
Нельзя выдавать метафору за каноническую семантику.

### 3.4 Direct executability by implication
Human Mode не имеет права “как бы автоматически” считаться исполнимым.

---

## 4. Допустимые surface-стратегии

### 4.1 Arrow notation
Примеры:
```text
A -> B
A => B
A <-> B
```

Допустимо, если роль легко восстанавливается:
- `->` обычно = transfer / direction
- `=>` обычно = causal or logical implication
- `<->` обычно = equivalence / mutual relation

### 4.2 Focus-first fragments
Пример:
```text
focus: resource transfer, zero-sum
```

### 4.3 Layered shorthand
Примеры:
```text
cycle(system)
zsum(A->B:res)
spr(seed -> form)
gen(template -> instance)
```

### 4.4 Structured prose
Допустима компактная фраза:
```text
system enters cyclical change under zero-sum transfer of resource
```

---

## 5. Human markers v0.1

### Recommended shorthand markers
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `time:lin`
- `time:cyc`
- `time:brn`
- `time:rec`
- `time:rev`
- `time:atm`
- `inv:zsum`
- `inv:nzsum`
- `state:bal`

### Examples
```text
spr(seed -> form)
gen(template -> module)
time:cyc(system change)
inv:zsum(A -> B : resource)
state:bal(system)
```

---

## 6. Human → Core projection rules

### Rule H1 — Focus reconstruction
У каждой Human-записи должен восстанавливаться один основной фокус.

### Rule H2 — Missing types may be restored only if obvious
Если из Human surface ясно, что `A` и `B` — сущности, тип `ENT` можно восстановить.

### Rule H3 — Scope must become explicit in Core
Даже если в Human scope намечен интуитивно, в Core он должен стать явным.

### Rule H4 — Pattern shorthand expands to pattern layer
`spr(...)`, `gen(...)`, `pal(...)` не превращаются напрямую в Exec; сначала они переходят в pattern layer/Core-compatible form.

### Rule H5 — Temporal and invariant hints must be normalized
`cycle(...)` → `FRM:TIME <mode=CYC; ...>`
`zero-sum(...)` → `FRM:INV <law=ZSUM; ...>`

---

## 7. Ambiguity limits

Human Mode допускает ограниченную двусмысленность только если она:
- не меняет тип конструкции;
- не ломает фокус;
- не ломает critical scope;
- не мешает восстановлению канонической формы.

Допустимая двусмысленность:
- стилистическая;
- риторическая;
- поверхностная.

Недопустимая двусмысленность:
- role ambiguity;
- scope ambiguity;
- focus ambiguity;
- class confusion;
- pattern/invariant/time confusion.

---

## 8. Examples

### Example H-1
**Human**
```text
A gives B resource, no net gain
```

**Core**
```text
[FRM:INV <law=ZSUM; scp=[
  [PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]
]>]
```

### Example H-2
**Human**
```text
system loops again
```

**Core**
```text
[FRM:TIME <mode=CYC; scp=[PRC:CHG <obj=[ENT:SYS]>]>]
```

### Example H-3
**Human**
```text
spr(seed -> form)
```

**Core**
```text
[PAT:SPR <core=[ENT:SEED]; res=[ENT:FORM]>]
```

### Example H-4
**Human**
```text
gen(template -> instance)
```

**Core**
```text
[PAT:GEN <code=[ENT:TEMPLATE]; dst=[ENT:INSTANCE]>]
```

### Example H-5
**Human**
```text
balanced system
```

**Core**
```text
[STA:BAL <ctx=[ENT:SYS]>]
```

---

## 9. Human-only constructs not allowed into Core as-is

Следующие формы нельзя переносить в Core без нормализации:
- purely poetic metaphors;
- free mystical symbols;
- undeclared surface axes;
- vague “energy-like” language without typed referents;
- emotional emphasis that changes semantics.

---

## 10. Criteria of readiness

Human Profile v0.1 можно считать рабочим, если:
- есть стабильный набор shorthand;
- есть projection rules;
- есть ambiguity limits;
- есть примеры Human → Core;
- записи Human Mode реально удобнее Core для человека, не ломая семантику.
````


## FILE: docs/SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md
Path: `docs/SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md`

Size: 4538 bytes

````markdown
# SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1

## Назначение
Этот документ собирает **план реализации проекта** в одном месте и связывает уже созданные спецификации в последовательную программу работ.

## Исходная позиция
Проект уже имеет:
- project pack;
- Core baseline;
- extension layer для pattern / time / invariant logic.

Значит, задача уже не в том, чтобы “придумать язык”, а в том, чтобы **довести архитектуру до проверяемой и реализуемой системы**.

## Главная цель
Построить SEMASCRIPT как систему, которая:
1. имеет устойчивое семантическое ядро;
2. поддерживает human-readable запись;
3. имеет executable subset;
4. может быть проверена на реальных кейсах.

---

## Потоки реализации

### 1. Core stream
Фокус:
- классы узлов;
- роли;
- focus rule;
- scope rule;
- canonical S-Linear;
- nested scenes;
- error classes.

Главный артефакт:
- `SEMASCRIPT_CORE_SPEC_v0.1.md`

### 2. Extension stream
Фокус:
- `SPR`
- `GEN`
- `PAL`
- `TIME:*`
- `ZSUM / NZSUM / BAL`

Главный артефакт:
- `SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`

### 3. Human stream
Фокус:
- compression rules;
- shorthand;
- readable surface forms;
- ambiguity limits;
- Human → Core projection.

Целевой артефакт:
- `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`

### 4. Exec stream
Фокус:
- executable subset;
- explicit typing;
- explicit scope;
- serialization;
- validation;
- execution constraints.

Целевой артефакт:
- `SEMASCRIPT_EXEC_PROFILE_v0.1.md`

### 5. Validation stream
Фокус:
- positive cases;
- negative cases;
- cross-profile cases;
- error verification.

Целевой артефакт:
- `SEMASCRIPT_TESTPACK_v0.1.md`

### 6. Tooling stream
Фокус:
- parser;
- validator;
- converters;
- corpus helpers.

Целевой результат:
- MVP toolchain

### 7. Visual stream
Фокус:
- shape classes;
- root glyph families;
- modifier markers;
- frame markers;
- 2D layout conventions.

Целевой артефакт:
- `SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`

---

## Порядок фаз

### Phase 0 — Baseline freeze
Уже собран:
- project identity
- architecture map
- current status
- roadmap
- scope v0.1

### Phase 1 — Core stabilization
Цель:
зафиксировать Core как source of truth.

### Phase 2 — Extension stabilization
Цель:
сделать pattern / time / invariant logic формальными расширениями, а не образами.

### Phase 3 — Testability
Цель:
собрать test pack и error discipline.

### Phase 4 — Human profile
Цель:
сделать compact human communication layer.

### Phase 5 — Exec profile
Цель:
сделать strict executable subset.

### Phase 6 — Tooling MVP
Цель:
доказать живость системы технически.

### Phase 7 — Glyph architecture
Цель:
построить визуальный слой после стабилизации семантики.

### Phase 8 — Corpus / pilots
Цель:
проверить систему на реальных типах сообщений и сценариев.

---

## Ближайшие deliverables
1. `SEMASCRIPT_TESTPACK_v0.1.md`
2. `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`
3. `SEMASCRIPT_EXEC_PROFILE_v0.1.md`
4. `SEMASCRIPT_PROFILE_MATRIX_v0.1.md`

---

## Что нельзя делать раньше времени
- не раздувать словарь;
- не уходить в финальный глиф-дизайн;
- не объявлять полноценный programming language без executable subset;
- не добавлять новые архетипы без decomposition;
- не смешивать human ambiguity и machine determinism.

---

## Критерии прогресса
- каждая новая конструкция проходит через Core;
- extension layer не вносит туман;
- human forms проецируются в Core;
- executable forms валидируются без догадки;
- система выдерживает corpus-based проверку.
````


## FILE: docs/SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md
Path: `docs/SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md`

Size: 1945 bytes

````markdown
# SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после three-way session merge / conflict detection:
**interactive conflict resolution / manual merge decisions**.

## Что это даёт
Теперь merge-layer умеет не только:
- обнаруживать конфликт,
- останавливать auto-merge,

но и:
- показать каждый conflict path,
- дать выбор `base / left / right / custom`,
- применить manual decisions,
- пересобрать итоговую merged session после полного разрешения конфликтов.

## Что добавлено
- `tooling/session_conflict_resolution.py`
- `/api/resolve-project-merge-conflicts`
- interactive conflict list in inspector
- bulk choices: `Use left for all`, `Use right for all`
- `run_conflict_resolution_checks.py`
- sample conflicted/resolved merge results

## Decision model
Каждое решение задаётся по `path`:
```json
{
  "source_text": { "choice": "left" }
}
```

или:
```json
{
  "source_text": { "choice": "custom", "value": "gen(template -> merged_instance)" }
}
```

## Как работает
1. сначала строится обычный three-way merge result;
2. если есть conflicts, inspector показывает их списком;
3. пользователь выбирает решения;
4. resolver применяет решения к `merged_source`;
5. если unresolved conflicts не осталось — пересобирается `merged_session`.

## Важное инженерное правило
Для text-based sessions `graph_document` больше не считается conflict-bearing source field.
Он derived от `source_text`, поэтому не создаёт лишний merge noise.
````


## FILE: docs/SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1.md
Path: `docs/SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1.md`

Size: 877 bytes

````markdown
# SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package commit / promote imported resolution into local named outcome set or release point:
**local outcome set diff / compare between imported promoted resolutions**.

## Что это даёт
Теперь система умеет сравнивать уже **локально committed promoted outcomes** после package import-resolution chain.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-local-imported-promoted-outcomes`
- compare panel in inspector
- `run_local_outcome_set_compare_checks.py`
- sample compare project / compare result JSON
````


## FILE: docs/SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1.md
Path: `docs/SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1.md`

Size: 1565 bytes

````markdown
# SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1

## Назначение
Этот документ описывает следующий слой после local outcome set diff / compare between imported promoted resolutions:
**local outcome set export / import as portable local promoted resolution package**.

## Что это даёт
Теперь система умеет:
- экспортировать локально committed imported promoted outcome set в переносимый portable package;
- импортировать этот package в другой workspace;
- materialize imported sessions в current lineage;
- создать imported local outcome set commit и registry entry.

## Что добавлено
- `tooling/project_local_outcome_set_package.py`
- package-aware `project_model.py`
- `/api/export-local-outcome-set-package`
- `/api/import-local-outcome-set-package`
- local outcome portable package panel in inspector
- `run_local_outcome_set_package_checks.py`
- sample local outcome set portable package JSON

## Export semantics v0.1
Экспортирует:
- local outcome set commit metadata
- resolved sessions
- promoted point
- portable package metadata

## Import semantics v0.1
Импорт:
- materialize-ит sessions как `local_outcome_set_package_import`
- создаёт imported local outcome commit entry в local outcome registry
- переносит promoted point, если он есть
- пишет history event `local_outcome_set_package_imported`
````


## FILE: docs/SEMASCRIPT_MANIFEST_v0.1.md
Path: `docs/SEMASCRIPT_MANIFEST_v0.1.md`

Size: 5861 bytes

````markdown
# SEMASCRIPT_MANIFEST_v0.1

## Назначение
Этот файл является сводной картой всех документов, собранных в current pack.

## Полный состав pack
- `00_PROJECT_IDENTITY.md`
- `01_ARCHITECTURE_MAP.md`
- `02_CURRENT_STATUS.md`
- `03_ROADMAP.md`
- `04_SCOPE_V0_1.md`
- `SEMASCRIPT_0_SEMANTIC_BASELINE.md`
- `SEMASCRIPT_CORE_SPEC_v0.1.md`
- `SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`
- `SEMASCRIPT_PROFILE_MATRIX_v0.1.md`
- `SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md`
- `SEMASCRIPT_TESTPACK_v0.1.md`
- `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`
- `SEMASCRIPT_EXEC_PROFILE_v0.1.md`
- `SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`
- `SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md`
- `SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md`
- `README.md`

## Логика чтения

### Быстрый вход в проект
1. `README.md`
2. `00_PROJECT_IDENTITY.md`
3. `01_ARCHITECTURE_MAP.md`
4. `02_CURRENT_STATUS.md`
5. `03_ROADMAP.md`

### Понимание semantic baseline
1. `04_SCOPE_V0_1.md`
2. `SEMASCRIPT_0_SEMANTIC_BASELINE.md`
3. `SEMASCRIPT_CORE_SPEC_v0.1.md`
4. `SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`

### Понимание режимов языка
1. `SEMASCRIPT_PROFILE_MATRIX_v0.1.md`
2. `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`
3. `SEMASCRIPT_EXEC_PROFILE_v0.1.md`

### Проверка и реализация
1. `SEMASCRIPT_TESTPACK_v0.1.md`
2. `SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md`
3. `SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md`
4. `SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md`

### Визуальный слой
1. `SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`

## Что теперь реально закрыто
- project pack
- scope v0.1
- semantic baseline
- Core
- extension layer
- profile split
- implementation plan
- test baseline
- human profile
- exec profile
- glyph architecture baseline
- starter corpus
- tooling MVP plan

## Что остаётся на следующий этап
- parser/validator implementation
- larger reference corpus
- glyph family drafts / SVG prototypes
- executable experiments
- version v0.2 refinement


## Обновление expanded baseline
Добавлено:
- расширенный fixture coverage;
- corpus, помеченный статусами `core-pass` / `exec-pass` / `core-only`;
- синхронизация testpack с tooling MVP.

- `SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1.md`

- `SEMASCRIPT_GRAMMAR_EXPANSION_v0.1.md`
- `SEMASCRIPT_AST_INTEGRATION_PACK_v0.1.md`
- `SEMASCRIPT_CORPUS_PIPELINE_v0.1.md`
- `SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1.md`
- `SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1.md`
- `SEMASCRIPT_STATE_MODEL_v0.1.md`
- `SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1.md`
- `SEMASCRIPT_SVG_RENDERER_SPEC_v0.1.md`
- `SEMASCRIPT_V0_2_HARDENING_SPEC.md`
- `SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md`
- `SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1.md`
- `SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1.md`
- `SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1.md`
- `SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1.md`
- `SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1.md`
- `SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1.md`
- `SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1.md`
- `SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1.md`
- `SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md`
- `SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1.md`
- `SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1.md`
- `SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1.md`
- `SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1.md`

- `SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1.md`
- `SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1.md`

- `SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1.md`
- `SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1.md`

- `SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1.md`

- `SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1.md`

- `SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1.md`

- `SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1.md`

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md`

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md`

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1.md`

- `SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1.md`

- `SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1.md`

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md`
````


## FILE: docs/SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1.md
Path: `docs/SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1.md`

Size: 1502 bytes

````markdown
# SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1

## Назначение
Этот документ описывает следующий слой после interactive conflict resolution / manual merge decisions:
**merge commit / resolved session insertion back into project workspace**.

## Что это даёт
Теперь merge-layer замыкается обратно в project workspace:
- finalized merged session можно commit-ить как новую session entry,
- commit получает provenance metadata,
- в history добавляется `merge_committed`,
- committed session сразу попадает в navigation / timeline / compare / merge.

## Что добавлено
- расширенный `project_model.py`
- `commit_merged_session_to_workspace(...)`
- `/api/commit-project-merge-result`
- merge commit panel in inspector
- `run_merge_commit_checks.py`
- sample merge commit project / result JSON

## Что пишет commit
### Session entry metadata
```json
{
  "commit_kind": "merge_commit",
  "merge_commit": {
    "base_session_id": "...",
    "left_session_id": "...",
    "right_session_id": "...",
    "conflict_count": 1,
    "resolved_count": 1,
    "unresolved_count": 0,
    "finalized": true
  }
}
```

### History event
- `merge_committed`

## Поведение
- можно commit-ить либо auto-merged result,
- либо manually resolved merge result,
- committed session может сразу стать active session.
````


## FILE: docs/SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1.md
Path: `docs/SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1.md`

Size: 1258 bytes

````markdown
# SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1

## Назначение
Этот документ описывает **multi-session project workspace / project index** как следующий слой после persisted session format.

## Что он даёт
Теперь можно работать не с одной сохранённой сессией, а с набором связанных сессий внутри проекта.

## Что добавлено
- `tooling/project_model.py`
- export/import project index API
- workspace session list в inspector
- active session switching
- multi-session sample project
- project round-trip smoke checks

## Project index structure
```json
{
  "project_index_version": "SEMASCRIPT_PROJECT_INDEX_v0.1",
  "project_name": "...",
  "active_session_id": "...",
  "sessions": [
    {
      "session_id": "...",
      "session_name": "...",
      "profile": "...",
      "source_mode": "...",
      "file_name": "...",
      "tags": [...],
      "session": { ... full session ... }
    }
  ]
}
```

## Что умеет inspector
- add current session into project workspace
- export project index
- import project index
- switch active session
- restore active session into full inspector view
````


## FILE: docs/SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1.md
Path: `docs/SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1.md`

Size: 2310 bytes

````markdown
# SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot diff / restore preview before apply:
**partial snapshot restore / selective workspace state import**.

## Что это даёт
Теперь система умеет не только полностью restore-ить frozen workspace из snapshot package,
но и **выборочно импортировать части snapshot state** в уже существующий текущий workspace.

## Что добавлено
- `tooling/project_snapshot_partial_import.py`
- partial-import aware `project_model.py`
- `/api/partial-import-project-from-snapshot`
- partial import panel in inspector
- `run_partial_snapshot_import_checks.py`
- sample partial import project / result JSON

## Import semantics v0.1
Это **non-destructive selective import**.

### Что можно импортировать
- `selected_session_ids`
- `selected_tag_point_names`
- `selected_snapshot_export_names`

### Как работает
- выбранные snapshot sessions вставляются в current workspace как **новые session entries**
- для них создаётся provenance `snapshot_partial_import`
- imported sessions строятся цепочкой в `target_branch_name`
- tag/release points импортируются, если их target session доступен после remap/import
- snapshot exports могут быть перенесены как frozen artifacts

## Provenance
Каждый imported session получает:
- `commit_kind = snapshot_partial_import`
- `snapshot_partial_import.import_name`
- `snapshot_partial_import.source_snapshot_name`
- `snapshot_partial_import.original_session_id`
- `snapshot_partial_import.source_branch_name`
- `snapshot_partial_import.target_branch_name`

## History
Добавлен history event:
- `snapshot_partial_imported`

## Ограничение v0.1
Это selective import, а не semantic merge:
- текущие sessions не перезаписываются
- imported sessions получают новые ids
- registry names при конфликте переименовываются с суффиксами
````


## FILE: docs/SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1.md
Path: `docs/SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1.md`

Size: 1507 bytes

````markdown
# SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1

## Назначение
Этот документ описывает первый слой **pattern decomposition** для SEMASCRIPT.

Его задача:
- переводить pattern macros в Core-compatible forms;
- сделать `SPR / GEN / PAL` пригодными для дальнейшей обработки;
- подготовить переход к executable semantics.

## Что делает decomposition layer

### `PAT:SPR`
Перевод:
```text
[PAT:SPR <core=[ENT:SEED]; res=[ENT:FORM]>]
->
[PRC:EXP <src=[ENT:SEED]; res=[ENT:FORM]>]
```

### `PAT:GEN`
Перевод:
```text
[PAT:GEN <code=[ENT:TEMPLATE]; dst=[ENT:INSTANCE]>]
->
[REL:DEP <dst=[ENT:INSTANCE]; src=[ENT:TEMPLATE]>]
```

### `PAT:PAL`
Перевод:
```text
[PAT:PAL <axis=[IDX:CENTER]; scope=[...]>]
->
[FRM:SCN <axis=[IDX:CENTER]; scp=[...]>]
```

## Архитектурный смысл
Это ещё не полный runtime.
Это **structural decomposition layer**, который:
- убирает pattern macros из operational path;
- сохраняет их смысл в Core-compatible form;
- позволяет validator / corpus pipeline работать дальше уже без PAT nodes в критических местах.

## Граница v0.1
Это decomposition, а не полный semantic proof.
Он не обещает исчерпывающую эквивалентность для всех будущих pattern forms.
````


## FILE: docs/SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md
Path: `docs/SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`

Size: 4080 bytes

````markdown
# SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1

## Статус
Draft extension layer specification

## Назначение
Этот документ стандартизирует расширяющие логические слои SEMASCRIPT поверх Core v0.1.

## Главный принцип
Ни один паттерн, временной режим или инвариант не считается частью системы, если он:
- не имеет определения;
- не имеет scope;
- не имеет канонической формы;
- не имеет decomposition;
- не разведен с соседними логическими классами.

---

# SECTION 1 — PATTERN LOGIC

## Общие правила
- Паттерн не заменяет Core
- Паттерн обязан иметь scope
- Паттерн не исполним сам по себе
- Pattern shorthand не равен мистике

## `SPR`
Смысл:
- развёртывание из ядра;
- рост по организованной траектории;
- повтор структурного принципа на новом масштабе.

Каноническая форма:
```text
[PAT:SPR <core=[...]; res=[...]>]
```

Не равно:
- просто `INC`;
- просто циклу;
- просто повторению.

## `GEN`
Смысл:
- кодируемая структура;
- передача шаблона;
- наследование;
- воспроизводимость.

Каноническая форма:
```text
[PAT:GEN <code=[...]; dst=[...]>]
```

Не равно:
- просто копии;
- просто повтору;
- просто памяти.

## `PAL`
Смысл:
- зеркальная организация;
- структурная симметрия;
- обратимость чтения на уровне формы;
- сохранение центральной оси.

Каноническая форма:
```text
[PAT:PAL <axis=[IDX:CENTER]; scope=[...]>]
```

Не равно:
- просто `EQU`;
- любой симметрии;
- любому циклу;
- любой обратимости.

---

# SECTION 2 — TEMPORAL LOGIC

## Общие правила
Временной режим задаётся через:
```text
[FRM:TIME <mode=...; scp=[...]>]
```

## Режимы
- `LIN` — линейное время
- `CYC` — циклическое время
- `BRN` — ветвящееся время
- `REC` — рекурсивное / вложенное время
- `REV` — обратимое время
- `ATM` — атемпоральность

Каждый режим должен иметь:
- definition
- scope
- различие с соседними режимами
- эталонные примеры

---

# SECTION 3 — INVARIANT LOGIC

## Общие правила
Инвариант задаётся через:
```text
[FRM:INV <law=...; scp=[...]>]
```

## `ZSUM`
Смысл:
- локальные выигрыши и потери допустимы;
- итоговая сумма внутри scope не меняется.

Не равно:
- `NEG`
- `REV`
- `PAL`
- `BAL`
- числу 0

## `NZSUM`
Смысл:
- операция меняет общий релевантный объём внутри scope;
- возникает чистый прирост или чистая потеря.

## `BAL`
Смысл:
- состояние уравновешенности или взаимной компенсации.

Не равно:
- `ZSUM`
- отсутствию конфликта
- неподвижности

---

## Error classes
- `E201` — undefined pattern scope
- `E202` — unmapped pattern macro
- `E203` — ambiguous time scope
- `E204` — conflicting time modes
- `E205` — undeclared invariant scope
- `E206` — invariant/pattern confusion
- `E207` — invariant/time confusion
- `E208` — forbidden semantic collapse
- `E209` — non-decomposable extension form
- `E210` — human-only metaphor in executable context
````


## FILE: docs/SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1.md
Path: `docs/SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1.md`

Size: 1822 bytes

````markdown
# SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1

## Назначение
Этот документ описывает **persisted project/session format** как следующий шаг после editable visual graph mode.

## Почему он идёт после graph mode
Сначала нужен рабочий graph editor.
Только после этого появляется полноценная сущность, которую стоит сохранять:
- source text
- normalized text / S-Linear
- graph
- AST
- runtime/state reports
- render outputs
- UI state

## Что добавлено
- `tooling/session_model.py`
- session export/import API в inspector
- session JSON textarea
- download current session
- sample session documents
- session smoke checks

## Session structure
```json
{
  "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
  "session_name": "...",
  "project": { ... },
  "documents": { ... },
  "reports": { ... },
  "render": { ... },
  "ui_state": { ... },
  "metadata": { ... }
}
```

### `project`
- profile
- source_mode
- source_text
- normalized_text
- slinear
- decomposed_slinear
- initial_state

### `documents`
- ast_document
- decomposed_ast_document
- graph_document
- decomposed_graph_document

### `reports`
- validation
- runtime_report
- state_report

### `render`
- svg_raw
- svg_decomposed

### `ui_state`
- selected_entity_id
- preview_mode
- decompose
- viewport
- panel visibility

## Что умеет inspector
- export text session
- export graph session
- import saved session
- restore graph/workspace/report/render state
- download session JSON

## Граница v0.1
Это persisted session format, но ещё не:
- multi-file project workspace
- versioned migration system
- collaborative project storage
- branch/merge semantics
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1.md`

Size: 1040 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package conflict resolution / manual import decisions:
**portable local outcome package commit / promote imported resolution into local named outcome set or release point**.

## Что это даёт
Теперь resolved import decisions по portable local outcome package можно:
- зафиксировать как локальный named outcome set;
- промотить в `release` или `tag` point;
- использовать как source-of-truth для дальнейшего local outcome export/compare.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit.py`
- commit-aware `project_model.py`
- `/api/commit-local-outcome-set-package-resolution`
- commit/promote panel in inspector
- `run_local_outcome_set_package_commit_checks.py`
- sample commit project / result JSON
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md`

Size: 1027 bytes

````markdown

# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package diff / compatibility check before import:
**portable local outcome package conflict resolution / manual import decisions**.

## Что это даёт
Теперь portable local outcome package import можно не только preview-ить, но и применять через manual decisions per packaged session.

## Decision model
Поддерживаются решения:
- `use_package`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое решение materialize-ится как новый:
- `commit_kind = local_outcome_set_package_import_resolution`

Результат сохраняется в registry:
- `local_outcome_set_package_resolutions`

## История
Добавлен history event:
- `local_outcome_set_package_import_resolved`
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1.md`

Size: 1137 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package commit / promote imported resolution into local named outcome set or release point:
**portable local outcome package diff / compare between committed imported outcomes**.

## Что это даёт
Теперь система умеет сравнивать уже committed imported portable local outcomes внутри текущего workspace.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-committed-portable-local-outcome-packages`
- compare panel in inspector
- `run_local_outcome_set_package_commit_compare_checks.py`
- sample compare project / compare result JSON

## Что сравнивается
- commit identity
- resolution name
- package name
- source commit name
- target branch name
- promoted point name / kind
- note
- resolved session ids
- resolution pairs
- materialized source texts
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md`

Size: 1266 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после local outcome set export / import as portable local promoted resolution package:
**portable local outcome package diff / compatibility check before import**.

## Что это даёт
Теперь portable local outcome package можно preview-ить до import:
- проверить совместимость версии;
- увидеть target branch;
- увидеть конфликты import name / promoted point;
- получить per-session compatibility preview;
- оценить conflict-like риск до import apply.

## Что добавлено
- `tooling/project_local_outcome_set_package_preview.py`
- preview-aware `project_model.py`
- `/api/preview-local-outcome-set-package-import`
- preview button/output in inspector
- `run_local_outcome_set_package_preview_checks.py`
- sample preview result/package JSON

## Preview semantics
Это **non-mutating preview**:
- history не пишется
- registry import не создаётся
- workspace не меняется
- возвращается только compatibility + diff preview
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1.md`

Size: 1293 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package diff / compare between committed imported outcomes:
**portable local outcome package export / import compare baseline or three-way merge between committed imported outcomes**.

## Что это даёт
Теперь система умеет:
- взять `base`, `left`, `right` committed portable local outcomes;
- построить baseline-aware three-way merge preview;
- показать auto-merged fragments;
- показать conflict items;
- дать основу для следующего шага — manual merge decisions / merge commit.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_merge.py`
- three-way-merge-aware `project_model.py`
- `/api/compare-or-three-way-merge-committed-portable-local-outcomes`
- three-way merge panel in inspector
- `run_portable_local_outcome_package_merge_checks.py`
- sample merge project / merge result JSON

## Семантика v0.1
Это **non-mutating baseline / three-way merge preview**.
Workspace не меняется.
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md`

Size: 1277 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package export / import compare baseline or three-way merge between committed imported outcomes:
**portable local outcome package three-way conflict resolution / manual merge decisions**.

## Что это даёт
Теперь baseline-aware three-way merge preview можно превратить в materialized merge-resolution chain:
- для каждого `original_session_id` принять merge decision;
- разрешить conflicts вручную;
- materialize-ить resolved sessions в lineage;
- сохранить resolution registry и provenance.

## Supported decisions
- `use_auto`
- `use_base`
- `use_left`
- `use_right`
- `skip`
- `custom_text`

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_merge_resolution.py`
- merge-resolution-aware `project_model.py`
- `/api/resolve-portable-local-outcome-package-three-way-merge-conflicts`
- merge decision panel in inspector
- `run_portable_local_outcome_package_merge_resolution_checks.py`
- sample merge resolution project / result JSON
````


## FILE: docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1.md
Path: `docs/SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1.md`

Size: 1704 bytes

````markdown
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1

## Purpose
This document describes the layer that follows:
- portable local outcome package baseline / three-way merge preview
- portable local outcome package three-way conflict resolution / manual merge decisions

The new layer is:
**portable local outcome package three-way merge commit / promote resolved outcome**

## What it adds
- turns a resolved portable local three-way merge into a committed reusable outcome
- records the committed merge in project lineage/history
- allows optional promote into a `release` or `tag` point
- re-exposes the committed result through `local_outcome_set_package_commits` so it can participate in later compare/merge cycles

## Added tooling
- `tooling/project_local_outcome_set_package_commit_merge_commit.py`
- project wrapper in `tooling/project_model.py`
- inspector service entry for merge commit/promote
- server route: `/api/commit-portable-local-outcome-package-three-way-merge-resolution`
- inspector controls for commit name / promote point / note
- `tooling/run_portable_local_outcome_package_merge_commit_checks.py`

## Result shape
The committed result stores:
- `commit_name`
- `resolution_name`
- `base_commit_name`
- `left_commit_name`
- `right_commit_name`
- `target_branch_name`
- `resolved_session_ids`
- `skipped_session_ids`
- `merge_pairs`
- `resolution_pairs`
- optional `promoted_point_name`
- optional `promoted_point_kind`

## Outcome
Portable local outcome package three-way merge is now a complete workflow:
1. compare baseline / three-way merge committed outcomes
2. resolve conflicts with manual decisions
3. commit/promote resolved merge into lineage
````


## FILE: docs/SEMASCRIPT_PROFILE_MATRIX_v0.1.md
Path: `docs/SEMASCRIPT_PROFILE_MATRIX_v0.1.md`

Size: 4606 bytes

````markdown
# SEMASCRIPT_PROFILE_MATRIX_v0.1

## Назначение
Этот документ фиксирует матрицу различий и связей между:
- `CORE`
- `HUMAN MODE`
- `EXEC MODE`

Его задача — удержать проект от смешения человеческой выразительности и исполнимой строгости.

## Главный принцип
Core — source of truth.  
Human Mode и Exec Mode — две разные проекции поверх одного semantic baseline.

---

## SYSTEM MODEL

### CORE
Каноническая семантическая форма.
Должна быть:
- обратимой;
- типизированной;
- проверяемой;
- независимой от surface-представления.

### HUMAN MODE
Человеко-ориентированная запись.
Допускает:
- компрессию;
- shorthand;
- выразительность;
- частичное опущение восстановимых деталей.

### EXEC MODE
Машинно-ориентированная запись.
Требует:
- явных типов;
- явного scope;
- строгих ролей;
- validation discipline;
- determinism.

---

## PROFILE MATRIX

| FEATURE | CORE | HUMAN MODE | EXEC MODE |
|---|---|---|---|
| Typed node | Required | Optional if recoverable | Required |
| Single focus | Required | Required | Required |
| Explicit roles | Required | Optional if topology is unambiguous | Required |
| Canonical linear projection | Required | Optional at surface | Required |
| Spatial composition | Allowed | Preferred | Allowed only if serializable |
| Metaphor | Forbidden | Allowed if mapped to Core | Forbidden |
| Emotional emphasis | Forbidden | Allowed | Forbidden unless typed |
| Omitted recoverable context | Forbidden | Allowed | Forbidden |
| Ambiguity tolerance | Forbidden | Limited | Forbidden |
| Temporal frame | Explicit if relevant | May be compressed | Required if relevant |
| Invariant layer | Explicit if relevant | Optional shorthand | Required if operationally relevant |
| Pattern layer | Allowed if decomposable | Allowed | Allowed only after decomposition |
| Scope declaration | Required | Optional if recoverable | Required |
| Type strictness | Medium-high | Low-medium | High |
| Validation | Structural | Readability-oriented | Structural + execution validity |
| Reversibility | Required | Desired | Required |
| Determinism | Desired | Not always required | Required |
| Partial fragment | Allowed only as marked fragment | Allowed | Forbidden |
| Undefined referent | Forbidden unless marked | Allowed via context | Forbidden |
| Executability | Not required | Not required | Required |
| Human readability | Desired | Required | Secondary |
| Serialization | Required | Optional | Required |

---

## NORMATIVE RULES

### Rule M1 — Core is authoritative
Если Human и Exec проекции расходятся, Core является авторитетным слоем.

### Rule M2 — Human may compress, but may not invent
Human Mode может сжимать или опускать только то, что можно восстановить по grammar + context.

### Rule M3 — Exec may restrict, but may not reinterpret
Exec Mode может требовать больше явности, чем Human surface, но не может менять Core meaning.

### Rule M4 — Pattern is not executable by name alone
`SPR`, `GEN`, `PAL` и другие pattern-макросы исполнимы только после operational decomposition.

### Rule M5 — Scope ambiguity kills execution
То, что человек ещё может “понять”, для Exec Mode уже может быть невалидным.

---

## SAME SEMANTICS IN 3 PROFILES

### Example A — Human
```text
ресурс ушёл от A к B, ничего не прибавилось
```

### Example A — Core
```text
[FRM:INV <law=ZSUM; scp=[
  [PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]
]>]
```

### Example A — Exec
```text
[EXEC:TRANSFER <
  src=[ENT:A];
  dst=[ENT:B];
  obj=[ENT:RES];
  invariant=[LAW:ZSUM]
>]
```

---

## Минимальный вывод
SEMASCRIPT может быть:
- языком общения;
- языком структурного мышления;
- основой для programming/execution layer;

но не как один плоский режим.  
Системно правильная форма — **shared Core + Human profile + Exec profile**.
````


## FILE: docs/SEMASCRIPT_PROJECT_STATUS_PACK_v0.2.md
Path: `docs/SEMASCRIPT_PROJECT_STATUS_PACK_v0.2.md`

Size: 15864 bytes

````markdown
# SEMASCRIPT Project Status Pack v0.2

## Current working baseline
- Active extracted bundle: `SEMASCRIPT_current_bundle`
- Source archive baseline: `SEMASCRIPT_All_In_One_v0_2_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS.zip`
- Bundle chain is cumulative: later archives add scope and entries rather than replacing the project model.

## Verified state on 2026-05-02
- `python tooling/run_environment_bootstrap_checks.py`
  - passed `env_bootstrap_self_check: passed=7 warnings=0 failed=0`
- `python tooling/run_v0_2_hardening_suite.py`
  - passed integrated non-browser suite
  - includes `editor_visual_inspector: passed=64 failed=0 total=64`
  - final marker: `v0_2_hardening_suite: passed=1 failed=0 total=1`
- `Set-Location .\tooling; python -c "import inspector_server; print('IMPORT_OK')"`
  - inspector server imports cleanly
- `python tooling/run_inspector_browser_ui_checks.py`
  - not run in this checkpoint; browser UI verification remains opt-in
  - runner was updated to assert the new package-guidance next-action cards
  - runner was updated to assert the new portable merge workstation guidance in the package and snapshot-to-portable browser flows

## Verified state on 2026-04-25
- `python run_inspector_smoke_checks.py`
  - passed `62/62`
- `python run_inspector_http_smoke_checks.py`
  - passed `15/15`
- `python run_inspector_http_e2e_checks.py`
  - passed `7/7`
- `python run_inspector_http_project_ops_e2e_checks.py`
  - passed `9/9`
- `python run_inspector_http_lifecycle_import_e2e_checks.py`
  - passed `7/7`
- `python run_inspector_http_graph_session_e2e_checks.py`
  - passed `7/7`
- `python run_portable_local_outcome_package_merge_resolution_checks.py`
  - passed `3/3`
- `python run_portable_local_outcome_package_merge_commit_checks.py`
  - passed `4/4`
- `python run_v0_2_hardening_suite.py`
  - passed end-to-end regression suite
- `python -c "import inspector_server"`
  - inspector server imports cleanly
- `python run_inspector_browser_ui_checks.py`
  - passed `8/8` browser UI scenarios
  - page load + default `human` profile + live profile guidance
  - human analyze + add current session to project
  - branch + release point + snapshot export flow
  - `core` profile mismatch preflight guidance without browser errors
  - snapshot/package guidance + cross-panel package-type mismatch hints
  - smart autofill for restore/import/reconcile names with manual override preserved
  - local outcome package preview -> resolve -> commit/promote with committed outcome bridged into portable merge selectors
  - standalone package import -> local outcome package export/import/commit -> portable merge compare/resolve/commit with downstream autofill checks
  - snapshot reconcile -> promoted standalone package export -> target-project package import -> local outcome package -> portable merge with snapshot/package/merge autofill checks
  - live standalone/local package summary cards after export, so package handoff no longer depends on reading raw JSON only

## What was completed in this iteration
- Refactored inspector from a single overloaded `app.js` into workflow modules:
  - project workspace / lifecycle / operations
  - graph session workspace
  - snapshot reconcile
  - reconcile commit package
  - local outcome set package
  - portable merge workstation
  - bootstrap / core / panel / action layer
- Added `Interactive Merge Workstation v2` for portable local outcome reconciliation.
- Added inspector frontend smoke coverage for workflow wiring and module registration.
- Fixed a live inspector server regression where modular frontend assets returned `404`.
- Added runtime HTTP smoke coverage for inspector static asset serving, `/api/samples`, and key `POST` routes including portable merge compare / resolve / commit.
- Closed inspector frontend/server API drift by wiring the missing lifecycle / reconcile-package / project-operations HTTP handlers in `inspector_server.py`.
- Added static route-parity regression so frontend `postJson("/api/...")` references must match live server handlers.
- Added localhost HTTP e2e scenario runner for:
  - snapshot reconcile resolution + commit
  - standalone outcome package preview / resolve / commit
  - local outcome package export / import-resolution / commit
  - portable local three-way merge compare / resolve / commit
- Fixed branch-aware project export/merge contract drift:
  - `export-project-index` now preserves `entry_metadata` and branch lineage hints from session entries
  - `commit-project-merge-result` now honors explicit `branch_name` from inspector frontend
- Added localhost HTTP project-operations e2e runner for:
  - branch-aware project export
  - create branch
  - compare / merge / resolve / commit
  - rebase / cherry-pick / squash / reset
- Added localhost HTTP lifecycle/direct-import e2e runner for:
  - switch active project session
  - partial snapshot import
  - direct snapshot reconcile apply
  - compare promoted reconcile commits
  - direct standalone package import
  - direct local outcome package import
  - compare committed portable local outcome packages
- Added localhost HTTP graph/session editor e2e runner for:
  - analyze text
  - text to graph
  - analyze graph
  - export text session
  - export graph session
  - import session
  - build project from exported sessions
- Added route-coverage parity regression:
  - every frontend `postJson("/api/...")` route must now appear in at least one inspector HTTP smoke/e2e check file
- Restored missing inspector sidebar lifecycle/operations panels in `inspector/index.html`:
  - branch creation + branch list
  - tag/release point management
  - snapshot export / restore / partial import / reconcile
  - rebase / reset / cherry-pick / squash controls
  - missing local outcome package preview action
- Added DOM parity regression:
  - every `document.getElementById("...")` referenced by `inspector/app.js` must now exist in `inspector/index.html`
- Added opt-in browser UI scenario runner:
  - `tooling/run_inspector_browser_ui_checks.py`
  - self-hosted temporary inspector server
  - Playwright-driven page load / analyze / project / branch / tag / snapshot verification
  - Playwright-driven profile mismatch preflight verification
  - screenshot artifacts under `tooling/browser_ui_artifacts/`
- Hardened inspector onboarding UX:
  - default profile switched to `human`
  - live profile-specific input guidance rendered in the sidebar
  - obvious `core`/`exec` vs human-shorthand mismatches are blocked client-side before hitting `400`
  - status messaging now points users toward the right profile instead of looking like a broken backend
- Hardened inspector package/import UX:
  - snapshot restore textarea now renders live snapshot package summaries with available session ids / tag points / snapshot names
  - partial import and snapshot reconcile now surface snapshot-scoped selection hints instead of raw empty CSV failure
  - standalone/local package textareas now detect wrong SEMASCRIPT package types before import attempts
  - restore/import/reconcile name fields now autofill from loaded snapshot/package metadata without overwriting manual edits
  - browser verification now covers live package guidance, snapshot-vs-standalone mismatch rendering, and metadata-driven autofill
- Closed a real inspector product gap in local outcome workflow:
  - local outcome package resolution can now be committed/promoted directly from the live UI
  - the committed portable-local outcome is rendered back into the inspector list and immediately becomes selectable in portable merge controls
- Closed a real inspector bridge gap between standalone and local outcome flows:
  - after `commit imported package resolution`, the local outcome export selector now falls back to `currentProject.snapshot_reconcile_commit_package_commits`
  - this keeps the live UI usable even when a route returns project state with commit objects but without a separate summary projection
  - browser verification now covers the full `standalone package -> local outcome package -> portable merge` click-path
- Added a full cross-project browser pipeline starting at snapshot reconcile:
  - source project import -> snapshot reconcile preview/apply/commit
  - standalone package export from the committed reconcile outcome
  - target project import -> standalone package preview/import/commit
  - local outcome package export/import/commit
  - portable local three-way merge compare/resolve/commit
- Added smoke protection for that browser runner path:
  - `run_inspector_smoke_checks.py` now statically asserts the new snapshot-to-portable browser scenario remains wired into the opt-in runner
- Hardened downstream inspector naming UX:
  - snapshot reconcile now autofills commit/promote names from the live reconcile result
  - standalone outcome export now autofills package name from the selected promoted reconcile commit
  - standalone package resolution now autofills commit/promote names before promote into local outcomes
  - local outcome export now autofills package name from the selected local outcome commit
  - portable merge resolution now autofills merge commit/promote names from the resolved merge result
  - export-selector change bindings now update package-name autofill live when the chosen source commit changes
- Browser verification now asserts this downstream autofill layer in the live UI:
  - snapshot reconcile commit/promote autofill before custom override
  - standalone package export-name autofill before custom override
  - standalone package resolution commit/promote autofill before custom override
  - local outcome export-name autofill before custom override
  - portable merge commit/promote autofill on the final merge commit path
- Reduced raw-JSON friction in package flows:
  - standalone package export now renders a structured current-package summary card in the live UI
  - local outcome package export now renders a structured current-package summary card in the live UI
  - these cards expose package name, commit/source lineage and resolved-session summary before any `Use current ... package` handoff
- Hardened `Interactive Merge Workstation v2` decision UX:
  - workstation overview now exposes manual decision and skipped counts alongside conflict/ready/needs-input counts
  - queue cards now mark ready / skipped / needs-input states directly
  - Decision Studio now shows selected session, status, decision, preview source and next safe action before relying on raw JSON panes
  - non-browser smoke guards the workstation guidance contract in the current `editor_visual_inspector: passed=64 failed=0 total=64` baseline
  - opt-in browser runner now asserts the new portable merge guidance in both package-pipeline and snapshot-to-portable flows
- Hardened package handoff guidance:
  - snapshot, standalone outcome package and local outcome package guidance cards now include an explicit `Next action:` line
  - valid package cards point users to preview/import/resolve/reconcile actions instead of forcing raw JSON interpretation
  - mismatch/error/empty cards now explain the safe next action before an import attempt
  - non-browser smoke now guards the package next-action contract as `editor_visual_inspector: passed=64 failed=0 total=64`
  - opt-in browser runner now asserts package next-action guidance in the package-guidance scenario

## Important findings from analysis
- Root archive chronology is internally consistent and strongly suggests a single cumulative development line.
- Several legacy documentation files inside the bundle still describe earlier project phases and lag behind the real codebase.
- The inspector refactor had progressed faster than the HTTP shell: `index.html` referenced modular frontend bundles, while `inspector_server.py` still only served a tiny legacy subset of static files.
- Browser-level verification is still desirable, but current regression coverage now protects the biggest non-browser failure modes: missing modular asset routes, missing inspector HTTP handlers, broken route/payload wiring on live localhost HTTP, and broken multi-step inspector outcome pipelines.
- The HTTP regression layer now covers both major inspector surfaces:
- The HTTP regression layer now covers four major inspector surfaces:
  - graph/session editor flows
  - lifecycle/direct-import flows
  - outcome/package pipelines
  - core branch/project operations
- Static inspector smoke now also guards that frontend API surface is not just implemented on the server, but actually exercised by the HTTP regression layer.
- A real product-level DOM drift was found and fixed: workflow controllers in `app.js` referenced more inspector controls than `index.html` actually rendered, so several lifecycle/snapshot flows were implemented but not reachable from the live UI.
- Static inspector smoke now also guards this DOM contract so future refactors cannot silently hide working workflows behind missing markup.
- Browser-level verification is no longer purely manual: there is now a repeatable UI runner for the core restored inspector flows, even though it stays outside the default hardening suite because it depends on live browser execution.
- The first browser-led UX pitfall is now explicitly closed: the inspector no longer defaults users into a high-friction `core` parse failure for the common shorthand input path.
- The next JSON-heavy UX pitfall is also materially reduced: snapshot/package textareas no longer behave like opaque raw blobs, and the live UI now helps distinguish snapshot vs standalone vs local outcome package payloads before a user fires the wrong operation.
- Repeated metadata entry is also reduced: inspector now pulls reasonable restore/import/reconcile names from loaded snapshot/package JSON while still respecting manual overrides.

## Current product/engineering state
SEMASCRIPT now has:
- multi-session project workspace with branches / tags / snapshots / lineage
- snapshot restore / partial import / snapshot reconcile flows
- standalone outcome package export / import / resolve / commit-promote
- portable local outcome package export / import / compare / three-way merge / commit-promote
- inspector `Interactive Merge Workstation v2`
- modular inspector frontend with dedicated workflow controllers
- inspector server/runtime checks for modular asset delivery
- live HTTP e2e coverage for both outcome pipelines and core project operations
- live HTTP e2e coverage for graph/session editor flows, lifecycle/import flows, outcome pipelines and core project operations

## Recommended next milestone
The next strong step is:
- browser-level verification and UX hardening for inspector workstation flows

This should focus on:
- live click-path verification for reconcile/package/portable-merge flows beyond the current package-guidance scenarios
- catching console/runtime UI issues that static smoke cannot see
- UX polish around decision density, preview readability and action affordances
- reducing the remaining raw-JSON burden with more guided import/preview affordances where possible
- optional higher-level end-to-end inspector regression automation

## Practical next entry points
- Inspector HTTP shell:
  - `tooling/inspector_server.py`
  - `tooling/run_inspector_http_smoke_checks.py`
- Unified regression entry:
- `tooling/run_v0_2_hardening_suite.py`
- Inspector UI shell:
  - `inspector/index.html`
  - `inspector/inspector-bootstrap-workflow.js`
  - `inspector/inspector-action-workflow.js`
- Inspector HTTP regression:
  - `tooling/run_inspector_http_smoke_checks.py`
  - `tooling/run_inspector_http_e2e_checks.py`
  - `tooling/run_inspector_http_project_ops_e2e_checks.py`
  - `tooling/run_inspector_http_lifecycle_import_e2e_checks.py`
  - `tooling/run_inspector_http_graph_session_e2e_checks.py`
````


## FILE: docs/SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md
Path: `docs/SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md`

Size: 1327 bytes

````markdown
# SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1

## Статус
Grammar-expanded starter corpus

## Новые важные кейсы

### Multi-scene invariant scope
Status: `core-pass`
**Human**
```text
inv:zsum(A -> B : resource; B -> C : credit)
```
**Core**
```text
[FRM:INV <law=ZSUM; scp=[[PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RESOURCE]>]; [PRC:TRF <src=[ENT:B]; dst=[ENT:C]; obj=[ENT:CREDIT]>]]>]
```

### Multi-scene temporal scope
Status: `core-pass`
**Human**
```text
time:cyc(system change; reserve change)
```
**Core**
```text
[FRM:TIME <mode=CYC; scp=[[PRC:CHG <obj=[ENT:SYSTEM]>]; [PRC:CHG <obj=[ENT:RESERVE]>]]>]
```

### Causal shorthand
Status: `core-pass`
**Human**
```text
time:lin(resource declines => system becomes unstable)
```
**Core**
```text
[FRM:TIME <mode=LIN; scp=[REL:CAU <cau=[STA:DEC <ctx=[ENT:RESOURCE]>]; res=[STA:STB {NEG} <ctx=[ENT:SYSTEM]>]>]>]
```

### Pattern + equality shorthand
Status: `core-pass`, `core-only`
**Human**
```text
pal(A equals A)
```
**Core**
```text
[PAT:PAL <axis=[IDX:CENTER]; scope=[REL:EQU <left=[ENT:A]; right=[ENT:A]>]>]
```

## Итог
Starter corpus теперь уже покрывает не только базовые одиночные формы, но и:
- multi-scene scope;
- richer Human normalization;
- list-scope grammar;
- causal shorthand.
````


## FILE: docs/SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1.md
Path: `docs/SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1.md`

Size: 1597 bytes

````markdown
# SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после squash / fold multiple sessions into one lineage commit:
**reset / restore branch head to historical session or lineage point**.

## Что это даёт
Теперь workspace умеет:
- выбрать ветку;
- выбрать historical session внутри этой ветки;
- переставить head ветки на эту historical point;
- зафиксировать reset в истории;
- отразить restored head в branch summary и lineage graph.

## Что добавлено
- `tooling/project_reset.py`
- branch-head override support in `project_branching.py`
- `/api/reset-project-branch-head`
- reset/restore panel in inspector
- `run_branch_reset_checks.py`
- sample branch reset project / result / lineage graph JSON

## Семантика v0.1
Это **non-destructive head restore**, а не удаление history.

### Как работает
- никакие session entries не удаляются;
- branch head переставляется на выбранный historical session;
- сохраняется `manual_head_session_id`;
- новые lineage nodes не создаются;
- lineage graph просто показывает другой head той же ветки.

## History event
- `branch_reset`

## Ограничение v0.1
Reset/restore разрешён только на historical session внутри той же ветки.
````


## FILE: docs/SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1.md
Path: `docs/SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1.md`

Size: 1292 bytes

````markdown
# SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot reconcile commit / promote resolved decisions:
**resolution set diff / compare between promoted reconcile outcomes**.

## Что это даёт
Теперь система умеет:
- выбрать два promoted reconcile outcomes;
- сравнить их как resolution sets;
- увидеть различия по metadata, resolved sessions, resolution pairs и materialized source text outcomes.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-snapshot-reconcile-commits`
- compare panel in inspector
- `run_snapshot_reconcile_commit_compare_checks.py`
- sample compare project / result JSON

## Что сравнивается
- `snapshot_name`
- `resolution_name`
- `target_branch_name`
- `promoted_point_name`
- `promoted_point_kind`
- `note`
- `resolved_session_ids`
- `resolution_pairs`
- materialized `source_text` for resolved sessions

## Формат результата
- `identity`
- `metadata`
- `resolved_sessions`
- `resolution_pairs`
- `resolved_session_texts`
- `summary`
````


## FILE: docs/SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1.md
Path: `docs/SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1.md`

Size: 1460 bytes

````markdown
# SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1

## Назначение
Этот документ описывает следующий слой после resolution set diff / compare between promoted reconcile outcomes:
**resolution set export / import as standalone promoted outcome package**.

## Что это даёт
Теперь promoted reconcile outcome можно:
- экспортировать в переносимый standalone package;
- импортировать этот package в другой workspace;
- materialize imported outcome как новый lineage-aware imported commit;
- переносить promoted point вместе с outcome.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package.py`
- package-aware `project_model.py`
- export/import package endpoints in inspector
- `run_snapshot_reconcile_commit_package_checks.py`
- sample standalone package export/import JSON

## Package semantics v0.1
Standalone package содержит:
- exported reconcile commit metadata
- resolved sessions
- optional promoted point
- portable package metadata

Import пакета:
- не подменяет текущий workspace,
- а materialize-ит imported sessions как новые package-import commits,
- создаёт imported reconcile commit entry,
- при наличии promoted point переносит его как новый tag/release point.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1.md`

Size: 1716 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot merge / reconcile imported state with current workspace lineage:
**snapshot conflict detection / reconcile preview before apply**.

## Что это даёт
Теперь система умеет до reconcile apply:
- взять current workspace;
- взять snapshot package;
- выбрать snapshot sessions для reconcile;
- построить non-mutating reconcile preview;
- определить conflict-like расхождения между snapshot state и current head target branch.

## Что добавлено
- `tooling/project_snapshot_reconcile_preview.py`
- reconcile preview-aware `project_model.py`
- `/api/preview-snapshot-reconcile-in-project`
- preview button/panel in reconcile section of inspector
- `run_snapshot_reconcile_preview_checks.py`
- sample reconcile preview result JSON

## Preview semantics v0.1
Это **non-mutating reconcile preview**.

### Что показывает preview
Для каждого selected snapshot session:
- `current_head_session_id`
- `same_source_as_head`
- `same_profile_as_head`
- `exact_match`
- `conflict_like`
- `status`

### Что значит `conflict_like`
`conflict_like=true` означает, что source snapshot session расходится с current head по `source_text`.
Это ещё не semantic merge conflict solver, но уже корректный pre-apply risk signal.

## Важное свойство
Preview не пишет history, не создаёт reconcile registry и не меняет current workspace.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1.md`

Size: 1635 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot conflict detection / reconcile preview before apply:
**snapshot conflict resolution / manual reconcile decisions**.

## Что это даёт
Теперь reconcile-layer умеет не только:
- preview-ить conflict-like ситуации,
- показать risk before apply,

но и:
- принять manual decisions per snapshot session,
- materialize resolved reconcile commits,
- зафиксировать decision provenance,
- встроить resolved chain в current workspace lineage.

## Что добавлено
- `tooling/project_snapshot_reconcile_resolution.py`
- resolution-aware `project_model.py`
- `/api/resolve-snapshot-reconcile-conflicts`
- manual reconcile decision controls in inspector
- `run_snapshot_reconcile_resolution_checks.py`
- sample reconcile resolution project / result JSON

## Decision model v0.1
Поддерживаются решения:
- `use_snapshot`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое решение создаёт либо:
- новый resolved reconcile commit,
- либо skip without commit.

Resolved commits получают provenance:
- `commit_kind = snapshot_reconcile_resolution`
- `snapshot_reconcile_resolution.decision_choice`
- `snapshot_reconcile_resolution.resolved_with_head_session_id`
- `snapshot_reconcile_resolution.conflict_like`

## История
Добавлен history event:
- `snapshot_reconcile_resolved`
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1.md`

Size: 1357 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot import / workspace restore from immutable export:
**snapshot diff / restore preview before apply**.

## Что это даёт
Теперь система умеет:
- взять текущий workspace;
- взять immutable snapshot package;
- построить dry-run preview restore;
- показать diff текущего project state и snapshot frozen state;
- дать оператору понять, что изменится до restore apply.

## Что добавлено
- `tooling/project_snapshot_diff.py`
- snapshot preview-aware `project_model.py`
- `/api/preview-project-snapshot-restore`
- preview button/panel in inspector restore section
- `run_snapshot_restore_preview_checks.py`
- sample preview result JSON

## Preview semantics v0.1
Это **non-mutating restore preview**.

### Что сравнивается
- project name
- active session / active branch
- sessions
- branches
- tag points
- snapshot exports
- snapshot restores

### Что возвращается
- `snapshot_restore_preview_version`
- `restore_target`
- `scalar_diff`
- `collections`
- `summary`

Restore preview не пишет history и не меняет workspace.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1.md`

Size: 1557 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после tag / release points over sessions and lineage states:
**snapshot / immutable workspace state export by tag or release point**.

## Что это даёт
Теперь project workspace умеет:
- взять существующий tag/release point как anchor;
- собрать immutable snapshot export package;
- заморозить состояние workspace на момент экспорта;
- сохранить snapshot registry в `project_index`;
- восстанавливать snapshot summary и скачивать snapshot package из inspector.

## Что добавлено
- `tooling/project_snapshot.py`
- snapshot-aware `project_model.py`
- `/api/create-project-snapshot-export`
- snapshot panel in inspector
- `run_snapshot_export_checks.py`
- sample snapshot export package JSON

## Snapshot package
Snapshot содержит:
- `snapshot_name`
- `source_point_name`
- `source_point_kind`
- `target_session_id`
- `anchor`
- `immutability`
- `export_state`
  - workspace summary
  - branch summary
  - lineage graph
  - dependency map
  - timeline
  - tag point summary
  - `project_index_frozen`

## Важный принцип
Snapshot export хранит **frozen copy** project state без вложенных `snapshot_exports`.
Это исключает recursive snapshot growth и делает export устойчивым.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1.md`

Size: 1556 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot / immutable workspace state export by tag or release point:
**snapshot import / workspace restore from immutable export**.

## Что это даёт
Теперь система умеет:
- импортировать immutable snapshot package;
- восстановить project workspace из frozen project state;
- восстановить active anchor/session;
- сохранить restore provenance;
- отразить restore в history и inspector.

## Что добавлено
- `tooling/project_snapshot_restore.py`
- restore-aware `project_model.py`
- `/api/restore-project-from-snapshot-export`
- restore panel in inspector
- `run_snapshot_restore_checks.py`
- sample restored project / result JSON

## Restore semantics v0.1
Это **workspace restore from frozen snapshot export**.

### Как работает
- берётся `export_state.project_index_frozen`;
- проект восстанавливается в нормализованную workspace-форму;
- создаётся restore registry entry;
- пишется history event `snapshot_restored`;
- при `activate_anchor=true` активируется snapshot anchor session.

## Restore registry
В restored project хранится:
- `snapshot_restores`

Это позволяет видеть provenance restore-операций внутри самого workspace.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1.md`

Size: 2079 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1

## Назначение
Этот документ описывает следующий слой после partial snapshot restore / selective workspace state import:
**snapshot merge / reconcile imported state with current workspace lineage**.

## Что это даёт
Теперь система умеет не только выборочно импортировать snapshot state,
но и **встраивать snapshot sessions в текущую lineage как reconciliation-операцию**.

## Что добавлено
- `tooling/project_snapshot_reconcile.py`
- reconcile-aware `project_model.py`
- `/api/reconcile-snapshot-into-project`
- snapshot reconcile panel in inspector
- `run_snapshot_reconcile_checks.py`
- sample snapshot reconcile project / result JSON

## Семантика v0.1
Это **materialized replay onto current lineage**.

### Как работает
- выбираются `selected_session_ids` из snapshot;
- определяется `target_branch_name` в текущем workspace;
- каждый выбранный snapshot session materialize-ится как новый reconcile commit;
- первый reconcile commit parent-ится к текущему head target branch;
- следующие reconcile commits строятся цепочкой поверх предыдущего reconcile;
- provenance фиксирует `reconciled_with_head_session_id`.

## Provenance
Каждый reconcile commit получает:
- `commit_kind = snapshot_reconcile`
- `snapshot_reconcile.reconcile_name`
- `snapshot_reconcile.source_snapshot_name`
- `snapshot_reconcile.original_session_id`
- `snapshot_reconcile.reconciled_with_head_session_id`
- `snapshot_reconcile.conflict_like`

## History event
- `snapshot_reconciled`

## Граница v0.1
Это ещё не semantic conflict solver.
`conflict_like` — инженерный сигнал, что imported snapshot state расходится с current head по `source_text`.
````


## FILE: docs/SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1.md
Path: `docs/SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1.md`

Size: 1608 bytes

````markdown
# SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot conflict resolution / manual reconcile decisions:
**snapshot reconcile commit / promote resolved decisions into named resolution set or release lineage point**.

## Что это даёт
Теперь resolved reconcile decisions можно:
- оформить как **named resolution set**;
- зафиксировать в отдельном reconcile commit registry;
- при необходимости промотить последний resolved lineage point в `tag` или `release`.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit.py`
- commit-aware `project_model.py`
- `/api/commit-snapshot-reconcile-resolution`
- commit / promote panel in inspector
- `run_snapshot_reconcile_commit_checks.py`
- sample commit / promote result JSON

## Семантика v0.1
Этот слой не создаёт новый reconcile replay.
Он:
- берёт уже существующий `snapshot_reconcile_resolution_result`;
- регистрирует его как named resolution set;
- optionally creates tag/release point on the last resolved session.

## Что пишет registry
- `snapshot_reconcile_commits[commit_name]`
  - `resolution_name`
  - `snapshot_name`
  - `target_branch_name`
  - `resolved_session_ids`
  - `promoted_point_name`
  - `promoted_point_kind`

## История
Добавлен history event:
- `snapshot_reconcile_committed`
````


## FILE: docs/SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1.md
Path: `docs/SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1.md`

Size: 1686 bytes

````markdown
# SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1

## Назначение
Этот документ описывает следующий слой после cherry-pick / selective session replay across branches:
**squash / fold multiple sessions into one lineage commit**.

## Что это даёт
Теперь workspace умеет:
- выбрать несколько session entries;
- свернуть их в один новый lineage commit;
- вставить его в target branch;
- сохранить provenance fold-операции;
- отразить folded origin в lineage graph.

## Что добавлено
- `tooling/project_squash.py`
- `/api/squash-project-sessions`
- squash panel in inspector
- `run_squash_checks.py`
- sample squashed project / result / lineage graph JSON

## Squash policy v0.1
Это **conservative materialized squash**, а не semantic reduction нескольких программ в одну.

### Как работает
- выбирается ordered list `source_session_ids`;
- materialized state берётся из последней session в списке;
- создаётся новый commit в `target_branch_name`;
- обычный parent = current head target branch;
- дополнительно lineage graph получает `squash_origin` edges от всех folded sessions.

### Provenance
Каждый squash commit получает:
- `commit_kind = squash_fold`
- `squash_fold.source_session_ids`
- `squash_fold.source_branch_names`
- `squash_fold.target_branch_name`
- `squash_fold.materialized_from_session_id`
- `squash_fold.folded_count`

## History event
- `branch_squashed`
````


## FILE: docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1.md
Path: `docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1.md`

Size: 1513 bytes

````markdown

# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package conflict resolution / manual import decisions:
**standalone outcome package commit / promote imported resolution into local named outcome set or release point**.

## Что это даёт
Теперь import-resolution layer умеет не только:
- preview-ить package compatibility,
- принять manual import decisions,
- materialize resolved import commits,

но и:
- оформить результат как local named outcome set,
- optionally промотить последний resolved imported point в local tag/release,
- зафиксировать commit provenance и history.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_commit.py`
- commit-aware `project_model.py`
- `/api/commit-snapshot-reconcile-commit-package-resolution`
- local outcome set commit / promote controls in inspector
- `run_snapshot_reconcile_commit_package_commit_checks.py`

## Семантика
Этот слой не делает новый import replay.
Он оформляет уже существующий `snapshot_reconcile_commit_package_resolution_result`
как local committed outcome set.

## История
Добавлен history event:
- `snapshot_reconcile_commit_package_committed`
````


## FILE: docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md
Path: `docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md`

Size: 1972 bytes

````markdown

# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package diff / compatibility check before import:
**standalone outcome package conflict resolution / manual import decisions**.

## Что это даёт
Теперь portable outcome package import умеет не только:
- preview-ить compatibility,
- показать conflict-like cases before import,

но и:
- принять manual decisions per packaged resolved session,
- materialize resolved package-import commits,
- встроить их в current workspace lineage,
- зафиксировать decision provenance и историю.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_resolution.py`
- resolution-aware `project_model.py`
- `/api/resolve-snapshot-reconcile-commit-package-import`
- manual decision controls in inspector package import panel
- `run_snapshot_reconcile_commit_package_resolution_checks.py`
- sample package resolution result JSON

## Decision model v0.1
Поддерживаются решения:
- `use_package`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое применённое решение создаёт либо:
- новый resolved package-import commit,
- либо skip without commit.

## Provenance
Resolved imported commits получают:
- `commit_kind = snapshot_reconcile_commit_package_import_resolution`
- `snapshot_reconcile_commit_package_import_resolution.resolution_name`
- `snapshot_reconcile_commit_package_import_resolution.decision_choice`
- `snapshot_reconcile_commit_package_import_resolution.resolved_with_head_session_id`
- `snapshot_reconcile_commit_package_import_resolution.conflict_like`

## История
Добавлен history event:
- `snapshot_reconcile_commit_package_import_resolved`
````


## FILE: docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md
Path: `docs/SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md`

Size: 1527 bytes

````markdown

# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после resolution set export / import as standalone promoted outcome package:
**standalone outcome package diff / compatibility check before import**.

## Что это даёт
Теперь система умеет:
- взять текущий workspace;
- взять standalone promoted outcome package;
- построить dry-run preview before import;
- показать compatibility и conflict-like сигналы до apply-import.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_preview.py`
- package-preview aware `project_model.py`
- `/api/preview-snapshot-reconcile-commit-package-import`
- preview button in standalone package import panel
- `run_snapshot_reconcile_commit_package_preview_checks.py`
- sample standalone package preview result JSON

## Preview semantics v0.1
Это **non-mutating package import preview**.

### Что проверяется
- package version support
- import name availability
- target branch existence / branch creation need
- promoted point collision
- per-session compatibility vs current target head chain
- conflict-like divergence by `source_text`

### Что возвращается
- `import_target`
- `metadata`
- `collections`
- `compatibility`
- `preview_items`
- `summary`

Preview не изменяет workspace и не пишет history.
````


## FILE: docs/SEMASCRIPT_STATE_MODEL_v0.1.md
Path: `docs/SEMASCRIPT_STATE_MODEL_v0.1.md`

Size: 3073 bytes

````markdown
# SEMASCRIPT_STATE_MODEL_v0.1

## Назначение
Этот документ задаёт **execution state container** для SEMASCRIPT v0.1.

Его задача:
- принимать runtime plan;
- применять его к состоянию;
- хранить ресурсы, state assertions, dependencies, observations, actions и history;
- дать первый stateful execution layer поверх runtime semantics.

## Главный принцип
Runtime v0.1 строит **plan / accept-reject semantics**.  
State model v0.1 строит **state transition result**.

---

## 1. Структура состояния

```json
{
  "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
  "resources": {},
  "states": {},
  "dependencies": [],
  "observations": [],
  "actions": [],
  "expansions": [],
  "history": [],
  "metadata": {
    "applied_steps": 0,
    "last_schedule": null
  }
}
```

### Поля
- `resources` — инвентари по сущностям
- `states` — зафиксированные состояния по сущностям
- `dependencies` — dependency edges
- `observations` — observation records
- `actions` — action records
- `expansions` — результаты `EXPAND`
- `history` — применённые шаги
- `metadata` — applied count / last schedule

---

## 2. Что state model применяет

### `TRANSFER`
- уменьшает ресурс у `src`
- увеличивает ресурс у `dst`
- проверяет баланс источника

### `CREATE`
- увеличивает ресурс у `dst`

### `DESTROY`
- уменьшает ресурс у `ctx` или `GLOBAL`

### `ACT`
- пишет action record
- пишет history

### `OBSERVE`
- пишет observation record
- пишет history

### `CHANGE`
- фиксирует состояние сущности
- пишет history

### `DEPENDENCY`
- создаёт dependency edge

### `EXPAND`
- создаёт expansion record

### `ASSERT_STATE`
- фиксирует состояние в `states`

---

## 3. Инварианты на state layer

### `ZSUM`
После применения плана общий ресурсный total должен остаться тем же.

### `NZSUM`
Разрешает чистый прирост / убыль.

### `BAL`
На state layer v0.1 не является прямым operational law.

---

## 4. Ошибки state layer

- `S_BALANCE` — недостаточный баланс
- `S_INV_ZSUM` — нарушение ZSUM на уровне состояния
- `S_OP` — неподдерживаемый state operation

Runtime errors (`R_*`) также прокидываются в итоговый state report, если runtime не принял план.

---

## 5. Практический смысл
Теперь система умеет:
1. Human/Core/Exec -> normalize/parse
2. AST -> validate
3. runtime -> plan
4. state model -> final state transition

Это первый настоящий stateful execution layer проекта.
````


## FILE: docs/SEMASCRIPT_SVG_RENDERER_SPEC_v0.1.md
Path: `docs/SEMASCRIPT_SVG_RENDERER_SPEC_v0.1.md`

Size: 1481 bytes

````markdown
# SEMASCRIPT_SVG_RENDERER_SPEC_v0.1

## Назначение
Этот документ описывает **renderer / SVG prototypes** для SEMASCRIPT v0.1.

Его задача:
- визуализировать AST/Core/Exec структуры в SVG;
- проверить читаемость class shapes;
- проверить видимость frame boundaries;
- проверить list-scope layout;
- дать прототипный visual layer без финального glyph-design.

## Что добавлено
- `tooling/svg_renderer.py`
- `tooling/render_to_svg.py`
- `tooling/render_corpus_svgs.py`
- `tooling/run_svg_renderer_checks.py`

## Визуальные принципы v0.1

### Class shapes
- `ENT` -> ellipse
- `PRC` -> triangle
- `STA` -> rectangle
- `REL` -> diamond
- `PAT` -> pentagon-like prototype
- `EXEC` -> hexagon-like prototype
- `IDX` -> point/circle
- `FRM` -> rounded container frame

### Layout
- `north` roles -> above body
- `west` roles -> left
- `east` roles -> right
- `south` roles -> below
- `FRM:*` renders `scp/scope` inside a visible container
- `list-scope` renders as dashed box with stacked items

## Граница v0.1
Это **structural SVG renderer**, а не финальная glyph system.
Он нужен для:
- structural validation,
- visual debugging,
- prototype layout checks.

Он не решает:
- финальную эстетику,
- font system,
- production glyphset,
- compact orthography.
````


## FILE: docs/SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1.md
Path: `docs/SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1.md`

Size: 1204 bytes

````markdown
# SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1

## Назначение
Этот документ описывает следующий слой после reset / restore branch head:
**tag / release points over sessions and lineage states**.

## Что это даёт
Теперь workspace умеет:
- создавать именованные tag/release points;
- привязывать их к session / lineage point;
- сохранять их в project index;
- отражать их в history и lineage graph;
- восстанавливать их вместе с workspace.

## Что добавлено
- `tooling/project_tags.py`
- tag-aware `project_model.py`
- `/api/create-project-tag-release-point`
- tag/release panel in inspector
- `run_tag_release_checks.py`
- sample tag/release project / result / lineage graph JSON

## Что хранится
Каждая точка содержит:
- `tag_name`
- `point_kind = tag | release`
- `target_session_id`
- `target_session_name`
- `branch_name`
- `note`
- `lineage_state`

## History event
- `tag_release_created`

## Lineage graph
Nodes теперь могут нести attached tag/release annotations.
````


## FILE: docs/SEMASCRIPT_TESTPACK_v0.1.md
Path: `docs/SEMASCRIPT_TESTPACK_v0.1.md`

Size: 637 bytes

````markdown
# SEMASCRIPT_TESTPACK_v0.1

## Статус
Grammar-expanded validation pack aligned with parser/validator/normalizer

## Покрытие
- 16 positive Core cases
- 14 negative Core cases
- 8 positive Exec cases
- 9 negative Exec cases
- 10 positive Human normalization cases
- 5 negative Human normalization cases

## Новые grammar areas
- list-scope forms
- multi-scene wrappers
- causal shorthand normalization
- richer scene vocabulary for Human Mode

## Минимальный критерий успеха
Все expanded fixture-наборы проходят smoke-test без неожиданных расхождений.
````


## FILE: docs/SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1.md
Path: `docs/SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1.md`

Size: 2029 bytes

````markdown
# SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1

## Назначение
Этот документ описывает следующий слой после cross-session compare / diff mode:
**three-way session merge / conflict detection**.

## Что это даёт
Теперь project workspace умеет:
- брать `base / left / right` sessions,
- делать трёхсторонний merge source-bearing полей,
- выявлять конфликты,
- выдавать либо merged session, либо explicit conflict list.

## Главный принцип
Merge работает не по derived reports/render artifacts, а по тем данным, которые реально определяют сессию:
- `session_name`
- `profile`
- `source_mode`
- `source_text`
- `initial_state`
- `graph_document`
- `ui_state`

После успешного auto-merge merged session пересобирается заново через session model.

## Что добавлено
- `tooling/session_merge.py`
- `/api/merge-project-sessions-three-way`
- merge panel in inspector
- `run_session_merge_checks.py`
- sample merge sessions / project / merge result JSON

## Conflict policy v0.1
### Auto-merge
Разрешается если:
- left == right
- left == base
- right == base

### Conflict
Возникает если:
- left и right оба изменили base по-разному
- concurrent divergent list change
- concurrent divergent scalar change

## Граница v0.1
Это уже полезный three-way merge layer,
но ещё не:
- interactive manual conflict resolver
- semantic merge engine
- graph-aware merge heuristics beyond conservative list policy

## Session name policy
`session_name` в v0.1 считается merge-metadata и не блокирует auto-merge.
При расхождении имён используется мягкая политика выбора или синтезируется имя вида `Merged: left + right`.
````


## FILE: docs/SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md
Path: `docs/SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md`

Size: 1951 bytes

````markdown
# SEMASCRIPT_TOOLING_MVP_PLAN_v0.1

## Статус
Draft tooling plan

## Назначение
Этот документ описывает минимальный инструментальный стек для проверки SEMASCRIPT v0.1.

## Цель MVP
Не “полная IDE”, а минимальный набор инструментов, который доказывает, что SEMASCRIPT:
- парсится;
- валидируется;
- различает классы ошибок;
- может проецировать Human → Core;
- может проверять Core → Exec пригодность.

---

## MVP components

### 1. Core parser
Вход:
- канонические S-Linear формы

Выход:
- parse tree / AST

### 2. Core validator
Проверяет:
- focus;
- typing;
- roles;
- scope;
- nesting;
- canonical validity.

### 3. Extension validator
Проверяет:
- pattern scope;
- time mode scope;
- invariant declarations;
- forbidden semantic collapses.

### 4. Human normalizer
Минимально поддерживает:
- shorthand `spr(...)`
- `gen(...)`
- `pal(...)`
- `time:*`
- `inv:*`

### 5. Exec validator
Проверяет:
- required roles;
- typing;
- undeclared constraints;
- unsupported pattern macros;
- determinism.

---

## Suggested folder structure
```text
/tools
  /parser
  /validator
  /normalizer
  /exec_validator
  /fixtures
```

---

## Suggested milestones

### Tool M1
Parse canonical Core forms

### Tool M2
Validate positive/negative cases from test pack

### Tool M3
Normalize minimal Human shorthand

### Tool M4
Validate minimal Exec subset

### Tool M5
Run corpus-based smoke tests

---

## Success criteria
Tooling MVP считается достаточным для v0.1, если:
- positive test cases pass;
- negative cases fail for expected reasons;
- human shorthand normalizes predictably;
- exec validation rejects underdefined forms.
````


## FILE: docs/SEMASCRIPT_V0_2_HARDENING_SPEC.md
Path: `docs/SEMASCRIPT_V0_2_HARDENING_SPEC.md`

Size: 7217 bytes

````markdown
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
````


## FILE: docs/SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1.md
Path: `docs/SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1.md`

Size: 1974 bytes

````markdown
# SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1

## Назначение
Этот документ описывает следующий слой после multi-session project workspace:
**workspace navigation / dependency map between sessions**.

## Что это даёт
Теперь project workspace показывает не только список сессий, но и карту их связей:
- какие сессии производят сущности;
- какие сессии их потребляют;
- где есть shared entities;
- как переключаться по проекту не списком, а по структуре связей.

## Что добавлено
- `tooling/workspace_navigation.py`
- dependency-map inclusion in `project_model.workspace_to_inspector_payload`
- project dependency map panel in inspector
- clickable session nodes in workspace map
- `run_workspace_navigation_checks.py`
- `sample_dependency_project_index.json`

## Как строятся связи
На v0.1 карта использует инженерную эвристику:

### Flow link
Создаётся, если:
- session A производит токены через `dst/res/right`
- session B потребляет те же токены через `src/code/cau/left/obj/ctx/agt`

### Shared link
Создаётся, если:
- flow-link не найден,
- но у двух сессий есть общие сущности в AST/state artifacts

## Что умеет inspector
- визуально показывать dependency map проекта
- кликать по session-node
- переключать active session прямо с карты
- видеть active session highlighted

## Граница v0.1
Это ещё не formal proof graph и не full semantic dependency engine.
Это полезная инженерная navigation map поверх существующего workspace layer.
````


## FILE: docs/SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1.md
Path: `docs/SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1.md`

Size: 1571 bytes

````markdown
# SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1

## Назначение
Этот документ описывает следующий слой после workspace navigation / dependency map:
**workspace timeline / session evolution history**.

## Что это даёт
Теперь проект показывает не только:
- какие сессии существуют,
- как они связаны,

но и:
- как workspace эволюционировал по шагам,
- когда были добавлены сессии,
- когда менялась active session,
- как переходить по проекту через timeline events.

## Что добавлено
- `tooling/workspace_timeline.py`
- timeline-aware `project_model.py`
- `run_workspace_timeline_checks.py`
- timeline panel in inspector
- clickable timeline events for active-session switching
- `sample_timeline_project_index.json`

## Event types v0.1
- `workspace_created`
- `session_added`
- `active_session_set`
- `active_session_switched`

## Что хранится
Timeline хранится прямо в `project_index.history.events`.

Каждое событие содержит:
- `seq`
- `event_type`
- `title`
- `session_id`
- `session_name`
- `payload`

## Что умеет inspector
- показывать timeline проекта
- подсвечивать события активной сессии
- переключать active session из timeline
- сохранять/восстанавливать timeline через project JSON
````


## FILE: tooling/corpus/inspector_sample_input.txt
Path: `tooling/corpus/inspector_sample_input.txt`

Size: 25 bytes

````markdown
gen(template -> instance)
````


## FILE: tooling/corpus/sample_human.txt
Path: `tooling/corpus/sample_human.txt`

Size: 54 bytes

````markdown
time:lin(resource declines => system becomes unstable)
````


## FILE: tooling/corpus/sample_pattern.txt
Path: `tooling/corpus/sample_pattern.txt`

Size: 17 bytes

````markdown
spr(seed -> form)
````


## FILE: tooling/corpus/sample_pattern_decomposed.txt
Path: `tooling/corpus/sample_pattern_decomposed.txt`

Size: 42 bytes

````markdown
[PRC:EXP <src=[ENT:SEED]; res=[ENT:FORM]>]
````


## FILE: tooling/corpus/sample_render_core.txt
Path: `tooling/corpus/sample_render_core.txt`

Size: 83 bytes

````markdown
[FRM:INV <law=ZSUM; scp=[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]>]
````


## FILE: tooling/corpus/sample_render_human.txt
Path: `tooling/corpus/sample_render_human.txt`

Size: 25 bytes

````markdown
gen(template -> instance)
````


## FILE: tooling/corpus/sample_render_multi.txt
Path: `tooling/corpus/sample_render_multi.txt`

Size: 116 bytes

````markdown
[FRM:TIME <mode=LIN; scp=[[EXEC:ACT <agt=[ENT:HUM]; obj=[ENT:SYS]>]; [EXEC:CHANGE <obj=[ENT:SYS]; res=[STA:DEC]>]]>]
````


## FILE: tooling/corpus/sample_runtime.txt
Path: `tooling/corpus/sample_runtime.txt`

Size: 116 bytes

````markdown
[FRM:TIME <mode=LIN; scp=[[EXEC:ACT <agt=[ENT:HUM]; obj=[ENT:SYS]>]; [EXEC:CHANGE <obj=[ENT:SYS]; res=[STA:DEC]>]]>]
````


## FILE: tooling/corpus/sample_state_input.txt
Path: `tooling/corpus/sample_state_input.txt`

Size: 57 bytes

````markdown
[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]
````
