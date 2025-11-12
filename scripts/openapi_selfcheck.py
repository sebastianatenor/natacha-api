#!/usr/bin/env python3
import os, subprocess, sys
base = os.environ.get("BASE") or ""
if not base:
    print("❌ BASE vacío"); sys.exit(1)
subprocess.check_call(["bash","scripts/openapi_selfcheck.sh"])
