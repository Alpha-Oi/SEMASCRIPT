# SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot import / workspace restore from immutable export:
**snapshot diff / restore preview before apply**.

## Что это даёт
Теперь система умеет:
- взять текущий workspace;
- взять immutable snapshot package;
- построить dry-run preview restore;
- показать diff текущего project state и snapshot frozen state;
- дать оператору понять, что изменится до restore apply.

## Что добавлено
- `tooling/project_snapshot_diff.py`
- snapshot preview-aware `project_model.py`
- `/api/preview-project-snapshot-restore`
- preview button/panel in inspector restore section
- `run_snapshot_restore_preview_checks.py`
- sample preview result JSON

## Preview semantics v0.1
Это **non-mutating restore preview**.

### Что сравнивается
- project name
- active session / active branch
- sessions
- branches
- tag points
- snapshot exports
- snapshot restores

### Что возвращается
- `snapshot_restore_preview_version`
- `restore_target`
- `scalar_diff`
- `collections`
- `summary`

Restore preview не пишет history и не меняет workspace.
