# SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1

## Назначение
Этот документ описывает следующий слой после partial snapshot restore / selective workspace state import:
**snapshot merge / reconcile imported state with current workspace lineage**.

## Что это даёт
Теперь система умеет не только выборочно импортировать snapshot state,
но и **встраивать snapshot sessions в текущую lineage как reconciliation-операцию**.

## Что добавлено
- `tooling/project_snapshot_reconcile.py`
- reconcile-aware `project_model.py`
- `/api/reconcile-snapshot-into-project`
- snapshot reconcile panel in inspector
- `run_snapshot_reconcile_checks.py`
- sample snapshot reconcile project / result JSON

## Семантика v0.1
Это **materialized replay onto current lineage**.

### Как работает
- выбираются `selected_session_ids` из snapshot;
- определяется `target_branch_name` в текущем workspace;
- каждый выбранный snapshot session materialize-ится как новый reconcile commit;
- первый reconcile commit parent-ится к текущему head target branch;
- следующие reconcile commits строятся цепочкой поверх предыдущего reconcile;
- provenance фиксирует `reconciled_with_head_session_id`.

## Provenance
Каждый reconcile commit получает:
- `commit_kind = snapshot_reconcile`
- `snapshot_reconcile.reconcile_name`
- `snapshot_reconcile.source_snapshot_name`
- `snapshot_reconcile.original_session_id`
- `snapshot_reconcile.reconciled_with_head_session_id`
- `snapshot_reconcile.conflict_like`

## History event
- `snapshot_reconciled`

## Граница v0.1
Это ещё не semantic conflict solver.
`conflict_like` — инженерный сигнал, что imported snapshot state расходится с current head по `source_text`.
