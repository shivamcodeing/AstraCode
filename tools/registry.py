import subprocess
import json
import requests
from pathlib import Path

TOOLS = {}

def register(name, desc, params, fn):
    TOOLS[name] = {"name": name, "description": desc, "parameters": params, "execute": fn}

# Shell
def run_shell(cmd, safe_mode=True):
    if safe_mode:
        return {"status": "blocked", "message": "Safe mode: Enable --unsafe or edit config.yaml to allow shell."}
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except Exception as e:
        return {"error": str(e)}

register("run_shell", "Execute terminal commands", {
    "type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]
}, run_shell)

# File
def file_op(action, path, content=""):
    try:
        p = Path(path)
        if action == "read": return {"content": p.read_text() if p.exists() else "Not found"}
        if action == "write":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return {"status": "written"}
        if action == "list": return {"files": [f.name for f in p.iterdir()] if p.is_dir() else []}
        return {"error": "Invalid action"}
    except Exception as e:
        return {"error": str(e)}

register("file_op", "Read, write, or list files", {
    "type": "object", "properties": {
        "action": {"type": "string", "enum": ["read", "write", "list"]},
        "path": {"type": "string"}, "content": {"type": "string"}
    }, "required": ["action", "path"]
}, file_op)

# Web
def web_req(method, url, body="", headers=None):
    try:
        res = requests.request(method.upper(), url, data=body, headers=headers or {}, timeout=15)
        return {"status": res.status_code, "content": res.text[:2000]}
    except Exception as e:
        return {"error": str(e)}

register("web_req", "HTTP GET/POST requests", {
    "type": "object", "properties": {
        "method": {"type": "string", "enum": ["get", "post"]},
        "url": {"type": "string"}, "body": {"type": "string"}, "headers": {"type": "object"}
    }, "required": ["method", "url"]
}, web_req)

def get_tool_schemas():
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}} for t in TOOLS.values()]

def execute_tool(name, args, safe_mode=True):
    tool = TOOLS.get(name)
    if not tool: return {"error": f"Tool '{name}' not found"}
    if name == "run_shell": return tool["execute"](args.get("command", ""), safe_mode=safe_mode)
    if name == "file_op": return tool["execute"](args.get("action"), args.get("path"), args.get("content", ""))
    if name == "web_req": return tool["execute"](args.get("method"), args.get("url"), args.get("body", ""), args.get("headers"))
    return tool["execute"](**args)