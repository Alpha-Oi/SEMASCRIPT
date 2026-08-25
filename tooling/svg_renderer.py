
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import html
import json

from human_normalizer import normalize
from semascript_ast import load_ast_document, text_to_ast_document
from pattern_decomposer import decompose_ast_document


ASTValue = Dict[str, Any]
ASTNode = Dict[str, Any]


NORTH_ROLES = {"time", "tim", "mode", "law", "ctx", "axis"}
WEST_ROLES = {"src", "agt", "cau", "code", "left"}
EAST_ROLES = {"dst", "obj", "res", "dep", "right"}
FRAME_SCOPE_ROLES = {"scp", "scope"}


@dataclass
class Layout:
    width: float
    height: float
    anchor_x: float
    anchor_y: float


def _text_w(text: str, size: int = 12) -> float:
    return max(18.0, len(text) * (size * 0.58))


def _esc(text: str) -> str:
    return html.escape(str(text))


def _shape_dims(class_name: str) -> Tuple[float, float]:
    if class_name == "ENT":
        return 90, 56
    if class_name == "PRC":
        return 110, 64
    if class_name == "STA":
        return 108, 58
    if class_name == "REL":
        return 108, 64
    if class_name == "PAT":
        return 118, 66
    if class_name == "EXEC":
        return 118, 64
    if class_name == "IDX":
        return 56, 40
    return 110, 60


def _zone(role: str) -> str:
    if role in NORTH_ROLES:
        return "north"
    if role in WEST_ROLES:
        return "west"
    if role in EAST_ROLES:
        return "east"
    return "south"


def _measure_value(value: ASTValue) -> Layout:
    kind = value["kind"]
    if kind == "node":
        return _measure_node(value)
    if kind == "list":
        items = value["items"]
        if not items:
            return Layout(80, 40, 40, 20)
        inner = [_measure_value(item) for item in items]
        width = max(l.width for l in inner) + 24
        height = sum(l.height for l in inner) + (len(inner) - 1) * 16 + 32
        return Layout(width, height, width / 2, 18)
    if kind == "typed_literal":
        label = f"{value['class_name']}:{value['root']}"
        w = _text_w(label, 12) + 24
        h = 34
        return Layout(w, h, w / 2, h / 2)
    if kind == "raw_token":
        w = _text_w(value["value"], 12) + 20
        h = 30
        return Layout(w, h, w / 2, h / 2)
    return Layout(80, 40, 40, 20)


def _measure_stack(role_entries: List[dict]) -> Tuple[float, float]:
    if not role_entries:
        return 0.0, 0.0
    child_layouts = [_measure_value(entry["value"]) for entry in role_entries]
    width = max(layout.width + _text_w(entry["name"], 11) + 18 for layout, entry in zip(child_layouts, role_entries))
    height = sum(layout.height for layout in child_layouts) + (len(child_layouts) - 1) * 14
    return width, height


def _measure_frame(node: ASTNode) -> Layout:
    roles = node.get("roles", [])
    scope_entry = None
    chips = []
    for entry in roles:
        if entry["name"] in FRAME_SCOPE_ROLES:
            scope_entry = entry
        else:
            chips.append(entry)

    scope_layout = _measure_value(scope_entry["value"]) if scope_entry else Layout(120, 48, 60, 24)
    chip_height = 24 if chips else 0
    chip_width = 0
    if chips:
        chip_width = sum(_text_w(f"{e['name']}={_value_label(e['value'])}", 11) + 18 for e in chips) + max(0, len(chips) - 1) * 8

    width = max(260, scope_layout.width + 40, chip_width + 24)
    height = 38 + chip_height + 16 + scope_layout.height + 20
    return Layout(width, height, width / 2, 18)


