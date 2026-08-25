# SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot conflict detection / reconcile preview before apply:
**snapshot conflict resolution / manual reconcile decisions**.

## Что это даёт
Теперь reconcile-layer умеет не только:
- preview-ить conflict-like ситуации,
- показать risk before apply,

но и:
- принять manual decisions per snapshot session,
- materialize resolved reconcile commits,
- зафиксировать decision provenance,
- встроить resolved chain в current workspace lineage.

## Что добавлено
- `tooling/project_snapshot_reconcile_resolution.py`
- resolution-aware `project_model.py`
- `/api/resolve-snapshot-reconcile-conflicts`
- manual reconcile decision controls in inspector
- `run_snapshot_reconcile_resolution_checks.py`
- sample reconcile resolution project / result JSON

## Decision model v0.1
Поддерживаются решения:
- `use_snapshot`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое решение создаёт либо:
- новый resolved reconcile commit,
- либо skip without commit.

Resolved commits получают provenance:
- `commit_kind = snapshot_reconcile_resolution`
- `snapshot_reconcile_resolution.decision_choice`
- `snapshot_reconcile_resolution.resolved_with_head_session_id`
- `snapshot_reconcile_resolution.conflict_like`

## История
Добавлен history event:
- `snapshot_reconcile_resolved`
