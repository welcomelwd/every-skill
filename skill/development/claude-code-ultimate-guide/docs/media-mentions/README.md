# Media Mentions Tracker

Tracks all external sources that mention the Claude Code Ultimate Guide (GitHub or cc.bruniaux.com).

## Source of truth

`mentions.yaml` — one entry per mention.

## Schema

```yaml
- id: "001"                  # Sequential, zero-padded
  platform: article          # article | reddit | linkedin-own | linkedin-other | twitter | directory | instagram | podcast | forum | video
  url: "https://..."
  title: "..."
  author: "..."              # Handle, name, or publication name. Use "unknown" if not found.
  date: "YYYY-MM-DD"         # Publication date, or null if unknown
  angle: "..."               # One sentence: how they framed the guide
  reach: unknown             # low (<1K) | medium (1K-10K) | high (10K-100K) | viral (100K+) | unknown | null (own property)
  status: active             # active | dead | paywall
  notes: "..."               # Optional. Anything worth remembering (quote, context, SEO value).
  first_seen: "YYYY-MM-DD"   # Date we logged it
```

## Adding a new mention

1. Add an entry to `mentions.yaml` with the next sequential id.
2. Update `meta.total_mentions` and `meta.last_updated`.
3. Commit: `docs: add media mention — [platform] [author/publication]`

## Slash command

`/track-mention <url>` — not yet implemented. Add manually for now.

## Stats (as of 2026-04-14)

| Platform | Count |
|---|---|
| Articles / blogs | 10 |
| Videos (YouTube) | 2 |
| Podcasts | 1 |
| Reddit | 3 |
| LinkedIn (own) | 2 |
| LinkedIn (third-party) | 5 |
| Twitter / X | 2 |
| Instagram | 1 |
| Directories / registries | 7 |
| Forums (HN) | 1 |
| **Total** | **34** |

### Languages spotted

| Language | Mentions |
|---|---|
| English | 28 |
| French | 3 |
| Spanish | 1 |
| Korean | 1 |

## Slash command

Run `/track-mentions` to search for new mentions via Perplexity and update this file automatically.
