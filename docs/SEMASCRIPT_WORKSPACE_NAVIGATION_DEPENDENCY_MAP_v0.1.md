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
