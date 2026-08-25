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
