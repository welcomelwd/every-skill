# Scan Famous / High-Star MCP Skills

Scan the most popular MCP skills to find issues in well-known packages. This is the highest-value content for Skills Sec.

## Steps

1. Load the registry and sort by stars:
```bash
cd /Users/user/Downloads/agent-threat-rules
node -e "
const r = require('./mcp-registry.json');
const top = r.entries
  .filter(e => e.stars && e.stars > 50)
  .sort((a,b) => b.stars - a.stars)
  .slice(0, 30);
top.forEach((e,i) => console.log((i+1) + '. [' + (e.stars||0) + ' stars] ' + e.name + ' — ' + (e.description||'').slice(0,80)));
"
```

2. Show the top 30 by stars. Ask which ones to scan (or scan all).

3. For each selected skill, run the full audit pipeline:
   - npm pack → extract → ATR scan → AST analysis → verdict

4. For any CRITICAL or HIGH results:
   - Present findings using T1 (Famous Skill Expose) template
   - Fill in all template variables with real data
   - Generate both EN and ZH versions
   - **Responsible disclosure reminder**: "72-hour window — notify author first?"
   - Ask: approve post or edit?

5. For CLEAN results with many stars:
   - Note as "verified safe" — potential whitelist entry
   - Generate a positive post: "{SKILL_NAME} ({STARS} stars) — scanned clean. Safe to use."

6. Summary: N scanned, N CRITICAL, N HIGH, N CLEAN, N posts generated
