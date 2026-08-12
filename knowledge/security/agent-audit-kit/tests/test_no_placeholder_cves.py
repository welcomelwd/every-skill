"""Guard: no placeholder CVE identifiers in shipped code, the rule bundle, or docs.

A placeholder like ``CVE-2026-99999`` slipping into the rule registry
(``agent_audit_kit/rules/builtin.py``), a rule's ``cve_references``, the signed
``rules.json`` bundle, or the docs would be a *false coverage claim* — the tool
would advertise a CVE that does not exist. This fence sweeps the shipped
surfaces for CVE-shaped identifiers whose sequence number is a known placeholder
and fails with the offending ``file:line``.

Scope is deliberate:
- IN:  ``agent_audit_kit/**``, ``rules.json``, ``docs/**``.
- OUT: ``tests/**`` — fixtures and mocks legitimately use placeholder CVEs (e.g.
  ``tests/test_cve_watcher_dedup.py`` mocks an NVD payload with
  ``CVE-2026-99999``), so scanning tests would flag intended test data. This file
  also lives under ``tests/`` and names the placeholders below, so excluding
  ``tests/`` keeps the guard from tripping on itself.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sequence numbers (the NNNN+ part of CVE-YYYY-NNNN) that only ever appear in
# placeholder / template identifiers, never in a real disclosure.
_PLACEHOLDER_SEQS = {"99999", "999999", "00000", "0000", "12345", "11111"}

# CVE-YYYY-NNNN(+): a 4-digit year then a >=4-digit sequence. Case-insensitive so
# a lowercase "cve-..." slip is still caught; real IDs are uppercase.
_CVE_RE = re.compile(r"CVE-(\d{4})-(\d{4,})", re.IGNORECASE)

# Binary / non-decodable assets we should not try to read as text.
_SKIP_SUFFIXES = {
    ".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico",
    ".woff", ".woff2", ".ttf", ".otf", ".cast", ".gz", ".zip", ".whl",
}


def _target_files() -> list[Path]:
    files: list[Path] = []
    for root_name in ("agent_audit_kit", "docs"):
        root = REPO_ROOT / root_name
        if root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file())
    bundle = REPO_ROOT / "rules.json"
    if bundle.is_file():
        files.append(bundle)

    out: list[Path] = []
    for p in files:
        if "tests" in p.parts:  # explicit tests/ exclusion (see module docstring)
            continue
        if p.suffix.lower() in _SKIP_SUFFIXES:
            continue
        out.append(p)
    return out


def test_no_placeholder_cves_in_shipped_surfaces() -> None:
    offenders: list[str] = []
    for path in _target_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in _CVE_RE.finditer(line):
                if m.group(2) in _PLACEHOLDER_SEQS:
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    offenders.append(f"{rel}:{lineno}: {m.group(0)}")

    assert not offenders, (
        "placeholder CVE identifier(s) found in shipped code / rule bundle / docs "
        "— these are a false coverage claim and must be removed or replaced with a "
        "real CVE:\n  " + "\n  ".join(offenders)
    )
