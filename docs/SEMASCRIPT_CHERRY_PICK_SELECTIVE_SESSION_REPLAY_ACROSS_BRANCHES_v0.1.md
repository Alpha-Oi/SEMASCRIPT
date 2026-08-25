# SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1

## Назначение
Этот документ описывает следующий слой после branch rebase / replay onto target lineage:
**cherry-pick / selective session replay across branches**.

## Что это даёт
Теперь workspace умеет:
- выбрать одну или несколько session entries;
- выбрать target branch;
- replay-ить выбранные sessions как новые commits в target branch;
- сохранять provenance cherry-pick;
- отражать результат в lineage graph и history.

## Что добавлено
- `tooling/project_cherrypick.py`
- `/api/cherry-pick-project-sessions`
- cherry-pick panel in inspector
- `run_cherry_pick_checks.py`
- sample cherry-picked project / result / lineage graph JSON

## Semantics v0.1
Это **selective replay**, а не перенос ссылки на исходный commit.

### Как работает
- выбранные `source_session_ids` replay-ятся в указанном порядке;
- первый cherry-pick commit получает parent = current head target branch;
- следующие cherry-pick commits строятся цепочкой поверх предыдущего cherry-pick;
- новые replay commits живут в `target_branch_name`.

## Provenance
Каждый replay commit получает:
- `commit_kind = cherry_pick`
- `cherry_pick.source_session_id`
- `cherry_pick.source_branch_name`
- `cherry_pick.target_branch_name`
- `cherry_pick.cherry_pick_index`

## History event
- `branch_cherry_picked`
