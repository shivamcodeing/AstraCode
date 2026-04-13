# 🌪️ AstraCode CLI v0.1

```text
 █████╗ ██████╗ ██╗   ██╗██╗  ██╗████████╗
██╔══██╗██╔══██╗██║   ██║╚██╗██╔╝╚══██╔══╝
███████║██████╔╝██║   ██║ ╚███╔╝    ██║
██╔══██║██╔══██╗██║   ██║ ██╔██╗    ██║
██║  ██║██████╔╝╚██████╔╝██╔╝ ██╗   ██║
╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝
        🌪️ AstraCode CLI v0.1


A lightweight, streaming-enabled, MCP-ready AI Agent built specifically to run smoothly on Android devices (Termux) with as little as 4GB RAM. AstraCode is designed for developers who want a powerful, local-first AI assistant in their terminal.

---

## ✨ Features

* 📱 **Termux Optimized:** Runs flawlessly on Android environments without heavy GUI dependencies.
* 🧠 **Smart AI Routing:** Automatically switches between local models (Ollama) and online APIs (OpenRouter) if the local model isn't running.
* 🛠️ **Built-in Tool Calling:**
  * `run_shell`: Execute terminal commands directly.
  * `file_op`: Read, write, and list files.
  * `web_req`: Fetch data via HTTP GET/POST requests.
* 💾 **RAM-Friendly Memory:** Auto-trims conversation context to prevent Out-Of-Memory (OOM) errors (defaults to 4096 tokens).
* 🔌 **MCP Ready:** Includes a Model Context Protocol (MCP) `stdio` bridge to pipe your agent into Claude Desktop, Cursor, or other IDEs.
* 🎨 **Beautiful CLI UX:** Real-time markdown streaming and tool execution badges using `rich`.

---

## 🚀 Quick Start (Termux / Linux)

### 1. Install Prerequisites
Make sure you have Python, Git, and optionally Ollama installed.

```bash
pkg update && pkg install python git ollama
