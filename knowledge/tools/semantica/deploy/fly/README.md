# Fly.io

Deploy from a clean checkout using the root Dockerfile:

```bash
flyctl auth login
flyctl launch --copy-config --config deploy/fly/fly.toml --no-deploy
# Replace <falkordb-app-name> with your FalkorDB Fly app name.
# Fly.io private networking uses .internal hostnames — do not use localhost
# unless FalkorDB is a co-located process inside the same Machine.
flyctl secrets set FALKORDB_HOST=<falkordb-app-name>.internal FALKORDB_PORT=6379
flyctl deploy --config deploy/fly/fly.toml
```

Change `app` in `fly.toml` before launch if the default app name is already taken.
