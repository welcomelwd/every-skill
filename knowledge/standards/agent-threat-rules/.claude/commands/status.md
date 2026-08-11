# Skills Sec Status Dashboard

Show current status of the scanning pipeline and content queue.

## Steps

1. Scan pipeline status:
```bash
cd /Users/user/Downloads/agent-threat-rules
echo "=== Registry ==="
node -e "const r=require('./mcp-registry.json');console.log('Total entries:',r.totalEntries);console.log('Crawled at:',r.crawledAt)" 2>/dev/null || echo "No registry found"

echo ""
echo "=== Cumulative Scans ==="
node -e "const d=require('./data/scan-cumulative.json');const r=d.results||[];console.log('Total scanned:',r.length);console.log('CRITICAL:',r.filter(x=>x.riskLevel==='CRITICAL').length);console.log('HIGH:',r.filter(x=>x.riskLevel==='HIGH').length);console.log('CLEAN:',r.filter(x=>x.riskLevel==='CLEAN'||x.riskLevel==='LOW').length);console.log('Last scan:',d.auditedAt)" 2>/dev/null || echo "No cumulative data"

echo ""
echo "=== Today's Batch ==="
BATCH="data/scan-batch-$(date +%Y%m%d).json"
[ -f "$BATCH" ] && node -e "const d=require('./$BATCH');console.log('Today scanned:',d.results?.length||0)" || echo "No batch today"

echo ""
echo "=== Pending Posts ==="
POSTS="posts/$(date +%Y-%m-%d)"
[ -d "$POSTS" ] && ls "$POSTS"/*.md 2>/dev/null | wc -l | xargs echo "Posts ready:" || echo "No posts today"
```

2. Show summary in a clean dashboard format:
   - Registry coverage (how many skills discovered vs scanned)
   - Scan progress (percentage of registry scanned)
   - Content queue (posts awaiting approval)
   - Last scan date
   - Next actions recommended

3. Suggest next action based on state:
   - If no scan today → "Run /scan-daily"
   - If posts pending → "Run /review-posts"
   - If it's Sunday → "Run /weekly-report"
   - If registry is stale (>3 days) → "Registry needs refresh"
