# Scan Specific Skill

Scan a specific MCP skill by npm package name or GitHub URL.

## Input
$ARGUMENTS — npm package name (e.g. `mcp-server-filesystem`) or GitHub URL

## Steps

1. If argument is a GitHub URL, extract the npm package name from package.json
2. Run single-package audit:
```bash
cd /Users/user/Downloads/agent-threat-rules && npx tsx scripts/audit-npm-skills-v2.ts --limit 1 --offset 0 --output "data/scan-single-$(date +%Y%m%d%H%M%S).json"
```

Note: For single package scanning, we need to create a temporary registry entry. Instead:

```bash
cd /Users/user/Downloads/agent-threat-rules
mkdir -p /tmp/atr-single-scan
npm pack $ARGUMENTS --pack-destination /tmp/atr-single-scan 2>/dev/null
```

3. If the package downloads successfully, run the ATR engine against it
4. Present findings using the "Plain Language Consequences" template (T3):
   - What the skill claims to do
   - What it actually does (each finding in plain language)
   - What consequences the user faces
   - ATR rules triggered
5. If CRITICAL or HIGH:
   - Generate a Skills Sec post draft using templates from `templates/post-templates.json`
   - Ask: "Post this? Which platforms?"
6. If CLEAN:
   - Report clean status
   - Ask if I want to add to whitelist
