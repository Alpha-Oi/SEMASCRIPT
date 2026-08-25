# SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1

## Статус
Draft visual architecture

## Назначение
Этот документ задаёт начальную архитектуру глифов для SEMASCRIPT.

Его задача:
- построить визуальный слой без разрушения Core;
- стандартизировать shape classes;
- отделить класс формы от корня смысла;
- задать систему модификаторов;
- подготовить базу для SVG / шрифта / редактора.

## Главный принцип
Глиф — это surface-carrier смысла, а не самостоятельный источник семантики.

Визуальный слой вторичен по отношению к Core.

---

## 1. Layered glyph model

Каждый глиф в v0.1 должен рассматриваться как трёхслойный объект:
1. **Class shape**
2. **Semantic root**
3. **Operational markers**

---

## 2. Class shapes

### ENT
Базовая форма: круг / кругоподобная замкнутая фигура

### PRC
Базовая форма: треугольник / направленная острая форма

### STA
Базовая форма: квадрат / прямоугольная устойчивая форма

### REL
Базовая форма: ромб / узловой стык

### MOD
Базовая форма: дуга / малая приставка / надстройка

### FRM
Базовая форма: контейнер / рамка / охватывающий контур

### IDX
Базовая форма: точка / маркер / осевая отметка

---

## 3. Semantic root principle

Внутри class shape должен находиться root-pattern.

Root-pattern:
- не должен ломать читаемость class shape;
- должен быть различим на малом размере;
- должен быть пригоден для сериализации и повторения;
- не должен превращаться в декоративный шум.

---

## 4. Modifier system

### Suggested markers
- `NEG` — диагональный штрих / slash
- `INT` — усилительный дублирующий контур
- `PLR` — множественный маркер / повторная точка
- `UNC` — пунктирный контур
- `NEC` — утолщённый контур
- `POT` — полуконтур / открытая возможность
- `CND` — верхний условный маркер

### Rule
Модификатор не должен скрывать class identity.

---

## 5. Frame markers

### `FRM:TIME`
внешний временной контур или режимный header-marker

### `FRM:INV`
инвариантный замыкающий контур с law marker

### `FRM:CND`
условная рамка с северным заголовком

### `FRM:SCN`
общая сценическая рамка

---

## 6. Spatial composition rules

### Rule G1 — Focus first
Фокус визуально должен быть наиболее считываемым узлом.

### Rule G2 — Scope visibility
Scope должен быть видим не только логически, но и композиционно.

### Rule G3 — Nesting beats proximity
Вложенный блок должен выглядеть вложенным.

### Rule G4 — Modifier attachment must be clear
Должно быть ясно, к чему относится модификатор.

### Rule G5 — Frame boundaries must be readable
Рамка обязана показывать, что входит в её действие.

---

## 7. Visual priorities
1. class identity
2. focus readability
3. frame / scope readability
4. role-supporting layout
5. modifier clarity
6. root distinctiveness
7. aesthetic refinement

---

## 8. Early glyph families

### Core class family
- ENT base
- PRC base
- STA base
- REL base
- MOD base
- FRM base
- IDX base

### Minimal root family
16–32 базовых корня на черновом уровне.

### Modifier family
6–10 служебных маркеров.

### Frame family
4–6 базовых рамок.

---

## 9. Glyph validation checklist

Для каждого глифа проверить:
1. Читается ли его класс?
2. Видно ли отличие от соседних классов?
3. Не съедает ли root-pattern class shape?
4. Можно ли однозначно прицепить модификатор?
5. Можно ли уменьшить знак без потери различимости?
6. Можно ли сериализовать / переиспользовать знак?
7. Не создаёт ли графика скрытую неописанную семантику?

---

## 10. What v0.1 does not finalize
Этот документ не фиксирует:
- финальный художественный стиль;
- полный алфавит;
- готовый шрифт;
- редактор;
- финальную систему stroke-weight;
- финальный orthographic beauty layer.

---

## 11. Criteria of readiness
Glyph Architecture v0.1 можно считать собранной, если:
- shape classes стандартизированы;
- модификаторы разведены;
- рамки имеют понятную композиционную роль;
- есть baseline для SVG / font experiments;
- визуальный слой не противоречит Core semantics.
