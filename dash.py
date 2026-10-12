# -*- coding: utf-8 -*-
import sys
import os
import time
import json
import subprocess
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

BANNER = r"""
  ██████╗ ███████╗██╗███╗   ██╗████████╗
  ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
  ██║   ██║███████╗██║██╔██╗ ██║   ██║   
  ██║   ██║╚════██║██║██║╚██╗██║   ██║   
  ╚██████╔╝███████║██║██║ ╚████║   ██║   
   ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
}

REPORT_DIR = os.path.expanduser("~/osint_reports")


def banner():
    console.clear()
    console.print(Align.center(Panel(Text(BANNER, style="bold green"), border_style="green", box=box.DOUBLE)))
    console.print(Align.center("[dim]OSINT Dashboard // v1.0 // iSH Edition[/dim]\n"))


def check_telegram(username):
    username = username.lstrip("@").strip()
    url = f"https://t.me/{username}"
    result = {
        "username": username,
        "exists": False,
        "title": None,
        "description": None,
        "photo": None,
        "type": "неизвестно",
        "url": url,
        "checked_at": datetime.now().isoformat(),
    }

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")

            title_tag = soup.find("meta", property="og:title")
            if title_tag and title_tag.get("content"):
                result["title"] = title_tag["content"].strip()

            desc_tag = soup.find("meta", property="og:description")
            if desc_tag and desc_tag.get("content"):
                result["description"] = desc_tag["content"].strip()

            img_tag = soup.find("meta", property="og:image")
            if img_tag and img_tag.get("content"):
                result["photo"] = img_tag["content"].strip()

            if "tgme_page_extra" in r.text:
                result["exists"] = True
                if "subscribers" in r.text or "підписників" in r.text or "подписчиков" in r.text:
                    result["type"] = "канал/группа"
                elif "last seen" in r.text.lower() or "був" in r.text.lower() or "был" in r.text.lower():
                    result["type"] = "пользователь"
                else:
                    result["type"] = "пользователь"

            bio_div = soup.find("div", class_="tgme_page_description")
            if bio_div:
                result["description"] = bio_div.get_text(separator=" ", strip=True)

        elif r.status_code == 404:
            result["exists"] = False

    except requests.exceptions.Timeout:
        result["error"] = "timeout"
    except requests.exceptions.ConnectionError:
        result["error"] = "нет соединения"
    except Exception as e:
        result["error"] = str(e)

    return result


def render_telegram(data):
    if "error" in data:
        console.print(Panel(f"[red]Ошибка: {data['error']}[/red]", border_style="red"))
        return

    if not data["exists"]:
        console.print(Panel(
            f"[bold red]✗ НЕ НАЙДЕН[/bold red]\n\n"
            f"[white]Username:[/white] [cyan]@{data['username']}[/cyan]\n"
            f"[white]URL:[/white] {data['url']}",
            title="[red]TELEGRAM[/red]",
            border_style="red",
            box=box.DOUBLE
        ))
        return

    table = Table(show_header=False, box=box.ROUNDED, border_style="green", padding=(0, 2))
    table.add_column("k", style="dim white", no_wrap=True)
    table.add_column("v", style="bold")

    table.add_row("Статус", "[green]✓ СУЩЕСТВУЕТ[/green]")
    table.add_row("Юзернейм", f"[cyan]@{data['username']}[/cyan]")
    table.add_row("Тип", f"[yellow]{data['type']}[/yellow]")
    if data["title"]:
        table.add_row("Имя", data["title"])
    if data["description"]:
        desc = data["description"][:200] + ("..." if len(data["description"]) > 200 else "")
        table.add_row("Описание", desc)
    if data["photo"]:
        table.add_row("Аватар", f"[link={data['photo']}]открыть[/link]")
    table.add_row("URL", f"[link={data['url']}]{data['url']}[/link]")

    console.print(Panel(table, title="[bold green]TELEGRAM[/bold green]", border_style="green", box=box.DOUBLE))


def run_sherlock(username):
    sherlock_path = os.path.expanduser("~/sherlock/sherlock/sherlock.py")
    if not os.path.exists(sherlock_path):
        console.print("[red]Sherlock не найден в ~/sherlock/sherlock/sherlock.py[/red]")
        return None

    console.print(f"\n[cyan]Запускаю Sherlock для @{username}...[/cyan]\n")
    try:
        proc = subprocess.run(
            ["python3", sherlock_path, username, "--local"],
            capture_output=True, text=True, timeout=300
        )
        return proc.stdout
    except Exception as e:
        console.print(f"[red]Ошибка запуска Sherlock: {e}[/red]")
        return None


def save_report(username, tg_data, sherlock_data):
    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f"{REPORT_DIR}/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"OSINT REPORT for @{username}\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write("--- TELEGRAM ---\n")
        f.write(json.dumps(tg_data, ensure_ascii=False, indent=2))
        f.write("\n\n--- SHERLOCK ---\n")
        if sherlock_data:
            f.write(sherlock_data)
        else:
            f.write("(not run)\n")

    console.print(f"\n[green]✓ Отчёт сохранён:[/green] {filename}")


def menu():
    console.print("\n[bold cyan]═══ МЕНЮ ═══[/bold cyan]")
    console.print("[1] Проверить Telegram-юзер")
    console.print("[2] Прогнать Sherlock (поиск по 400+ сайтам)")
    console.print("[3] Полный отчёт (Telegram + Sherlock) → сохранить в файл")
    console.print("[4] Выход\n")


def main():
    banner()

    if len(sys.argv) > 1:
        username = sys.argv[1].lstrip("@").strip()
    else:
        username = Prompt.ask("[bold cyan]Введи юзернейм (без @)[/bold cyan]").lstrip("@").strip()

    if not username:
        console.print("[red]Пустой ввод.[/red]")
        return

    console.print(f"\n[cyan]Проверяю @{username}...[/cyan]\n")
    tg_data = check_telegram(username)
    render_telegram(tg_data)

    while True:
        menu()
        choice = Prompt.ask("[bold yellow]Выбор[/bold yellow]", choices=["1", "2", "3", "4"])

        if choice == "1":
            render_telegram(tg_data)

        elif choice == "2":
            out = run_sherlock(username)
            if out:
                console.print(Panel(out, title="[bold green]SHERLOCK[/bold green]", border_style="green"))

        elif choice == "3":
            sh = run_sherlock(username)
            save_report(username, tg_data, sh)

        elif choice == "4":
            console.print("[dim]Выход.[/dim]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Прервано.[/dim]")