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
