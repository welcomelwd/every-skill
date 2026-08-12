"""Standards crosswalk (rule → NSA MCP CSI + OWASP Agentic) + TASKS-004 (SEP-2663)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from agent_audit_kit.cli import cli
from agent_audit_kit.output import crosswalk
from agent_audit_kit.rules.builtin import RULES
from agent_audit_kit.scanners.mcp_tasks import scan as tasks_scan


# ---------------------------------------------------------------------------
# Crosswalk
# ---------------------------------------------------------------------------


def test_crosswalk_covers_every_rule() -> None:
    rows = crosswalk.build_crosswalk()
    assert {r.rule_id for r in rows} == set(RULES)
    # deterministic order
    assert [r.rule_id for r in rows] == sorted(RULES)


def test_new_pack_rules_map_to_expected_csi_controls() -> None:
    rows = {r.rule_id: r for r in crosswalk.build_crosswalk()}
    routing = " ".join(rows["AAK-MCP-ROUTING-DESYNC-001"].nsa_csi_controls)
    assert "Validate parameters" in routing
    apps1 = " ".join(rows["AAK-MCP-APPS-001"].nsa_csi_controls)
    assert "Constrain and sandbox tool execution" in apps1
    apps2 = " ".join(rows["AAK-MCP-APPS-002"].nsa_csi_controls)
    assert "Filter and monitor output pipelines" in apps2
    tasks4 = " ".join(rows["AAK-TASKS-004"].nsa_csi_controls)
    assert "Design for boundaries" in tasks4
    # OWASP Agentic present
    assert any("ASI05" in a for a in rows["AAK-MCP-APPS-001"].owasp_agentic)
    assert any("ASI08" in a for a in rows["AAK-TASKS-004"].owasp_agentic)


def test_crosswalk_markdown_and_text_render() -> None:
    md = crosswalk.render_markdown()
    assert "AgentAuditKit standards crosswalk" in md
    assert "U/OO/6030316-26" in md  # NSA CSI doc id
    assert "OWASP Agentic Top-10" in md
    assert "`AAK-MCP-APPS-001`" in md
    txt = crosswalk.render_text()
    assert "AAK-TASKS-004" in txt


def test_report_command_emits_crosswalk() -> None:
    res = CliRunner().invoke(cli, ["report", "--framework", "standards-crosswalk", "--format", "text"])
    assert res.exit_code == 0, res.output
    assert "standards crosswalk" in res.output
    assert "AAK-MCP-ROUTING-DESYNC-001" in res.output


# ---------------------------------------------------------------------------
# AAK-TASKS-004 (SEP-2663 task-flood DoS)
# ---------------------------------------------------------------------------


def _tasks(tmp: Path, src: str) -> set[str]:
    (tmp / "tasks.py").write_text(src, encoding="utf-8")
    return {f.rule_id for f in tasks_scan(tmp)[0]}


def test_tasks004_unbounded_create_fires(tmp_path: Path) -> None:
    src = (
        "class TaskStore:\n"
        "    def create_task(self, spec):\n"
        "        self._rows[spec.id] = Task(spec)\n"
        "    def cancel_task(self, i):\n"
        "        pass\n"
        "    expires_at = 1\n"  # has TTL + cancel -> NOT TASKS-003; still no quota -> TASKS-004
    )
    ids = _tasks(tmp_path, src)
    assert "AAK-TASKS-004" in ids
    assert "AAK-TASKS-003" not in ids  # distinct from the TTL/cancel rule


def test_tasks004_with_quota_clears(tmp_path: Path) -> None:
    src = (
        "import asyncio\n"
        "class TaskStore:\n"
        "    _sem = asyncio.Semaphore(10)  # max_concurrent bound\n"
        "    async def create_task(self, spec):\n"
        "        async with self._sem:\n"
        "            self._rows[spec.id] = Task(spec)\n"
        "    expires_at = 1\n"
        "    def cancel_task(self, i):\n"
        "        pass\n"
    )
    assert "AAK-TASKS-004" not in _tasks(tmp_path, src)


def test_tasks004_needs_creation_path(tmp_path: Path) -> None:
    """A read-only task store with no creation path must not fire 004."""
    src = "class TaskStore:\n    def get_task(self, owner, i):\n        return self._rows[i]\n    expires_at = 1\n    def cancel_task(self, i): pass\n"
    assert "AAK-TASKS-004" not in _tasks(tmp_path, src)
