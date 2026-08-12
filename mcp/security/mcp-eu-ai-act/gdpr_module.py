"""
GDPR Compliance Module — Regulation module for the multi-regulation compliance scanner.

Detects personal data processing patterns in codebases and checks GDPR compliance.
Same engine as EU AI Act: scan codebase → rules → rapport.

Architecture: This module provides GDPR-specific data (patterns, checks, templates).
The server.py imports and exposes GDPR tools via MCP.
"""

import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

# ============================================================
# GDPR — Data Processing Detection Patterns
# ============================================================

# Config/manifest patterns: libraries that process personal data
GDPR_CONFIG_PATTERNS = {
    "database_orm": [
        r'"sqlalchemy"', r"\bsqlalchemy\s*[>=<~!]",
        r'"django"', r"\bdjango\s*[>=<~!]",
        r'"sequelize"', r'"prisma"', r'"mongoose"',
        r'"typeorm"', r'"peewee"', r'"tortoise-orm"',
    ],
    "analytics": [
        r'"google-analytics"', r'"@google-analytics/',
        r'"segment"', r'"mixpanel"', r'"amplitude"',
        r'"posthog"', r'"plausible"', r'"matomo"',
    ],
    "email_service": [
        r'"sendgrid"', r'"mailgun"', r'"nodemailer"',
        r'"mailchimp"', r'"ses"', r'"postmark"',
    ],
    "auth_provider": [
        r'"passport"', r'"auth0"', r'"firebase-admin"',
        r'"keycloak"', r'"next-auth"', r'"supertokens"',
        r'"python-jose"', r'"pyjwt"',
    ],
    "payment": [
        r'"stripe"', r"\bstripe\s*[>=<~!]",
        r'"braintree"', r'"paypal"',
    ],
    "cookie_tracking": [
        r'"cookie-parser"', r'"js-cookie"',
        r'"react-cookie"', r'"cookies-next"',
    ],
    "cloud_storage": [
        r'"boto3"', r'"aws-sdk"', r'"@aws-sdk/',
        r'"google-cloud-storage"', r'"azure-storage"',
    ],
    "encryption": [
        r'"bcrypt"', r"\bbcrypt\s*[>=<~!]",
        r'"argon2"', r'"cryptography"',
        r'"passlib"', r'"python-dotenv"',
    ],
}

# Source code patterns: indicators of personal data processing
GDPR_CODE_PATTERNS = {
    "pii_fields": [
        r"\bemail\b.*=",
        r"\bphone\b.*=",
        r"\baddress\b.*=",
        r"\bfirst_name\b", r"\blast_name\b", r"\bfull_name\b",
        r"\bdate_of_birth\b", r"\bbirthday\b",
        r"\bssn\b", r"\bsocial_security\b",
        r"\bpassport_number\b", r"\bnational_id\b",
        r"\bip_address\b", r"\buser_agent\b",
    ],
    "database_queries": [
        r"SELECT\s+.*FROM\s+users",
        r"INSERT\s+INTO\s+users",
        r"UPDATE\s+users\s+SET",
        r"DELETE\s+FROM\s+users",
        r"\.find\(\{.*email",
        r"User\.objects\.",
        r"User\.query\.",
    ],
    "cookie_operations": [
        r"document\.cookie",
        r"res\.cookie\(",
        r"set_cookie\(",
        r"setCookie\(",
        r"response\.set_cookie",
    ],
    "ip_logging": [
        r"request\.ip\b",
        r"request\.remote_addr",
        r"X-Forwarded-For",
        r"req\.ip\b",
        r"REMOTE_ADDR",
    ],
    "user_tracking": [
        r"analytics\.track",
        r"analytics\.identify",
        r"gtag\(",
        r"fbq\(",
        r"_paq\.push",
        r"mixpanel\.track",
        r"posthog\.capture",
    ],
    "geolocation": [
        r"navigator\.geolocation",
        r"geoip",
        r"geo_ip",
        r"maxmind",
        r"ip2location",
    ],
    "file_uploads": [
        r"multer\(",
        r"formidable\(",
        r"file\.save\(",
        r"upload_file",
        r"FileField",
        r"ImageField",
    ],
    "consent_mechanism": [
        r"consent",
        r"opt.in",
        r"opt.out",
        r"cookie.banner",
        r"cookie.consent",
        r"gdpr.consent",
        r"privacy.accept",
    ],
    "data_deletion": [
        r"delete.account",
        r"delete.user",
        r"right.to.erasure",
        r"data.erasure",
        r"forget.me",
        r"anonymize",
        r"pseudonymize",
    ],
    "encryption_usage": [
        r"bcrypt\.hash",
        r"argon2\.hash",
        r"hashlib\.",
        r"crypto\.createHash",
        r"AES",
        r"encrypt\(",
        r"decrypt\(",
    ],
    "data_export": [
        r"export.data",
        r"download.data",
        r"data.portability",
        r"to_csv",
        r"to_json.*user",
    ],
}

