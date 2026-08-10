# Railway

Deploys the Knowledge Explorer from the root `Dockerfile` and checks `/api/health`.

```bash
railway login
railway init
railway add --database redis
railway variable --set "FALKORDB_HOST=${{Redis.REDISHOST}}"
railway variable --set "FALKORDB_PORT=${{Redis.REDISPORT}}"
railway variable --set "ALLOWED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}"
railway up
```

The Redis plugin variables are wired to the requested FalkorDB env names for deployment compatibility. The Explorer currently reads these settings but does not persist graph state to FalkorDB.
