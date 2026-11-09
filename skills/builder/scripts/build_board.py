#!/usr/bin/env python3
"""Compile a compact diagram specification into an editable OpenBoard file."""

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

from render_preview import render_svg
from route_connections import label_position, route_connection, validate_arrow_clearance

SHAPES = {"rectangle", "ellipse", "diamond", "frame", "code"}
STROKES = {"line", "arrow", "freehand"}
TYPES = SHAPES | STROKES | {"text"}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def order_key(order):
    length = 1
    while order >= 62 ** length:
        order -= 62 ** length
        length += 1
    if length > 26:
        fail("diagram has too many elements")
    digits = []
    for _ in range(length):
        digits.append(ALPHABET[order % 62])
        order //= 62
    return chr(ord("a") + length - 1) + "".join(reversed(digits))


def fail(message):
    raise ValueError(message)


def number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{name} must be a finite number")
    if positive and value <= 0:
        fail(f"{name} must be positive")
    return value


def color(value, name):
    if value != "transparent" and (not isinstance(value, str) or not HEX.fullmatch(value)):
        fail(f"{name} must be #RRGGBB or transparent")
    return value


def point(value, name):
    if not isinstance(value, list) or len(value) != 2:
        fail(f"{name} must be [x, y]")
    return [number(value[0], f"{name}[0]"), number(value[1], f"{name}[1]")]


def base_element(element_id, kind, x, y, width, height, stroke, fill, order, dashed=False):
    seed = int(hashlib.sha256(element_id.encode()).hexdigest()[:8], 16)
    return {
        "id": element_id, "type": kind, "x": x, "y": y, "width": width, "height": height,
        "angle": 0, "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
        "index": order_key(order),
        "roundness": None, "seed": seed, "version": 1, "versionNonce": seed,
        "isDeleted": False, "boundElements": [], "updated": int(time.time() * 1000),
        "link": None, "locked": False,
    }


def wrapped(text, width, font_size):
    limit = max(7, int(width / (font_size * 0.56)))
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            if len(line) + len(word) + 1 > limit:
                lines.append(line)
                line = word
            else:
                line += " " + word
        lines.append(line)
    return "\n".join(lines)


def text_element(element_id, text, x, y, width, height, font_size, ink, order,
                 container_id=None, align="left", frame_id=None):
    item = base_element(element_id, "text", x, y, width, height, ink, "transparent", order)
    item.update({
        "text": text, "originalText": text, "fontSize": font_size, "fontFamily": 2,
        "textAlign": align, "verticalAlign": "middle" if container_id else "top",
        "containerId": container_id, "autoResize": False, "lineHeight": 1.25,
        "frameId": frame_id,
    })
    return item


def path_element(element_id, kind, absolute_points, order, ink="#374151", dashed=False,
                 start_binding=None, end_binding=None):
    if len(absolute_points) < 2:
        fail(f"{element_id}: at least two points are required")
    x, y = absolute_points[0]
    points = [[px - x, py - y] for px, py in absolute_points]
    item = base_element(element_id, kind, x, y,
                        max(px for px, _ in points) - min(px for px, _ in points),
                        max(py for _, py in points) - min(py for _, py in points),
                        ink, "transparent", order, dashed)
    item.update({"points": points, "lastCommittedPoint": None})
    if kind in {"line", "arrow"}:
        item.update({"startBinding": start_binding, "endBinding": end_binding,
                     "startArrowhead": None, "endArrowhead": "arrow" if kind == "arrow" else None,
                     "elbowed": False})
    if kind == "freedraw":
        item.update({"pressures": [0.5] * len(points), "simulatePressure": True})
    return item


