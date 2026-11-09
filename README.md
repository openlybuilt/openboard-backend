# OpenBoard backend

An authenticated Cloudflare Worker API for OpenBoard, with D1 storage. Each board is scoped to the Clerk user who owns it.

For local development, install dependencies with `pnpm install`, set `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY` in an ignored `.dev.vars` file, then run `pnpm db:migrate:local` and `pnpm dev`. Set `FRONTEND_ORIGIN` in `wrangler.jsonc` to the exact local frontend origin.

The database ID in `wrangler.jsonc` is for local development only. `wrangler.production.jsonc` binds the production OpenBoard database and origin. Configure the production Clerk keys as Worker secrets, then apply migrations and deploy with the production configuration:

```sh
pnpm exec wrangler d1 migrations apply DB --remote --config wrangler.production.jsonc
pnpm exec wrangler deploy --config wrangler.production.jsonc
```

The production configuration requires `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` as Worker secrets. Never commit them or expose the secret key to the frontend. Verify `/health`, authentication, and board isolation after deployment.
