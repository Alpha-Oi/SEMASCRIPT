# SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1

## Назначение
Этот документ описывает следующий слой после resolution set diff / compare between promoted reconcile outcomes:
**resolution set export / import as standalone promoted outcome package**.

## Что это даёт
Теперь promoted reconcile outcome можно:
- экспортировать в переносимый standalone package;
- импортировать этот package в другой workspace;
- materialize imported outcome как новый lineage-aware imported commit;
- переносить promoted point вместе с outcome.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package.py`
- package-aware `project_model.py`
- export/import package endpoints in inspector
- `run_snapshot_reconcile_commit_package_checks.py`
- sample standalone package export/import JSON

## Package semantics v0.1
Standalone package содержит:
- exported reconcile commit metadata
- resolved sessions
- optional promoted point
- portable package metadata

Import пакета:
- не подменяет текущий workspace,
- а materialize-ит imported sessions как новые package-import commits,
- создаёт imported reconcile commit entry,
- при наличии promoted point переносит его как новый tag/release point.
