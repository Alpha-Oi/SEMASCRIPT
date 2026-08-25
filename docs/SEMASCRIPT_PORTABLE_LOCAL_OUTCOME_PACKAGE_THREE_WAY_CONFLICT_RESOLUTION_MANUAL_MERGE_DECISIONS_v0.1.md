# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package export / import compare baseline or three-way merge between committed imported outcomes:
**portable local outcome package three-way conflict resolution / manual merge decisions**.

## Что это даёт
Теперь baseline-aware three-way merge preview можно превратить в materialized merge-resolution chain:
- для каждого `original_session_id` принять merge decision;
- разрешить conflicts вручную;
- materialize-ить resolved sessions в lineage;
- сохранить resolution registry и provenance.

## Supported decisions
- `use_auto`
- `use_base`
- `use_left`
- `use_right`
- `skip`
- `custom_text`

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_merge_resolution.py`
- merge-resolution-aware `project_model.py`
- `/api/resolve-portable-local-outcome-package-three-way-merge-conflicts`
- merge decision panel in inspector
- `run_portable_local_outcome_package_merge_resolution_checks.py`
- sample merge resolution project / result JSON
