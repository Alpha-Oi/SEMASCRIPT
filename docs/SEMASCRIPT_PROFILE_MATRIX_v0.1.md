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
