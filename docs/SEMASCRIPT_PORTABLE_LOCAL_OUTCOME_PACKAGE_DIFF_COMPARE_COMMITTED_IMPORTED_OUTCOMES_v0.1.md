# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package commit / promote imported resolution into local named outcome set or release point:
**portable local outcome package diff / compare between committed imported outcomes**.

## Что это даёт
Теперь система умеет сравнивать уже committed imported portable local outcomes внутри текущего workspace.

## Что добавлено
- `tooling/project_local_outcome_set_package_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-committed-portable-local-outcome-packages`
- compare panel in inspector
- `run_local_outcome_set_package_commit_compare_checks.py`
- sample compare project / compare result JSON

## Что сравнивается
- commit identity
- resolution name
- package name
- source commit name
- target branch name
- promoted point name / kind
- note
- resolved session ids
- resolution pairs
- materialized source texts
