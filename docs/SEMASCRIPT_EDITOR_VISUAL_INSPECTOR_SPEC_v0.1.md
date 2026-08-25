# SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1

## Назначение
Этот документ описывает **editor / visual inspector** как следующий UI-слой SEMASCRIPT после v0.2 hardening.

## Почему сейчас
Теперь под ним уже есть устойчивый operational contour:
- Human normalizer
- AST
- validation
- pattern decomposition
- runtime
- state model
- batch corpus
- SVG renderer
- hardening regression suite

## Что делает inspector
Inspector объединяет в одном локальном интерфейсе:
1. source input
2. profile selection (`human/core/exec`)
3. optional decomposition
4. initial state JSON
5. normalized text / S-Linear
6. AST view
7. validation view
8. runtime view
9. state view
10. SVG preview

## Что добавлено
- `tooling/inspector_service.py`
- `tooling/inspector_server.py`
- `tooling/run_inspector_smoke_checks.py`
- `inspector/index.html`
- `inspector/app.js`
- `inspector/styles.css`

## Как запускать
```bash
python tooling/inspector_server.py --host 127.0.0.1 --port 8765
```

После этого открыть в браузере:
```text
http://127.0.0.1:8765
```

## Граница v0.1
Это local inspector, а не production multi-user IDE.
Он нужен для:
- engineering inspection,
- visual debugging,
- manual scenario analysis,
- UI validation поверх уже собранной системы.
