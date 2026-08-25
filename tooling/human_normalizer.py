
from __future__ import annotations

import re


class HumanNormalizationError(Exception):
    """Raised when a Human shorthand cannot be normalized."""


NAME = r'[A-Za-z_][\w-]*(?:\s+[A-Za-z_][\w-]*)*'


def _ent(name: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_]+", "_", name.strip()).upper().strip("_")
    if not token:
        raise HumanNormalizationError("Empty entity token")
    return f"[ENT:{token}]"


def _split_top_level(text: str, sep: str) -> list[str]:
    parts = []
    depth = 0
    current = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)

        if depth == 0 and text.startswith(sep, i):
            parts.append("".join(current).strip())
            current = []
            i += len(sep)
            continue

        current.append(ch)
        i += 1

    parts.append("".join(current).strip())
    return [p for p in parts if p]


def _normalize_state_transition(subject: str, state_word: str) -> str:
    mapping = {
        "stable": "[STA:STB <ctx={ctx}>]",
        "unstable": "[STA:STB {{NEG}} <ctx={ctx}>]",
        "open": "[STA:OPN <ctx={ctx}>]",
        "closed": "[STA:CLS <ctx={ctx}>]",
        "balanced": "[STA:BAL <ctx={ctx}>]",
    }
    key = state_word.lower()
    if key not in mapping:
        raise HumanNormalizationError(f"Unsupported state word: {state_word!r}")
    return mapping[key].format(ctx=_ent(subject))


def _normalize_state_wrapper(wrapper: str, target: str) -> str:
    mapping = {
        "bal": "BAL",
        "stable": "STB",
        "unstable": "STB_NEG",
        "open": "OPN",
        "closed": "CLS",
    }
    key = wrapper.lower()
    if key not in mapping:
        raise HumanNormalizationError(f"Unsupported state wrapper: {wrapper!r}")
    if mapping[key] == "BAL":
        return f"[STA:BAL <ctx={_ent(target)}>]"
    if mapping[key] == "STB":
        return f"[STA:STB <ctx={_ent(target)}>]"
    if mapping[key] == "STB_NEG":
        return f"[STA:STB {{NEG}} <ctx={_ent(target)}>]"
    if mapping[key] == "OPN":
        return f"[STA:OPN <ctx={_ent(target)}>]"
    if mapping[key] == "CLS":
        return f"[STA:CLS <ctx={_ent(target)}>]"
    raise HumanNormalizationError(f"Unsupported state wrapper: {wrapper!r}")


