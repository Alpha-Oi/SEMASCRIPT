
# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1

## Назначение
Этот документ описывает следующий слой после portable local outcome package diff / compatibility check before import:
**portable local outcome package conflict resolution / manual import decisions**.

## Что это даёт
Теперь portable local outcome package import можно не только preview-ить, но и применять через manual decisions per packaged session.

## Decision model
Поддерживаются решения:
- `use_package`
- `use_current`
- `skip`
- `custom_text`

## Семантика
Каждое решение materialize-ится как новый:
- `commit_kind = local_outcome_set_package_import_resolution`

Результат сохраняется в registry:
- `local_outcome_set_package_resolutions`

## История
Добавлен history event:
- `local_outcome_set_package_import_resolved`
