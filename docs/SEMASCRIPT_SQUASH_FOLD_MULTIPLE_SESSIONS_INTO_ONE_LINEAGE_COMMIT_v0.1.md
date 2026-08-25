# SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1

## Назначение
Этот документ описывает следующий слой после cherry-pick / selective session replay across branches:
**squash / fold multiple sessions into one lineage commit**.

## Что это даёт
Теперь workspace умеет:
- выбрать несколько session entries;
- свернуть их в один новый lineage commit;
- вставить его в target branch;
- сохранить provenance fold-операции;
- отразить folded origin в lineage graph.

## Что добавлено
- `tooling/project_squash.py`
- `/api/squash-project-sessions`
- squash panel in inspector
- `run_squash_checks.py`
- sample squashed project / result / lineage graph JSON

## Squash policy v0.1
Это **conservative materialized squash**, а не semantic reduction нескольких программ в одну.

### Как работает
- выбирается ordered list `source_session_ids`;
- materialized state берётся из последней session в списке;
- создаётся новый commit в `target_branch_name`;
- обычный parent = current head target branch;
- дополнительно lineage graph получает `squash_origin` edges от всех folded sessions.

### Provenance
Каждый squash commit получает:
- `commit_kind = squash_fold`
- `squash_fold.source_session_ids`
- `squash_fold.source_branch_names`
- `squash_fold.target_branch_name`
- `squash_fold.materialized_from_session_id`
- `squash_fold.folded_count`

## History event
- `branch_squashed`
