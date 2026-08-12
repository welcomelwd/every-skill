"""CI fence for the determinism benchmark.

`benchmarks/determinism/run.py` scans a fixed committed corpus N times with the
real engine and asserts one shared finding-set digest (0% variance). This test
runs the benchmark and fails if the engine ever becomes non-deterministic — the
reproducibility claim in `benchmarks/determinism/RESULTS.md` and the README
comparison row is thereby enforced, not just asserted in prose.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "determinism_run", _ROOT / "benchmarks" / "determinism" / "run.py"
)
assert _SPEC and _SPEC.loader
determinism_run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(determinism_run)


def test_twenty_runs_one_digest() -> None:
    data = determinism_run.run_benchmark(runs=20)
    assert data["corpus_size"] > 0, "corpus must be non-empty"
    assert data["distinct_digests"] == 1, (
        f"engine is non-deterministic: {data['distinct_digests']} distinct "
        f"finding-set digests across {data['runs']} runs"
    )
    assert data["digest"], "a single shared SHA-256 digest must be produced"


def test_digest_is_stable_across_independent_invocations() -> None:
    """Two independent benchmark invocations must agree (cross-process-ish)."""
    a = determinism_run.run_benchmark(runs=3)
    b = determinism_run.run_benchmark(runs=3)
    assert a["digest"] == b["digest"], "digest drifted between invocations"


def test_published_results_md_matches_live_run() -> None:
    """The published RESULTS.md must re-verify against a live run.

    RESULTS.md is a public evidence artifact whose whole value is that a reader can
    reproduce the digest on the shipped version. Nothing read it before, so it
    silently staled 18 releases (v0.3.46 / 231 rules -> v0.3.64 / 273 rules) while
    the two tests above stayed green. This fence ties the file to the code: the
    header version/rule-count stamp and the published SHA-256 must both match a
    fresh run, so the next release cannot re-stale it without failing CI.
    """
    import re

    from agent_audit_kit import RULE_COUNT, __version__

    fix = "python benchmarks/determinism/run.py --write"
    results = (_ROOT / "benchmarks" / "determinism" / "RESULTS.md").read_text(
        encoding="utf-8"
    )

    stamp = f"v{__version__} ({RULE_COUNT} rules)"
    assert stamp in results, (
        f"RESULTS.md header does not stamp {stamp!r} — the artifact is stale. "
        f"Regenerate it: `{fix}`."
    )

    m = re.search(
        r"Shared SHA-256 \(finding set\)\s*\|\s*`([0-9a-f]{64})`", results
    )
    assert m, (
        f"RESULTS.md is missing the `Shared SHA-256 (finding set)` digest row. "
        f"Regenerate it: `{fix}`."
    )
    published_digest = m.group(1)
    live_digest = determinism_run.run_benchmark(runs=3)["digest"]
    assert published_digest == live_digest, (
        f"RESULTS.md digest {published_digest} != live-run digest {live_digest}: "
        f"the published evidence no longer reproduces on this version. "
        f"Regenerate it: `{fix}`."
    )
