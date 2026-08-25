# SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1

## Назначение
Этот документ описывает следующий слой после workspace timeline / session evolution history:
**cross-session compare / diff mode**.

## Что это даёт
Теперь project workspace умеет не только:
- хранить и переключать сессии,
- строить dependency map,
- показывать timeline,

но и:
- сравнивать две выбранные сессии напрямую,
- видеть структурные и execution-различия,
- сравнивать сущности, inputs/outputs, runtime-операции и state metrics.

## Что добавлено
- `tooling/session_diff.py`
- `/api/compare-project-sessions` in inspector server
- compare panel in inspector UI
- `run_cross_session_compare_checks.py`
- sample compare sessions / project / diff JSON

## Что сравнивается v0.1
### Identity
- `profile`
- `source_mode`

### Structure
- `slinear`
- `decomposed_slinear`
- `entities`
- `inputs`
- `outputs`
- `state_nodes`

### Execution
- `runtime_accepted`
- `state_accepted`
- `runtime_ops`
- `dependency_count`
- `expansion_count`
- `action_count`
- `observation_count`
- `history_len`

## Граница v0.1
Это уже полезный engineering diff,
но ещё не semantic theorem prover и не three-way merge.
