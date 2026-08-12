"""Tests for GDPR compliance module (gdpr_module.py).

Covers: GDPRChecker, pattern detection, compliance checks, templates, reports.
"""

import os
import re
import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

# Add parent dir to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gdpr_module import (
    GDPRChecker,
    GDPR_CONFIG_PATTERNS,
    GDPR_CODE_PATTERNS,
    GDPR_REQUIREMENTS,
    GDPR_GUIDANCE,
    GDPR_TEMPLATES,
    CODE_EXTENSIONS,
    CONFIG_FILE_NAMES,
    MAX_FILES,
    MAX_FILE_SIZE,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project directory."""
    return tmp_path


@pytest.fixture
def project_with_pii(tmp_path):
    """Project with PII fields in Python code."""
    py_file = tmp_path / "models.py"
    py_file.write_text("""
class User:
    email = "user@example.com"
    first_name = "John"
    last_name = "Doe"
    date_of_birth = "1990-01-01"
""")
    return tmp_path


@pytest.fixture
def project_with_config(tmp_path):
    """Project with GDPR-relevant config patterns."""
    req = tmp_path / "requirements.txt"
    req.write_text("""
sqlalchemy>=2.0
stripe>=5.0
bcrypt>=4.0
""")
    return tmp_path


@pytest.fixture
def project_with_tracking(tmp_path):
    """Project with user tracking code."""
    js_file = tmp_path / "analytics.js"
    js_file.write_text("""
analytics.track('page_view', { page: window.location.pathname });
gtag('event', 'conversion');
""")
    return tmp_path


@pytest.fixture
def project_with_cookies(tmp_path):
    """Project with cookie operations."""
    js_file = tmp_path / "cookies.js"
    js_file.write_text("""
document.cookie = "session_id=abc123";
""")
    return tmp_path


@pytest.fixture
def project_with_consent(tmp_path):
    """Project with consent mechanism."""
    py_file = tmp_path / "consent.py"
    py_file.write_text("""
def check_gdpr_consent(user):
    return user.consent is True

def handle_opt_in(user):
    user.opt_in = True
""")
    return tmp_path


@pytest.fixture
def project_with_deletion(tmp_path):
    """Project with data deletion capability."""
    py_file = tmp_path / "delete.py"
    py_file.write_text("""
def delete_account(user_id):
    anonymize(user_id)
""")
    return tmp_path


@pytest.fixture
def project_with_encryption(tmp_path):
    """Project with encryption usage."""
    py_file = tmp_path / "security.py"
    py_file.write_text("""
import hashlib
hashed = bcrypt.hash(password)
""")
    return tmp_path


@pytest.fixture
def project_with_geolocation(tmp_path):
    """Project with geolocation code."""
    js_file = tmp_path / "geo.js"
    js_file.write_text("""
navigator.geolocation.getCurrentPosition(callback);
""")
    return tmp_path


@pytest.fixture
def project_with_uploads(tmp_path):
    """Project with file upload code."""
    py_file = tmp_path / "uploads.py"
    py_file.write_text("""
class Document:
    file = FileField(upload_to='docs/')
""")
    return tmp_path


@pytest.fixture
def project_with_db_queries(tmp_path):
    """Project with database queries on user data."""
    py_file = tmp_path / "queries.py"
    py_file.write_text("""
result = db.execute("SELECT * FROM users WHERE id = ?", user_id)
User.objects.filter(email=email)
""")
    return tmp_path


@pytest.fixture
def project_with_ip_logging(tmp_path):
    """Project with IP logging."""
    py_file = tmp_path / "middleware.py"
    py_file.write_text("""
def log_request(request):
    ip = request.remote_addr
    logger.info(f"Request from {ip}")
""")
    return tmp_path


@pytest.fixture
def project_with_export(tmp_path):
    """Project with data export functionality."""
    py_file = tmp_path / "export.py"
    py_file.write_text("""
def export_data(user_id):
    data = get_user_data(user_id)
    return data.to_csv()
