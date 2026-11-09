# Flowchart

- Give the process a clear start and outcome. Put ordinary steps in sequence in one reading direction.
- Use a decision shape only for an actual branch; label each outgoing outcome. Put branches back together where the process rejoins.
- For a four-step cycle, place the steps at top, left, bottom, and right around a clear center. Keep top and bottom centered on the same axis, left and right on another, and match the gaps between peer cards. Put a repeat condition in the center only if it describes the cycle; the cycle's arrows must still connect the actual steps in order. The [loop layout example](../loop-layout.example.json) shows this arrangement.
- Route exceptions and retry loops outside the main path. Use one or two turns per edge of a diamond-shaped cycle when possible. Leave room for labels, keep the center clear, and verify the last arrow returns to the first step.
- Keep step labels as short verbs or outcomes. If the process has multiple responsible actors, consider a swimlane instead.
- Check that every branch has a destination and that the visible directions match the described process.
