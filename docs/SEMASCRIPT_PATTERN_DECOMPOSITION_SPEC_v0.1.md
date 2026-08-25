# SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1

## Назначение
Этот документ описывает первый слой **pattern decomposition** для SEMASCRIPT.

Его задача:
- переводить pattern macros в Core-compatible forms;
- сделать `SPR / GEN / PAL` пригодными для дальнейшей обработки;
- подготовить переход к executable semantics.

## Что делает decomposition layer

### `PAT:SPR`
Перевод:
```text
[PAT:SPR <core=[ENT:SEED]; res=[ENT:FORM]>]
->
[PRC:EXP <src=[ENT:SEED]; res=[ENT:FORM]>]
```

### `PAT:GEN`
Перевод:
```text
[PAT:GEN <code=[ENT:TEMPLATE]; dst=[ENT:INSTANCE]>]
->
[REL:DEP <dst=[ENT:INSTANCE]; src=[ENT:TEMPLATE]>]
```

### `PAT:PAL`
Перевод:
```text
[PAT:PAL <axis=[IDX:CENTER]; scope=[...]>]
->
[FRM:SCN <axis=[IDX:CENTER]; scp=[...]>]
```

## Архитектурный смысл
Это ещё не полный runtime.
Это **structural decomposition layer**, который:
- убирает pattern macros из operational path;
- сохраняет их смысл в Core-compatible form;
- позволяет validator / corpus pipeline работать дальше уже без PAT nodes в критических местах.

## Граница v0.1
Это decomposition, а не полный semantic proof.
Он не обещает исчерпывающую эквивалентность для всех будущих pattern forms.
