# SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1

## Назначение
Этот документ описывает Human normalizer MVP и его grammar-expanded версию.

## Что он делает
Human normalizer:
1. принимает стандартизированный Human shorthand;
2. переводит его в Core form;
3. подаёт результат в parser/validator pipeline.

## Поддерживаемые wrappers
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `state:bal(...)`
- `inv:zsum(...)`
- `inv:nzsum(...)`
- `time:*`

## Поддерживаемые scene forms
- transfer
- observe
- act-on
- create
- destroy
- dependency
- equality
- decline / increase
- becomes-state
- causality via `=>`
- multi-scene via `;`

## Граница MVP
Это не parser свободного русского или английского текста.
Это deterministic shorthand normalizer.

## Практический смысл
Нормализатор уже позволяет:
- писать короткие Human forms;
- получать из них валидный Core;
- проверять их через tooling MVP;
- расширять corpus без ручной переписи каждого кейса.
