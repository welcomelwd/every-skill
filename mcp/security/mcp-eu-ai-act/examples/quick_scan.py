#!/usr/bin/env python3
"""
Quick scan example - Scan a project and check EU AI Act compliance in 10 lines.

Usage:
    python3 examples/quick_scan.py /path/to/your/project
    python3 examples/quick_scan.py .  # scan current directory
"""

import sys
import json
sys.path.insert(0, ".")
from server import MCPServer

project = sys.argv[1] if len(sys.argv) > 1 else "."
server = MCPServer()

# Scan for AI frameworks
scan = server.handle_request("scan_project", {"project_path": project})
print(f"Files scanned: {scan['results']['files_scanned']}")
print(f"AI frameworks found: {list(scan['results']['detected_models'].keys())}")

# Check compliance (default: limited risk)
check = server.handle_request("check_compliance", {"project_path": project})
print(f"\nCompliance: {check['results']['compliance_percentage']}%")
for req, passed in check['results']['compliance_status'].items():
    print(f"  {'PASS' if passed else 'FAIL'} {req}")
