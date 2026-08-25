# SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1

## Назначение
Этот документ описывает следующий слой после tag / release points over sessions and lineage states:
**snapshot / immutable workspace state export by tag or release point**.

## Что это даёт
Теперь project workspace умеет:
- взять существующий tag/release point как anchor;
- собрать immutable snapshot export package;
- заморозить состояние workspace на момент экспорта;
- сохранить snapshot registry в `project_index`;
- восстанавливать snapshot summary и скачивать snapshot package из inspector.

## Что добавлено
- `tooling/project_snapshot.py`
- snapshot-aware `project_model.py`
- `/api/create-project-snapshot-export`
- snapshot panel in inspector
- `run_snapshot_export_checks.py`
- sample snapshot export package JSON

## Snapshot package
Snapshot содержит:
- `snapshot_name`
- `source_point_name`
- `source_point_kind`
- `target_session_id`
- `anchor`
- `immutability`
- `export_state`
  - workspace summary
  - branch summary
  - lineage graph
  - dependency map
  - timeline
  - tag point summary
  - `project_index_frozen`

## Важный принцип
Snapshot export хранит **frozen copy** project state без вложенных `snapshot_exports`.
Это исключает recursive snapshot growth и делает export устойчивым.