# ============================================================
# GDPR — Compliance Requirements by Processing Type
# ============================================================

GDPR_REQUIREMENTS = {
    "controller": {
        "description": "Data controller obligations (you decide why and how personal data is processed)",
        "requirements": [
            "Lawful basis for processing (Art. 6)",
            "Privacy notice / Information to data subjects (Art. 13-14)",
            "Data Protection Impact Assessment if high risk (Art. 35)",
            "Records of processing activities (Art. 30)",
            "Data Protection Officer if required (Art. 37)",
            "Data breach notification procedure (Art. 33-34)",
            "Data subject rights mechanisms (Art. 15-22)",
            "Data processing agreements with processors (Art. 28)",
            "International transfer safeguards if applicable (Art. 44-49)",
        ],
    },
    "processor": {
        "description": "Data processor obligations (you process data on behalf of a controller)",
        "requirements": [
            "Data processing agreement with controller (Art. 28)",
            "Records of processing activities (Art. 30)",
            "Security measures (Art. 32)",
            "Data breach notification to controller (Art. 33)",
            "Sub-processor authorization (Art. 28)",
        ],
    },
    "minimal_processing": {
        "description": "Minimal personal data processing (e.g., basic auth, no analytics)",
        "requirements": [
            "Privacy notice (Art. 13)",
            "Lawful basis documented (Art. 6)",
            "Basic security measures (Art. 32)",
        ],
    },
}

# ============================================================
# GDPR — Actionable Guidance
# ============================================================