def _measure_node(node: ASTNode) -> Layout:
    if node["class_name"] == "FRM":
        return _measure_frame(node)

    body_w, body_h = _shape_dims(node["class_name"])
    roles = node.get("roles", [])
    north = [r for r in roles if _zone(r["name"]) == "north"]
    west = [r for r in roles if _zone(r["name"]) == "west"]
    east = [r for r in roles if _zone(r["name"]) == "east"]
    south = [r for r in roles if _zone(r["name"]) == "south"]

    north_w, north_h = _measure_stack(north)
    west_w, west_h = _measure_stack(west)
    east_w, east_h = _measure_stack(east)
    south_w, south_h = _measure_stack(south)

    mid_h = max(body_h, west_h, east_h)
    width = west_w + (18 if west_w else 0) + body_w + (18 if east_w else 0) + east_w
    width = max(width, north_w, south_w, body_w)
    height = north_h + (18 if north_h else 0) + mid_h + (18 if south_h else 0) + south_h
    return Layout(width, height, width / 2, north_h + (18 if north_h else 0) + mid_h / 2)


def _value_label(value: ASTValue) -> str:
    kind = value["kind"]
    if kind == "raw_token":
        return value["value"]
    if kind == "typed_literal":
        return f"{value['class_name']}:{value['root']}"
    if kind == "node":
        return f"{value['class_name']}:{value['root']}"
    if kind == "list":
        return "list"
    return "value"


