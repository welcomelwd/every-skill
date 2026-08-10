# Render

This Blueprint provisions a Docker web service plus a Render Key Value instance and wires the datastore host/port into the Explorer env vars.

```bash
render login
render blueprints validate deploy/render/render.yaml
render blueprint apply deploy/render/render.yaml
```

After creation, update `ALLOWED_ORIGINS` in the Render dashboard if you attach a custom domain.
