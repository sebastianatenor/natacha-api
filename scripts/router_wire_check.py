#!/usr/bin/env python3
import os, subprocess, sys
base = os.environ.get("BASE") or ""
if not base:
    print("❌ BASE vacío (definí NATACHA_BASE_URL como repo var/secret)"); sys.exit(1)
subprocess.check_call(["bash","scripts/router_wire_check.sh"])
