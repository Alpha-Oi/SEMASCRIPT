# SEMASCRIPT_AST_INTEGRATION_PACK_v0.1

## Назначение
Этот документ описывает слой интеграции между:
- parser/normalizer text forms
- AST schema
- validator pipeline

## Что добавлено
- `semascript_ast.py`
- `parse_to_ast.py`
- `serialize_ast.py`
- `validate_ast.py`

## Роль
Теперь parser и normalizer могут выдавать не только внутренние Python-структуры, но и канонический AST document JSON, согласованный с `SEMASCRIPT_AST_SCHEMA_v0.1`.

## Главный маршрут
```text
Human/Core/Exec text -> parse/normalize -> AST JSON -> validate -> report
```

## Важный эффект
Это снимает главный текущий разрыв между:
- спецификацией AST
- реальным tooling MVP
