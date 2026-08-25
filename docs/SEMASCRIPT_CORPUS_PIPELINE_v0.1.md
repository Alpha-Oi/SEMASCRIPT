# SEMASCRIPT_CORPUS_PIPELINE_v0.1

## Назначение
Этот документ описывает batch pipeline для corpus обработки.

## Что добавлено
- `normalize_corpus.py`
- `validate_corpus.py`
- `corpus/corpus_manifest.json`
- sample normalized corpus JSON
- sample validation report JSON

## Pipeline
1. взять `corpus_manifest.json`
2. определить profile (`human/core/exec`)
3. если `human` — прогнать normalizer
4. построить AST document
5. прогнать validator
6. записать normalized corpus / validation report

## Выходные форматы
- `SEMASCRIPT_CORPUS_NORMALIZED_v0.1`
- `SEMASCRIPT_CORPUS_REPORT_v0.1`

## Практический смысл
Это переводит систему от одиночных fixtures к batch-проверке корпуса.
