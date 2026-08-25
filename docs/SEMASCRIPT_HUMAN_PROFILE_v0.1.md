# SEMASCRIPT_HUMAN_PROFILE_v0.1

## Статус
Draft communicative profile

## Назначение
Этот документ задаёт **Human Mode** для SEMASCRIPT.

Его задача:
- сделать язык пригодным для человеческого чтения и записи;
- разрешить контролируемую компрессию;
- определить допустимые сокращения;
- удержать границу между выразительностью и хаосом;
- обеспечить Human → Core проекцию.

## Главный принцип
Human Mode может быть компактнее Core, но не может вводить смысл, который нельзя восстановить в Core.

---

## 1. Роль Human Mode
Human Mode нужен для:
- быстрых сообщений;
- концептуальных записей;
- причинно-следственных схем;
- структурного общения;
- образовательных и проектных заметок;
- наглядной работы с pattern / time / invariant logic.

Он не предназначен для:
- окончательной семантической истины;
- замены Core;
- прямого исполнения.

---

## 2. Что Human Mode разрешает

### 2.1 Compression
Разрешено:
- сокращать повторяющиеся элементы;
- опускать очевидные типы;
- заменять канонические формы человекочитаемыми шаблонами;
- использовать стрелки, краткие маркеры, фокусные слова.

### 2.2 Recoverable omission
Разрешено опускать только то, что:
- восстанавливается из общего grammar;
- однозначно выводится из ближайшего контекста;
- не влияет на critical scope.

### 2.3 Emphasis
Разрешено:
- выделение фокуса;
- акцент;
- тематическое сжатие;
- маркировка важности;
- surface shorthand для уже стандартизированных паттернов.

### 2.4 Pattern shorthand
Разрешены shorthand-формы для:
- `SPR`
- `GEN`
- `PAL`
- `TIME:*`
- `ZSUM / NZSUM / BAL`

Но только если они стандартизированы и читаемы.

---

## 3. Что Human Mode запрещает

### 3.1 Unrecoverable ambiguity
Запрещено:
- писать так, что роль нельзя восстановить;
- смешивать несколько смыслов без markers;
- опираться только на интуитивную картинку.

### 3.2 Decorative-only glyphs
Нельзя использовать символ, если он:
- не маппится в Core;
- не имеет scope;
- не имеет понятной роли.

### 3.3 Human metaphor as Core fact
Нельзя выдавать метафору за каноническую семантику.

### 3.4 Direct executability by implication
Human Mode не имеет права “как бы автоматически” считаться исполнимым.

---

## 4. Допустимые surface-стратегии

### 4.1 Arrow notation
Примеры:
```text
A -> B
A => B
A <-> B
```

Допустимо, если роль легко восстанавливается:
- `->` обычно = transfer / direction
- `=>` обычно = causal or logical implication
- `<->` обычно = equivalence / mutual relation

### 4.2 Focus-first fragments
Пример:
```text
focus: resource transfer, zero-sum
```

### 4.3 Layered shorthand
Примеры:
```text
cycle(system)
zsum(A->B:res)
spr(seed -> form)
gen(template -> instance)
```

### 4.4 Structured prose
Допустима компактная фраза:
```text
system enters cyclical change under zero-sum transfer of resource
```

---

## 5. Human markers v0.1

### Recommended shorthand markers
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `time:lin`
- `time:cyc`
- `time:brn`
- `time:rec`
- `time:rev`
- `time:atm`
- `inv:zsum`
- `inv:nzsum`
- `state:bal`

### Examples
```text
spr(seed -> form)
gen(template -> module)
time:cyc(system change)
inv:zsum(A -> B : resource)
state:bal(system)
```

---

## 6. Human → Core projection rules

### Rule H1 — Focus reconstruction
У каждой Human-записи должен восстанавливаться один основной фокус.

### Rule H2 — Missing types may be restored only if obvious
Если из Human surface ясно, что `A` и `B` — сущности, тип `ENT` можно восстановить.

### Rule H3 — Scope must become explicit in Core
Даже если в Human scope намечен интуитивно, в Core он должен стать явным.

### Rule H4 — Pattern shorthand expands to pattern layer
`spr(...)`, `gen(...)`, `pal(...)` не превращаются напрямую в Exec; сначала они переходят в pattern layer/Core-compatible form.

### Rule H5 — Temporal and invariant hints must be normalized
`cycle(...)` → `FRM:TIME <mode=CYC; ...>`
`zero-sum(...)` → `FRM:INV <law=ZSUM; ...>`

---

## 7. Ambiguity limits

Human Mode допускает ограниченную двусмысленность только если она:
- не меняет тип конструкции;
- не ломает фокус;
- не ломает critical scope;
- не мешает восстановлению канонической формы.

Допустимая двусмысленность:
- стилистическая;
- риторическая;
- поверхностная.

Недопустимая двусмысленность:
- role ambiguity;
- scope ambiguity;
- focus ambiguity;
- class confusion;
- pattern/invariant/time confusion.

---

## 8. Examples

### Example H-1
**Human**
```text
A gives B resource, no net gain
```

**Core**
```text
[FRM:INV <law=ZSUM; scp=[
  [PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]
]>]
```

### Example H-2
**Human**
```text
system loops again
```

**Core**
```text
[FRM:TIME <mode=CYC; scp=[PRC:CHG <obj=[ENT:SYS]>]>]
```

### Example H-3
**Human**
```text
spr(seed -> form)
```

**Core**
```text
[PAT:SPR <core=[ENT:SEED]; res=[ENT:FORM]>]
```

### Example H-4
**Human**
```text
gen(template -> instance)
```

**Core**
```text
[PAT:GEN <code=[ENT:TEMPLATE]; dst=[ENT:INSTANCE]>]
```

### Example H-5
**Human**
```text
balanced system
```

**Core**
```text
[STA:BAL <ctx=[ENT:SYS]>]
```

---

## 9. Human-only constructs not allowed into Core as-is

Следующие формы нельзя переносить в Core без нормализации:
- purely poetic metaphors;
- free mystical symbols;
- undeclared surface axes;
- vague “energy-like” language without typed referents;
- emotional emphasis that changes semantics.

---

## 10. Criteria of readiness

Human Profile v0.1 можно считать рабочим, если:
- есть стабильный набор shorthand;
- есть projection rules;
- есть ambiguity limits;
- есть примеры Human → Core;
- записи Human Mode реально удобнее Core для человека, не ломая семантику.
