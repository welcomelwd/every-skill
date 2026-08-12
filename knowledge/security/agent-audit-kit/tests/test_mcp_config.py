from __future__ import annotations

from pathlib import Path

from agent_audit_kit.scanners.mcp_config import scan


def test_vulnerable_mcp_triggers_expected_rules(vulnerable_mcp_project: Path) -> None:
    findings, _ = scan(vulnerable_mcp_project)
    rule_ids = {f.rule_id for f in findings}

    # Must trigger these rules
    assert "AAK-MCP-001" in rule_ids, "Should detect remote server without auth"
    assert "AAK-MCP-002" in rule_ids, "Should detect shell injection in command"
    assert "AAK-MCP-003" in rule_ids, "Should detect hardcoded secrets in env"
    assert "AAK-MCP-004" in rule_ids, "Should detect excessive server count (13 servers)"
    assert "AAK-MCP-005" in rule_ids, "Should detect npx/uvx usage"
    assert "AAK-MCP-006" in rule_ids, "Should detect relative path command"
    assert "AAK-MCP-007" in rule_ids, "Should detect unpinned package version"
    assert "AAK-MCP-008" in rule_ids, "Should detect headersHelper"
    assert "AAK-MCP-009" in rule_ids, "Should detect internal network URL"


def test_clean_mcp_produces_zero_findings(clean_mcp_project: Path) -> None:
    findings, _ = scan(clean_mcp_project)
    assert len(findings) == 0, f"Clean MCP config should produce zero findings, got: {[f.rule_id for f in findings]}"


def test_empty_file(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text("")
    findings, _ = scan(tmp_path)
    assert len(findings) == 0


def test_malformed_json(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text("{not valid json!!!")
    findings, _ = scan(tmp_path)
    assert len(findings) == 0


def test_missing_keys(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {}}')
    findings, _ = scan(tmp_path)
    assert len(findings) == 0


def test_env_variable_references_not_flagged(tmp_path: Path) -> None:
    """Env values that are ${VAR} references should NOT be flagged."""
    import json
    config = {
        "mcpServers": {
            "safe-server": {
                "command": "node",
                "args": ["server.js"],
                "env": {
                    "API_KEY": "${MY_API_KEY}",
                    "SECRET_TOKEN": "${SECRET_FROM_VAULT}"
                }
            }
        }
    }
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    secret_findings = [f for f in findings if f.rule_id == "AAK-MCP-003"]
    assert len(secret_findings) == 0, "Variable references should not be flagged as hardcoded secrets"


def test_authenticated_remote_server_not_flagged(tmp_path: Path) -> None:
    """Remote server WITH auth headers should not trigger AAK-MCP-001."""
    import json
    config = {
        "mcpServers": {
            "authed-remote": {
                "url": "https://mcp.example.com/api",
                "headers": {
                    "Authorization": "Bearer sk-abc123"
                }
            }
        }
    }
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    no_auth_findings = [f for f in findings if f.rule_id == "AAK-MCP-001"]
    assert len(no_auth_findings) == 0


# ---------------------------------------------------------------------------
# #475 — AAK-MCP-001 must recognize custom API-key auth headers (X-*-Key family)
# ---------------------------------------------------------------------------


def test_custom_apikey_header_via_env_not_flagged(tmp_path: Path) -> None:
    """#475 benign case: a vendor-prefixed API-key header whose value is an env
    reference IS the server's declared auth scheme — AAK-MCP-001 must not fire.
    (These were the 2 confirmed benign-slice false positives.)"""
    import json
    config = {
        "mcpServers": {
            "nefesh": {"type": "http", "url": "https://mcp.nefesh.ai/mcp",
                       "headers": {"X-Nefesh-Key": "${SECRET}"}},
            "satoshidata": {"type": "http", "url": "https://satoshidata.ai/mcp/v1/",
                            "headers": {"X-WR-API-Key": "${SECRET}"}},
            "google": {"type": "http", "url": "https://mcp.example.com/mcp",
                       "headers": {"X-Goog-Api-Key": "${GOOGLE_API_KEY}"}},
            "generic": {"type": "http", "url": "https://api.acme.dev/mcp",
                        "headers": {"X-Api-Key": "${ACME_API_KEY}"}},
        }
    }
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    assert not [f for f in findings if f.rule_id == "AAK-MCP-001"], (
        "custom X-*-Key auth headers with env values must not fire AAK-MCP-001"
    )


def test_apikey_placeholder_value_not_flagged(tmp_path: Path) -> None:
    """A placeholder value (YOUR_..._HERE) is a declared-but-unfilled scheme."""
    import json
    config = {"mcpServers": {"s": {"type": "http", "url": "https://x/mcp",
              "headers": {"X-Goog-Api-Key": "YOUR_STITCH_API_KEY_HERE"}}}}
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    assert not [f for f in findings if f.rule_id == "AAK-MCP-001"]


def test_x402_payment_header_not_flagged(tmp_path: Path) -> None:
    """x402 X-PAYMENT gates access (pay-to-access); the endpoint is not openly
    reachable, so AAK-MCP-001 does not fire. Explicit decision for #475."""
    import json
    config = {"mcpServers": {"x402": {"type": "http", "url": "https://api.lattiq.ai/mcp",
              "headers": {"X-PAYMENT": "${SECRET}"}}}}
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    assert not [f for f in findings if f.rule_id == "AAK-MCP-001"]


def test_hardcoded_custom_apikey_literal_still_flagged(tmp_path: Path) -> None:
    """True positive: a custom auth header carrying a HARDCODED literal secret
    exposes the credential in the config, so AAK-MCP-001 still fires."""
    import json
    config = {"mcpServers": {"leaky": {"type": "http", "url": "https://api.acme.dev/mcp",
              "headers": {"X-Acme-Key": "sk-live-9f8e7d6c5b4a3210deadbeefcafef00d"}}}}
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    assert [f for f in findings if f.rule_id == "AAK-MCP-001"], (
        "a hardcoded literal in a custom auth header must still fire AAK-MCP-001"
    )


def test_non_auth_header_only_still_flagged(tmp_path: Path) -> None:
    """Preserved true positive: a remote server whose only header is a non-auth
    header (Accept) has no credential and must still fire (the ai.spala shape)."""
    import json
    config = {"mcpServers": {"public": {"type": "http", "url": "https://mcp.spala.ai/mcp",
              "headers": {"Accept": "application/json"}}}}
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    assert [f for f in findings if f.rule_id == "AAK-MCP-001"], (
        "a non-auth header (Accept) must not suppress AAK-MCP-001"
    )


def test_absolute_path_command_not_flagged(tmp_path: Path) -> None:
    """Commands with absolute paths should not trigger AAK-MCP-006."""
    import json
    config = {
        "mcpServers": {
            "absolute-path": {
                "command": "/usr/local/bin/mcp-server",
                "args": ["--port", "3000"]
            }
        }
    }
    (tmp_path / ".mcp.json").write_text(json.dumps(config))
    findings, _ = scan(tmp_path)
    relative_findings = [f for f in findings if f.rule_id == "AAK-MCP-006"]
    assert len(relative_findings) == 0
