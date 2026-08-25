# SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1

## Назначение
Этот документ описывает **batch runtime/state corpus pipeline** для SEMASCRIPT v0.1.

Его задача:
- прогонять серию сценариев через runtime;
- прогонять те же сценарии через state model;
- собирать batch-отчёты;
- выявлять системные ошибки не по одному примеру, а по корпусу.

## Что добавлено
- `tooling/run_runtime_corpus.py`
- `tooling/run_state_corpus.py`
- `tooling/run_batch_runtime_state_corpus_checks.py`
- `tooling/corpus/runtime_state_corpus_manifest.json`
- sample runtime/state corpus reports

## Pipeline
1. взять `runtime_state_corpus_manifest.json`
2. для каждого entry:
   - прочитать `profile`
   - запустить runtime
   - при необходимости запустить state model с `initial_state`
3. собрать:
   - runtime batch report
   - state batch report
   - summary counts

## Форматы отчётов
### Runtime batch
- `accepted`
- `plan_length`
- `schedule`
- `invariant_law`
- `errors`
- `notes`

### State batch
- `accepted`
- `history_len`
- `dependency_count`
- `expansion_count`
- `action_count`
- `observation_count`
- `errors`

## Практический смысл
Этот слой переводит runtime/state execution из точечных smoke-тестов в **серийную корпусную проверку**.
