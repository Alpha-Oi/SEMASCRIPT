# SEMASCRIPT_GRAMMAR_EXPANSION_v0.1

## Назначение
Этот документ описывает расширение grammar слоя для parser/validator/normalizer.

## Что добавлено

### 1. List-scope syntax
Теперь parser поддерживает list-scope конструкции вида:
```text
[FRM:INV <law=ZSUM; scp=[[PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]; [PRC:TRF <src=[ENT:B]; dst=[ENT:C]; obj=[ENT:CREDIT]>]]>]
```

Это позволяет:
- задавать несколько сцен внутри `scp`;
- собирать multi-scene временные и инвариантные рамки;
- делать scope-list внутри pattern forms.

### 2. Expanded Human scene grammar
Human normalizer теперь поддерживает:
- transfer scene
- observe scene
- act-on scene
- create scene
- destroy scene
- dependency scene
- equality scene
- decline/increase states
- becomes-state transitions
- causal shorthand через `=>`
- multi-scene scope через `;`

### 3. MVP boundary
Расширение grammar не превращает систему в freeform natural-language parser.
Всё ещё поддерживается только стандартизированный shorthand.

## Архитектурный смысл
Это расширение важно, потому что:
- делает `scp` пригодным для реальных сценических блоков;
- усиливает Human → Core bridge;
- готовит систему к batch corpus normalization;
- приближает grammar к реальным use-case, а не только к toy examples.

## Что остаётся следующим шагом
- richer nested list semantics;
- batch normalizer for corpus files;
- parser support for broader literal/value types;
- deeper executable mapping for decomposed patterns.
