# Semantic map

Write this compact JSON before assigning coordinates. It captures what the board says; the [builder specification](diagram-spec.md) captures where and how it is drawn. See [the example](semantic-map.example.json).

| Field | Meaning |
| --- | --- |
| `goal`, `audience` | The question answered and who should understand it. |
| `diagramType` | `architecture`, `flowchart`, `org-chart`, or `swimlane`. Choose the type from the content when the user has not chosen one. |
| `source` | `{ "kind": "brief" \| "reference-image" \| "repository", "path": "..." }`; omit `path` for a spoken brief. |
| `entities` | `{id,label,role,kind,parentId?,evidence?}`. `role` is `boundary` or `node`. `parentId` names a boundary, never another node. |
| `connections` | `{from,to,kind,label?,evidence?}`. Endpoints name entity IDs. A connection means a directed relationship, not containment. |
| `unknowns` | Unresolved claims or details that should not silently appear as facts on the board. |

Use stable, unique IDs. Every `parentId`, `from`, and `to` must resolve. Containment must be acyclic. Keep one abstraction level per view; omit detail that does not help answer `goal`. For a repository source, put a code path and symbol or configuration key in `evidence` for each substantive entity and connection. An import alone does not prove a runtime call. For an image source, preserve visible hierarchy and arrow direction; mark illegible content as unknown rather than guessing.

The map has no `x`, `y`, `width`, or colors. Convert boundaries to frames, nodes to shapes or text, and connections to arrows only after its meaning is settled. Save the map alongside the generated board so a later revision can change the layout without rediscovering the structure.
