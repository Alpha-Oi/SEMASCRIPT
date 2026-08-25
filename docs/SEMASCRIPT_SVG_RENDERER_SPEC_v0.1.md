# SEMASCRIPT_SVG_RENDERER_SPEC_v0.1

## Назначение
Этот документ описывает **renderer / SVG prototypes** для SEMASCRIPT v0.1.

Его задача:
- визуализировать AST/Core/Exec структуры в SVG;
- проверить читаемость class shapes;
- проверить видимость frame boundaries;
- проверить list-scope layout;
- дать прототипный visual layer без финального glyph-design.

## Что добавлено
- `tooling/svg_renderer.py`
- `tooling/render_to_svg.py`
- `tooling/render_corpus_svgs.py`
- `tooling/run_svg_renderer_checks.py`

## Визуальные принципы v0.1

### Class shapes
- `ENT` -> ellipse
- `PRC` -> triangle
- `STA` -> rectangle
- `REL` -> diamond
- `PAT` -> pentagon-like prototype
- `EXEC` -> hexagon-like prototype
- `IDX` -> point/circle
- `FRM` -> rounded container frame

### Layout
- `north` roles -> above body
- `west` roles -> left
- `east` roles -> right
- `south` roles -> below
- `FRM:*` renders `scp/scope` inside a visible container
- `list-scope` renders as dashed box with stacked items

## Граница v0.1
Это **structural SVG renderer**, а не финальная glyph system.
Он нужен для:
- structural validation,
- visual debugging,
- prototype layout checks.

Он не решает:
- финальную эстетику,
- font system,
- production glyphset,
- compact orthography.