def _normalize_scene(expr: str) -> str:
    expr = expr.strip()

    if not expr:
        raise HumanNormalizationError("Empty scene")

    if expr.startswith("[") and expr.endswith("]"):
        return expr

    causal_parts = _split_top_level(expr, "=>")
    if len(causal_parts) == 2:
        left = _normalize_scene(causal_parts[0])
        right = _normalize_scene(causal_parts[1])
        return f"[REL:CAU <cau={left}; res={right}>]"
    elif len(causal_parts) > 2:
        raise HumanNormalizationError(f"Unsupported chained causality: {expr!r}")

    # canonical transfer shorthand
    m = re.fullmatch(fr'({NAME})\s*->\s*({NAME})\s*:\s*({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:TRF <src={_ent(m.group(1))}; dst={_ent(m.group(2))}; obj={_ent(m.group(3))}>]"

    # natural transfer aliases
    m = re.fullmatch(fr'({NAME})\s+gives\s+({NAME})\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:TRF <src={_ent(m.group(1))}; dst={_ent(m.group(2))}; obj={_ent(m.group(3))}>]"

    m = re.fullmatch(fr'({NAME})\s+transfers\s+({NAME})\s+to\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:TRF <src={_ent(m.group(1))}; dst={_ent(m.group(3))}; obj={_ent(m.group(2))}>]"

    m = re.fullmatch(fr'({NAME})\s+returns\s+({NAME})\s+to\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:TRF <src={_ent(m.group(1))}; dst={_ent(m.group(3))}; obj={_ent(m.group(2))}>]"

    # observes
    m = re.fullmatch(fr'({NAME})\s+observes\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:OBS <agt={_ent(m.group(1))}; obj={_ent(m.group(2))}>]"

    # acts on
    m = re.fullmatch(fr'({NAME})\s+acts?\s+on\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:ACT <agt={_ent(m.group(1))}; obj={_ent(m.group(2))}>]"

    # creates
    m = re.fullmatch(fr'({NAME})\s+creates\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:CRT <dst={_ent(m.group(1))}; obj={_ent(m.group(2))}>]"

    # destroys
    m = re.fullmatch(fr'({NAME})\s+destroys\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:DST <ctx={_ent(m.group(1))}; obj={_ent(m.group(2))}>]"

    # depends on
    m = re.fullmatch(fr'({NAME})\s+depends\s+on\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[REL:DEP <dst={_ent(m.group(1))}; src={_ent(m.group(2))}>]"

    # equals
    m = re.fullmatch(fr'({NAME})\s+equals\s+({NAME})', expr, flags=re.IGNORECASE)
    if m:
        return f"[REL:EQU <left={_ent(m.group(1))}; right={_ent(m.group(2))}>]"

    # changes
    m = re.fullmatch(fr'({NAME})\s+changes?', expr, flags=re.IGNORECASE)
    if m:
        return f"[PRC:CHG <obj={_ent(m.group(1))}>]"

    # declines / decreases
    m = re.fullmatch(fr'({NAME})\s+(declines?|decreases?)', expr, flags=re.IGNORECASE)
    if m:
        return f"[STA:DEC <ctx={_ent(m.group(1))}>]"

    # increases / grows
    m = re.fullmatch(fr'({NAME})\s+(increases?|grows?)', expr, flags=re.IGNORECASE)
    if m:
        return f"[STA:INC <ctx={_ent(m.group(1))}>]"

    # becomes state
    m = re.fullmatch(fr'({NAME})\s+becomes\s+(stable|unstable|open|closed|balanced)', expr, flags=re.IGNORECASE)
    if m:
        return _normalize_state_transition(m.group(1), m.group(2))

    # stabilizes
    m = re.fullmatch(fr'({NAME})\s+stabilizes?', expr, flags=re.IGNORECASE)
    if m:
        return f"[STA:STB <ctx={_ent(m.group(1))}>]"

    raise HumanNormalizationError(f"Unsupported scene shorthand: {expr!r}")


def _normalize_scope(expr: str) -> str:
    parts = _split_top_level(expr, ";")
    if len(parts) == 1:
        return _normalize_scene(parts[0])

    normalized = [_normalize_scene(part) for part in parts]
    return "[" + "; ".join(normalized) + "]"


def normalize(text: str) -> str:
    s = text.strip()

    m = re.fullmatch(fr'spr\(\s*({NAME})\s*->\s*({NAME})\s*\)', s, flags=re.IGNORECASE)
    if m:
        return f"[PAT:SPR <core={_ent(m.group(1))}; res={_ent(m.group(2))}>]"

    m = re.fullmatch(fr'gen\(\s*({NAME})\s*->\s*({NAME})\s*\)', s, flags=re.IGNORECASE)
    if m:
        return f"[PAT:GEN <code={_ent(m.group(1))}; dst={_ent(m.group(2))}>]"

    m = re.fullmatch(fr'pal\(\s*(.+)\s*\)', s, flags=re.IGNORECASE)
    if m:
        scope = _normalize_scope(m.group(1))
        return f"[PAT:PAL <axis=[IDX:CENTER]; scope={scope}>]"

    m = re.fullmatch(fr'state:(bal|stable|unstable|open|closed)\(\s*({NAME})\s*\)', s, flags=re.IGNORECASE)
    if m:
        return _normalize_state_wrapper(m.group(1), m.group(2))

    m = re.fullmatch(fr'inv:zsum\(\s*(.+)\s*\)', s, flags=re.IGNORECASE)
    if m:
        scope = _normalize_scope(m.group(1))
        return f"[FRM:INV <law=ZSUM; scp={scope}>]"

    m = re.fullmatch(fr'inv:nzsum\(\s*(.+)\s*\)', s, flags=re.IGNORECASE)
    if m:
        scope = _normalize_scope(m.group(1))
        return f"[FRM:INV <law=NZSUM; scp={scope}>]"

    m = re.fullmatch(fr'time:(lin|cyc|brn|rec|rev|atm)\(\s*(.+)\s*\)', s, flags=re.IGNORECASE)
    if m:
        mode = m.group(1).upper()
        scope = _normalize_scope(m.group(2))
        return f"[FRM:TIME <mode={mode}; scp={scope}>]"

    # direct scene form is allowed in v0.2 hardening
    return _normalize_scene(s)
