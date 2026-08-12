#!/usr/bin/env python3
"""
Full report example - Generate a complete EU AI Act compliance report.

Scans the project, checks compliance at all risk levels, and saves a JSON report.

Usage:
    python3 examples/full_report.py /path/to/your/project
    python3 examples/full_report.py .  # scan current directory
"""

import sys
import json
sys.path.insert(0, ".")
from server import MCPServer

project = sys.argv[1] if len(sys.argv) > 1 else "."
server = MCPServer()

print("=" * 60)
print("EU AI Act Compliance Report")
print("=" * 60)

# 1. Scan project
scan = server.handle_request("scan_project", {"project_path": project})
print(f"\nProject: {project}")
print(f"Files scanned: {scan['results']['files_scanned']}")
print(f"AI files detected: {len(scan['results']['ai_files'])}")

if scan['results']['detected_models']:
    print("\nDetected frameworks:")
    for fw, files in scan['results']['detected_models'].items():
        print(f"  - {fw}: {len(files)} file(s)")

# 2. Check compliance at each risk level
for level in ["minimal", "limited", "high"]:
    check = server.handle_request("check_compliance", {
        "project_path": project,
        "risk_category": level
    })
    score = check['results']['compliance_percentage']
    print(f"\n--- {level.upper()} risk: {score}% compliant ---")
    for req, passed in check['results']['compliance_status'].items():
        print(f"  {'PASS' if passed else 'FAIL'} {req}")

# 3. Generate and save full report
report = server.handle_request("generate_report", {
    "project_path": project,
    "risk_category": "limited"
})

output_file = "eu-ai-act-report.json"
with open(output_file, "w") as f:
    json.dump(report['results'], f, indent=2)

print(f"\nFull report saved to: {output_file}")
print("\nRecommendations:")
for rec in report['results']['recommendations']:
    print(f"  - {rec}")
