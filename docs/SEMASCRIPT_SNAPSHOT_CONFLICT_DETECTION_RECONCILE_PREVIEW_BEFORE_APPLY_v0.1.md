# SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1

## Назначение
Этот документ описывает следующий слой после snapshot merge / reconcile imported state with current workspace lineage:
**snapshot conflict detection / reconcile preview before apply**.

## Что это даёт
Теперь система умеет до reconcile apply:
- взять current workspace;
- взять snapshot package;
- выбрать snapshot sessions для reconcile;
- построить non-mutating reconcile preview;
- определить conflict-like расхождения между snapshot state и current head target branch.

## Что добавлено
- `tooling/project_snapshot_reconcile_preview.py`
- reconcile preview-aware `project_model.py`
- `/api/preview-snapshot-reconcile-in-project`
- preview button/panel in reconcile section of inspector
- `run_snapshot_reconcile_preview_checks.py`
- sample reconcile preview result JSON

## Preview semantics v0.1
Это **non-mutating reconcile preview**.

### Что показывает preview
Для каждого selected snapshot session:
- `current_head_session_id`
- `same_source_as_head`
- `same_profile_as_head`
- `exact_match`
- `conflict_like`
- `status`

### Что значит `conflict_like`
`conflict_like=true` означает, что source snapshot session расходится с current head по `source_text`.
Это ещё не semantic merge conflict solver, но уже корректный pre-apply risk signal.

## Важное свойство
Preview не пишет history, не создаёт reconcile registry и не меняет current workspace.
