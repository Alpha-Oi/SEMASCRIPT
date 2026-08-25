# SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1

## Назначение
Этот документ описывает следующий слой после cross-session compare / diff mode:
**three-way session merge / conflict detection**.

## Что это даёт
Теперь project workspace умеет:
- брать `base / left / right` sessions,
- делать трёхсторонний merge source-bearing полей,
- выявлять конфликты,
- выдавать либо merged session, либо explicit conflict list.

## Главный принцип
Merge работает не по derived reports/render artifacts, а по тем данным, которые реально определяют сессию:
- `session_name`
- `profile`
- `source_mode`
- `source_text`
- `initial_state`
- `graph_document`
- `ui_state`

После успешного auto-merge merged session пересобирается заново через session model.

## Что добавлено
- `tooling/session_merge.py`
- `/api/merge-project-sessions-three-way`
- merge panel in inspector
- `run_session_merge_checks.py`
- sample merge sessions / project / merge result JSON

## Conflict policy v0.1
### Auto-merge
Разрешается если:
- left == right
- left == base
- right == base

### Conflict
Возникает если:
- left и right оба изменили base по-разному
- concurrent divergent list change
- concurrent divergent scalar change

## Граница v0.1
Это уже полезный three-way merge layer,
но ещё не:
- interactive manual conflict resolver
- semantic merge engine
- graph-aware merge heuristics beyond conservative list policy

## Session name policy
`session_name` в v0.1 считается merge-metadata и не блокирует auto-merge.
При расхождении имён используется мягкая политика выбора или синтезируется имя вида `Merged: left + right`.
