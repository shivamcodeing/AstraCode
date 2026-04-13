import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from core.config import load_config
from core.agent import AstraAgent
from core.session import load_session, save_session
from skills.loader import load_skills
from mcp.bridge import MCPBridge

LOGO = r"""
 █████╗ ██████╗ ██╗   ██╗██╗  ██╗████████╗
██╔══██╗██╔══██╗██║   ██║╚██╗██╔╝╚══██╔══╝
███████║██████╔╝██║   ██║ ╚███╔╝    ██║
██╔══██║██╔══██╗██║   ██║ ██╔██╗    ██║
██║  ██║██████╔╝╚██████╔╝██╔╝ ██╗   ██║
╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝
        🌪️ AstraCode CLI v0.1
"""

def main():
    parser = argparse.ArgumentParser(description="AstraCode AI Agent")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP stdio server")
    parser.add_argument("--unsafe", action="store_true", help="Allow shell execution")
    parser.add_argument("--session", type=str, default="default", help="Session name to load/save")
    args = parser.parse_args()

    config = load_config()
    if args.unsafe:
        config["safe_mode"] = False

    # 1. Load custom skills
    load_skills()

    # 2. Initialize agent
    agent = AstraAgent(config)

    # 3. Load session history or set system prompt
    history = load_session(args.session)
    if not history:
        history = [{"role": "system", "content": "You are AstraCode, a terminal AI agent for coding, automation, and system control. Use tools when needed."}]

    # Inject history into memory manager
    agent.memory.messages = history
    agent.memory._trim()  # Ensure context stays within 4GB limit

    # MCP Mode
    if args.mcp:
        MCPBridge(safe_mode=config.get("safe_mode", True)).run_stdio()
        return

    # CLI Mode
    console = Console()
    console.print(Panel(LOGO, title="AstraCode", border_style="cyan"))
    console.print(f"[bold green]✅ Session: '{args.session}' | Type 'exit' to quit.[/bold green]\n")

    while True:
        try:
            prompt = console.input("[bold cyan]👤 You:[/bold cyan] ")
            if prompt.lower() in ["exit", "quit"]:
                save_session(args.session, agent.memory.messages)
                console.print("[yellow]👋 Session saved. Shutting down...[/yellow]")
                break
            if not prompt.strip(): continue

            console.print("[bold purple]🌪️ AstraCode:[/bold purple] ", end="")
            with Live(console=console, refresh_per_second=12) as live:
                full = ""
                for chunk in agent.run(prompt):
                    full = chunk
                    live.update(Markdown(full))
            console.print("\n" + "-"*50 + "\n")

        except KeyboardInterrupt:
            save_session(args.session, agent.memory.messages)
            console.print("\n[yellow]⚠️ Interrupted. Session saved.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()