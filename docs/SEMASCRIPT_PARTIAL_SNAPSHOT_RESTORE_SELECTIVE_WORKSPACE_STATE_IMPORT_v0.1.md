# SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot diff / restore preview before apply:
**partial snapshot restore / selective workspace state import**.

## Что это даёт
Теперь система умеет не только полностью restore-ить frozen workspace из snapshot package,
но и **выборочно импортировать части snapshot state** в уже существующий текущий workspace.

## Что добавлено
- `tooling/project_snapshot_partial_import.py`
- partial-import aware `project_model.py`
- `/api/partial-import-project-from-snapshot`
- partial import panel in inspector
- `run_partial_snapshot_import_checks.py`
- sample partial import project / result JSON

## Import semantics v0.1
Это **non-destructive selective import**.

### Что можно импортировать
- `selected_session_ids`
- `selected_tag_point_names`
- `selected_snapshot_export_names`

### Как работает
- выбранные snapshot sessions вставляются в current workspace как **новые session entries**
- для них создаётся provenance `snapshot_partial_import`
- imported sessions строятся цепочкой в `target_branch_name`
- tag/release points импортируются, если их target session доступен после remap/import
- snapshot exports могут быть перенесены как frozen artifacts

## Provenance
Каждый imported session получает:
- `commit_kind = snapshot_partial_import`
- `snapshot_partial_import.import_name`
- `snapshot_partial_import.source_snapshot_name`
- `snapshot_partial_import.original_session_id`
- `snapshot_partial_import.source_branch_name`
- `snapshot_partial_import.target_branch_name`

## History
Добавлен history event:
- `snapshot_partial_imported`

## Ограничение v0.1
Это selective import, а не semantic merge:
- текущие sessions не перезаписываются
- imported sessions получают новые ids
- registry names при конфликте переименовываются с суффиксами
