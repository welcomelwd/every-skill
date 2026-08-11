# Notify Skill Authors (Responsible Disclosure)

Open GitHub issues on flagged repos to notify authors before public disclosure.

## Steps

1. Check what needs notification:
```bash
cd /Users/user/Downloads/agent-threat-rules
node -e "
const fs = require('fs');
const hist = fs.existsSync('data/notification-history.json') ? JSON.parse(fs.readFileSync('data/notification-history.json','utf-8')) : [];
console.log('Previously notified:', hist.length);
hist.filter(h => new Date(h.disclosureDate) > new Date()).forEach(h =>
  console.log('  Pending disclosure:', h.package, '→', h.disclosureDate)
);
hist.filter(h => new Date(h.disclosureDate) <= new Date()).forEach(h =>
  console.log('  Ready to disclose:', h.package, '(since', h.disclosureDate + ')')
);
"
```

2. Run notification for latest batch (dry-run first):
```bash
cd /Users/user/Downloads/agent-threat-rules
BATCH=$(ls data/scan-batch-*.json 2>/dev/null | sort | tail -1)
npx tsx scripts/notify-author.ts --input "$BATCH" --dry-run
```

3. Show which repos would get issues. Ask for confirmation.

4. If confirmed, run for real:
```bash
cd /Users/user/Downloads/agent-threat-rules
BATCH=$(ls data/scan-batch-*.json 2>/dev/null | sort | tail -1)
npx tsx scripts/notify-author.ts --input "$BATCH"
```

5. Show summary: N notified, disclosure dates
