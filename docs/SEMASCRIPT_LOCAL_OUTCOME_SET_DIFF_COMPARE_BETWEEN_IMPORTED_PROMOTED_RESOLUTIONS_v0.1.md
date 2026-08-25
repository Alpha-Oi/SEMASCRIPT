# SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package commit / promote imported resolution into local named outcome set or release point:
**local outcome set diff / compare between imported promoted resolutions**.

## Что это даёт
Теперь система умеет сравнивать уже **локально committed promoted outcomes** после package import-resolution chain.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-local-imported-promoted-outcomes`
- compare panel in inspector
- `run_local_outcome_set_compare_checks.py`
- sample compare project / compare result JSON
