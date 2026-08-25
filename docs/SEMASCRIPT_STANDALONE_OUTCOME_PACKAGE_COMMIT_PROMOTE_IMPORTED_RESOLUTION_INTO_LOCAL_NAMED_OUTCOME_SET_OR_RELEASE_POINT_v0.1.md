
# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package conflict resolution / manual import decisions:
**standalone outcome package commit / promote imported resolution into local named outcome set or release point**.

## Что это даёт
Теперь import-resolution layer умеет не только:
- preview-ить package compatibility,
- принять manual import decisions,
- materialize resolved import commits,

но и:
- оформить результат как local named outcome set,
- optionally промотить последний resolved imported point в local tag/release,
- зафиксировать commit provenance и history.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_commit.py`
- commit-aware `project_model.py`
- `/api/commit-snapshot-reconcile-commit-package-resolution`
- local outcome set commit / promote controls in inspector
- `run_snapshot_reconcile_commit_package_commit_checks.py`

## Семантика
Этот слой не делает новый import replay.
Он оформляет уже существующий `snapshot_reconcile_commit_package_resolution_result`
как local committed outcome set.

## История
Добавлен history event:
- `snapshot_reconcile_commit_package_committed`