GDPR_GUIDANCE = {
    "privacy_policy": {
        "what": "Create a privacy policy informing users about data processing",
        "why": "Art. 13-14 — Data subjects must be informed about processing purposes, legal basis, retention, and rights",
        "how": [
            "Create docs/PRIVACY_POLICY.md (use generate_gdpr_templates tool)",
            "Include: identity of controller, processing purposes, legal basis",
            "Include: data retention periods, data subject rights, contact info",
            "Make accessible: link from website footer, app settings, README",
        ],
        "gdpr_article": "Art. 13-14",
        "effort": "medium",
    },
    "consent_mechanism": {
        "what": "Implement consent collection where consent is the legal basis",
        "why": "Art. 7 — Consent must be freely given, specific, informed, unambiguous",
        "how": [
            "Implement opt-in (not pre-ticked) consent checkboxes",
            "Record: what was consented to, when, how, by whom",
            "Implement consent withdrawal mechanism (as easy as giving consent)",
            "For cookies: implement cookie banner with granular choices",
        ],
        "gdpr_article": "Art. 7",
        "effort": "medium",
    },
    "data_subject_rights": {
        "what": "Implement mechanisms for data subject rights (access, deletion, portability)",
        "why": "Art. 15-22 — Data subjects can request access, rectification, erasure, portability",
        "how": [
            "Implement data export endpoint (JSON/CSV format)",
            "Implement account deletion (true deletion or anonymization)",
            "Implement data access request workflow",
            "Response deadline: 1 month (Art. 12)",
        ],
        "gdpr_article": "Art. 15-22",
        "effort": "high",
    },
    "dpia": {
        "what": "Conduct a Data Protection Impact Assessment for high-risk processing",
        "why": "Art. 35 — Required when processing is likely to result in high risk to individuals",
        "how": [
            "Create docs/DPIA.md (use generate_gdpr_templates tool)",
            "Describe: processing operations, purposes, necessity, proportionality",
            "Assess: risks to rights and freedoms of data subjects",
            "Define: measures to mitigate identified risks",
        ],
        "gdpr_article": "Art. 35",
        "effort": "high",
    },
    "data_breach_procedure": {
        "what": "Document data breach detection and notification procedure",
        "why": "Art. 33-34 — Notify supervisory authority within 72h, data subjects if high risk",
        "how": [
            "Create docs/DATA_BREACH_PROCEDURE.md",
            "Define: how breaches are detected (monitoring, alerts)",
            "Define: assessment process (severity, affected data, affected individuals)",
            "Define: notification workflow (DPA within 72h, data subjects if high risk)",
        ],
        "gdpr_article": "Art. 33-34",
        "effort": "medium",
    },
    "security_measures": {
        "what": "Implement appropriate technical and organizational security measures",
        "why": "Art. 32 — Security appropriate to the risk (encryption, access control, testing)",
        "how": [
            "Encrypt personal data at rest and in transit (TLS, AES-256)",
            "Implement access control (principle of least privilege)",
            "Hash passwords (bcrypt/argon2, never plaintext)",
            "Regular security testing and vulnerability scanning",
            "Logging and monitoring of access to personal data",
        ],
        "gdpr_article": "Art. 32",
        "effort": "medium",
    },
    "records_of_processing": {
        "what": "Maintain records of processing activities",
        "why": "Art. 30 — Controllers and processors must document their processing activities",
        "how": [
            "Create docs/RECORDS_OF_PROCESSING.md (use generate_gdpr_templates tool)",
            "Document: each processing activity, purpose, categories of data, recipients",
            "Document: retention periods, international transfers, security measures",
            "Keep records up to date and available for supervisory authority",
        ],
        "gdpr_article": "Art. 30",
        "effort": "medium",
    },
    "dpa": {
        "what": "Establish Data Processing Agreements with all processors",
        "why": "Art. 28 — Processing by a processor must be governed by a contract",
        "how": [
            "Identify all third-party processors (cloud, analytics, email, payment)",
            "Ensure DPA exists for each: subject matter, duration, nature, purpose",
            "Include: processor obligations, sub-processor rules, audit rights",
            "Review DPAs annually",
        ],
        "gdpr_article": "Art. 28",
        "effort": "medium",
    },
}

# ============================================================
# GDPR — Compliance Templates
# ============================================================

