#!/usr/bin/env python3
"""Frozen, citable MCP-security research baseline (v1.0).

Emits an immutable, byte-deterministic snapshot of AgentAuditKit's measurements
over the State-of-MCP-2026 corpus, so a single number can be cited and later
re-measured against. This is the **pre-2026-07-28-spec** baseline; the
re-measure is scheduled for 2026-08-11 (see
``docs/research/mcp-security-baseline-v1.0.md``).

This module does NOT contain a scanner and adds NO detection rules. It REUSES
the shipped engine and the existing State-of-MCP harness primitives:

  - ``run_report.aggregate`` helpers (``_config_sources``, ``_content_key``,
    ``_scan_text``, ``_transport_signals``) — the same offline, deterministic
    corpus pass the published report uses.
  - ``agent_audit_kit.rules.builtin.RULES`` — rule titles + severities.
  - ``agent_audit_kit.scanners.oauth_misconfig`` regexes — PRM / inline-auth /
    remote-server signals, reused only to *classify auth posture*, not to add a
    finding.

The snapshot records, per config and in aggregate:
  - corpus size + provenance and the collection window (data, not a wall clock),
  - auth-posture distribution (no-auth / bearer / oauth2.1 / unknown),
  - transport distribution (stdio / sse / streamable-http),
  - per-rule HIGH/CRITICAL hit counts,
  - the measured benign-slice HIGH/CRITICAL false-positive rate + its denominator
    (read from ``benchmarks/false_positive/results.json``).

Determinism: sorted keys, stable float rounding, and NO wall-clock value in the
payload (the collection window comes from the corpus manifest, which is data).
Two runs over the same corpus produce byte-identical output; a SHA-256 over
those bytes makes the figure tamper-evident.

Emit (offline, deterministic — no network, no LLM):
    python research/state-of-mcp-2026/baseline.py \
        --corpus benchmarks/data \
        --registry-manifest research/state-of-mcp-2026/corpus/registry-manifest.json \
        --benign-results benchmarks/false_positive/results.json \
        --out research/state-of-mcp-2026/baseline/mcp-security-baseline-v1.0-2026-07-27.json

Re-measure later against the frozen baseline (one command):
    python research/state-of-mcp-2026/baseline.py \
        --compare research/state-of-mcp-2026/baseline/mcp-security-baseline-v1.0-2026-07-27.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent_audit_kit.rules.builtin import RULES
from agent_audit_kit.scanners.oauth_misconfig import (
    _MCP_INLINE_AUTH_RE,
    _MCP_REMOTE_RE,
    _PRM_DISCOVERY_RE,
)

_HERE = Path(__file__).resolve().parent

# The four posture buckets are always present in the payload, even at zero, so
# a later re-measure diffs against a stable shape.
_POSTURE_BUCKETS = ("no-auth", "bearer", "oauth2.1", "unknown")
_TRANSPORT_BUCKETS = ("stdio", "sse", "streamable-http", "unknown")

_DEFAULT_BASELINE_ID = "mcp-security-baseline-v1.0-2026-07-27"


def _load_run_report() -> Any:
    """Import the sibling harness module to reuse its corpus primitives."""
    spec = importlib.util.spec_from_file_location(
        "somcp_run_report", _HERE / "run_report.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 1) if d else 0.0


def _auth_posture(text: str, rules_here: set[str], is_remote: bool) -> str:
    """Classify one config's auth posture from its content only (offline).

    Priority: an OAuth 2.1 discovery surface (RFC 9728 PRM) outranks a static
    credential header, which outranks a remote server we could not find auth on.
    Local stdio-only configs have no remote auth surface -> ``unknown``.
    """
    if _PRM_DISCOVERY_RE.search(text):
        return "oauth2.1"
    if _MCP_INLINE_AUTH_RE.search(text) and _MCP_REMOTE_RE.search(text):
        return "bearer"
    if "AAK-MCP-001" in rules_here or is_remote:
        return "no-auth"
    return "unknown"


def _collection_window(registry_manifest: Path | None) -> dict[str, str]:
    """The collection window is DATA (read from the manifest), never a runtime
    clock — that is what keeps the payload byte-deterministic."""
    fetched = "unknown"
    if registry_manifest and registry_manifest.is_file():
        try:
            m = json.loads(registry_manifest.read_text(encoding="utf-8"))
            fetched = str(m.get("fetched_at", "unknown"))
        except (ValueError, OSError):
            fetched = "unknown"
    return {
        "registry_fetched_at": fetched,
        "crawl_corpus": "benchmarks/data (GitHub-crawled .mcp.json; gitignored, not redistributed)",
        "note": (
            f"Corpus collected on/before {fetched}; predates the 2026-07-28 MCP "
            "spec revision. Re-measure scheduled for 2026-08-11."
        ),
    }


def _false_positive_rate(benign_results: Path | None) -> dict[str, Any]:
    """Read the benign-slice HIGH/CRITICAL FP rate from the committed benchmark
    results (numerator + denominator). The hand-adjudication (2 FP / 1 TP /
    1 ambiguous = 50% adjudicated) lives in benchmarks/false_positive/triage.md."""
    fp: dict[str, Any] = {
        "source": "benchmarks/false_positive/results.json",
        "benign_slice_n": None,
        "benign_slice_predicate": None,
        "high_critical_findings": None,
        "high_critical_config_rate": None,
        "hand_adjudication": {
            "raters": 1,
            "false_positive": 2,
            "true_positive": 1,
            "ambiguous": 1,
            "adjudicated_fp_rate": 0.5,
            "wilson_95ci": [0.15, 0.85],
            "note": (
                "Single rater; ambiguous counts in the denominator, not as an FP. "
                "Both FPs share one root cause (AAK-MCP-001 not recognising custom "
                "API-key headers). See benchmarks/false_positive/triage.md."
            ),
        },
    }
    if benign_results and benign_results.is_file():
        try:
            b = json.loads(benign_results.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return fp
        n = int(b.get("benign_slice_n", 0)) or None
        hc = int(b.get("configs_with_high_critical", 0))
        fp["benign_slice_n"] = n
        fp["benign_slice_predicate"] = b.get("benign_slice_predicate")
        fp["high_critical_findings"] = b.get("high_critical_findings", hc)
        rate = b.get("high_critical_config_rate")
        fp["high_critical_config_rate"] = (
            round(float(rate), 4) if rate is not None else (round(hc / n, 4) if n else None)
        )
    return fp


def build_snapshot(
    corpus: Path,
    registry_manifest: Path | None,
    benign_results: Path | None,
    *,
    baseline_id: str = _DEFAULT_BASELINE_ID,
    tool_version: str,
    rule_count: int,
) -> dict[str, Any]:
    """Single deterministic corpus pass -> the frozen baseline payload."""
    rr = _load_run_report()
    sources = rr._config_sources(corpus, registry_manifest)

    seen: set[str] = set()
    total = 0
    duplicates = 0
    unparseable = 0
    src_counts: Counter[str] = Counter()
    transport_entries: Counter[str] = Counter()
    posture_counts: Counter[str] = Counter()
    rule_hc_configs: Counter[str] = Counter()
    has_critical = 0
    has_high = 0
    per_config: list[dict[str, Any]] = []

    for ident, text, src in sources:
        key = rr._content_key(text)
        if key is None:
            unparseable += 1
            continue
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)

        result = rr._scan_text(text)
        total += 1
        src_counts[src] += 1

        tr_counts, is_remote = rr._transport_signals(text)
        transport_entries.update(tr_counts)

        rules_here = {f.rule_id for f in result.findings}
        posture = _auth_posture(text, rules_here, is_remote)
        posture_counts[posture] += 1

        sev_here = {f.severity.value for f in result.findings}
        if "critical" in sev_here:
            has_critical += 1
        if "high" in sev_here:
            has_high += 1

        hc_rules = sorted(
            {f.rule_id for f in result.findings if f.severity.value in ("high", "critical")}
        )
        for rid in hc_rules:
            rule_hc_configs[rid] += 1

        # Stable, non-local-path id: public registry name, or a content hash for
        # gitignored crawl configs (never a local filesystem path).
        cid = ident if src == "registry" else f"crawl:{key[:16]}"
        per_config.append(
            {
                "id": cid,
                "source": src,
                "auth_posture": posture,
                "transports": sorted(tr_counts.keys()),
                "high_critical_rules": hc_rules,
            }
        )

    per_config.sort(key=lambda r: (r["id"], r["source"]))

    def _sev(rid: str) -> str:
        r = RULES.get(rid)
        return r.severity.value if r else "?"

    def _title(rid: str) -> str:
        r = RULES.get(rid)
        return r.title if r else rid

    rule_hc = [
        {
            "rule_id": rid,
            "severity": _sev(rid),
            "title": _title(rid),
            "configs": n,
            "config_pct": _pct(n, total),
        }
        for rid, n in sorted(rule_hc_configs.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    registry_n = src_counts.get("registry", 0)

    return {
        "baseline_id": baseline_id,
        "baseline_version": "1.0",
        "schema_version": "1",
        "tool": "agent-audit-kit",
        "tool_version": tool_version,
        "ruleset_rule_count": rule_count,
        "spec_baseline": {
            "measured_against": "pre-2026-07-28 MCP specification revision",
            "re_measure_scheduled": "2026-08-11",
            "post_spec_comparison": "not yet available — the 2026-07-28 spec has not shipped as of this snapshot",
        },
        "collection_window": _collection_window(registry_manifest),
        "corpus": {
            "distinct_configs_scanned": total,
            "total_candidates": len(sources),
            "duplicates_removed": duplicates,
            "unparseable_removed": unparseable,
            "sources": dict(sorted(src_counts.items())),
            "reproducible_subset": {
                "source": "research/state-of-mcp-2026/corpus/registry-manifest.json",
                "n": registry_n,
                "note": (
                    "Only the registry corpus is committed to git; the crawl "
                    "configs are gitignored and not redistributed, so full-corpus "
                    "numbers are not independently re-scannable — the registry "
                    "subset is."
                ),
            },
        },
        "auth_posture_distribution": {
            bucket: {
                "configs": posture_counts.get(bucket, 0),
                "pct": _pct(posture_counts.get(bucket, 0), total),
            }
            for bucket in _POSTURE_BUCKETS
        },
        "transport_distribution": {
            bucket: {"entries": transport_entries.get(bucket, 0)}
            for bucket in _TRANSPORT_BUCKETS
        },
        "configs_with_critical": {"configs": has_critical, "pct": _pct(has_critical, total)},
        "configs_with_high": {"configs": has_high, "pct": _pct(has_high, total)},
        "rule_high_critical_hit_counts": rule_hc,
        "false_positive_rate": _false_positive_rate(benign_results),
        "per_config": per_config,
    }


def canonical_bytes(snapshot: dict[str, Any]) -> bytes:
    """The exact, byte-deterministic serialization the SHA-256 is taken over."""
    return (json.dumps(snapshot, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "utf-8"
    )


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# --compare: diff a later snapshot against the frozen baseline
# ---------------------------------------------------------------------------


def _rate_pct(fp: dict[str, Any]) -> float:
    r = fp.get("high_critical_config_rate")
    return round(100.0 * float(r), 2) if r is not None else 0.0


def compare(base: dict[str, Any], later: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-dimension deltas (absolute + percentage-point) of ``later`` vs ``base``."""
    rows: list[dict[str, Any]] = []

    def add(dim: str, b_abs: float, l_abs: float, b_pct: float | None, l_pct: float | None) -> None:
        rows.append(
            {
                "dimension": dim,
                "baseline": b_abs,
                "later": l_abs,
                "delta_abs": round(l_abs - b_abs, 4),
                "baseline_pct": b_pct,
                "later_pct": l_pct,
                "delta_pp": round(l_pct - b_pct, 2) if (b_pct is not None and l_pct is not None) else None,
            }
        )

    add(
        "corpus.distinct_configs_scanned",
        base["corpus"]["distinct_configs_scanned"],
        later["corpus"]["distinct_configs_scanned"],
        None,
        None,
    )
    for bucket in _POSTURE_BUCKETS:
        b = base["auth_posture_distribution"].get(bucket, {"configs": 0, "pct": 0.0})
        latr = later["auth_posture_distribution"].get(bucket, {"configs": 0, "pct": 0.0})
        add(f"auth_posture.{bucket}", b["configs"], latr["configs"], b["pct"], latr["pct"])
    for bucket in _TRANSPORT_BUCKETS:
        b = base["transport_distribution"].get(bucket, {"entries": 0})["entries"]
        latr = later["transport_distribution"].get(bucket, {"entries": 0})["entries"]
        add(f"transport.{bucket}", b, latr, None, None)
    for key in ("configs_with_critical", "configs_with_high"):
        b = base[key]
        latr = later[key]
        add(key, b["configs"], latr["configs"], b["pct"], latr["pct"])
    bfp, lfp = base["false_positive_rate"], later["false_positive_rate"]
    add(
        "benign_slice_high_critical_findings",
        bfp.get("high_critical_findings") or 0,
        lfp.get("high_critical_findings") or 0,
        _rate_pct(bfp),
        _rate_pct(lfp),
    )
    # Per-rule HIGH/CRITICAL deltas (union of both snapshots' rules).
    b_rules = {r["rule_id"]: r["configs"] for r in base["rule_high_critical_hit_counts"]}
    l_rules = {r["rule_id"]: r["configs"] for r in later["rule_high_critical_hit_counts"]}
    for rid in sorted(set(b_rules) | set(l_rules)):
        add(f"rule.{rid}", b_rules.get(rid, 0), l_rules.get(rid, 0), None, None)
    return rows


