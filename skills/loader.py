import yaml
from pathlib import Path
from tools.registry import register

SKILLS_DIR = Path("skills")
SKILLS_DIR.mkdir(exist_ok=True)

def load_skills():
    for file in SKILLS_DIR.glob("*.yaml"):
        try:
            with open(file) as f:
                data = yaml.safe_load(f)
            print(f"[Skill] Loaded: {data['name']} v{data['version']}")
            # Yaha aap custom tools ya prompt injection kar sakte ho
            # Example: data.get("extra_prompt", "")
        except Exception as e:
            print(f"[Skill] Error loading {file.name}: {e}")