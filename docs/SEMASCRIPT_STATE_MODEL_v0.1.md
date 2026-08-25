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
