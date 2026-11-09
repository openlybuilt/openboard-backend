# Hierarchy and connections

Use this for every semantic map, regardless of source or diagram type.

- **Choose boxes by meaning.** Include an entity when it is needed to explain the goal, owns a step or data, or changes the path. Keep peer boxes at a similar level of detail. Give repeated roles consistent shapes and dimensions.
- **Choose boundaries by ownership.** Containment means an entity is inside a runtime, organization, actor lane, or other named domain. Set `parentId` in the map and `container` in the builder JSON. Never draw an arrow merely to express containment. Limit nesting to what the audience can read.
- **Choose arrows by relationship.** Each arrow needs a direction and a specific meaning: request, event, decision outcome, report, handoff, or data flow. Label ambiguous arrows. Do not turn every code import or every nearby pair of boxes into a connection.
- **Design the reading path.** Pick a primary direction and align peers. Keep at least 24 px between ordinary cards, with wider corridors for multiple or returning arrows. Use a consistent color family for each role and variation only where it conveys meaning.
- **Review before and after layout.** Check the map for missing or invented entities, reversed links, cycles that need explanation, and unclear ownership. After rendering, inspect the preview for clipped labels, crossings, and crowded branches. The builder avoids content, but a crowded board may still need more space.

For a reference image, list its visible groups, nodes, arrowheads, labels, and branch outcomes first. Preserve the structure and reading order rather than tracing pixels. If content is illegible, record it in `unknowns`; do not silently guess.
