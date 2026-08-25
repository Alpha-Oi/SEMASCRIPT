# SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot reconcile commit / promote resolved decisions:
**resolution set diff / compare between promoted reconcile outcomes**.

## Что это даёт
Теперь система умеет:
- выбрать два promoted reconcile outcomes;
- сравнить их как resolution sets;
- увидеть различия по metadata, resolved sessions, resolution pairs и materialized source text outcomes.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_compare.py`
- compare-aware `project_model.py`
- `/api/compare-snapshot-reconcile-commits`
- compare panel in inspector
- `run_snapshot_reconcile_commit_compare_checks.py`
- sample compare project / result JSON

## Что сравнивается
- `snapshot_name`
- `resolution_name`
- `target_branch_name`
- `promoted_point_name`
- `promoted_point_kind`
- `note`
- `resolved_session_ids`
- `resolution_pairs`
- materialized `source_text` for resolved sessions

## Формат результата
- `identity`
- `metadata`
- `resolved_sessions`
- `resolution_pairs`
- `resolved_session_texts`
- `summary`
