
import os
import sys
import time

print("S1: sys ports", file=sys.stderr)
import sys

print("S2: load_dotenv", file=sys.stderr)
from dotenv import load_dotenv
load_dotenv(".env")

print("S3: mcp.server.fastmcp", file=sys.stderr)
try:
    from mcp.server.fastmcp import FastMCP
    print("S3 Done", file=sys.stderr)
except Exception as e:
    print(f"S3 Fail: {e}", file=sys.stderr)

print("S4: app.metrics", file=sys.stderr)
try:
    from app.metrics import MetricsService
    print("S4 Done", file=sys.stderr)
except Exception as e:
    print(f"S4 Fail: {e}", file=sys.stderr)

print("S5: FastMCP Init", file=sys.stderr)
try:
    mcp = FastMCP(name="bitrix_crm")
    print("S5 Done", file=sys.stderr)
except Exception as e:
    print(f"S5 Fail: {e}", file=sys.stderr)

print("🚀 Startup Debug Complete", file=sys.stderr)
