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
