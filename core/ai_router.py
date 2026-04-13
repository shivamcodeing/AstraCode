import os
from openai import OpenAI
from rich.console import Console

console = Console()

class AIRouter:
    def __init__(self, config):
        self.pref = config.get("ai_preference", "auto")
        self.local_model = config.get("local_model", "qwen2.5:1.5b")
        self.online_model = config.get("online_model", "anthropic/claude-3-haiku")
        self.api_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY", "")

    def get_client(self):
        if self.pref in ["local", "auto"]:
            try:
                client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
                # Quick ping
                client.models.list()
                return client, self.local_model
            except Exception:
                if self.pref == "auto" and self.api_key:
                    console.print("[yellow]⚠️ Ollama not running. Falling back to OpenRouter.[/yellow]")
                else:
                    raise ConnectionError("Ollama not reachable. Start it or switch to online mode.")

        if not self.api_key:
            raise ValueError("OpenRouter API key missing. Set `openrouter_api_key` in config.yaml or `OPENROUTER_API_KEY` env.")
        return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key), self.online_model

    def chat_stream(self, messages, tools=None):
        client, model = self.get_client()
        return client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools or [],
            stream=True
        )