""")
    return tmp_path


@pytest.fixture
def full_project(tmp_path):
    """Project with multiple GDPR patterns."""
    # PII in code
    (tmp_path / "models.py").write_text("email = 'test@test.com'\nfirst_name = 'Test'")
    # Tracking
    (tmp_path / "track.js").write_text("analytics.track('event');")
    # Config
    (tmp_path / "requirements.txt").write_text("sqlalchemy>=2.0\nstripe>=5.0")
    # Consent
    (tmp_path / "consent.py").write_text("def check_consent(): pass")
    # Encryption
    (tmp_path / "crypto.py").write_text("bcrypt.hash(pwd)")
    # GDPR docs
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "PRIVACY_POLICY.md").write_text("# Privacy Policy\nOur company processes data for services.")
    (docs / "DPIA.md").write_text("# DPIA\n[Your company name]\n[e.g. analytics]\n[Date]")
    (docs / "RECORDS_OF_PROCESSING.md").write_text("# Records\nProcessing activities documented.")
    (docs / "DATA_BREACH_PROCEDURE.md").write_text("# Breach Procedure\nReport within 72h.")
    (docs / "DPA.md").write_text("# Data Processing Agreement")
    return tmp_path


# ============================================================
# Tests: Constants and Patterns
# ============================================================

class TestConstants:
    """Test that constants are properly defined."""

    def test_gdpr_config_patterns_not_empty(self):
        assert len(GDPR_CONFIG_PATTERNS) >= 8
        for category, patterns in GDPR_CONFIG_PATTERNS.items():
            assert len(patterns) > 0, f"Empty patterns for {category}"

    def test_gdpr_code_patterns_not_empty(self):
        assert len(GDPR_CODE_PATTERNS) >= 10
        for category, patterns in GDPR_CODE_PATTERNS.items():
            assert len(patterns) > 0, f"Empty patterns for {category}"

    def test_gdpr_requirements_roles(self):
        assert "controller" in GDPR_REQUIREMENTS
        assert "processor" in GDPR_REQUIREMENTS
        assert "minimal_processing" in GDPR_REQUIREMENTS
        for role, info in GDPR_REQUIREMENTS.items():
            assert "description" in info
            assert "requirements" in info
            assert len(info["requirements"]) > 0

    def test_gdpr_guidance_keys(self):
        expected = ["privacy_policy", "consent_mechanism", "data_subject_rights",
                    "dpia", "data_breach_procedure", "security_measures",
                    "records_of_processing", "dpa"]
        for key in expected:
            assert key in GDPR_GUIDANCE
            g = GDPR_GUIDANCE[key]
            assert "what" in g
            assert "why" in g
            assert "how" in g
            assert "gdpr_article" in g
            assert "effort" in g

    def test_gdpr_templates_keys(self):
        expected = ["privacy_policy", "dpia", "records_of_processing", "data_breach_procedure"]
        for key in expected:
            assert key in GDPR_TEMPLATES
            t = GDPR_TEMPLATES[key]
            assert "filename" in t
            assert "content" in t
            assert len(t["content"]) > 100

    def test_code_extensions(self):
        assert ".py" in CODE_EXTENSIONS
        assert ".js" in CODE_EXTENSIONS
        assert ".ts" in CODE_EXTENSIONS

    def test_config_file_names(self):
        assert "requirements.txt" in CONFIG_FILE_NAMES
        assert "package.json" in CONFIG_FILE_NAMES
        assert "pyproject.toml" in CONFIG_FILE_NAMES

    def test_max_limits(self):
        assert MAX_FILES == 5000
        assert MAX_FILE_SIZE == 1_000_000

    def test_patterns_are_valid_regex(self):
        """All patterns should compile as valid regex."""
        for category, patterns in GDPR_CODE_PATTERNS.items():
            for p in patterns:
                re.compile(p, re.IGNORECASE)
        for category, patterns in GDPR_CONFIG_PATTERNS.items():
            for p in patterns:
                re.compile(p, re.IGNORECASE)


# ============================================================
# Tests: GDPRChecker Init
# ============================================================

class TestGDPRCheckerInit:

    def test_init_sets_path(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        assert checker.project_path == tmp_project

    def test_init_empty_state(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        assert checker.detected_patterns == {}
        assert checker.files_scanned == 0
        assert checker.flagged_files == []


# ============================================================
# Tests: scan_project
# ============================================================

class TestScanProject:

    def test_scan_nonexistent_path(self):
        checker = GDPRChecker("/nonexistent/path")
        result = checker.scan_project()
        assert "error" in result

    def test_scan_empty_project(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.scan_project()
        assert result["files_scanned"] == 0
        assert result["detected_patterns"] == {}
        assert result["flagged_files"] == []
        assert "processing_summary" in result

    def test_scan_detects_pii(self, project_with_pii):
        checker = GDPRChecker(str(project_with_pii))
        result = checker.scan_project()
        assert result["files_scanned"] == 1
        assert "pii_fields" in result["detected_patterns"]
        assert len(result["flagged_files"]) > 0

    def test_scan_detects_config_patterns(self, project_with_config):
        checker = GDPRChecker(str(project_with_config))
        result = checker.scan_project()
        assert result["files_scanned"] >= 1
        assert "database_orm" in result["detected_patterns"] or "payment" in result["detected_patterns"]

    def test_scan_detects_tracking(self, project_with_tracking):
        checker = GDPRChecker(str(project_with_tracking))
        result = checker.scan_project()
        assert "user_tracking" in result["detected_patterns"]

    def test_scan_detects_cookies(self, project_with_cookies):
        checker = GDPRChecker(str(project_with_cookies))
        result = checker.scan_project()
        assert "cookie_operations" in result["detected_patterns"]

    def test_scan_detects_consent(self, project_with_consent):
        checker = GDPRChecker(str(project_with_consent))
        result = checker.scan_project()
        assert "consent_mechanism" in result["detected_patterns"]

    def test_scan_detects_encryption(self, project_with_encryption):
        checker = GDPRChecker(str(project_with_encryption))
        result = checker.scan_project()
        assert "encryption_usage" in result["detected_patterns"]

    def test_scan_detects_ip_logging(self, project_with_ip_logging):
        checker = GDPRChecker(str(project_with_ip_logging))
        result = checker.scan_project()
        assert "ip_logging" in result["detected_patterns"]

    def test_scan_detects_geolocation(self, project_with_geolocation):
        checker = GDPRChecker(str(project_with_geolocation))
        result = checker.scan_project()
        assert "geolocation" in result["detected_patterns"]

    def test_scan_detects_uploads(self, project_with_uploads):
        checker = GDPRChecker(str(project_with_uploads))
        result = checker.scan_project()
        assert "file_uploads" in result["detected_patterns"]

    def test_scan_detects_db_queries(self, project_with_db_queries):
        checker = GDPRChecker(str(project_with_db_queries))
        result = checker.scan_project()
        assert "database_queries" in result["detected_patterns"]

    def test_scan_detects_data_deletion(self, project_with_deletion):
        checker = GDPRChecker(str(project_with_deletion))
        result = checker.scan_project()
        assert "data_deletion" in result["detected_patterns"]

    def test_scan_detects_data_export(self, project_with_export):
        checker = GDPRChecker(str(project_with_export))
        result = checker.scan_project()
        assert "data_export" in result["detected_patterns"]

    def test_scan_skips_large_files(self, tmp_path):
        """Files larger than MAX_FILE_SIZE should be skipped."""
        large_file = tmp_path / "large.py"
        large_file.write_text("x" * (MAX_FILE_SIZE + 1))
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert result["files_scanned"] == 0

    def test_scan_skips_non_code_files(self, tmp_path):
        """Non-code, non-config files should be skipped."""
        (tmp_path / "readme.txt").write_text("email = test@test.com")
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert result["files_scanned"] == 0

    def test_scan_full_project(self, full_project):
        checker = GDPRChecker(str(full_project))
        result = checker.scan_project()
        assert result["files_scanned"] >= 4
        assert "pii_fields" in result["detected_patterns"]
        assert result["processing_summary"]["processes_personal_data"] is True


# ============================================================
# Tests: _summarize_processing
# ============================================================

class TestSummarizeProcessing:

    def test_low_risk_empty(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert summary["risk_level"] == "low"
        assert summary["processes_personal_data"] is False
        assert summary["processing_role"] == "minimal_processing"

    def test_medium_risk_with_pii(self, project_with_pii):
        checker = GDPRChecker(str(project_with_pii))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert summary["risk_level"] in ("medium", "high")
        assert summary["processes_personal_data"] is True
        assert summary["processing_role"] == "controller"

    def test_high_risk_multiple_factors(self, tmp_path):
        """PII + tracking + geolocation = high risk."""
        (tmp_path / "app.py").write_text("""
