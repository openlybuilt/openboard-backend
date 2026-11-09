# Codebase architecture

Use this when the source is a repository. The aim is an evidence-backed explanation of a system or a named workflow, not an inventory of files.

1. Start from the user's question. If none is given, make a system overview and state that scope. Inspect the repository's manifests, workspace configuration, entry points, deployment files, API routes, persistence code, and relevant environment-variable **names**. Use `rg --files` and focused `rg` searches before broad reads.
2. Trace a real path through the code. Follow caller to callee and client to server; check what runs in the browser, server, worker, database, or external service. Distinguish a direct call, HTTP request, event, queue, and stored data.
3. Draw a boundary only when it represents a meaningful runtime, deployment, trust, ownership, or data boundary. A directory, package, import, or class is not automatically a separate service. Group implementation details inside the runtime that owns them.
4. Give every substantive box and arrow evidence in the [semantic map](semantic-map.md): repository-relative path plus symbol or config key. For example, an HTTP arrow needs both the requesting code and the receiving route when both are available. Check direction and auth before naming the arrow.
5. Mark behavior that is configured externally, inferred, or not visible in the repo as an unknown. Do not invent a connection to complete the picture. Keep secrets and values out of the map; a setting's name is enough.

For a large system, prefer one readable view answering the user's question. Split distinct workflows into separate boards rather than shrinking text or drawing every import as an arrow. Before rendering, use [hierarchy and connections](hierarchy-and-connections.md), then the chosen diagram-type guide.
