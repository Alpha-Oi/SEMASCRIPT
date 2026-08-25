# SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1

## Назначение
Этот документ описывает следующий слой после local outcome set diff / compare between imported promoted resolutions:
**local outcome set export / import as portable local promoted resolution package**.

## Что это даёт
Теперь система умеет:
- экспортировать локально committed imported promoted outcome set в переносимый portable package;
- импортировать этот package в другой workspace;
- materialize imported sessions в current lineage;
- создать imported local outcome set commit и registry entry.

## Что добавлено
- `tooling/project_local_outcome_set_package.py`
- package-aware `project_model.py`
- `/api/export-local-outcome-set-package`
- `/api/import-local-outcome-set-package`
- local outcome portable package panel in inspector
- `run_local_outcome_set_package_checks.py`
- sample local outcome set portable package JSON

## Export semantics v0.1
Экспортирует:
- local outcome set commit metadata
- resolved sessions
- promoted point
- portable package metadata

## Import semantics v0.1
Импорт:
- materialize-ит sessions как `local_outcome_set_package_import`
- создаёт imported local outcome commit entry в local outcome registry
- переносит promoted point, если он есть
- пишет history event `local_outcome_set_package_imported`
