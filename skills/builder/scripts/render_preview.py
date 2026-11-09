"""Render an OpenBoard document as a standalone SVG review preview."""

from html import escape
from math import atan2, cos, sin


def value(number):
    return f"{number:.2f}".rstrip("0").rstrip(".") if isinstance(number, float) else str(number)


def ink(element):
    return escape(element["strokeColor"], quote=True)


def path_points(element):
    return [(element["x"] + dx, element["y"] + dy) for dx, dy in element["points"]]


def shape_svg(element):
    x, y, w, h = (value(element[key]) for key in ("x", "y", "width", "height"))
    color = ink(element)
    fill = escape(element["backgroundColor"], quote=True)
    if fill == "#ffffff01":
        fill = "#111827"
    style = (f'fill="{fill}" stroke="{color}" stroke-width="{value(element["strokeWidth"])}"'
             + (' stroke-dasharray="8 5"' if element["strokeStyle"] == "dashed" else ""))
    if element["type"] == "ellipse":
        body = f'<ellipse cx="{value(element["x"] + element["width"] / 2)}" cy="{value(element["y"] + element["height"] / 2)}" rx="{value(element["width"] / 2)}" ry="{value(element["height"] / 2)}" {style}/>'
    elif element["type"] == "diamond":
        cx, cy = element["x"] + element["width"] / 2, element["y"] + element["height"] / 2
        points = f'{value(cx)},{y} {value(element["x"] + element["width"])},{value(cy)} {value(cx)},{value(element["y"] + element["height"])} {x},{value(cy)}'
        body = f'<polygon points="{points}" {style}/>'
    else:
        body = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{8 if element["type"] != "frame" else 4}" {style}/>'
    if element["type"] == "frame" and element.get("name"):
        body += f'<text x="{value(element["x"] + 14)}" y="{value(element["y"] + 25)}" fill="#334155" font-size="16" font-weight="650">{escape(element["name"])}</text>'
    if element.get("customData", {}).get("kind") == "arc-code-block":
        data = element["customData"]
        body += f'<text x="{value(element["x"] + 16)}" y="{value(element["y"] + 27)}" fill="#a5b4fc" font-size="13" font-weight="600">{escape(data.get("filename") or data.get("language", "code"))}</text>'
        for index, line in enumerate(data.get("code", "").splitlines()[:max(0, int((element["height"] - 54) / 18))]):
            body += f'<text x="{value(element["x"] + 16)}" y="{value(element["y"] + 55 + index * 18)}" fill="#e5e7eb" font-size="13" font-family="monospace">{escape(line)}</text>'
    return body


def text_svg(element):
    lines = element["text"].split("\n")
    size = element["fontSize"]
    line_height = size * element.get("lineHeight", 1.25)
    total = line_height * len(lines)
    top = element["y"] + (max(0, element["height"] - total) / 2 if element.get("verticalAlign") == "middle" else 0)
    x = element["x"] + (element["width"] / 2 if element.get("textAlign") == "center" else 0)
    anchor = "middle" if element.get("textAlign") == "center" else "start"
    chunks = []
    for index, line in enumerate(lines):
        chunks.append(f'<text x="{value(x)}" y="{value(top + size + index * line_height)}" fill="{ink(element)}" font-size="{value(size)}" text-anchor="{anchor}">{escape(line)}</text>')
    return "".join(chunks)


def stroke_svg(element):
    points = path_points(element)
    if len(points) < 2:
        return ""
    d = "M " + " L ".join(f"{value(x)} {value(y)}" for x, y in points)
    color = ink(element)
    body = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{value(element["strokeWidth"])}" stroke-linecap="round" stroke-linejoin="round"'
    if element["strokeStyle"] == "dashed":
        body += ' stroke-dasharray="7 5"'
    body += "/>"
    if element["type"] == "arrow" and element.get("endArrowhead"):
        end = points[-1]
        previous = next((p for p in reversed(points[:-1]) if p != end), points[-2])
        angle = atan2(end[1] - previous[1], end[0] - previous[0])
        a = (end[0] - 12 * cos(angle - 0.45), end[1] - 12 * sin(angle - 0.45))
        b = (end[0] - 12 * cos(angle + 0.45), end[1] - 12 * sin(angle + 0.45))
        body += f'<polygon points="{value(end[0])},{value(end[1])} {value(a[0])},{value(a[1])} {value(b[0])},{value(b[1])}" fill="{color}"/>'
    return body


def render_svg(board, width, height):
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{value(width)}" height="{value(height)}" viewBox="0 0 {value(width)} {value(height)}">',
              f'<rect x="0" y="0" width="{value(width)}" height="{value(height)}" fill="{escape(board["openboard"]["canvasColor"], quote=True)}"/>',
              '<g font-family="Arial, Helvetica, sans-serif">']
    for element in board["elements"]:
        kind = element["type"]
        if kind in {"rectangle", "ellipse", "diamond", "frame"}:
            pieces.append(shape_svg(element))
        elif kind == "text":
            pieces.append(text_svg(element))
        elif kind in {"line", "arrow", "freedraw"}:
            pieces.append(stroke_svg(element))
    pieces.extend(["</g>", "</svg>"])
    return "\n".join(pieces) + "\n"
