# ATR Coverage Report

Generated: 2026-03-12 | Rules: 71 (54 experimental + 17 draft) | Version: 0.4.0

## OWASP Top 10 for Agentic Applications (2026) Coverage

| Risk | Description | ATR Rules | Status |
|------|-------------|-----------|--------|
| ASI01 | Agent Goal Hijack | ATR-2026-001, 002, 003, 004, 005, 020, 030, 032 | Covered |
| ASI02 | Tool Misuse and Exploitation | ATR-2026-010, 011, 012, 013, 062, 063, 066 | Covered |
| ASI03 | Identity and Privilege Abuse | ATR-2026-012, 021, 040, 041, 064, 074 | Covered |
| ASI04 | Agentic Supply Chain Vulnerabilities | ATR-2026-060, 061, 065, 072, 073 | Covered |
| ASI05 | Unexpected Code Execution | ATR-2026-010, 050, 051, 062 | Covered |
| ASI06 | Memory and Context Poisoning | ATR-2026-002, 004, 020, 070, 075 | Covered |
| ASI07 | Multi-Agent Manipulation | (no explicit ASI07 references found in rules) | Gap |
| ASI08 | Agentic RAG Poisoning | (no explicit ASI08 references found in rules; ATR-2026-070 covers RAG poisoning via ASI06) | Partial |
| ASI09 | Insufficient Logging and Monitoring | (no explicit ASI09 references found in rules) | Gap |
| ASI10 | Rogue Agents | ATR-2026-030, 074 | Covered |

**Coverage: 6 of 10 risks covered, 2 partial, 2 gaps.**

Notes:
- ASI07 (Multi-Agent Manipulation): No rules explicitly target ASI07. Some cross-agent patterns exist under ASI01/ASI10 (ATR-2026-030, 032, 074) but multi-agent protocol-level attacks are not addressed.
- ASI08 (Agentic RAG Poisoning): ATR-2026-070 covers textual RAG poisoning but maps to ASI06, not ASI08. Embedding-level poisoning is not covered.
- ASI09 (Insufficient Logging and Monitoring): Out of scope for detection rules. This is an engine/platform concern.

## OWASP LLM Top 10 (2025) Coverage

| Risk | Description | ATR Rules | Status |
|------|-------------|-----------|--------|
| LLM01 | Prompt Injection | ATR-2026-001, 002, 003, 004, 005, 010, 011, 030, 032, 066, 070, 073, 075 | Covered |
| LLM02 | Sensitive Information Disclosure | ATR-2026-020, 021, 075 | Covered |
| LLM03 | Supply Chain Vulnerabilities | ATR-2026-060, 061, 062, 063, 064, 065, 070, 072, 073 | Covered |
| LLM04 | Data and Model Poisoning | (no explicit LLM04 references found) | Gap |
| LLM05 | Improper Output Handling | ATR-2026-010, 011, 013, 030, 060, 061, 066 | Covered |
| LLM06 | Excessive Agency | ATR-2026-012, 013, 030, 032, 040, 041, 050, 051, 062, 063, 064, 072, 074 | Covered |
| LLM07 | System Prompt Leakage | ATR-2026-020, 021 | Covered |
| LLM08 | Excessive Agency (Vector Stores) | ATR-2026-070, 074 | Covered |
| LLM09 | Misinformation | (no explicit LLM09 references found) | Gap |
| LLM10 | Unbounded Consumption | ATR-2026-050, 051, 072 | Covered |

**Coverage: 7 of 10 risks covered, 3 gaps.**

Notes:
- LLM04 (Data and Model Poisoning): No rules explicitly target LLM04. ATR-2026-070 and 073 address related patterns but map to LLM01/LLM03.
- LLM09 (Misinformation): No rules target misinformation or hallucination detection. Requires semantic analysis beyond regex.
- Detection is regex-based; sophisticated attacks using paraphrasing or semantic manipulation may evade detection (see [LIMITATIONS.md](LIMITATIONS.md)).

## CVE Coverage

| CVE | Description | ATR Rules |
|-----|-------------|-----------|
| CVE-2024-5184 | LLM prompt injection vulnerability | ATR-2026-001, 002, 003, 004 |
| CVE-2024-3402 | LLM prompt injection bypass | ATR-2026-001, 003 |
| CVE-2024-22524 | Indirect prompt injection via content | ATR-2026-002 |
| CVE-2025-53773 | GitHub Copilot RCE via prompt injection | ATR-2026-001, 003 |
| CVE-2025-32711 | System prompt leakage / indirect injection | ATR-2026-002, 004, 011, 020, 021 |
| CVE-2026-24307 | Agent memory/context manipulation | ATR-2026-002, 020 |
| CVE-2025-68143 | MCP tool response RCE | ATR-2026-010, 066 |
| CVE-2025-68144 | MCP tool response injection | ATR-2026-010, 066 |
| CVE-2025-68145 | MCP tool response exploitation | ATR-2026-010 |
| CVE-2025-6514 | MCP malicious response | ATR-2026-010 |
| CVE-2025-59536 | Tool output injection / hidden capability | ATR-2026-010, 011, 062 |
| CVE-2026-21852 | MCP server compromise | ATR-2026-010 |
| CVE-2026-0628 | Privilege escalation via agent tools | ATR-2026-040 |

**Total: 13 CVE references mapped to 16 rules.** Mappings are based on attack pattern similarity; empirical validation against CVE payloads has not been performed.

