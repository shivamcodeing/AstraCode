import subprocess
import json
import requests
import shlex
from pathlib import Path

TOOLS = {}

def register(name, desc, params, fn):
    TOOLS[name] = {
        "name": name,
        "description": desc,
        "parameters": params,
        "execute": fn
    }

# ──────────────────────────────────────────────────────────────
# 1. Shell Tool
# ──────────────────────────────────────────────────────────────
def run_shell(cmd, safe_mode=True):
    if safe_mode:
        return {"status": "blocked", "message": "Safe mode: Use `--unsafe` flag to enable shell execution."}
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30s"}
    except Exception as e:
        return {"error": str(e)}

register("run_shell", "Execute terminal commands", {
    "type": "object",
    "properties": {"command": {"type": "string"}},
    "required": ["command"]
}, run_shell)

# ──────────────────────────────────────────────────────────────
# 2. File Tool (4GB RAM Optimized)
# ──────────────────────────────────────────────────────────────
def file_op(action, path, content=""):
    try:
        p = Path(path)
        if action == "read":
            if not p.exists():
                return {"content": "", "error": "File not found"}
            # Prevent OOM on 4GB devices
            if p.stat().st_size > 2 * 1024 * 1024:  # 2MB limit
                return {"content": "", "error": "File too large (>2MB). Read in chunks or use shell."}
            return {"content": p.read_text(errors="ignore")}
        if action == "write":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return {"status": "written", "path": str(p)}

        if action == "list":
            if not p.is_dir():
                return {"error": "Not a directory"}
            return {"files": [f.name for f in p.iterdir()]}

        return {"error": "Invalid action. Use: read, write, list"}
    except PermissionError:
        return {"error": "Permission denied"}
    except Exception as e:
        return {"error": str(e)}

register("file_op", "Read, write, or list files (max 2MB read)", {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["read", "write", "list"]},
        "path": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["action", "path"]
}, file_op)

# ──────────────────────────────────────────────────────────────
# 3. Web Tool
# ──────────────────────────────────────────────────────────────
def web_req(method, url, body="", headers=None):
    try:
        res = requests.request(method.upper(), url, data=body, headers=headers or {}, timeout=15)
        # Limit response to prevent memory bloat
        content = res.text[:3000] if res.text else ""
        return {"status": res.status_code, "content": content}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}

register("web_req", "HTTP GET/POST requests", {
    "type": "object",
    "properties": {
        "method": {"type": "string", "enum": ["get", "post"]},
        "url": {"type": "string"},
        "body": {"type": "string"},
        "headers": {"type": "object"}
    },
    "required": ["method", "url"]
}, web_req)
# ──────────────────────────────────────────────────────────────
# 4. Git Tool
# ──────────────────────────────────────────────────────────────
def git_cmd(command):
    try:
        res = subprocess.run(f"git {command}", shell=True, capture_output=True, text=True, timeout=15)
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except Exception as e:
        return {"error": str(e)}

register("git_cmd", "Run git commands", {
    "type": "object",
    "properties": {"command": {"type": "string"}},
    "required": ["command"]
}, git_cmd)

# ──────────────────────────────────────────────────────────────
# 5. Project Scaffolder
# ──────────────────────────────────────────────────────────────
def project_init(lang, name):
    safe_name = shlex.quote(name)
    if lang == "python":
        cmd = f"mkdir -p {safe_name} && touch {safe_name}/main.py {safe_name}/requirements.txt"
    elif lang == "web":
        cmd = f"mkdir -p {safe_name} && touch {safe_name}/index.html {safe_name}/style.css {safe_name}/script.js"
    else:
        cmd = f"mkdir -p {safe_name}"

    git_res = git_cmd("init")
    shell_res = run_shell(cmd, safe_mode=False)

    return {
        "git_init": git_res,
        "scaffold": shell_res,
        "project": name,
        "lang": lang
    }

register("project_init", "Scaffold a new project folder", {
    "type": "object",
    "properties": {
        "lang": {"type": "string", "enum": ["python", "web", "other"]},
        "name": {"type": "string"}
    },
    "required": ["lang", "name"]
}, project_init)

# ──────────────────────────────────────────────────────────────
# Schema & Execution Router# ──────────────────────────────────────────────────────────────
def get_tool_schemas():
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            }
        }
        for t in TOOLS.values()
    ]

def execute_tool(name, args, safe_mode=True):
    tool = TOOLS.get(name)
    if not tool:
        return {"error": f"Tool '{name}' not found"}

    fn = tool["execute"]

    # Tool-specific safe dispatch
    if name == "run_shell":
        return fn(args.get("command", ""), safe_mode=safe_mode)
    if name == "file_op":
        return fn(args.get("action"), args.get("path"), args.get("content", ""))
    if name == "web_req":
        return fn(args.get("method"), args.get("url"), args.get("body", ""), args.get("headers"))
    if name == "git_cmd":
        return fn(args.get("command"))
    if name == "project_init":
        return fn(args.get("lang"), args.get("name"))

    # Fallback for any future tool
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": f"Tool argument mismatch: {e}"}