email = "test@test.com"
first_name = "John"
""")
        (tmp_path / "track.js").write_text("analytics.track('event');")
        (tmp_path / "geo.js").write_text("navigator.geolocation.getCurrentPosition(cb);")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert summary["risk_level"] == "high"
        assert summary["risk_factors"] >= 3

    def test_positive_signals_consent(self, tmp_path):
        """Consent mechanism detected as positive signal."""
        (tmp_path / "consent.py").write_text("def handle_consent(): pass")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert "Consent mechanism detected" in summary["positive_signals"]

    def test_positive_signals_deletion(self, project_with_deletion):
        checker = GDPRChecker(str(project_with_deletion))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert "Data deletion/export capability detected" in summary["positive_signals"]

    def test_positive_signals_encryption(self, project_with_encryption):
        checker = GDPRChecker(str(project_with_encryption))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert "Encryption usage detected" in summary["positive_signals"]

    def test_tracking_only_is_processor(self, project_with_tracking):
        checker = GDPRChecker(str(project_with_tracking))
        checker.scan_project()
        summary = checker._summarize_processing()
        assert summary["processing_role"] == "processor"


# ============================================================
# Tests: check_compliance
# ============================================================

class TestCheckCompliance:

    def test_invalid_role(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.check_compliance("invalid_role")
        assert "error" in result

    def test_controller_compliance_empty(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        checker.scan_project()
        result = checker.check_compliance("controller")
        assert result["processing_role"] == "controller"
        assert "compliance_status" in result
        assert "compliance_score" in result
        assert "compliance_percentage" in result
        assert result["compliance_percentage"] == 0.0

    def test_processor_compliance(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        checker.scan_project()
        result = checker.check_compliance("processor")
        assert result["processing_role"] == "processor"
        # Processor has fewer requirements
        assert "dpia" not in result["compliance_status"]

    def test_minimal_processing_compliance(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        checker.scan_project()
        result = checker.check_compliance("minimal_processing")
        assert result["processing_role"] == "minimal_processing"

    def test_controller_with_docs(self, full_project):
        checker = GDPRChecker(str(full_project))
        checker.scan_project()
        result = checker.check_compliance("controller")
        status = result["compliance_status"]
        assert status["privacy_policy"] is True
        assert status["dpia"] is True
        assert status["records_of_processing"] is True
        assert status["data_breach_procedure"] is True
        assert status["dpa"] is True
        assert result["compliance_percentage"] > 0

    def test_compliance_detects_consent(self, tmp_path):
        (tmp_path / "app.py").write_text("user_consent = True")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        result = checker.check_compliance("controller")
        assert result["compliance_status"]["consent_mechanism"] is True

    def test_compliance_detects_encryption(self, tmp_path):
        (tmp_path / "sec.py").write_text("bcrypt.hash(password)")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        result = checker.check_compliance("controller")
        assert result["compliance_status"]["security_measures"] is True

    def test_quality_notes_unfilled_template(self, tmp_path):
        """Unfilled templates should generate quality notes."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "PRIVACY_POLICY.md").write_text(
            "# Privacy\n[Your company name]\n[Email address]\n[Date]\n[Duration]"
        )
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        result = checker.check_compliance("controller")
        assert "quality_notes" in result
        if result["compliance_status"].get("privacy_policy"):
            assert "privacy_policy" in result["quality_notes"]

    def test_quality_notes_customized(self, full_project):
        """Customized docs should not have quality notes."""
        checker = GDPRChecker(str(full_project))
        checker.scan_project()
        result = checker.check_compliance("controller")
        # The privacy policy in full_project is customized (no [brackets])
        quality = result.get("quality_notes", {})
        assert "privacy_policy" not in quality


