---
name: builder
description: Create a new editable OpenBoard diagram from a brief, reference image, or codebase, with a visual preview and an importable .openboard file. Use for architecture diagrams, flowcharts, organization charts, swimlanes, and other whiteboards; not for account access or editing an existing board.
---

# Create an OpenBoard diagram

1. Identify the question the board must answer and its audience. Accept a brief, reference image, or repository. For a repository, read [codebase architecture](references/codebase-architecture.md) and inspect the code before drawing. Ask only about a missing decision that would change the diagram's meaning.
2. Write a coordinate-free [semantic map](references/semantic-map.md) of entities, containment, connections, evidence, and unknowns. Use [hierarchy and connections](references/hierarchy-and-connections.md) to decide what becomes a box, boundary, or arrow. Read only the guide for the selected diagram type: [architecture](references/types/architecture.md), [flowchart](references/types/flowchart.md), [org chart](references/types/org-chart.md), or [swimlane](references/types/swimlane.md).
3. Convert the map to positioned JSON using [the builder specification](references/diagram-spec.md). For an application diagram, use only the application name as its title. Do not add a subtitle, source credit, or revision text to the board unless requested. Run `python3 scripts/build_board.py diagram.json --out output/board.openboard --preview output/board.svg` from this skill's directory. The builder needs only Python's standard library and no OpenBoard server.
4. Inspect the SVG at full size. Revise spacing, labels, and routes until the structure reads clearly and the builder reports no errors. Deliver the `.openboard` file and SVG preview. Save the semantic map alongside them, but show its source evidence only when asked. The user can import the board through OpenBoard's **Open** menu.

An image is a reference for structure and content, not a mandate to trace pixels. Preserve visible relationships without inventing illegible details. Repo-derived claims need source evidence; mark unresolved points as unknowns. The SVG is a review artifact; the `.openboard` file contains editable elements. This skill creates new boards only and does not access accounts.
