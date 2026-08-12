"""Single-source-of-truth fence for the State-of-MCP corpus-refresh ``--target``.

``fetch_registry.py --target N`` is the ONE network step in an otherwise offline,
reproducible report. ``fetch()`` stops at ``len(records) >= target or not cursor``,
so a target smaller than the registry's distinct-latest count stops **early** and
yields a corpus that cannot reproduce the published headline N. Four surfaces quote
this command and must agree, and the value must be large enough to walk the whole
registry (``> `` the committed manifest's ``distinct_latest_servers``):

1. ``Makefile`` — the ``corpus`` target (what ``make corpus`` actually runs).
2. ``research/state-of-mcp-2026/fetch_registry.py`` — the argparse default.
3. ``research/state-of-mcp-2026/PREVALENCE.md`` — the published reproduce command.
4. ``research/state-of-mcp-2026/REPORT.md`` — the published reproduce command.

They disagreed once: the Makefile + argparse default said ``700`` while both docs
said ``5000``, so anyone who ran the documented refresh got a ~700-of-1,641 corpus
and a different headline N — in a report whose entire pitch is reproducibility. This
is the same class of guard ``test_version_consistency.py`` plays for the version: a
number published in prose must be gated by a test.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESEARCH = REPO / "research" / "state-of-mcp-2026"
FETCH = RESEARCH / "fetch_registry.py"
PREVALENCE = RESEARCH / "PREVALENCE.md"
REPORT = RESEARCH / "REPORT.md"
MAKEFILE = REPO / "Makefile"
MANIFEST = RESEARCH / "corpus" / "registry-manifest.json"

# `fetch_registry.py --target N` as quoted in the Makefile and the two docs.
_CMD_TARGET_RE = re.compile(r"fetch_registry\.py --target (\d+)")


def _makefile_target() -> int:
    m = _CMD_TARGET_RE.search(MAKEFILE.read_text(encoding="utf-8"))
    assert m, "Makefile `corpus` target has no `fetch_registry.py --target N` line"
    return int(m.group(1))


def _argparse_default() -> int:
    # `parser.add_argument("--target", type=int, default=N, ...)`
    m = re.search(r'--target".*?default=(\d+)', FETCH.read_text(encoding="utf-8"), re.DOTALL)
    assert m, "fetch_registry.py has no `--target` argparse default"
    return int(m.group(1))


def _doc_targets(path: Path) -> list[int]:
    return [int(x) for x in _CMD_TARGET_RE.findall(path.read_text(encoding="utf-8"))]


def test_corpus_target_agrees_across_all_surfaces() -> None:
    mk = _makefile_target()
    ap = _argparse_default()
    prev = _doc_targets(PREVALENCE)
    rep = _doc_targets(REPORT)
    assert prev, "PREVALENCE.md quotes no `fetch_registry.py --target` command"
    assert rep, "REPORT.md quotes no `fetch_registry.py --target` command"
    values = {mk, ap, *prev, *rep}
    assert values == {mk}, (
        f"corpus --target disagrees across surfaces: Makefile={mk}, "
        f"argparse-default={ap}, PREVALENCE.md={prev}, REPORT.md={rep}. "
        "Pick one canonical value and make it true in all four."
    )


def test_corpus_target_walks_whole_registry() -> None:
    """The canonical target must exceed the committed manifest's distinct-latest
    count — otherwise ``make corpus`` stops early (``len(records) >= target``) and
    the documented refresh cannot reproduce the published corpus. This keeps the
    value derived from the manifest, not guessed."""
    target = _makefile_target()
    n = json.loads(MANIFEST.read_text(encoding="utf-8"))["distinct_latest_servers"]
    assert target > n, (
        f"corpus --target ({target}) must exceed the committed manifest's "
        f"distinct_latest_servers ({n}) so the registry walk runs to "
        "cursor-exhaustion rather than stopping early."
    )
