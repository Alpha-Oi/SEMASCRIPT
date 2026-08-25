# SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot conflict resolution / manual reconcile decisions:
**snapshot reconcile commit / promote resolved decisions into named resolution set or release lineage point**.

## Что это даёт
Теперь resolved reconcile decisions можно:
- оформить как **named resolution set**;
- зафиксировать в отдельном reconcile commit registry;
- при необходимости промотить последний resolved lineage point в `tag` или `release`.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit.py`
- commit-aware `project_model.py`
- `/api/commit-snapshot-reconcile-resolution`
- commit / promote panel in inspector
- `run_snapshot_reconcile_commit_checks.py`
- sample commit / promote result JSON

## Семантика v0.1
Этот слой не создаёт новый reconcile replay.
Он:
- берёт уже существующий `snapshot_reconcile_resolution_result`;
- регистрирует его как named resolution set;
- optionally creates tag/release point on the last resolved session.

## Что пишет registry
- `snapshot_reconcile_commits[commit_name]`
  - `resolution_name`
  - `snapshot_name`
  - `target_branch_name`
  - `resolved_session_ids`
  - `promoted_point_name`
  - `promoted_point_kind`

## История
Добавлен history event:
- `snapshot_reconcile_committed`
