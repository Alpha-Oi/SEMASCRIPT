# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package diff / compare between committed imported outcomes:
**portable local outcome package export / import compare baseline or three-way merge between committed imported outcomes**.

## Что это даёт
Теперь система умеет:
- взять `base`, `left`, `right` committed portable local outcomes;
- построить baseline-aware three-way merge preview;
- показать auto-merged fragments;
- показать conflict items;
- дать основу для следующего шага — manual merge decisions / merge commit.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_merge.py`
- three-way-merge-aware `project_model.py`
- `/api/compare-or-three-way-merge-committed-portable-local-outcomes`
- three-way merge panel in inspector
- `run_portable_local_outcome_package_merge_checks.py`
- sample merge project / merge result JSON

## Семантика v0.1
Это **non-mutating baseline / three-way merge preview**.
Workspace не меняется.
