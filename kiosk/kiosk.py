import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
API = "http://localhost:8000/api"
history = []

def send(message: str) -> str:
    history.append({"role": "user", "content": message})
    res = requests.post(f"{API}/chat", json={"messages": history})
    reply = res.json()["reply"]
    history.append({"role": "assistant", "content": reply})
    return reply

def main():
    console.print(Panel("🏨 Grand Hotel AI Receptionist\nType 'quit' to exit", style="bold blue"))
    greeting = send("Hello, a guest has just approached the reception desk.")
    console.print(f"\n[bold green]Receptionist:[/] {greeting}\n")

    while True:
        user_input = Prompt.ask("[bold yellow]You[/]")
        if user_input.lower() in ("quit", "exit"):
            console.print("[bold blue]Thank you for visiting Grand Hotel. Goodbye![/]")
            break
        reply = send(user_input)
        console.print(f"\n[bold green]Receptionist:[/] {reply}\n")

if __name__ == "__main__":
    main()
