# SEMASCRIPT Tooling MVP v0.1 — Grammar Expanded

Это расширенный parser/validator/normalizer bundle для SEMASCRIPT.

## Что уже умеет
- парсить канонические одиночные конструкции;
- парсить list-scope значения:
  ```text
  scp=[[NODE]; [NODE]]
  ```
- валидировать базовые Core правила;
- валидировать минимальный Exec subset;
- нормализовать стандартизированный Human shorthand в Core;
- прогонять expanded fixtures.

## Human normalizer grammar
Поддерживаемые wrappers:
- `spr(...)`
- `gen(...)`
- `pal(...)`
- `state:bal(...)`
- `inv:zsum(...)`
- `inv:nzsum(...)`
- `time:lin(...)`
- `time:cyc(...)`
- `time:brn(...)`
- `time:rec(...)`
- `time:rev(...)`
- `time:atm(...)`

Поддерживаемые scene forms:
- `A -> B : resource`
- `human observes object`
- `human acts on system`
- `system creates resource`
- `system destroys resource`
- `form depends on code`
- `A equals B`
- `resource declines`
- `resource increases`
- `system becomes unstable`
- causal form: `scene1 => scene2`
- multi-scene list: `scene1; scene2`

## Ограничение
Это всё ещё deterministic shorthand normalizer, а не parser свободного естественного языка.

## Environment bootstrap self-check

Read-only check for the current SEMASCRIPT bootstrap contract:

```bash
python tooling/run_environment_bootstrap_checks.py
```

It checks required project files, current Python executable/version, absence or presence of standard dependency manifests, and optional Playwright availability. Missing Playwright is a warning, not a failure, for non-browser tasks.

The broad non-browser hardening suite now runs this self-check before the other checks:

```bash
python tooling/run_v0_2_hardening_suite.py
```

Browser UI checks remain opt-in and separate:

```bash
python tooling/run_inspector_browser_ui_checks.py
```

## Примеры запуска
Проверка Core:
```bash
python validate_cli.py sample_core.txt --mode core
```

Проверка Exec:
```bash
python validate_cli.py sample_exec.txt --mode exec
```

Прогон Core/Exec fixtures:
```bash
python run_fixture_validation.py
```

Прогон Human normalization fixtures:
```bash
python run_human_normalization_checks.py
```

Нормализация shorthand:
```bash
python normalize_cli.py human_sample.txt
```
