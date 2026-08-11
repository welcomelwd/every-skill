# Monitor Security Events

Scan X and Hacker News for AI/MCP security incidents, generate SkillsSec response posts.

## Steps

1. Run the monitor:
```bash
cd /Users/user/Downloads/agent-threat-rules
export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
python3 scripts/monitor-security-events.py --generate
```

2. Show discovered events and generated posts for review.

3. For each generated post, ask:
   - A) Post now (via browser)
   - B) Edit first
   - C) Skip
   - D) Save to viral-posts-db (if the original event post format is worth saving)
