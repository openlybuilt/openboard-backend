# Hierarchy and connections

Use this for every semantic map, regardless of source or diagram type.

- **Choose boxes by meaning.** Include an entity when it is needed to explain the goal, owns a step or data, or changes the path. Keep peer boxes at a similar level of detail. Give repeated roles consistent shapes and dimensions.
- **Choose boundaries by ownership.** Containment means an entity is inside a runtime, organization, actor lane, or other named domain. Set `parentId` in the map and `container` in the builder JSON. Never draw an arrow merely to express containment. Limit nesting to what the audience can read.
- **Choose arrows by relationship.** Each arrow needs a direction and a specific meaning: request, event, decision outcome, report, handoff, or data flow. Label ambiguous arrows. Do not turn every code import or every nearby pair of boxes into a connection.
- **Design the reading path.** Pick a primary direction and align peers. Keep at least 24 px between ordinary cards, with wider corridors for multiple or returning arrows. Use a consistent color family for each role and variation only where it conveys meaning.
- **Reserve arrow corridors.** Position cards so direct arrows are possible. Among clear routes, prefer the shortest path, then the fewest turns. Avoid crossings, shared segments, and even endpoint contact between unrelated arrows. Arrows may meet where they intentionally branch or share a node. If a route needs several detours, move the cards before forcing waypoints.
- **Size text before boxes.** Use the builder's large defaults (28 px card labels, 24 px frame headings, 20 px connection labels) as a starting point. Enlarge cards or shorten labels when text wraps beyond the available height; do not shrink labels merely to fit a crowded layout.
- **Review before and after layout.** Check the map for missing or invented entities, reversed links, cycles that need explanation, and unclear ownership. After rendering, inspect the preview for clipped labels, crossings, crowded branches, and arrowheads pointing the wrong way. The builder avoids content, but a crowded board may still need more space.

For a reference image, list its visible groups, nodes, arrowheads, labels, and branch outcomes first. Preserve the structure and reading order rather than tracing pixels. If content is illegible, record it in `unknowns`; do not silently guess.