def _fmt_delta_table(rows: list[dict[str, Any]], base_id: str, later_id: str) -> str:
    out = [
        f"Baseline: {base_id}",
        f"Later:    {later_id}",
        "",
        f"{'dimension':<44} {'baseline':>10} {'later':>10} {'Δabs':>8} {'Δpp':>8}",
        "-" * 84,
    ]
    for r in rows:
        pp = "" if r["delta_pp"] is None else f"{r['delta_pp']:+.2f}"
        out.append(
            f"{r['dimension']:<44} {r['baseline']:>10} {r['later']:>10} "
            f"{r['delta_abs']:>+8.4g} {pp:>8}"
        )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _tool_version() -> str:
    from agent_audit_kit import __version__

    return __version__


def _rule_count() -> int:
    return len(RULES)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="benchmarks/data")
    parser.add_argument(
        "--registry-manifest",
        default=str(_HERE / "corpus" / "registry-manifest.json"),
    )
    parser.add_argument(
        "--benign-results", default="benchmarks/false_positive/results.json"
    )
    parser.add_argument(
        "--out",
        default=str(_HERE / "baseline" / f"{_DEFAULT_BASELINE_ID}.json"),
    )
    parser.add_argument("--name", default=_DEFAULT_BASELINE_ID, help="baseline_id label")
    parser.add_argument(
        "--compare",
        metavar="BASELINE_FILE",
        default=None,
        help="Diff a freshly-computed snapshot against BASELINE_FILE (the frozen v1.0).",
    )
    args = parser.parse_args(argv)

    corpus = Path(args.corpus)
    if not corpus.is_dir():
        raise SystemExit(
            f"Corpus dir {corpus} not found. The registry manifest alone still "
            "works; populate benchmarks/data for the full corpus."
        )
    reg = Path(args.registry_manifest) if args.registry_manifest else None
    benign = Path(args.benign_results) if args.benign_results else None

    snapshot = build_snapshot(
        corpus,
        reg,
        benign,
        baseline_id=args.name,
        tool_version=_tool_version(),
        rule_count=_rule_count(),
    )

    if args.compare:
        base = json.loads(Path(args.compare).read_text(encoding="utf-8"))
        rows = compare(base, snapshot)
        print(
            _fmt_delta_table(
                rows, base.get("baseline_id", args.compare), snapshot["baseline_id"]
            )
        )
        return 0

    data = canonical_bytes(snapshot)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    digest = sha256_hex(data)
    (out.parent / f"{out.name}.sha256").write_text(
        f"{digest}  {out.name}\n", encoding="utf-8"
    )
    fp = snapshot["false_positive_rate"]
    ap = snapshot["auth_posture_distribution"]
    print(
        f"baseline_id : {snapshot['baseline_id']}\n"
        f"corpus      : {snapshot['corpus']['distinct_configs_scanned']} configs "
        f"({snapshot['corpus']['sources']})\n"
        f"auth posture: no-auth {ap['no-auth']['configs']} ({ap['no-auth']['pct']}%) | "
        f"bearer {ap['bearer']['configs']} | oauth2.1 {ap['oauth2.1']['configs']} | "
        f"unknown {ap['unknown']['configs']}\n"
        f"benign FP   : {fp['high_critical_findings']}/{fp['benign_slice_n']} HIGH/CRITICAL "
        f"({fp['high_critical_config_rate']}) | adjudicated 2/4 = 50%\n"
        f"SHA-256     : {digest}\n"
        f"wrote       : {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