## MITRE ATLAS Coverage

| Technique | Description | ATR Rules |
|-----------|-------------|-----------|
| AML.T0051 | LLM Prompt Injection | ATR-2026-001, 002, 003, 004, 005, 020, 030, 032, 074, 075 |
| AML.T0051.000 | Direct Prompt Injection | ATR-2026-001, 004 |
| AML.T0051.001 | Indirect Prompt Injection | ATR-2026-002, 010, 011, 066, 070, 074 |
| AML.T0054 | LLM Jailbreak | ATR-2026-003 |
| AML.T0053 | LLM Plugin Compromise | ATR-2026-011, 012, 050, 051, 063 |
| AML.T0056 | LLM Meta Prompt Extraction | ATR-2026-010, 020, 061 |
| AML.T0043 | Craft Adversarial Data | ATR-2026-005, 030, 032 |
| AML.T0010 | ML Supply Chain Compromise | ATR-2026-060, 061, 062, 065 |
| AML.T0040 | AI Model Inference API Access | ATR-2026-040, 041, 064 |
| AML.T0046 | Spamming ML System with Chaff Data | ATR-2026-050, 051 |
| AML.T0049 | Exploit Public-Facing Application | ATR-2026-013 |
| AML.T0050 | Command and Scripting Interpreter | ATR-2026-040 |
| AML.T0047 | ML-Enabled Product or Service | ATR-2026-041 |
| AML.T0044 | Full ML Model Access | ATR-2026-072 |
| AML.T0024 | Exfiltration via ML Inference API | ATR-2026-063, 072 |
| AML.T0020 | Poison Training Data | ATR-2026-070, 073 |
| AML.T0018 | Backdoor ML Model | ATR-2026-073 |
| AML.T0055 | Unsecured Credentials | ATR-2026-021 |
| AML.T0057 | LLM Data Leakage | ATR-2026-021 |
| AML.T0052.000 | Spearphishing via Social Engineering LLM | ATR-2026-030 |

## MITRE ATT&CK Coverage

| Technique | Description | ATR Rules |
|-----------|-------------|-----------|
| T1059 | Command and Scripting Interpreter | ATR-2026-010, 012 |
| T1071 | Application Layer Protocol | ATR-2026-010, 013 |
| T1083 | File and Directory Discovery | ATR-2026-012 |
| T1090 | Proxy | ATR-2026-013 |
| T1548 | Abuse Elevation Control Mechanism | ATR-2026-040 |
| T1611 | Escape to Host | ATR-2026-040 |
| T1078 | Valid Accounts | ATR-2026-074 |
| T1550 | Use Alternate Authentication Material | ATR-2026-074 |
| T1565 | Data Manipulation | ATR-2026-070 |
| T1565.001 | Stored Data Manipulation | ATR-2026-075 |
| T1195 | Supply Chain Compromise | ATR-2026-060 |

## Known Gaps

The following attack categories are **not covered** by ATR's current rule set:

### Detection Gaps

1. **Multi-modal attacks (image-based prompt injection)** -- ATR rules operate on text content only. Attacks embedded in images, audio, or video (e.g., OCR-based prompt injection via screenshots, steganographic payloads in images sent to vision models) are not detectable with regex patterns.

2. **Embedding and vector poisoning attacks** -- Attacks that manipulate vector embeddings at the numerical level (e.g., adversarial perturbations to embedding vectors, cosine similarity manipulation) are outside the scope of text-based regex detection. ATR-2026-070 covers textual RAG poisoning but not embedding-level attacks.

3. **OAuth/SSO token theft via agent** -- While ATR-2026-021 detects credential exposure in agent output, there are no rules for detecting agents being manipulated into initiating OAuth flows, intercepting authorization codes, or abusing delegated credentials through redirect manipulation.

4. **Real-time behavioral anomaly detection** -- ATR rules use static pattern matching (regex). They cannot detect behavioral anomalies that require temporal analysis, such as unusual tool call frequency, atypical data access patterns over time, or gradual behavioral drift. This requires runtime statistical analysis beyond regex capabilities.

5. **Misinformation and hallucination detection (LLM09:2025)** -- No rules target factually incorrect or fabricated outputs. Detecting hallucinations requires ground-truth comparison or semantic analysis, which is outside the scope of regex-based detection.

6. **Logging and monitoring completeness (ASI09:2026)** -- ATR defines what to detect, not how to log or monitor. Ensuring sufficient logging coverage is an engine implementation concern, not a rule concern.

7. **Adversarial suffix attacks** -- GCG-style adversarial suffixes (e.g., random-looking token sequences that cause model misbehavior) produce strings that are statistically random and cannot be reliably matched by regex patterns without extreme false positive rates.

8. **Multilingual prompt injection** -- While some obfuscation is covered (homoglyphs, encoding), prompt injection payloads written entirely in non-English languages (e.g., Chinese, Arabic, Korean instruction overrides) are not systematically addressed.

9. **Agent-to-agent protocol-level attacks** -- ATR rules inspect message content but not protocol metadata. Attacks that manipulate message routing, ordering, timing, or protocol headers in multi-agent communication frameworks are not covered.

10. **Model denial-of-service via context stuffing** -- While ATR-2026-051 detects resource exhaustion patterns, there are no rules for detecting deliberate context window stuffing attacks designed to push the system prompt out of the context window.
