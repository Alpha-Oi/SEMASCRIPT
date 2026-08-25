# SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot / immutable workspace state export by tag or release point:
**snapshot import / workspace restore from immutable export**.

## Что это даёт
Теперь система умеет:
- импортировать immutable snapshot package;
- восстановить project workspace из frozen project state;
- восстановить active anchor/session;
- сохранить restore provenance;
- отразить restore в history и inspector.

## Что добавлено
- `tooling/project_snapshot_restore.py`
- restore-aware `project_model.py`
- `/api/restore-project-from-snapshot-export`
- restore panel in inspector
- `run_snapshot_restore_checks.py`
- sample restored project / result JSON

## Restore semantics v0.1
Это **workspace restore from frozen snapshot export**.

### Как работает
- берётся `export_state.project_index_frozen`;
- проект восстанавливается в нормализованную workspace-форму;
- создаётся restore registry entry;
- пишется history event `snapshot_restored`;
- при `activate_anchor=true` активируется snapshot anchor session.

## Restore registry
В restored project хранится:
- `snapshot_restores`

Это позволяет видеть provenance restore-операций внутри самого workspace.
