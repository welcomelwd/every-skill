"""`aak watch-cve` CVE-feed poller.

Polls disclosed-CVE feeds (OX timeline, CERT/CC, ThaiCERT advisories,
IronPlate weekly intel) and surfaces entries that AAK does not yet cover. The
daemon is intentionally minimal — fetch, dedupe, dispatch — so a downstream
operator can wire it into Slack / a webhook / a GitHub-issue creator without
taking on a heavyweight runtime.

**Status: [experimental] — no live feed fetchers are wired yet.** Every entry in
`FEED_REGISTRY` is `_stub_fetcher`, which raises `NotImplementedError`. Rather
than fetch nothing and exit 0 (which looks like a clean run that found no new
CVEs), `run_watch` classifies its feeds up front, prints `feed <id>: NOT
IMPLEMENTED` for each stub, and exits non-zero when *every* configured feed is a
stub. A real fetcher can be registered by overriding `FEED_REGISTRY[<id>]` with
a callable returning `list[dict]`; `run_watch` then polls only the live feeds.

`run_watch(feed_ids, emit, interval_seconds, max_iterations, dry_run)` is the
entry point. Each iteration over the *live* feeds:

    1. Fetch the feed.
    2. Diff against the local "seen" set in `~/.agent-audit-kit/watch-state.json`.
    3. For every new entry without an AAK rule mapping, emit a notification
       (or, in dry-run, print the body to stdout).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable


_STATE_DIR = Path(os.environ.get("AAK_HOME", str(Path.home() / ".agent-audit-kit")))
_STATE_FILE = _STATE_DIR / "watch-state.json"


def _load_state() -> dict[str, Any]:
    if not _STATE_FILE.is_file():
        return {"seen": []}
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"seen": []}


def _save_state(state: dict[str, Any]) -> None:
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    _STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _stub_fetcher(feed_id: str) -> list[dict[str, Any]]:
    """Explicitly-unimplemented feed fetcher. Raises so `aak watch-cve` fails
    loud instead of silently reporting an empty feed.

    `run_watch` never calls this directly — it detects stub feeds by identity
    and reports them as NOT IMPLEMENTED — but raising keeps the contract honest
    for any caller that invokes a stub fetcher through `FEED_REGISTRY`. Tests
    inject a real fetcher by overriding `FEED_REGISTRY[<id>]`.
    """
    raise NotImplementedError(
        f"feed {feed_id!r} has no fetcher — `aak watch-cve` is an experimental "
        "stub and ships no live CVE feeds. File an issue at "
        "https://github.com/sattyamjjain/agent-audit-kit/issues if you need it."
    )


FEED_REGISTRY: dict[str, Callable[[str], list[dict[str, Any]]]] = {
    "ox": _stub_fetcher,
    "cert-cc": _stub_fetcher,
    "thaicert": _stub_fetcher,
    "ironplate": _stub_fetcher,
}


def _emit(target: str | None, payload: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run or target is None:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        sys.stdout.flush()
        return
    # Notification sinks are not implemented. Log to stderr so consumers know
    # the daemon isn't silently dropping events.
    sys.stderr.write(
        f"[aak watch] sink {target!r} not implemented; payload follows:\n"
    )
    sys.stderr.write(json.dumps(payload, indent=2) + "\n")
    sys.stderr.flush()


def run_watch(
    *,
    feed_ids: list[str],
    emit: str | None,
    interval_seconds: int,
    max_iterations: int,
    dry_run: bool,
) -> int:
    """Run the watch loop over the *live* feeds.

    Returns 0 on a clean poll of at least one live feed, and non-zero (2) when
    every configured feed is an unimplemented stub — so a run that could only
    ever find nothing fails loud instead of masquerading as success.
    """
    unknown = [f for f in feed_ids if f not in FEED_REGISTRY]
    stub = [f for f in feed_ids if FEED_REGISTRY.get(f) is _stub_fetcher]
    live = [
        f for f in feed_ids
        if f in FEED_REGISTRY and FEED_REGISTRY.get(f) is not _stub_fetcher
    ]

    for feed_id in unknown:
        sys.stderr.write(f"[aak watch] unknown feed: {feed_id}\n")
    for feed_id in stub:
        sys.stderr.write(f"[aak watch] feed {feed_id}: NOT IMPLEMENTED\n")

    if not live:
        sys.stderr.write(
            "[aak watch] no live feed fetchers configured — `aak watch-cve` is "
            "[experimental] and ships no live CVE feeds. Exiting non-zero so this "
            "does not look like a clean run that found nothing.\n"
        )
        sys.stderr.flush()
        return 2

    state = _load_state()
    seen: set[str] = set(state.get("seen", []) or [])
    iteration = 0
    try:
        while True:
            iteration += 1
            for feed_id in live:
                fetcher = FEED_REGISTRY[feed_id]
                try:
                    entries = fetcher(feed_id)
                except Exception as exc:  # noqa: BLE001 — keep daemon alive
                    sys.stderr.write(f"[aak watch] {feed_id} fetch failed: {exc}\n")
                    continue
                for entry in entries:
                    cve = entry.get("cve_id") or entry.get("id")
                    if not cve or cve in seen:
                        continue
                    seen.add(cve)
                    _emit(
                        emit,
                        {
                            "feed": feed_id,
                            "cve": cve,
                            "title": entry.get("title", ""),
                            "url": entry.get("url", ""),
                            "covered": False,
                        },
                        dry_run=dry_run,
                    )
            state["seen"] = sorted(seen)
            _save_state(state)
            if max_iterations and iteration >= max_iterations:
                return 0
            time.sleep(max(1, interval_seconds))
    except KeyboardInterrupt:
        return 0


__all__ = ["FEED_REGISTRY", "run_watch"]
