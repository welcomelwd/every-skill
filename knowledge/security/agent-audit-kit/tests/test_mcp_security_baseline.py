"""Guards for the frozen, citable MCP security baseline v1.0.

Ties the committed snapshot to the SHA-256 cited in the research doc (so the
number is tamper-evident), asserts the payload is byte-deterministic across two
runs over the same corpus, and pins the schema (the dimensions a re-measure must
diff against). Fast: a tiny synthetic corpus for determinism + committed-artifact
reads; no full 1,374-config scan.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RESEARCH = REPO / "research" / "state-of-mcp-2026"
SNAPSHOT = RESEARCH / "baseline" / "mcp-security-baseline-v1.0-2026-07-27.json"
SHA_SIDECAR = RESEARCH / "baseline" / "mcp-security-baseline-v1.0-2026-07-27.json.sha256"
DOC = REPO / "docs" / "research" / "mcp-security-baseline-v1.0.md"


def _load_baseline() -> Any:
    spec = importlib.util.spec_from_file_location("aak_baseline", RESEARCH / "baseline.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tiny_corpus(root: Path) -> Path:
    corpus = root / "data"
    corpus.mkdir()
    (corpus / "noauth.json").write_text(
        json.dumps({"mcpServers": {"r": {"type": "http", "url": "https://x/mcp"}}}),
        encoding="utf-8",
    )
    (corpus / "bearer.json").write_text(
        json.dumps(
            {"mcpServers": {"r": {"type": "http", "url": "https://y/mcp",
                                  "headers": {"Authorization": "Bearer t"}}}}
        ),
        encoding="utf-8",
    )
    (corpus / "stdio.json").write_text(
        json.dumps({"mcpServers": {"s": {"command": "python", "args": ["a.py"]}}}),
        encoding="utf-8",
    )
    return corpus


# ---------------------------------------------------------------------------
# Determinism (requirement #2)
# ---------------------------------------------------------------------------


def test_snapshot_is_byte_deterministic(tmp_path: Path) -> None:
    """Two runs over the same corpus produce identical bytes."""
    mod = _load_baseline()
    corpus = _tiny_corpus(tmp_path)
    kw = dict(baseline_id="test", tool_version="9.9.9", rule_count=262)
    a = mod.canonical_bytes(mod.build_snapshot(corpus, None, None, **kw))
    b = mod.canonical_bytes(mod.build_snapshot(corpus, None, None, **kw))
    assert a == b
    # And the SHA-256 over those bytes is therefore stable too.
    assert mod.sha256_hex(a) == mod.sha256_hex(b)


def test_posture_buckets_are_always_present(tmp_path: Path) -> None:
    """All four posture buckets exist even at zero, so a re-measure diffs a
    stable shape."""
    mod = _load_baseline()
    snap = mod.build_snapshot(
        _tiny_corpus(tmp_path), None, None,
        baseline_id="t", tool_version="9.9.9", rule_count=262,
    )
    assert set(snap["auth_posture_distribution"]) == {"no-auth", "bearer", "oauth2.1", "unknown"}
    # The synthetic corpus has one no-auth, one bearer, one stdio (unknown).
    ap = snap["auth_posture_distribution"]
    assert ap["no-auth"]["configs"] == 1
    assert ap["bearer"]["configs"] == 1
    assert ap["unknown"]["configs"] == 1


# ---------------------------------------------------------------------------
# Tamper-evidence (requirement #3): committed snapshot <-> cited SHA-256
# ---------------------------------------------------------------------------


def test_committed_snapshot_matches_sidecar_sha() -> None:
    digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    assert SHA_SIDECAR.read_text(encoding="utf-8").split()[0] == digest


def test_doc_cites_the_exact_sha() -> None:
    digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    assert digest in DOC.read_text(encoding="utf-8"), (
        "docs/research/mcp-security-baseline-v1.0.md must cite the snapshot SHA-256"
    )


# ---------------------------------------------------------------------------
# Schema (requirement #1): the dimensions the baseline must record
# ---------------------------------------------------------------------------


def test_frozen_snapshot_records_required_dimensions() -> None:
    d = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert d["baseline_id"] == "mcp-security-baseline-v1.0-2026-07-27"
    # corpus size + collection window (window is data, not a wall-clock)
    assert d["corpus"]["distinct_configs_scanned"] == 1374
    assert d["collection_window"]["registry_fetched_at"] == "2026-07-19"
    # auth posture, transport
    assert set(d["auth_posture_distribution"]) == {"no-auth", "bearer", "oauth2.1", "unknown"}
    assert set(d["transport_distribution"]) >= {"stdio", "sse", "streamable-http"}
    # per-rule HIGH/CRITICAL hit counts, all high/critical severity
    hc = d["rule_high_critical_hit_counts"]
    assert hc and all(r["severity"] in ("high", "critical") for r in hc)
    # FP rate WITH its denominator
    fp = d["false_positive_rate"]
    assert fp["benign_slice_n"] == 368
    assert fp["high_critical_findings"] == 4
    assert fp["hand_adjudication"]["adjudicated_fp_rate"] == 0.5
    # per config
    assert len(d["per_config"]) == d["corpus"]["distinct_configs_scanned"]


def test_no_wall_clock_timestamp_in_payload() -> None:
    """The payload must carry no runtime timestamp — only the collection window,
    which is data read from the corpus manifest."""
    raw = SNAPSHOT.read_text(encoding="utf-8")
    for banned in ("generated_at", "emitted_at", "timestamp", "run_at"):
        assert banned not in raw, f"payload must not embed a wall-clock field ({banned})"


# ---------------------------------------------------------------------------
# --compare (requirement #4)
# ---------------------------------------------------------------------------


def test_compare_emits_abs_and_pp_deltas() -> None:
    mod = _load_baseline()
    base = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows = mod.compare(base, base)  # self-diff -> all zero deltas
    dims = {r["dimension"] for r in rows}
    assert "corpus.distinct_configs_scanned" in dims
    assert any(d.startswith("auth_posture.") for d in dims)
    assert any(d.startswith("transport.") for d in dims)
    assert any(d.startswith("rule.") for d in dims)
    for r in rows:
        assert r["delta_abs"] == 0
        assert "delta_pp" in r  # present (None where a pp delta is undefined)
