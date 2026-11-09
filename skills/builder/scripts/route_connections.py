"""Obstacle-aware orthogonal paths for editable OpenBoard arrows."""

from heapq import heappop, heappush

CLEARANCE = 12
BEND_COST = 22
CROSSING_COST = 75


def rectangle(element, margin=0):
    return (element["x"] - margin, element["y"] - margin,
            element["x"] + element["width"] + margin,
            element["y"] + element["height"] + margin)


def obstacles(elements):
    blocked = []
    for element in elements:
        kind = element["type"]
        if kind in {"rectangle", "ellipse", "diamond"}:
            blocked.append((element["id"], rectangle(element, CLEARANCE)))
        elif kind == "frame" and element.get("name"):
            title_width = min(element["width"] - 20, max(100, len(element["name"]) * 9 + 28))
            blocked.append((element["id"] + "-title", (element["x"] + 8, element["y"] + 3,
                                                      element["x"] + title_width, element["y"] + 35)))
        elif kind == "text" and element.get("containerId") is None:
            blocked.append((element["id"], rectangle(element, 6)))
    return blocked


def contains(rect, point):
    left, top, right, bottom = rect
    return left < point[0] < right and top < point[1] < bottom


def hits(rect, start, end):
    left, top, right, bottom = rect
    if start[0] == end[0]:
        return left < start[0] < right and max(min(start[1], end[1]), top) < min(max(start[1], end[1]), bottom)
    if start[1] == end[1]:
        return top < start[1] < bottom and max(min(start[0], end[0]), left) < min(max(start[0], end[0]), right)
    return True


def collisions(points, blocked, ignore=()):
    ignored = set(ignore)
    return sorted({name for name, rect in blocked if name not in ignored
                   and any(hits(rect, a, b) for a, b in zip(points, points[1:]))})


def crosses_endpoint_interior(points, source, target):
    return any(hits(rectangle(shape), a, b) for shape in (source, target)
               for a, b in zip(points, points[1:]))


def port(shape, side):
    x, y, w, h = (shape[key] for key in ("x", "y", "width", "height"))
    if side == "left":
        return (x, y + h / 2), (x - CLEARANCE - 2, y + h / 2)
    if side == "right":
        return (x + w, y + h / 2), (x + w + CLEARANCE + 2, y + h / 2)
    if side == "top":
        return (x + w / 2, y), (x + w / 2, y - CLEARANCE - 2)
    return (x + w / 2, y + h), (x + w / 2, y + h + CLEARANCE + 2)


def orthogonalize(points, axis):
    result = [tuple(points[0])]
    for index, next_point in enumerate(points[1:], 1):
        next_point = tuple(next_point)
        current = result[-1]
        if current[0] != next_point[0] and current[1] != next_point[1]:
            last = index == len(points) - 1
            elbow = ((current[0], next_point[1]) if axis == "horizontal" else (next_point[0], current[1])) if last else ((next_point[0], current[1]) if axis == "horizontal" else (current[0], next_point[1]))
            if elbow != current:
                result.append(elbow)
        if next_point != result[-1]:
            result.append(next_point)
    return simplify(result)


def simplify(points):
    result = []
    for point in points:
        point = tuple(point)
        if point == (result[-1] if result else None):
            continue
        if len(result) >= 2 and ((result[-2][0] == result[-1][0] == point[0]) or
                                 (result[-2][1] == result[-1][1] == point[1])):
            result[-1] = point
        else:
            result.append(point)
    return result


def crossing_penalty(start, end, previous):
    penalty = 0
    for route in previous:
        for a, b in zip(route, route[1:]):
            if start[0] == end[0] and a[1] == b[1]:
                if min(start[1], end[1]) < a[1] < max(start[1], end[1]) and min(a[0], b[0]) < start[0] < max(a[0], b[0]):
                    penalty += CROSSING_COST
            elif start[1] == end[1] and a[0] == b[0]:
                if min(start[0], end[0]) < a[0] < max(start[0], end[0]) and min(a[1], b[1]) < start[1] < max(a[1], b[1]):
                    penalty += CROSSING_COST
            elif start[0] == end[0] == a[0] == b[0] and max(min(start[1], end[1]), min(a[1], b[1])) < min(max(start[1], end[1]), max(a[1], b[1])):
                penalty += CROSSING_COST / 3
            elif start[1] == end[1] == a[1] == b[1] and max(min(start[0], end[0]), min(a[0], b[0])) < min(max(start[0], end[0]), max(a[0], b[0])):
                penalty += CROSSING_COST / 3
    return penalty


