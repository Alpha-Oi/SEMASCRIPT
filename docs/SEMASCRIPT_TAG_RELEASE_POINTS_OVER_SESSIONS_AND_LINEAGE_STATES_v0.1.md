# SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1

## Назначение
Этот документ описывает следующий слой после reset / restore branch head:
**tag / release points over sessions and lineage states**.

## Что это даёт
Теперь workspace умеет:
- создавать именованные tag/release points;
- привязывать их к session / lineage point;
- сохранять их в project index;
- отражать их в history и lineage graph;
- восстанавливать их вместе с workspace.

## Что добавлено
- `tooling/project_tags.py`
- tag-aware `project_model.py`
- `/api/create-project-tag-release-point`
- tag/release panel in inspector
- `run_tag_release_checks.py`
- sample tag/release project / result / lineage graph JSON

## Что хранится
Каждая точка содержит:
- `tag_name`
- `point_kind = tag | release`
- `target_session_id`
- `target_session_name`
- `branch_name`
- `note`
- `lineage_state`

## History event
- `tag_release_created`

## Lineage graph
Nodes теперь могут нести attached tag/release annotations.