GDPR_TEMPLATES = {
    "privacy_policy": {
        "filename": "PRIVACY_POLICY.md",
        "content": """# Privacy Policy — GDPR Art. 13-14

## 1. Controller Identity
- **Organization**: [Your company name]
- **Contact**: [Email address]
- **DPO**: [DPO contact if applicable]

## 2. Data We Collect
| Data Category | Examples | Legal Basis | Retention |
|---------------|----------|-------------|-----------|
| Account data | Email, name | Contract (Art. 6.1.b) | Until account deletion |
| Usage data | Pages visited, features used | Legitimate interest (Art. 6.1.f) | [Duration] |
| Payment data | Transaction ID (no card numbers) | Contract (Art. 6.1.b) | Legal obligation period |

## 3. How We Use Your Data
- [Purpose 1: e.g., Provide the service]
- [Purpose 2: e.g., Send transactional emails]
- [Purpose 3: e.g., Improve the product]

## 4. Third-Party Processors
| Processor | Purpose | Location | DPA |
|-----------|---------|----------|-----|
| [e.g. Stripe] | Payment processing | US (SCCs) | Yes |
| [e.g. OVH] | Hosting | EU | Yes |

## 5. Your Rights (Art. 15-22)
You have the right to:
- **Access** your personal data (Art. 15)
- **Rectify** inaccurate data (Art. 16)
- **Erase** your data ("right to be forgotten") (Art. 17)
- **Restrict** processing (Art. 18)
- **Data portability** (Art. 20)
- **Object** to processing (Art. 21)

To exercise these rights: [contact method]
Response time: within 1 month.

## 6. Data Security
[Describe security measures: encryption, access control, etc.]

## 7. International Transfers
[Describe if data is transferred outside EU/EEA and safeguards used]

## 8. Complaints
You can lodge a complaint with your local supervisory authority (e.g., CNIL in France).

## 9. Updates
This policy was last updated on [Date]. We will notify you of significant changes.
""",
    },
    "dpia": {
        "filename": "DPIA.md",
        "content": """# Data Protection Impact Assessment — GDPR Art. 35

## 1. Processing Description
- **Processing activity**: [Describe what personal data is processed and how]
- **Purpose**: [Why this processing is necessary]
- **Data categories**: [Types of personal data involved]
- **Data subjects**: [Who is affected: users, employees, customers]
- **Volume**: [Approximate number of data subjects]

## 2. Necessity & Proportionality
- **Legal basis**: [Art. 6 basis: consent, contract, legitimate interest, etc.]
- **Necessity**: [Why this processing is necessary for the stated purpose]
- **Proportionality**: [Why less intrusive alternatives are insufficient]
- **Data minimization**: [How you limit data collection to what's needed]

## 3. Risk Assessment
| Risk | Likelihood | Impact | Affected Rights | Mitigation |
|------|-----------|--------|-----------------|------------|
| [Unauthorized access] | [Low/Med/High] | [Low/Med/High] | [Privacy, security] | [Encryption, access control] |
| [Data breach] | [Low/Med/High] | [Low/Med/High] | [Privacy] | [Monitoring, incident response] |
| [Profiling without consent] | [Low/Med/High] | [Low/Med/High] | [Non-discrimination] | [Opt-in consent] |

## 4. Measures to Mitigate Risks
- [Measure 1: e.g., End-to-end encryption]
- [Measure 2: e.g., Access logging and monitoring]
- [Measure 3: e.g., Regular security audits]
- [Measure 4: e.g., Staff training on data protection]

## 5. DPO Opinion
[If applicable, include DPO review and recommendation]

## 6. Review Schedule
- **Next review**: [Date or trigger event]
- **Review frequency**: [Annual or after significant changes]
""",
    },
    "records_of_processing": {
        "filename": "RECORDS_OF_PROCESSING.md",
        "content": """# Records of Processing Activities — GDPR Art. 30

## Controller Information
- **Name**: [Organization]
- **Contact**: [Contact details]
- **DPO**: [If applicable]

## Processing Activities

### Activity 1: [e.g., User Account Management]
| Field | Value |
|-------|-------|
| Purpose | [e.g., Provide user accounts for the service] |
| Legal basis | [e.g., Contract Art. 6.1.b] |
| Data categories | [e.g., Name, email, password hash] |
| Data subjects | [e.g., Registered users] |
| Recipients | [e.g., Hosting provider (OVH)] |
| International transfers | [e.g., None / US with SCCs] |
| Retention period | [e.g., Until account deletion + 30 days] |
| Security measures | [e.g., Encryption at rest, bcrypt passwords] |

### Activity 2: [e.g., Analytics]
| Field | Value |
|-------|-------|
| Purpose | [e.g., Understand product usage] |
| Legal basis | [e.g., Legitimate interest Art. 6.1.f] |
| Data categories | [e.g., Page views, feature usage, anonymized IP] |
| Data subjects | [e.g., All visitors] |
| Recipients | [e.g., Analytics provider] |
| International transfers | [e.g., Describe] |
| Retention period | [e.g., 26 months] |
| Security measures | [e.g., IP anonymization, no PII stored] |
""",
    },
    "data_breach_procedure": {
        "filename": "DATA_BREACH_PROCEDURE.md",
        "content": """# Data Breach Response Procedure — GDPR Art. 33-34

## 1. Breach Detection
- **Monitoring**: [How breaches are detected: alerts, logs, user reports]
- **Classification**: Assess severity using: data type, volume, encryption status, affected individuals

## 2. Response Timeline (Art. 33)
| Action | Deadline | Responsible |
|--------|----------|-------------|
| Initial assessment | Within 4 hours | [Role] |
| DPA notification (if required) | Within 72 hours | [DPO/Role] |
| Data subject notification (if high risk) | Without undue delay | [Role] |
| Post-incident review | Within 2 weeks | [Role] |

## 3. DPA Notification Content (Art. 33.3)
- Nature of the breach (categories and approximate number of data subjects)
- Name and contact of DPO or contact point
- Likely consequences of the breach
- Measures taken or proposed to address the breach

## 4. Data Subject Notification (Art. 34)
Required when breach is likely to result in HIGH RISK to rights and freedoms.
Must include: clear language, nature of breach, DPO contact, likely consequences, measures taken.

## 5. Documentation
Document ALL breaches (even those not requiring notification):
- Date of detection
- Nature of breach
- Data and individuals affected
- Consequences
- Remedial actions taken

## 6. Post-Incident Review
- Root cause analysis
- Process improvements
- Staff training updates if needed
""",
    },
}

