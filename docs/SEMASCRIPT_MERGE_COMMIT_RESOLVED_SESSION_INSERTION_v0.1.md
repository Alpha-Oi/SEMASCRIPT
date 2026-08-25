# SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1

## Назначение
Этот документ описывает следующий слой после interactive conflict resolution / manual merge decisions:
**merge commit / resolved session insertion back into project workspace**.

## Что это даёт
Теперь merge-layer замыкается обратно в project workspace:
- finalized merged session можно commit-ить как новую session entry,
- commit получает provenance metadata,
- в history добавляется `merge_committed`,
- committed session сразу попадает в navigation / timeline / compare / merge.

## Что добавлено
- расширенный `project_model.py`
- `commit_merged_session_to_workspace(...)`
- `/api/commit-project-merge-result`
- merge commit panel in inspector
- `run_merge_commit_checks.py`
- sample merge commit project / result JSON

## Что пишет commit
### Session entry metadata
```json
{
  "commit_kind": "merge_commit",
  "merge_commit": {
    "base_session_id": "...",
    "left_session_id": "...",
    "right_session_id": "...",
    "conflict_count": 1,
    "resolved_count": 1,
    "unresolved_count": 0,
    "finalized": true
  }
}
```

### History event
- `merge_committed`

## Поведение
- можно commit-ить либо auto-merged result,
- либо manually resolved merge result,
- committed session может сразу стать active session.
