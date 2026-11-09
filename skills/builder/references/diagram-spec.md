# Diagram specification

Use this after the [semantic map](semantic-map.md) and the selected diagram-type guide have established the meaning and layout. The builder accepts JSON with `title`, optional `canvas`, `elements`, and `connections`. Coordinates are absolute pixels. IDs are unique strings. Put large containers before their contents so they render behind them. An optional `container` names a `frame` element and is saved as its OpenBoard `frameId`.

```json
{
  "title": "Service request",
  "canvas": { "width": 900, "height": 540, "background": "plain", "color": "#ffffff" },
  "elements": [
    { "id": "team", "type": "frame", "x": 40, "y": 90, "width": 820, "height": 390, "label": "Service team", "fill": "#f4f7fb", "stroke": "#8094b0" },
    { "id": "request", "type": "rectangle", "container": "team", "x": 90, "y": 230, "width": 210, "height": 90, "label": "Request received", "fill": "#e8f2ff" },
    { "id": "review", "type": "rectangle", "container": "team", "x": 570, "y": 230, "width": 210, "height": 90, "label": "Review request", "fill": "#e8f2ff" }
  ],
  "connections": [{ "from": "request", "to": "review", "label": "assign" }]
}
```

## Elements

| Type | Key fields | OpenBoard use |
| --- | --- | --- |
| `rectangle`, `ellipse`, `diamond` | `x`, `y`, `width`, `height`, `label` | Editable shape with a bound text label. |
| `frame` | Shape fields; `label` names the frame | Native editable frame; use for groups, lanes, or page regions. |
| `text` | `x`, `y`, `text`, `fontSize` | Standalone text. |
| `code` | `x`, `y`, `width`, `height`, `code`, `language`, `filename` | OpenBoard code block. |
| `line`, `arrow`, `freehand` | `x`, `y`, `points` | Points are `[x,y]` offsets from the element origin. |

Shape fields: `fill`, `stroke`, `strokeWidth`, `dashed`, `fontSize`, `textColor`, and `container`. Colors must be six-digit hex codes or `transparent`. The default canvas is white and plain; `background` may be `plain`, `dots`, or `grid`. Labels default to 28 px on cards and standalone text, and 24 px on frame headings. Frame headings are editable text within the frame. The builder rejects labels that cannot fit their card; enlarge the shape or shorten the label.

Connections use `from` and `to` shape IDs, optional `label`, `labelAt`, `fontSize`, `stroke`, `dashed`, `axis`, `fromSide`, `toSide`, and `via`. Connection labels default to 20 px. `axis` is `auto`, `vertical`, or `horizontal`; for a controlled loop, set both `fromSide` and `toSide` to `top`, `right`, `bottom`, or `left` instead. `via` is a list of absolute `[x,y]` waypoints; the builder inserts elbows between diagonal waypoints. Without it, the builder selects the shortest clear route, then the one with the fewest turns. Unrelated arrows must remain separated; arrows sharing a node may meet. If waypoints cross content or an unrelated arrow, the builder uses a clear automatic route and reports that change. If no clear route exists, enlarge the canvas or move cards. `labelAt` proposes the top-left position of a label as an absolute `[x,y]`; the builder moves it to a clear area when necessary. A connection is saved as an editable, bound OpenBoard arrow.
