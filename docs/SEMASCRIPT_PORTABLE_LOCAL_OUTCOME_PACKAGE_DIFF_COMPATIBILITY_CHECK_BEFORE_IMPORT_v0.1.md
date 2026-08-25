# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1

## Назначение
Этот документ описывает следующий слой после local outcome set export / import as portable local promoted resolution package:
**portable local outcome package diff / compatibility check before import**.

## Что это даёт
Теперь portable local outcome package можно preview-ить до import:
- проверить совместимость версии;
- увидеть target branch;
- увидеть конфликты import name / promoted point;
- получить per-session compatibility preview;
- оценить conflict-like риск до import apply.

## Что добавлено
- `tooling/project_local_outcome_set_package_preview.py`
- preview-aware `project_model.py`
- `/api/preview-local-outcome-set-package-import`
- preview button/output in inspector
- `run_local_outcome_set_package_preview_checks.py`
- sample preview result/package JSON

## Preview semantics
Это **non-mutating preview**:
- history не пишется
- registry import не создаётся
- workspace не меняется
- возвращается только compatibility + diff preview
