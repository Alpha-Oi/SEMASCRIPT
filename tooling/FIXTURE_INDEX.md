# SEMASCRIPT_FIXTURE_INDEX_v0.1

## Назначение
Этот документ описывает fixture-набор для grammar-expanded tooling bundle.

## Наборы
- `core_positive.json` — 16 валидных Core-конструкций
- `core_negative.json` — 14 невалидных Core-конструкций
- `exec_positive.json` — 8 валидных Exec-конструкций
- `exec_negative.json` — 9 невалидных Exec-конструкций
- `human_normalization_positive.json` — 10 валидных Human shorthand cases
- `human_normalization_negative.json` — 5 невалидных Human shorthand cases

## Что добавлено в grammar expansion
- list-scope syntax:
  ```text
  scp=[[NODE]; [NODE]]
  ```
- более сложные scene shorthands для normalizer-а;
- causal scene form через `=>`;
- multiple scene blocks через `;`.

## Что покрыто
- `FRM:INV` с multi-scene scope
- `FRM:TIME` с multi-scene scope
- `PAT:PAL` со scope-list
- `creates`, `destroys`, `depends on`, `equals`
- `declines`, `becomes unstable/stable/open/closed/balanced`
- human shorthand normalization для multi-scene wrappers
