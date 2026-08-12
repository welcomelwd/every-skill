# Manual adjudication — benign-slice HIGH/CRITICAL findings

This is the human pass that makes the false-positive number credible. Every
HIGH/CRITICAL finding the harness surfaces on the benign slice is adjudicated by
hand: **true positive** (the config really has the issue), **false positive**
(AAK is wrong), or **ambiguous** (defensible either way). Findings are **not**
auto-labelled.

- **Rater:** single rater (the maintainer). No second rater, so there is no
  inter-rater agreement statistic — stated as a limitation in `RESULTS.md`.
- **Scope:** the top 30 HIGH/CRITICAL findings on the benign slice, ranked
  deterministically by severity → rule id → config → evidence. The 2026-07-20
  run produced **4** HIGH/CRITICAL findings total, so all 4 are adjudicated
  (fewer than 30).
- **Verdict rule:** the false-positive *rate* = (false positives) / (all
  adjudicated). Ambiguous verdicts count in the denominator but not as false
  positives (conservative — does not inflate the FP rate).

## Template (copy per finding)

| # | Rule ID | Config | Verdict | One-line reason |
|--:|---------|--------|:-------:|-----------------|
| … | `AAK-…` | `<server name>` | TP / FP / ambiguous | … |

## Adjudication — 2026-07-20 run (n = 4 HIGH/CRITICAL)

| # | Rule ID | Config | Verdict | One-line reason |
|--:|---------|--------|:-------:|-----------------|
| 1 | `AAK-MCP-001` | `ai.nefesh/human-state` | **FALSE POSITIVE** | Server authenticates with a custom `X-Nefesh-Key` API-key header; `AAK-MCP-001` only recognises `Authorization`/`Bearer`, so it wrongly reports "no authentication". |
| 2 | `AAK-MCP-001` | `ai.satoshidata/wallet-intelligence` | **FALSE POSITIVE** | Same gap: `X-WR-API-Key` is an API-key auth header (literally "API-Key"); the rule misses non-`Authorization` credential headers. |
| 3 | `AAK-MCP-001` | `ai.lattiq/x402-trading-signals` | **AMBIGUOUS** | `X-PAYMENT` gates access via the x402 pay-to-access protocol — access control, but not identity authentication; "no auth" is defensible either way. |
| 4 | `AAK-MCP-001` | `ai.spala/public-mcp` | **TRUE POSITIVE** | The only header is `Accept` (content negotiation, not auth); the server is named `public-mcp` and genuinely exposes a remote endpoint with no authentication. |

### Tally

- False positives: **2** (both a single root cause — `AAK-MCP-001` not recognising custom API-key headers).
- True positives: **1**.
- Ambiguous: **1**.
- **Benign-slice HIGH/CRITICAL false-positive rate = 2 / 4 = 50.0%** (Wilson 95% CI [15.0%, 85.0%]; n is small, so the interval is wide).

### Follow-up filed

The two false positives share one fixable gap — `AAK-MCP-001`'s "no auth" check
should recognise common API-key credential headers (`X-*-Key`, `X-API-Key`,
`Api-Key`, and the x402 `X-PAYMENT` case reviewed) as authentication, not just
`Authorization`/`Bearer`. Tracked as
[#475](https://github.com/sattyamjjain/agent-audit-kit/issues/475).

## Adjudication — 2026-07-22 re-run (post-#475, n = 1 HIGH/CRITICAL)

[#475](https://github.com/sattyamjjain/agent-audit-kit/issues/475) shipped:
`AAK-MCP-001` now recognises the `X-*-Key` / `*-API-Key` credential-header family
and the x402 `X-PAYMENT` access gate (value-aware — a hardcoded literal still
fires). Re-running the harness on the same 368-config slice:

| # | Rule ID | Config | Verdict | One-line reason |
|--:|---------|--------|:-------:|-----------------|
| 1 | `AAK-MCP-001` | `ai.spala/public-mcp` | **TRUE POSITIVE** | Sole header is `Accept` (content negotiation, not auth); a genuinely unauthenticated remote endpoint. Correctly flagged. |

### Tally (post-#475)

- False positives: **0** (both prior FPs — `X-Nefesh-Key`, `X-WR-API-Key` — cleared).
- True positives: **1**.
- Ambiguous: **0** (the x402 `X-PAYMENT` case is now recognised as a declared access gate).
- **Benign-slice HIGH/CRITICAL false-positive rate = 0 / 1 = 0.0%** (Wilson 95% CI [0.0%, 79.3%]; n = 1, interval very wide).
- No new HIGH/CRITICAL findings were introduced elsewhere on the corpus (full-corpus AAK-MCP-001 configs 497 → 492, delta −5, 0 newly firing).
