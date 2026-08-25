# SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после three-way session merge / conflict detection:
**interactive conflict resolution / manual merge decisions**.

## Что это даёт
Теперь merge-layer умеет не только:
- обнаруживать конфликт,
- останавливать auto-merge,

но и:
- показать каждый conflict path,
- дать выбор `base / left / right / custom`,
- применить manual decisions,
- пересобрать итоговую merged session после полного разрешения конфликтов.

## Что добавлено
- `tooling/session_conflict_resolution.py`
- `/api/resolve-project-merge-conflicts`
- interactive conflict list in inspector
- bulk choices: `Use left for all`, `Use right for all`
- `run_conflict_resolution_checks.py`
- sample conflicted/resolved merge results

## Decision model
Каждое решение задаётся по `path`:
```json
{
  "source_text": { "choice": "left" }
}
```

или:
```json
{
  "source_text": { "choice": "custom", "value": "gen(template -> merged_instance)" }
}
```

## Как работает
1. сначала строится обычный three-way merge result;
2. если есть conflicts, inspector показывает их списком;
3. пользователь выбирает решения;
4. resolver применяет решения к `merged_source`;
5. если unresolved conflicts не осталось — пересобирается `merged_session`.

## Важное инженерное правило
Для text-based sessions `graph_document` больше не считается conflict-bearing source field.
Он derived от `source_text`, поэтому не создаёт лишний merge noise.