# ============================================================
# Tests: _check_file and _check_file_quality
# ============================================================

class TestFileChecks:

    def test_check_file_root(self, tmp_path):
        (tmp_path / "PRIVACY_POLICY.md").write_text("# Privacy")
        checker = GDPRChecker(str(tmp_path))
        assert checker._check_file("PRIVACY_POLICY.md") is True

    def test_check_file_docs_dir(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "DPIA.md").write_text("# DPIA")
        checker = GDPRChecker(str(tmp_path))
        assert checker._check_file("DPIA.md") is True

    def test_check_file_missing(self, tmp_path):
        checker = GDPRChecker(str(tmp_path))
        assert checker._check_file("NONEXISTENT.md") is False

    def test_check_file_quality_customized(self, tmp_path):
        (tmp_path / "PRIVACY_POLICY.md").write_text(
            "# Privacy Policy\nWe at ArkForge process your data for service delivery."
        )
        checker = GDPRChecker(str(tmp_path))
        quality = checker._check_file_quality("PRIVACY_POLICY.md")
        assert quality["exists"] is True
        assert quality["customized"] is True
        assert quality["unfilled_placeholders"] <= 2

    def test_check_file_quality_template(self, tmp_path):
        (tmp_path / "DPIA.md").write_text(
            "[Your company name]\n[Email address]\n[Date]\n[Duration]\n[Role]\n[Describe]"
        )
        checker = GDPRChecker(str(tmp_path))
        quality = checker._check_file_quality("DPIA.md")
        assert quality["exists"] is True
        assert quality["customized"] is False
        assert quality["unfilled_placeholders"] > 2

    def test_check_file_quality_missing(self, tmp_path):
        checker = GDPRChecker(str(tmp_path))
        quality = checker._check_file_quality("NONEXISTENT.md")
        assert quality["exists"] is False


