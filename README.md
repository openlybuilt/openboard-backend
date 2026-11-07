# Whiteboard backend

An authenticated Cloudflare Worker API for OpenBoard, with D1 storage. Each board is scoped to the Clerk user who owns it.

For local development, install dependencies with `pnpm install`, set `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY` in an ignored `.dev.vars` file, then run `pnpm db:migrate:local` and `pnpm dev`. Set `FRONTEND_ORIGIN` in `wrangler.jsonc` to the exact local frontend origin.

The database ID in `wrangler.jsonc` is for local development only. Configure a real D1 database, secrets, and frontend origin before deployment.
