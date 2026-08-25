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
