import sys
import json
from tools.registry import get_tool_schemas, execute_tool

class MCPBridge:
    def __init__(self, safe_mode=True):
        self.safe_mode = safe_mode

    def run_stdio(self):
        for line in sys.stdin:
            try:
                msg = json.loads(line.strip())
                rid = msg.get("id")
                if msg.get("method") == "tools/list":
                    resp = {"jsonrpc": "2.0", "id": rid, "result": {"tools": get_tool_schemas()}}
                elif msg.get("method") == "tools/call":
                    res = execute_tool(msg["params"]["name"], msg["params"]["arguments"], safe_mode=self.safe_mode)
                    resp = {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}
                else:
                    resp = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}}) + "\n")
                sys.stdout.flush()