# ============================================================
# GDPR — Checker Class
# ============================================================

CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".rb", ".php"}
CONFIG_FILE_NAMES = {
    "package.json", "package-lock.json",
    "requirements.txt", "requirements-dev.txt",
    "setup.py", "setup.cfg", "pyproject.toml",
    "Pipfile", "Pipfile.lock",
    "Cargo.toml", "go.mod", "Gemfile",
    "composer.json",
}
MAX_FILES = 5000
MAX_FILE_SIZE = 1_000_000
SKIP_DIRS = {
    ".venv", "venv", ".env", "env", "node_modules", ".git",
    "__pycache__", ".pytest_cache", ".tox", ".mypy_cache",
    "dist", "build", ".eggs", ".smithery", ".cache",
}


class GDPRChecker:
    """GDPR compliance checker — scans codebase for personal data processing patterns."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.detected_patterns = {}
        self.files_scanned = 0
        self.flagged_files = []

    def scan_project(self) -> Dict[str, Any]:
        """Scan the project for personal data processing patterns."""
        if not self.project_path.exists():
            return {"error": f"Path does not exist: {self.project_path}", "detected_patterns": {}}

        for file_path in self.project_path.rglob("*"):
            if SKIP_DIRS.intersection(file_path.parts):
                continue
            if self.files_scanned >= MAX_FILES:
                break
            if not file_path.is_file():
                continue
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            if file_path.suffix in CODE_EXTENSIONS:
                self._scan_code(file_path)
            elif file_path.name in CONFIG_FILE_NAMES:
                self._scan_config(file_path)

        # Summarize processing types detected
        processing_summary = self._summarize_processing()

        return {
            "files_scanned": self.files_scanned,
            "flagged_files": self.flagged_files,
            "detected_patterns": self.detected_patterns,
            "processing_summary": processing_summary,
        }

    def _scan_code(self, file_path: Path):
        self.files_scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            rel = str(file_path.relative_to(self.project_path))
            detections = []

            for category, patterns in GDPR_CODE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        detections.append(category)
                        self.detected_patterns.setdefault(category, []).append(rel)
                        break

            if detections:
                self.flagged_files.append({"file": rel, "categories": list(set(detections))})
        except Exception:
            pass

    def _scan_config(self, file_path: Path):
        self.files_scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            rel = str(file_path.relative_to(self.project_path))
            detections = []

            for category, patterns in GDPR_CONFIG_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        detections.append(category)
                        self.detected_patterns.setdefault(category, []).append(rel)
                        break

            if detections:
                self.flagged_files.append({"file": rel, "categories": list(set(detections)), "source": "config"})
        except Exception:
            pass

    def _summarize_processing(self) -> Dict[str, Any]:
        """Determine processing type and risk level from detected patterns."""
        has_pii = "pii_fields" in self.detected_patterns or "database_queries" in self.detected_patterns
        has_tracking = "user_tracking" in self.detected_patterns or "analytics" in self.detected_patterns
        has_consent = "consent_mechanism" in self.detected_patterns
        has_deletion = "data_deletion" in self.detected_patterns or "data_export" in self.detected_patterns
        has_encryption = "encryption_usage" in self.detected_patterns or "encryption" in self.detected_patterns
        has_geo = "geolocation" in self.detected_patterns
        has_uploads = "file_uploads" in self.detected_patterns

        # Risk level
        risk_factors = sum([has_pii, has_tracking, has_geo, has_uploads, not has_consent and has_pii])
        if risk_factors >= 3:
            risk_level = "high"
        elif risk_factors >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Positive signals
        positive = []
        if has_consent:
            positive.append("Consent mechanism detected")
        if has_deletion:
            positive.append("Data deletion/export capability detected")
        if has_encryption:
            positive.append("Encryption usage detected")

        return {
            "processes_personal_data": has_pii or has_tracking,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "positive_signals": positive,
            "processing_role": "controller" if has_pii else ("processor" if has_tracking else "minimal_processing"),
        }

    def check_compliance(self, processing_role: str = "controller") -> Dict[str, Any]:
        """Check GDPR compliance for a given processing role."""
        if processing_role not in GDPR_REQUIREMENTS:
            return {"error": f"Invalid role: {processing_role}. Valid: {list(GDPR_REQUIREMENTS.keys())}"}

        role_info = GDPR_REQUIREMENTS[processing_role]

        status = {
            "privacy_policy": self._check_file("PRIVACY_POLICY.md") or self._check_file("privacy-policy.md"),
            "consent_mechanism": "consent_mechanism" in self.detected_patterns,
            "data_subject_rights": "data_deletion" in self.detected_patterns or "data_export" in self.detected_patterns,
            "security_measures": "encryption_usage" in self.detected_patterns or "encryption" in self.detected_patterns,
            "records_of_processing": self._check_file("RECORDS_OF_PROCESSING.md"),
        }

        if processing_role == "controller":
            status["dpia"] = self._check_file("DPIA.md") or self._check_file("DATA_PROTECTION_IMPACT_ASSESSMENT.md")
            status["data_breach_procedure"] = self._check_file("DATA_BREACH_PROCEDURE.md")
            status["dpa"] = self._check_file("DATA_PROCESSING_AGREEMENT.md") or self._check_file("DPA.md")

        total = len(status)
        passed = sum(1 for v in status.values() if v)

        # Quality verification: check if GDPR docs are customized (not just starter templates)
        file_checks = {
            "privacy_policy": "PRIVACY_POLICY.md",
            "records_of_processing": "RECORDS_OF_PROCESSING.md",
        }
        if processing_role == "controller":
            file_checks["dpia"] = "DPIA.md"
            file_checks["data_breach_procedure"] = "DATA_BREACH_PROCEDURE.md"

        quality_notes = {}
        for check_name, fname in file_checks.items():
            if status.get(check_name):
                quality = self._check_file_quality(fname)
                if not quality["customized"]:
                    quality_notes[check_name] = f"File exists but appears to be an unfilled template ({quality['unfilled_placeholders']} placeholder sections remaining)"

        return {
            "processing_role": processing_role,
            "description": role_info["description"],
            "requirements": role_info["requirements"],
            "compliance_status": status,
            "compliance_score": f"{passed}/{total}",
            "compliance_percentage": round((passed / total) * 100, 1) if total > 0 else 0,
            "quality_notes": quality_notes,
        }

    def _check_file(self, filename: str) -> bool:
        return (self.project_path / filename).exists() or (self.project_path / "docs" / filename).exists()

    def _check_file_quality(self, filename: str) -> Dict[str, Any]:
        """Check if a GDPR document exists and has been customized (not just a starter template)."""
        for p in [self.project_path / filename, self.project_path / "docs" / filename]:
            if p.exists():
                try:
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    unfilled = len(re.findall(r'\[(?:Your |e\.g\.|Date|Duration|Role|Describe|Email)', content))
                    return {"exists": True, "customized": unfilled <= 2, "unfilled_placeholders": unfilled}
                except Exception:
                    return {"exists": True, "customized": False, "unfilled_placeholders": -1}
        return {"exists": False, "customized": False, "unfilled_placeholders": 0}

    def generate_report(self, scan_results: Dict, compliance_results: Dict) -> Dict[str, Any]:
        """Generate complete GDPR compliance report."""
        recommendations = []
        for check, passed in compliance_results.get("compliance_status", {}).items():
            if not passed:
                guidance = GDPR_GUIDANCE.get(check, {})
                recommendations.append({
                    "check": check,
                    "status": "FAIL",
                    "what": guidance.get("what", f"Missing: {check.replace('_', ' ')}"),
                    "why": guidance.get("why", "Required by GDPR"),
                    "how": guidance.get("how", [f"Create {check} documentation"]),
                    "template_available": check in GDPR_TEMPLATES,
                    "gdpr_article": guidance.get("gdpr_article", ""),
                    "effort": guidance.get("effort", "medium"),
                })
            else:
                recommendations.append({"check": check, "status": "PASS"})

        return {
            "report_date": datetime.now(timezone.utc).isoformat(),
            "regulation": "GDPR",
            "project_path": str(self.project_path),
            "scan_summary": {
                "files_scanned": scan_results.get("files_scanned", 0),
                "flagged_files": len(scan_results.get("flagged_files", [])),
                "processing_categories": list(scan_results.get("detected_patterns", {}).keys()),
            },
            "processing_summary": scan_results.get("processing_summary", {}),
            "compliance_summary": {
                "processing_role": compliance_results.get("processing_role", "unknown"),
                "compliance_score": compliance_results.get("compliance_score", "0/0"),
                "compliance_percentage": compliance_results.get("compliance_percentage", 0),
            },
            "recommendations": recommendations,
        }

    def get_templates(self, processing_role: str = "controller") -> Dict[str, Any]:
        """Return applicable GDPR compliance templates."""
        template_mapping = {
            "controller": ["privacy_policy", "dpia", "records_of_processing", "data_breach_procedure"],
            "processor": ["records_of_processing", "data_breach_procedure"],
            "minimal_processing": ["privacy_policy"],
        }

        applicable = template_mapping.get(processing_role, ["privacy_policy"])
        templates = {}
        for key in applicable:
            if key in GDPR_TEMPLATES:
                tmpl = GDPR_TEMPLATES[key]
                templates[key] = {
                    "filename": f"docs/{tmpl['filename']}",
                    "content": tmpl["content"],
                    "instructions": f"Save as docs/{tmpl['filename']}, fill in [bracketed] sections",
                }

        return {
            "regulation": "GDPR",
            "processing_role": processing_role,
            "templates_count": len(templates),
            "templates": templates,
            "usage": "Save each template in your project's docs/ directory. Fill in [bracketed] sections. Re-run gdpr_check_compliance to verify.",
        }
