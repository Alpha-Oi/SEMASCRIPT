# SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1

## Назначение
Этот документ описывает следующий слой после merge commit / resolved session insertion:
**branching / named merge lineage graph**.

## Что это даёт
Теперь workspace умеет:
- иметь named branches;
- создавать ветку от активной сессии;
- сохранять branch metadata у session entries;
- строить lineage graph с parent / merge-parent edges;
- показывать branch heads и lineage graph в inspector.

## Что добавлено
- `tooling/project_branching.py`
- branching-aware `project_model.py`
- create-branch API in inspector
- branch panel + lineage graph in inspector
- `run_branching_checks.py`
- sample branching project + lineage graph JSON

## Branch metadata
Каждая session entry теперь может нести:
```json
{
  "branching": {
    "branch_name": "main",
    "parent_session_ids": ["..."],
    "lineage_kind": "commit | merge_commit | root"
  }
}
```

## Lineage graph
Graph строится по:
- `branch_name`
- `parent_session_ids`
- `lineage_kind`

Типы ребер:
- `parent`
- `merge_parent`

## Merge commit integration
Merge commit теперь можно направить в named branch.
Committed session попадает в lineage graph как merge node.