def compile_board(spec):
    if not isinstance(spec, dict):
        fail("diagram must be an object")
    title = spec.get("title", "")
    if not isinstance(title, str):
        fail("title must be a string")
    canvas = spec.get("canvas", {})
    if not isinstance(canvas, dict):
        fail("canvas must be an object")
    width = number(canvas.get("width", 1200), "canvas.width", True)
    height = number(canvas.get("height", 800), "canvas.height", True)
    background = canvas.get("background", "plain")
    if background not in {"plain", "dots", "grid"}:
        fail("canvas.background must be plain, dots, or grid")
    canvas_color = color(canvas.get("color", "#ffffff"), "canvas.color")
    if canvas_color == "transparent":
        fail("canvas.color cannot be transparent")
    definitions = spec.get("elements", [])
    connections = spec.get("connections", [])
    if not isinstance(definitions, list) or not isinstance(connections, list):
        fail("elements and connections must be arrays")
    ids = set()
    for definition in definitions:
        if not isinstance(definition, dict):
            fail("every element must be an object")
        element_id = definition.get("id")
        if not isinstance(element_id, str) or not element_id or element_id in ids or element_id == "diagram-title":
            fail(f"invalid or duplicate element id: {element_id}")
        ids.add(element_id)
        if definition.get("type") not in TYPES:
            fail(f"{element_id}: unsupported element type")
    frames = {d["id"] for d in definitions if d["type"] == "frame"}
    by_id = {d["id"]: d for d in definitions}
    for definition in definitions:
        parent = definition.get("container")
        if parent is not None and (not isinstance(parent, str) or parent not in frames):
            fail(f"{definition['id']}: container must refer to a frame")
        seen = {definition["id"]}
        while parent is not None:
            if not isinstance(parent, str) or parent not in frames:
                fail(f"{definition['id']}: container must refer to a frame")
            if parent in seen:
                fail(f"{definition['id']}: frame containment cannot form a cycle")
            seen.add(parent)
            parent = by_id[parent].get("container")
    elements = []
    shapes = {}
    previous_routes = []

    def add(item):
        item["index"] = order_key(len(elements))
        elements.append(item)

    if title:
        add(text_element("diagram-title", title, 32, 20, width - 64, 52, 28, "#17212d", 0))
    for definition in definitions:
        element_id, kind = definition["id"], definition["type"]
        x = number(definition.get("x"), f"{element_id}.x")
        y = number(definition.get("y"), f"{element_id}.y")
        if x < 0 or y < 0 or x > width or y > height:
            fail(f"{element_id}: origin must be inside the canvas")
        stroke = color(definition.get("stroke", "#374151"), f"{element_id}.stroke")
        fill = color(definition.get("fill", "#ffffff"), f"{element_id}.fill")
        ink = color(definition.get("textColor", "#17212d"), f"{element_id}.textColor")
        font_size = number(definition.get("fontSize", 24 if kind == "frame" else 28),
                           f"{element_id}.fontSize", True)
        frame_id = definition.get("container")
        if kind in SHAPES:
            w = number(definition.get("width"), f"{element_id}.width", True)
            h = number(definition.get("height"), f"{element_id}.height", True)
            if x + w > width or y + h > height:
                fail(f"{element_id}: shape extends beyond the canvas")
            if frame_id is not None:
                parent = by_id[frame_id]
                px, py = number(parent.get("x"), f"{frame_id}.x"), number(parent.get("y"), f"{frame_id}.y")
                pw = number(parent.get("width"), f"{frame_id}.width", True)
                ph = number(parent.get("height"), f"{frame_id}.height", True)
                if x < px or y < py or x + w > px + pw or y + h > py + ph:
                    fail(f"{element_id}: shape must fit inside frame {frame_id}")
            item = base_element(element_id, "rectangle" if kind == "code" else kind,
                                x, y, w, h, stroke, fill, len(elements), definition.get("dashed", False))
            item["strokeWidth"] = number(definition.get("strokeWidth", 2), f"{element_id}.strokeWidth", True)
            item["frameId"] = frame_id
            if kind == "frame":
                item["name"] = ""
            if kind == "code":
                item.update({"strokeColor": "transparent", "backgroundColor": "#ffffff01",
                             "link": None, "customData": {"kind": "arc-code-block",
                                                       "code": str(definition.get("code", "")),
                                                       "filename": str(definition.get("filename", "")),
                                                       "language": str(definition.get("language", "python"))}})
            add(item)
            shapes[element_id] = item
            label = definition.get("label", "")
            if kind == "frame" and label:
                if not isinstance(label, str):
                    fail(f"{element_id}.label must be a string")
                heading_id = element_id + "-heading"
                if heading_id in ids:
                    fail(f"generated heading id conflicts with {heading_id}")
                ids.add(heading_id)
                heading_width = w - 32
                heading = wrapped(label, heading_width, font_size)
                heading_height = font_size * 1.25 * (heading.count("\n") + 1)
                if heading_height + 20 > h:
                    fail(f"{element_id}: frame heading does not fit; enlarge the frame or shorten its label")
                add(text_element(heading_id, heading, x + 16, y + 10, heading_width,
                                 heading_height, font_size, ink, len(elements), frame_id=element_id))
            if kind not in {"frame", "code"} and label:
                if not isinstance(label, str):
                    fail(f"{element_id}.label must be a string")
                text = wrapped(label, w - 24, font_size)
                lines = text.count("\n") + 1
                text_h = font_size * 1.25 * lines
                if text_h > h - 8:
                    fail(f"{element_id}: label does not fit; enlarge the card or shorten its label")
                label_id = element_id + "-label"
                if label_id in ids:
                    fail(f"generated label id conflicts with {label_id}")
                ids.add(label_id)
                add(text_element(label_id, text, x + 12, y + (h - text_h) / 2, w - 24,
                                 text_h, font_size, ink, len(elements), element_id, "center", frame_id))
                item["boundElements"].append({"type": "text", "id": label_id})
        elif kind == "text":
            text = definition.get("text", "")
            if not isinstance(text, str):
                fail(f"{element_id}.text must be a string")
            w = number(definition.get("width", max(100, len(text) * font_size * 0.6)), f"{element_id}.width", True)
            h = number(definition.get("height", max(30, (text.count("\n") + 1) * font_size * 1.25)), f"{element_id}.height", True)
            if x + w > width or y + h > height:
                fail(f"{element_id}: text extends beyond the canvas")
            add(text_element(element_id, wrapped(text, w, font_size), x, y, w, h,
                             font_size, ink, len(elements), frame_id=frame_id))
        else:
            points = definition.get("points")
            if not isinstance(points, list):
                fail(f"{element_id}.points must be an array")
            absolute = [[x + px, y + py] for px, py in [point(p, f"{element_id}.points") for p in points]]
            if any(px < 0 or py < 0 or px > width or py > height for px, py in absolute):
                fail(f"{element_id}: path extends beyond the canvas")
            item = path_element(element_id, "freedraw" if kind == "freehand" else kind,
                                absolute, len(elements), stroke, definition.get("dashed", False))
            item["frameId"] = frame_id
            add(item)
    for ordinal, connection in enumerate(connections):
        if not isinstance(connection, dict):
            fail("every connection must be an object")
        source_id, target_id = connection.get("from"), connection.get("to")
        if not isinstance(source_id, str) or not isinstance(target_id, str) or source_id not in shapes or target_id not in shapes or source_id == target_id:
            fail(f"connection {ordinal}: from/to must be different shape IDs")
        connection_id = connection.get("id", f"connection-{ordinal + 1}")
        if not isinstance(connection_id, str) or connection_id in ids:
            fail(f"connection {ordinal}: duplicate or invalid id")
        ids.add(connection_id)
        ink = color(connection.get("stroke", "#374151"), f"connection {ordinal}.stroke")
        via = connection.get("via", [])
        if not isinstance(via, list):
            fail(f"connection {ordinal}.via must be an array")
        axis = connection.get("axis", "auto")
        if axis not in {"auto", "horizontal", "vertical"}:
            fail(f"connection {ordinal}.axis must be auto, horizontal, or vertical")
        from_side, to_side = connection.get("fromSide"), connection.get("toSide")
        if (from_side is None) != (to_side is None):
            fail(f"connection {ordinal}: fromSide and toSide must be given together")
        if from_side is not None and (from_side not in {"top", "right", "bottom", "left"}
                                      or to_side not in {"top", "right", "bottom", "left"}):
            fail(f"connection {ordinal}: sides must be top, right, bottom, or left")
        checked_via = [point(p, f"connection {ordinal}.via") for p in via]
        absolute, warnings = route_connection(shapes[source_id], shapes[target_id], elements,
                                              width, height, axis, checked_via, previous_routes,
                                              (from_side, to_side) if from_side else None)
        for warning in warnings:
            print(f"connection {ordinal} ({source_id} → {target_id}): {warning}", file=sys.stderr)
        if any(px < 0 or py < 0 or px > width or py > height for px, py in absolute):
            fail(f"connection {ordinal}: route extends beyond the canvas")
        previous_routes.append({"source": source_id, "target": target_id,
                                "points": absolute})
        binding = lambda target: {"elementId": target, "focus": 0, "gap": 2}
        arrow = path_element(connection_id, "arrow", absolute, len(elements), ink,
                             connection.get("dashed", False), binding(source_id), binding(target_id))
        add(arrow)
        shapes[source_id]["boundElements"].append({"type": "arrow", "id": connection_id})
        shapes[target_id]["boundElements"].append({"type": "arrow", "id": connection_id})
        label = connection.get("label")
        if label:
            if not isinstance(label, str):
                fail(f"connection {ordinal}.label must be a string")
            label_size = number(connection.get("fontSize", 20),
                                f"connection {ordinal}.fontSize", True)
            preferred_label = point(connection["labelAt"], f"connection {ordinal}.labelAt") if "labelAt" in connection else None
            label_x, label_y = label_position(label, absolute, elements,
                                              [route["points"] for route in previous_routes],
                                              width, height, preferred_label, label_size)
            label_id = connection_id + "-label"
            if label_id in ids:
                fail(f"generated label id conflicts with {label_id}")
            ids.add(label_id)
            add(text_element(label_id, label, label_x, label_y,
                             max(100, len(label) * label_size * 0.56),
                             label_size * 1.5, label_size, ink, len(elements)))
    validate_arrow_clearance(elements)
    return {
        "type": "excalidraw", "version": 2, "source": "builder",
        "elements": elements,
        "appState": {"viewBackgroundColor": canvas_color, "gridSize": None},
        "files": {}, "openboard": {"background": background, "canvasColor": canvas_color},
    }, width, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagram", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    args = parser.parse_args()
    try:
        board, width, height = compile_board(json.loads(args.diagram.read_text()))
        svg = render_svg(board, width, height)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n")
        args.preview.write_text(svg)
        print(f"Wrote {args.out} and {args.preview} ({len(board['elements'])} editable elements)")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"OpenBoard build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