def _render_shape(node: ASTNode, x: float, y: float, w: float, h: float) -> List[str]:
    class_name = node["class_name"]
    cx = x + w / 2
    cy = y + h / 2
    lines: List[str] = []

    if class_name == "ENT":
        r = min(w, h) / 2 - 2
        lines.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{(w/2-2):.1f}" ry="{(h/2-2):.1f}" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "PRC":
        points = f"{x+w/2:.1f},{y+2:.1f} {x+w-2:.1f},{y+h-2:.1f} {x+2:.1f},{y+h-2:.1f}"
        lines.append(f'<polygon points="{points}" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "STA":
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" ry="6" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "REL":
        points = f"{cx:.1f},{y+2:.1f} {x+w-2:.1f},{cy:.1f} {cx:.1f},{y+h-2:.1f} {x+2:.1f},{cy:.1f}"
        lines.append(f'<polygon points="{points}" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "PAT":
        points = f"{cx:.1f},{y+2:.1f} {x+w-4:.1f},{y+h*0.36:.1f} {x+w*0.82:.1f},{y+h-2:.1f} {x+w*0.18:.1f},{y+h-2:.1f} {x+4:.1f},{y+h*0.36:.1f}"
        lines.append(f'<polygon points="{points}" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "EXEC":
        points = f"{x+12:.1f},{y+2:.1f} {x+w-12:.1f},{y+2:.1f} {x+w-2:.1f},{cy:.1f} {x+w-12:.1f},{y+h-2:.1f} {x+12:.1f},{y+h-2:.1f} {x+2:.1f},{cy:.1f}"
        lines.append(f'<polygon points="{points}" fill="white" stroke="black" stroke-width="1.5"/>')
    elif class_name == "IDX":
        lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{min(w,h)/4:.1f}" fill="white" stroke="black" stroke-width="1.5"/>')
    else:
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" ry="10" fill="white" stroke="black" stroke-width="1.5"/>')
    return lines


def _render_text_center(text: str, x: float, y: float, size: int = 12, weight: str = "normal") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="sans-serif" font-size="{size}" font-weight="{weight}">{_esc(text)}</text>'


def _render_value(value: ASTValue, x: float, y: float, elements: List[str]) -> Layout:
    kind = value["kind"]
    layout = _measure_value(value)

    if kind == "node":
        return _render_node(value, x, y, elements)

    if kind == "list":
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{layout.width:.1f}" height="{layout.height:.1f}" rx="8" ry="8" fill="none" stroke="black" stroke-dasharray="5,4" stroke-width="1.2"/>')
        elements.append(_render_text_center("list-scope", x + layout.width / 2, y + 15, 11, "bold"))
        cy = y + 24
        for item in value["items"]:
            item_layout = _measure_value(item)
            item_x = x + (layout.width - item_layout.width) / 2
            _render_value(item, item_x, cy, elements)
            cy += item_layout.height + 16
        return Layout(layout.width, layout.height, layout.anchor_x, layout.anchor_y)

    if kind == "typed_literal":
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{layout.width:.1f}" height="{layout.height:.1f}" rx="6" ry="6" fill="white" stroke="black" stroke-width="1.2"/>')
        elements.append(_render_text_center(_value_label(value), x + layout.width / 2, y + layout.height / 2 + 4, 11))
        return layout

    if kind == "raw_token":
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{layout.width:.1f}" height="{layout.height:.1f}" rx="6" ry="6" fill="white" stroke="black" stroke-width="1.0" stroke-dasharray="3,2"/>')
        elements.append(_render_text_center(value["value"], x + layout.width / 2, y + layout.height / 2 + 4, 11))
        return layout

    return layout


def _render_stack(role_entries: List[dict], x: float, y: float, elements: List[str], parent_anchor: Tuple[float, float], align: str = "left") -> Tuple[float, float]:
    if not role_entries:
        return 0.0, 0.0
    cy = y
    max_w = 0.0
    for entry in role_entries:
        child_layout = _measure_value(entry["value"])
        child_x = x if align == "left" else x - child_layout.width
        rendered = _render_value(entry["value"], child_x, cy, elements)
        child_anchor = (child_x + rendered.anchor_x, cy + rendered.anchor_y)
        elements.append(f'<line x1="{parent_anchor[0]:.1f}" y1="{parent_anchor[1]:.1f}" x2="{child_anchor[0]:.1f}" y2="{child_anchor[1]:.1f}" stroke="black" stroke-width="1.1"/>')
        lx = (parent_anchor[0] + child_anchor[0]) / 2
        ly = (parent_anchor[1] + child_anchor[1]) / 2 - 4
        elements.append(_render_text_center(entry["name"], lx, ly, 10))
        cy += rendered.height + 14
        max_w = max(max_w, rendered.width + _text_w(entry["name"], 10) + 12)
    return max_w, cy - y - 14 if role_entries else 0.0


def _render_frame(node: ASTNode, x: float, y: float, elements: List[str]) -> Layout:
    layout = _measure_frame(node)
    roles = node.get("roles", [])
    scope_entry = None
    chips = []
    for entry in roles:
        if entry["name"] in FRAME_SCOPE_ROLES:
            scope_entry = entry
        else:
            chips.append(entry)

    elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{layout.width:.1f}" height="{layout.height:.1f}" rx="14" ry="14" fill="white" stroke="black" stroke-width="1.6"/>')
    header = f"{node['class_name']}:{node['root']}"
    elements.append(_render_text_center(header, x + layout.width / 2, y + 22, 13, "bold"))

    chip_y = y + 32
    chip_x = x + 12
    if chips:
        for chip in chips:
            label = f"{chip['name']}={_value_label(chip['value'])}"
            cw = _text_w(label, 10) + 16
            elements.append(f'<rect x="{chip_x:.1f}" y="{chip_y:.1f}" width="{cw:.1f}" height="18" rx="8" ry="8" fill="white" stroke="black" stroke-width="1.0"/>')
            elements.append(_render_text_center(label, chip_x + cw / 2, chip_y + 13, 10))
            chip_x += cw + 8
        scope_top = chip_y + 28
    else:
        scope_top = y + 42

    if scope_entry:
        scope_layout = _measure_value(scope_entry["value"])
        scope_x = x + (layout.width - scope_layout.width) / 2
        _render_value(scope_entry["value"], scope_x, scope_top, elements)
        elements.append(_render_text_center(scope_entry["name"], x + 32, scope_top - 6, 10))
    return layout


def _render_node(node: ASTNode, x: float, y: float, elements: List[str]) -> Layout:
    if node["class_name"] == "FRM":
        return _render_frame(node, x, y, elements)

    layout = _measure_node(node)
    body_w, body_h = _shape_dims(node["class_name"])
    roles = node.get("roles", [])
    north = [r for r in roles if _zone(r["name"]) == "north"]
    west = [r for r in roles if _zone(r["name"]) == "west"]
    east = [r for r in roles if _zone(r["name"]) == "east"]
    south = [r for r in roles if _zone(r["name"]) == "south"]

    north_w, north_h = _measure_stack(north)
    west_w, west_h = _measure_stack(west)
    east_w, east_h = _measure_stack(east)
    south_w, south_h = _measure_stack(south)

    top_gap = 18 if north_h else 0
    bottom_gap = 18 if south_h else 0
    mid_h = max(body_h, west_h, east_h)
    body_x = x + west_w + (18 if west_w else 0) + (layout.width - (west_w + (18 if west_w else 0) + body_w + (18 if east_w else 0) + east_w)) / 2
    body_y = y + north_h + top_gap + (mid_h - body_h) / 2

    elements.extend(_render_shape(node, body_x, body_y, body_w, body_h))
    header = f"{node['class_name']}:{node['root']}"
    elements.append(_render_text_center(header, body_x + body_w / 2, body_y + body_h / 2 - 4, 12, "bold"))
    if node.get("modifiers"):
        elements.append(_render_text_center("{" + " ".join(node["modifiers"]) + "}", body_x + body_w / 2, body_y + body_h / 2 + 12, 10))

    parent_anchor = (body_x + body_w / 2, body_y + body_h / 2)

    if north:
        north_block_x = x + (layout.width - north_w) / 2
        _render_stack(north, north_block_x, y, elements, parent_anchor, "left")
    if west:
        west_y = y + north_h + top_gap + (mid_h - west_h) / 2
        _render_stack(west, x, west_y, elements, parent_anchor, "left")
    if east:
        east_y = y + north_h + top_gap + (mid_h - east_h) / 2
        _render_stack(east, x + layout.width, east_y, elements, parent_anchor, "right")
    if south:
        south_y = y + north_h + top_gap + mid_h + bottom_gap
        south_block_x = x + (layout.width - south_w) / 2
        _render_stack(south, south_block_x, south_y, elements, parent_anchor, "left")

    return layout


def render_svg_from_ast_document(doc: Dict[str, Any], width: Optional[int] = None, height: Optional[int] = None, padding: int = 24) -> str:
    ast = doc["ast"]
    layout = _measure_value(ast)
    canvas_w = int(width or (layout.width + padding * 2))
    canvas_h = int(height or (layout.height + padding * 2))
    elements: List[str] = []
    _render_value(ast, padding, padding, elements)

    header = ""
    if doc.get("source_text"):
        header = f'<text x="{padding}" y="16" font-family="sans-serif" font-size="10">{_esc(doc.get("source_profile", "unknown"))}</text>'

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        header,
        *elements,
        '</svg>',
    ]
    return "\n".join(svg)


def render_svg_from_text(text: str, profile: str = "core", decompose: bool = False) -> str:
    normalized = normalize(text) if profile == "human" else text
    doc = text_to_ast_document(
        normalized,
        source_profile="normalized" if profile == "human" else profile,
        source_text=text,
    )
    if profile == "human":
        doc["metadata"]["normalized_text"] = normalized
    if decompose:
        doc = decompose_ast_document(doc)
    return render_svg_from_ast_document(doc)


def render_svg_from_ast_file(path: str | Path) -> str:
    doc = load_ast_document(path)
    return render_svg_from_ast_document(doc)


def save_svg(svg: str, path: str | Path) -> None:
    Path(path).write_text(svg, encoding="utf-8")