def grid_route(start, end, blocked, previous, width, height):
    if any(contains(rect, start) or contains(rect, end) for _, rect in blocked):
        return None
    xs = {start[0], end[0], 8, width - 8}
    ys = {start[1], end[1], 8, height - 8}
    for _, (left, top, right, bottom) in blocked:
        xs.update((left - 2, right + 2))
        ys.update((top - 2, bottom + 2))
    xs = sorted(x for x in xs if 0 <= x <= width)
    ys = sorted(y for y in ys if 0 <= y <= height)
    xi, yi = {v: i for i, v in enumerate(xs)}, {v: i for i, v in enumerate(ys)}
    origin, target = (xi[start[0]], yi[start[1]]), (xi[end[0]], yi[end[1]])
    heap = [(0, 0, origin[0], origin[1], "")]
    best = {(origin[0], origin[1], ""): 0}
    parent = {}
    while heap:
        _, cost, i, j, direction = heappop(heap)
        state = (i, j, direction)
        if cost != best.get(state):
            continue
        if (i, j) == target:
            path = [(xs[i], ys[j])]
            while state in parent:
                state = parent[state]
                path.append((xs[state[0]], ys[state[1]]))
            return simplify(reversed(path)), cost
        for ni, nj, move in ((i - 1, j, "h"), (i + 1, j, "h"), (i, j - 1, "v"), (i, j + 1, "v")):
            if ni < 0 or nj < 0 or ni >= len(xs) or nj >= len(ys):
                continue
            a, b = (xs[i], ys[j]), (xs[ni], ys[nj])
            if any(hits(rect, a, b) for _, rect in blocked):
                continue
            step = abs(a[0] - b[0]) + abs(a[1] - b[1])
            next_cost = cost + step + (BEND_COST if direction and direction != move else 0)
            next_cost += crossing_penalty(a, b, previous)
            next_state = (ni, nj, move)
            if next_cost >= best.get(next_state, float("inf")):
                continue
            best[next_state] = next_cost
            parent[next_state] = state
            estimate = abs(b[0] - end[0]) + abs(b[1] - end[1])
            heappush(heap, (next_cost + estimate, next_cost, ni, nj, move))
    return None


def route_connection(source, target, elements, width, height, axis="auto", via=(), previous=()):
    blocked = obstacles(elements)
    skip = {source["id"], target["id"]}
    if via:
        sx = source["x"] + source["width"] / 2
        sy = source["y"] + source["height"] / 2
        tx = target["x"] + target["width"] / 2
        ty = target["y"] + target["height"] / 2
        horizontal = axis == "horizontal" or (axis == "auto" and abs(tx - sx) >= abs(ty - sy))
        if horizontal:
            sides = ("right", "left") if tx >= sx else ("left", "right")
        else:
            sides = ("bottom", "top") if ty >= sy else ("top", "bottom")
        start, _ = port(source, sides[0])
        end, _ = port(target, sides[1])
        manual = orthogonalize([start, *via, end], "horizontal" if horizontal else "vertical")
        if not collisions(manual, blocked, skip) and not crosses_endpoint_interior(manual, source, target):
            return manual, []
    sx = source["x"] + source["width"] / 2
    sy = source["y"] + source["height"] / 2
    tx = target["x"] + target["width"] / 2
    ty = target["y"] + target["height"] / 2
    choices = (("right", "left"), ("left", "right")) if axis == "horizontal" else (("bottom", "top"), ("top", "bottom")) if axis == "vertical" else (("right", "left"), ("bottom", "top"), ("left", "right"), ("top", "bottom"))
    candidates = []
    for from_side, to_side in choices:
        start, escape_start = port(source, from_side)
        end, escape_end = port(target, to_side)
        if not all(0 <= x <= width and 0 <= y <= height for x, y in (escape_start, escape_end)):
            continue
        route = grid_route(escape_start, escape_end, blocked, previous, width, height)
        if route is None:
            continue
        middle, cost = route
        full = simplify([start, escape_start, *middle, escape_end, end])
        if collisions(full, blocked, skip) or crosses_endpoint_interior(full, source, target):
            continue
        opposite = (from_side, to_side) in (("right", "left"), ("bottom", "top"))
        backward = (tx < sx and from_side == "right") or (tx > sx and from_side == "left") or (ty < sy and from_side == "bottom") or (ty > sy and from_side == "top")
        candidates.append((cost + (20 if backward else 0) + (0 if opposite else 10), full))
    if not candidates:
        raise ValueError(f"no clear arrow route from {source['id']} to {target['id']}; widen the gaps or canvas")
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1], (["manual waypoints crossed content; automatic route used"] if via else [])


