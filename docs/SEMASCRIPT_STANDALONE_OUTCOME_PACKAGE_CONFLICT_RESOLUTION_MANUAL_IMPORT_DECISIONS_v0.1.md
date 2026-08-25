
# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после standalone outcome package diff / compatibility check before import:
**standalone outcome package conflict resolution / manual import decisions**.

## Что это даёт
Теперь portable outcome package import умеет не только:
- preview-ить compatibility,
- показать conflict-like cases before import,

но и:
- принять manual decisions per packaged resolved session,
- materialize resolved package-import commits,
- встроить их в current workspace lineage,
- зафиксировать decision provenance и историю.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_resolution.py`
- resolution-aware `project_model.py`
- `/api/resolve-snapshot-reconcile-commit-package-import`
- manual decision controls in inspector package import panel
- `run_snapshot_reconcile_commit_package_resolution_checks.py`
- sample package resolution result JSON

## Decision model v0.1
Поддерживаются решения:
- `use_package`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое применённое решение создаёт либо:
- новый resolved package-import commit,
- либо skip without commit.

## Provenance
Resolved imported commits получают:
- `commit_kind = snapshot_reconcile_commit_package_import_resolution`
- `snapshot_reconcile_commit_package_import_resolution.resolution_name`
- `snapshot_reconcile_commit_package_import_resolution.decision_choice`
- `snapshot_reconcile_commit_package_import_resolution.resolved_with_head_session_id`
- `snapshot_reconcile_commit_package_import_resolution.conflict_like`

## История
Добавлен history event:
- `snapshot_reconcile_commit_package_import_resolved`
