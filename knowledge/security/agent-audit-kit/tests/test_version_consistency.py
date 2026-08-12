"""Single-source-of-truth fence for the package version.

Four surfaces must never disagree:

1. ``pyproject.toml``'s ``version`` (what PyPI/OIDC publishes).
2. ``agent_audit_kit.__version__`` (what the installed package reports).
3. Every self-referencing ``@vX.Y.Z`` / ``rev: vX.Y.Z`` pin in ``README.md``
   (what we tell users to install).
4. The newest ``vX.Y.Z`` git tag (the version that actually exists to resolve).

Surfaces 1-3 agreeing is not enough: ``@v0.3.61`` matched ``pyproject`` yet no
``v0.3.61`` tag was ever cut, so the README's Action snippet failed to resolve
for everyone who copied it. Surface 4 closes that gap — the pin must point at a
*released* tag, not merely at the declared version.

If a release can't cut the declared tag, the fix is to repin the README to a
tag that *does* resolve (and change the declared version to match) — not to
leave the surfaces disagreeing.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _newest_git_tag() -> str | None:
    """The newest ``vX.Y.Z`` git tag by semantic order, or ``None`` when git or
    the tag list is unavailable (e.g. a shallow CI checkout without tags)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "tag", "-l", "v*"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    versions: list[tuple[tuple[int, int, int], str]] = []
    for line in out.stdout.split():
        m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", line.strip())
        if m:
            versions.append(((int(m[1]), int(m[2]), int(m[3])), line.strip()))
    if not versions:
        return None
    versions.sort()
    return versions[-1][1]


def _pyproject_version() -> str:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert m, "pyproject.toml has no top-level version = \"...\""
    return m.group(1)


def _init_version() -> str:
    from agent_audit_kit import __version__

    return __version__


def test_pyproject_matches_dunder_version() -> None:
    assert _pyproject_version() == _init_version(), (
        f'pyproject version {_pyproject_version()!r} != '
        f'agent_audit_kit.__version__ {_init_version()!r}'
    )


def test_readme_self_pins_match_declared_version() -> None:
    """Every agent-audit-kit self-reference pin in README must equal the declared
    version, so the documented install/CI path always points at a real tag."""
    declared = _init_version()
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    # GitHub Action usage: `uses: sattyamjjain/agent-audit-kit@vX.Y.Z`
    action_pins = re.findall(
        r"sattyamjjain/agent-audit-kit@v(\d+\.\d+\.\d+)", readme
    )
    # pre-commit hook: `rev: vX.Y.Z` (README has one repos block — ours)
    precommit_pins = re.findall(r"rev:\s*v(\d+\.\d+\.\d+)", readme)
    # pip pin: `agent-audit-kit==X.Y.Z`
    pip_pins = re.findall(r"agent-audit-kit==(\d+\.\d+\.\d+)", readme)

    pins = action_pins + precommit_pins + pip_pins
    assert pins, (
        "README has no agent-audit-kit version pin to check — the @vX / rev: vX / "
        "==X snippets went missing; this fence would silently pass on nothing."
    )
    mismatched = [p for p in pins if p != declared]
    assert not mismatched, (
        f"README pins {sorted(set(mismatched))} disagree with declared version "
        f"{declared!r}. Repin the README (and re-cut the tag) so the documented "
        f"install path resolves."
    )


def test_readme_action_pin_matches_newest_git_tag() -> None:
    """The README's ``agent-audit-kit@vX.Y.Z`` Action pin must equal the newest
    git tag, so the documented CI snippet resolves to a real, *released* tag.

    ``test_readme_self_pins_match_declared_version`` proves README pin ==
    pyproject version; this proves README pin == newest released tag. Together
    they force pin == version == tag, which is what catches "version bumped but
    never tagged" — the exact break where README pinned ``@v0.3.61`` while the
    newest tag was ``v0.3.60`` and the action failed to resolve for every user
    who copied the snippet.

    Skips when no ``vX.Y.Z`` tag is reachable (a shallow CI checkout without
    ``fetch-tags``); CI fetches tags (``.github/workflows/ci.yml``) so this
    enforces there. A red result here during a release means: cut the tag.
    """
    newest = _newest_git_tag()
    if newest is None:
        pytest.skip("no vX.Y.Z git tag reachable in this checkout")

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    pins = re.findall(r"sattyamjjain/agent-audit-kit@v\d+\.\d+\.\d+", readme)
    assert pins, "README has no agent-audit-kit@vX.Y.Z Action pin to check"

    bad = sorted({p for p in pins if not p.endswith("@" + newest)})
    assert not bad, (
        f"README Action pin(s) {bad} do not match the newest git tag {newest!r}. "
        f"If you just bumped the version, cut the tag; if the README is behind, run "
        f"`python scripts/sync_repo_metadata.py --write` and re-tag. A pin to an "
        f"untagged version does not resolve for users."
    )
