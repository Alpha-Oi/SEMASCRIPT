
# SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после resolution set export / import as standalone promoted outcome package:
**standalone outcome package diff / compatibility check before import**.

## Что это даёт
Теперь система умеет:
- взять текущий workspace;
- взять standalone promoted outcome package;
- построить dry-run preview before import;
- показать compatibility и conflict-like сигналы до apply-import.

## Что добавлено
- `tooling/project_snapshot_reconcile_commit_package_preview.py`
- package-preview aware `project_model.py`
- `/api/preview-snapshot-reconcile-commit-package-import`
- preview button in standalone package import panel
- `run_snapshot_reconcile_commit_package_preview_checks.py`
- sample standalone package preview result JSON

## Preview semantics v0.1
Это **non-mutating package import preview**.

### Что проверяется
- package version support
- import name availability
- target branch existence / branch creation need
- promoted point collision
- per-session compatibility vs current target head chain
- conflict-like divergence by `source_text`

### Что возвращается
- `import_target`
- `metadata`
- `collections`
- `compatibility`
- `preview_items`
- `summary`

Preview не изменяет workspace и не пишет history.