def label_position(label, path, elements, previous, width, height, preferred=None):
    """Place a connection label beside a clear segment, never over content or a line."""
    label_width = max(80, len(label) * 8.5)
    label_height = 22
    blocked = obstacles(elements)

    def clear(x, y):
        rect = (x - 6, y - 6, x + label_width + 6, y + label_height + 6)
        if x < 0 or y < 0 or x + label_width > width or y + label_height > height:
            return False
        if any(max(rect[0], obstacle[0]) < min(rect[2], obstacle[2]) and
               max(rect[1], obstacle[1]) < min(rect[3], obstacle[3]) for _, obstacle in blocked):
            return False
        return not any(hits(rect, a, b) for route in previous for a, b in zip(route, route[1:]))

    if preferred is not None and clear(*preferred):
        return preferred
    segments = sorted(zip(path, path[1:]), key=lambda pair: abs(pair[0][0] - pair[1][0]) + abs(pair[0][1] - pair[1][1]), reverse=True)
    for start, end in segments:
        if start[1] == end[1]:
            middle = (start[0] + end[0]) / 2
            proposals = ((middle - label_width / 2, start[1] - label_height - 10),
                         (middle - label_width / 2, start[1] + 10))
        else:
            middle = (start[1] + end[1]) / 2
            proposals = ((start[0] + 10, middle - label_height / 2),
                         (start[0] - label_width - 10, middle - label_height / 2))
        for proposal in proposals:
            if clear(*proposal):
                return proposal
    anchors = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in segments]
    for anchor_x, anchor_y in anchors:
        for offset_y in (-60, 40, -90, 70, -120, 100):
            for offset_x in (0, -30, 30, -60, 60):
                proposal = (anchor_x - label_width / 2 + offset_x, anchor_y + offset_y)
                if clear(*proposal):
                    return proposal
    raise ValueError(f"no clear position for connection label {label!r}; add space or move the label")


def validate_arrow_clearance(elements):
    """Check the exported geometry, including labels added after earlier arrows."""
    by_id = {element["id"]: element for element in elements}
    blocked = obstacles(elements)
    for element in elements:
        if element["type"] != "arrow":
            continue
        path = [(element["x"] + x, element["y"] + y) for x, y in element["points"]]
        source_binding, target_binding = element.get("startBinding"), element.get("endBinding")
        source = by_id[source_binding["elementId"]] if source_binding else None
        target = by_id[target_binding["elementId"]] if target_binding else None
        ignored = (source["id"], target["id"]) if source and target else ()
        crossed = collisions(path, blocked, ignored)
        enters_card = bool(source and target and crosses_endpoint_interior(path, source, target))
        if crossed or enters_card:
            detail = ", ".join(crossed) if crossed else "an endpoint card"
            raise ValueError(f"arrow {element['id']} crosses {detail}; move the elements or add space")