# ============================================================
# Tests: generate_report
# ============================================================

class TestGenerateReport:

    def test_report_structure(self, full_project):
        checker = GDPRChecker(str(full_project))
        scan = checker.scan_project()
        compliance = checker.check_compliance("controller")
        report = checker.generate_report(scan, compliance)

        assert "report_date" in report
        assert report["regulation"] == "GDPR"
        assert "project_path" in report
        assert "scan_summary" in report
        assert "processing_summary" in report
        assert "compliance_summary" in report
        assert "recommendations" in report

    def test_report_date_format(self, full_project):
        checker = GDPRChecker(str(full_project))
        scan = checker.scan_project()
        compliance = checker.check_compliance("controller")
        report = checker.generate_report(scan, compliance)
        # Should be ISO format
        datetime.fromisoformat(report["report_date"])

    def test_report_recommendations_pass(self, full_project):
        checker = GDPRChecker(str(full_project))
        scan = checker.scan_project()
        compliance = checker.check_compliance("controller")
        report = checker.generate_report(scan, compliance)
        passed = [r for r in report["recommendations"] if r["status"] == "PASS"]
        assert len(passed) > 0

    def test_report_recommendations_fail(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        scan = checker.scan_project()
        compliance = checker.check_compliance("controller")
        report = checker.generate_report(scan, compliance)
        failed = [r for r in report["recommendations"] if r["status"] == "FAIL"]
        assert len(failed) > 0
        for rec in failed:
            assert "what" in rec
            assert "why" in rec
            assert "how" in rec

    def test_report_scan_summary(self, full_project):
        checker = GDPRChecker(str(full_project))
        scan = checker.scan_project()
        compliance = checker.check_compliance("controller")
        report = checker.generate_report(scan, compliance)
        assert report["scan_summary"]["files_scanned"] > 0
        assert report["scan_summary"]["flagged_files"] >= 0

    def test_report_empty_scan(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        report = checker.generate_report({}, {})
        assert report["scan_summary"]["files_scanned"] == 0
        assert report["compliance_summary"]["compliance_score"] == "0/0"


# ============================================================
# Tests: get_templates
# ============================================================

class TestGetTemplates:

    def test_controller_templates(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("controller")
        assert result["regulation"] == "GDPR"
        assert result["processing_role"] == "controller"
        assert result["templates_count"] == 4
        assert "privacy_policy" in result["templates"]
        assert "dpia" in result["templates"]
        assert "records_of_processing" in result["templates"]
        assert "data_breach_procedure" in result["templates"]

    def test_processor_templates(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("processor")
        assert result["templates_count"] == 2
        assert "records_of_processing" in result["templates"]
        assert "data_breach_procedure" in result["templates"]

    def test_minimal_processing_templates(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("minimal_processing")
        assert result["templates_count"] == 1
        assert "privacy_policy" in result["templates"]

    def test_unknown_role_fallback(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("unknown_role")
        assert result["templates_count"] == 1
        assert "privacy_policy" in result["templates"]

    def test_template_content(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("controller")
        for name, tmpl in result["templates"].items():
            assert "filename" in tmpl
            assert "content" in tmpl
            assert "instructions" in tmpl
            assert tmpl["filename"].startswith("docs/")

    def test_template_usage_note(self, tmp_project):
        checker = GDPRChecker(str(tmp_project))
        result = checker.get_templates("controller")
        assert "usage" in result
        assert "docs/" in result["usage"]


# ============================================================
# Tests: Config pattern detection
# ============================================================

class TestConfigPatterns:

    def test_detect_database_orm(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("sqlalchemy>=2.0")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "database_orm" in checker.detected_patterns

    def test_detect_analytics(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"mixpanel": "^2.0"}}')
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "analytics" in checker.detected_patterns

    def test_detect_email_service(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"sendgrid": "^7.0"}}')
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "email_service" in checker.detected_patterns

    def test_detect_auth_provider(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"passport": "^0.6"}}')
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "auth_provider" in checker.detected_patterns

    def test_detect_payment(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("stripe>=5.0")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "payment" in checker.detected_patterns

    def test_detect_cookie_tracking(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"js-cookie": "^3.0"}}')
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "cookie_tracking" in checker.detected_patterns

    def test_detect_cloud_storage(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"aws-sdk": "^3.0"}}')
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "cloud_storage" in checker.detected_patterns

    def test_detect_encryption_config(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("bcrypt>=4.0")
        checker = GDPRChecker(str(tmp_path))
        checker.scan_project()
        assert "encryption" in checker.detected_patterns


# ============================================================
# Tests: Edge cases
# ============================================================

class TestEdgeCases:

    def test_binary_file_in_project(self, tmp_path):
        """Binary files should not crash the scanner."""
        (tmp_path / "image.py").write_bytes(b"\x00\x01\x02\x03\xff\xfe")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert result["files_scanned"] >= 1

    def test_empty_python_file(self, tmp_path):
        (tmp_path / "empty.py").write_text("")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert result["files_scanned"] == 1
        assert len(result["flagged_files"]) == 0

    def test_multiple_patterns_same_file(self, tmp_path):
        (tmp_path / "app.py").write_text("""
email = "test@test.com"
SELECT * FROM users WHERE id = 1
document.cookie = "session"
request.remote_addr
""")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert len(result["detected_patterns"]) >= 2

    def test_relative_path(self, tmp_path):
        (tmp_path / "app.py").write_text("email = 'x@x.com'")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        for flagged in result["flagged_files"]:
            assert not flagged["file"].startswith("/")

    def test_nested_project(self, tmp_path):
        sub = tmp_path / "src" / "app"
        sub.mkdir(parents=True)
        (sub / "models.py").write_text("email = 'test@test.com'")
        checker = GDPRChecker(str(tmp_path))
        result = checker.scan_project()
        assert result["files_scanned"] >= 1
        assert "pii_fields" in result["detected_patterns"]
