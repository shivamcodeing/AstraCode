import json
from pathlib import Path

SESSION_DIR = Path("sessions")
SESSION_DIR.mkdir(exist_ok=True)

def save_session(name, messages):
    path = SESSION_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)

def load_session(name):
    path = SESSION_DIR / f"{name}.json"
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return []