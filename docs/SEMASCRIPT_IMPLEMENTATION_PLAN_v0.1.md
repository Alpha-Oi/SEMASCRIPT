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
