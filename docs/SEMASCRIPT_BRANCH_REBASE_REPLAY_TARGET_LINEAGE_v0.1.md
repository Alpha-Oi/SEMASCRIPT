# SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1

## Назначение
Этот документ описывает следующий слой после branching / named merge lineage graph:
**branch rebase / replay onto target lineage**.

## Что это даёт
Теперь workspace умеет:
- выбрать source branch;
- выбрать target branch;
- replay-ить commits source branch onto target lineage;
- создавать новые rebased session entries;
- обновлять head source branch;
- сохранять provenance rebase replay;
- отражать результат в lineage graph и timeline.

## Что добавлено
- `tooling/project_rebase.py`
- `/api/rebase-project-branch`
- rebase panel in inspector
- `run_branch_rebase_checks.py`
- sample rebased project / result / lineage graph JSON

## Rebase policy v0.1
Это **conservative replay rebase**, а не destructive history rewrite.

### Как работает
- source branch root не копируется;
- commits source branch после fork point replay-ятся как новые entries;
- первый replay commit получает parent = current head target branch;
- следующие replay commits строятся цепочкой поверх предыдущего replay;
- новые replay commits остаются в `source_branch_name`.

### Provenance
Каждый replay commit получает:
- `commit_kind = rebase_replay`
- `rebase_replay.source_branch_name`
- `rebase_replay.target_branch_name`
- `rebase_replay.original_session_id`
- `rebase_replay.replay_index`

## History event
- `branch_rebased`
