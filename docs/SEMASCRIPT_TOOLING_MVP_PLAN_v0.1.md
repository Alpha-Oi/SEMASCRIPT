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
