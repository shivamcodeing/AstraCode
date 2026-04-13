import json
from .ai_router import AIRouter
from .memory import MemoryManager
from tools.registry import get_tool_schemas, execute_tool

class AstraAgent:
    def __init__(self, config):
        self.ai = AIRouter(config)
        self.memory = MemoryManager(config.get("max_context_tokens", 4096))
        self.max_tool_calls = config.get("max_tool_calls", 5)
        self.safe_mode = config.get("safe_mode", True)
        self.tools_schema = get_tool_schemas()

    def run(self, prompt):
        self.memory.add({"role": "user", "content": prompt})
        tool_call_count = 0

        while True:
            stream = self.ai.chat_stream(self.memory.get_history(), tools=self.tools_schema)
            content = ""
            tool_calls = []

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    content += delta.content
                    yield content  # Streaming output

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        while idx >= len(tool_calls):
                            tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        if tc.id: tool_calls[idx]["id"] = tc.id
                        if tc.function.name: tool_calls[idx]["function"]["name"] = tc.function.name
                        if tc.function.arguments: tool_calls[idx]["function"]["arguments"] += tc.function.arguments

            if content:
                self.memory.add({"role": "assistant", "content": content})
            if tool_calls:
                self.memory.add({"role": "assistant", "tool_calls": tool_calls})

            if not tool_calls:
                break

            for tc in tool_calls:
                if tool_call_count >= self.max_tool_calls:
                    self.memory.add({"role": "system", "content": "⚠️ Max tool calls reached. Answer based on current context."})
                    break
                try:
                    args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
                except:
                    args = {}
                result = execute_tool(tc["function"]["name"], args, safe_mode=self.safe_mode)
                self.memory.add({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False)
                })
                tool_call_count += 1

            if tool_call_count >= self.max_tool_calls:
                break