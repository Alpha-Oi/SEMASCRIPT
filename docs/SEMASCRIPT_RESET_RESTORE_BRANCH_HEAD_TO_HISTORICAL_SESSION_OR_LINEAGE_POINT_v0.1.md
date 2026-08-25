# SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после squash / fold multiple sessions into one lineage commit:
**reset / restore branch head to historical session or lineage point**.

## Что это даёт
Теперь workspace умеет:
- выбрать ветку;
- выбрать historical session внутри этой ветки;
- переставить head ветки на эту historical point;
- зафиксировать reset в истории;
- отразить restored head в branch summary и lineage graph.

## Что добавлено
- `tooling/project_reset.py`
- branch-head override support in `project_branching.py`
- `/api/reset-project-branch-head`
- reset/restore panel in inspector
- `run_branch_reset_checks.py`
- sample branch reset project / result / lineage graph JSON

## Семантика v0.1
Это **non-destructive head restore**, а не удаление history.

### Как работает
- никакие session entries не удаляются;
- branch head переставляется на выбранный historical session;
- сохраняется `manual_head_session_id`;
- новые lineage nodes не создаются;
- lineage graph просто показывает другой head той же ветки.

## History event
- `branch_reset`

## Ограничение v0.1
Reset/restore разрешён только на historical session внутри той же ветки.
