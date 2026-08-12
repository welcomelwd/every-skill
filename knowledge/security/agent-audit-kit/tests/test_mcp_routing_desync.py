"""AAK-MCP-ROUTING-DESYNC-001 — SEP-2243 routable-header ↔ body desync."""

from __future__ import annotations

from pathlib import Path

from agent_audit_kit.rules.builtin import RULES
from agent_audit_kit.scanners.mcp_routing_desync import scan

RULE = "AAK-MCP-ROUTING-DESYNC-001"


def _ids(tmp: Path, name: str, src: str) -> set[str]:
    (tmp / name).write_text(src, encoding="utf-8")
    return {f.rule_id for f in scan(tmp)[0]}


def test_rule_registered() -> None:
    assert RULE in RULES
    r = RULES[RULE]
    assert r.severity.value == "high"
    assert r.category.value == "transport-security"
    assert "MCP07:2025" in r.owasp_mcp_references


def test_routes_on_header_without_body_check_fires(tmp_path: Path) -> None:
    src = (
        "from mcp.server import FastMCP\n"
        "def handle(request):\n"
        "    method = request.headers.get('Mcp-Method')\n"
        "    if method in ALLOWED_ROUTES:\n"
        "        return dispatch(method)\n"
    )
    assert RULE in _ids(tmp_path, "server.py", src)


def test_ts_router_on_mcp_name_header_fires(tmp_path: Path) -> None:
    src = (
        "// McpServer gateway\n"
        "const name = req.headers['mcp-name'];\n"
        "if (allowlist.has(name)) { return router.forward(name); }\n"
    )
    assert RULE in _ids(tmp_path, "gateway.ts", src)


def test_body_crosscheck_suppresses(tmp_path: Path) -> None:
    """The correct guard — header must equal the JSON-RPC body method — clears."""
    src = (
        "from mcp.server import FastMCP\n"
        "def handle(request):\n"
        "    method = request.headers.get('Mcp-Method')\n"
        "    body = request.json()\n"
        "    if method != body['method']:\n"
        "        raise ValueError('routing desync')\n"
        "    return dispatch(body['method'])\n"
    )
    assert RULE not in _ids(tmp_path, "server.py", src)


def test_no_routing_use_does_not_fire(tmp_path: Path) -> None:
    """Reading the header for logging only (no routing/authz) must not fire."""
    src = (
        "from mcp.server import FastMCP\n"
        "def handle(request):\n"
        "    logger.info('method header: %s', request.headers.get('Mcp-Method'))\n"
        "    return process(request.json())\n"
    )
    assert RULE not in _ids(tmp_path, "server.py", src)


def test_non_mcp_file_ignored(tmp_path: Path) -> None:
    src = "def h(req):\n    m = req.headers.get('Mcp-Method')\n    return route(m)\n"
    assert RULE not in _ids(tmp_path, "plain.py", src)
