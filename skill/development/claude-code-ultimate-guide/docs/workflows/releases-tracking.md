# Claude Code Releases Tracking

This repo maintains a condensed history of official Claude Code releases.

## Files

| File | Role |
|------|------|
| `machine-readable/claude-code-releases.yaml` | Source of truth (YAML) |
| `guide/core/claude-code-releases.md` | Human-readable version (Markdown) |
| `scripts/update-cc-releases.sh` | Script for checking new versions |

## Check for New Versions

```bash
./scripts/update-cc-releases.sh
```

The script:
1. Fetches the official CHANGELOG from GitHub
2. Compares against our tracked version
3. Displays new releases to condense

## Update Workflow

1. **Verify**: `./scripts/update-cc-releases.sh`
2. **Update YAML**: Add new entry in `claude-code-releases.yaml`
   - Update `latest` and `updated`
   - Add entry in `releases` (condensed: 2-4 highlights max)
   - Add to `breaking_summary` if applicable
   - Add to `milestones` if major feature
3. **Update Markdown**: Update `claude-code-releases.md` consistently
4. **Landing sync**: `./scripts/check-landing-sync.sh`
5. **Commit**: `docs: update Claude Code releases (vX.Y.Z)`

## YAML Entry Format

```yaml
- version: "2.1.13"
  date: "2026-01-20"
  highlights:
    - "Main feature"
    - "Other notable feature"
  breaking:
    - "Description of breaking change (if applicable)"
```
