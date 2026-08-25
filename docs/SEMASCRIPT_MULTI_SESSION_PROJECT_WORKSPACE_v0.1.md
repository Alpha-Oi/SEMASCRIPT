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
