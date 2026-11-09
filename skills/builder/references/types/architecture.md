# Architecture diagram

- Select a level: system context, runtime services, or one workflow. Do not mix all three in one crowded view.
- Make real runtime, deployment, trust, or data boundaries into frames. Place the actors or clients that initiate work on the left, processing in the middle, and durable stores or external destinations on the right when that matches the story.
- Label cross-boundary arrows with the request, event, or data being transferred. Show auth or another control boundary only if it matters to the goal.
- Keep internal implementation modules inside their owning runtime. A source-code folder is not a boundary by itself.
- Check that every service and cross-boundary arrow is supported by the source or clearly identified as a user-provided assumption.
