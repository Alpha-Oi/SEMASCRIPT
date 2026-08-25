# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package conflict resolution / manual import decisions:
**portable local outcome package commit / promote imported resolution into local named outcome set or release point**.

## Что это даёт
Теперь resolved import decisions по portable local outcome package можно:
- зафиксировать как локальный named outcome set;
- промотить в `release` или `tag` point;
- использовать как source-of-truth для дальнейшего local outcome export/compare.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit.py`
- commit-aware `project_model.py`
- `/api/commit-local-outcome-set-package-resolution`
- commit/promote panel in inspector
- `run_local_outcome_set_package_commit_checks.py`
- sample commit project / result JSON
