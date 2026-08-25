# SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1

## Назначение
Этот документ описывает **persisted project/session format** как следующий шаг после editable visual graph mode.

## Почему он идёт после graph mode
Сначала нужен рабочий graph editor.
Только после этого появляется полноценная сущность, которую стоит сохранять:
- source text
- normalized text / S-Linear
- graph
- AST
- runtime/state reports
- render outputs
- UI state

## Что добавлено
- `tooling/session_model.py`
- session export/import API в inspector
- session JSON textarea
- download current session
- sample session documents
- session smoke checks

## Session structure
```json
{
  "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
  "session_name": "...",
  "project": { ... },
  "documents": { ... },
  "reports": { ... },
  "render": { ... },
  "ui_state": { ... },
  "metadata": { ... }
}
```

### `project`
- profile
- source_mode
- source_text
- normalized_text
- slinear
- decomposed_slinear
- initial_state

### `documents`
- ast_document
- decomposed_ast_document
- graph_document
- decomposed_graph_document

### `reports`
- validation
- runtime_report
- state_report

### `render`
- svg_raw
- svg_decomposed

### `ui_state`
- selected_entity_id
- preview_mode
- decompose
- viewport
- panel visibility

## Что умеет inspector
- export text session
- export graph session
- import saved session
- restore graph/workspace/report/render state
- download session JSON

## Граница v0.1
Это persisted session format, но ещё не:
- multi-file project workspace
- versioned migration system
- collaborative project storage
- branch/merge semantics
