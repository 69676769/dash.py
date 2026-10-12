# -*- coding: utf-8 -*-
import sys
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

BANNER = r"""
  ████████╗ ██████╗     ███████╗ ██████╗ █████╗ ███╗   ██╗
  ╚══██╔══╝██╔════╝     ██╔════╝██╔════╝██╔══██╗████╗  ██║
     ██║   ██║  ███╗    ███████╗██║     ███████║██╔██╗ ██║
     ██║   ██║   ██║    ╚════██║██║     ██╔══██║██║╚██╗██║
     ██║   ╚██████╔╝    ███████║╚██████╗██║  ██║██║ ╚████║
     ╚═╝    ╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
}

def banner():
    console.print(Align.center(Panel(Text(BANNER, style="bold green"), border_style="green", box=box.DOUBLE)))
    console.print(Align.center("[dim]real telegram checker // v1.0[/dim]\n"))

def check_username(username):
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

def render_result(data):
    if "error" in data:
        console.print(Panel(f"[red]Ошибка запроса: {data['error']}[/red]", border_style="red"))
        return

    if not data["exists"]:
        console.print()
        console.print(Panel(
            f"[bold red]✗ АККАУНТ НЕ НАЙДЕН[/bold red]\n\n"
            f"[white]Username:[/white] [cyan]@{data['username']}[/cyan]\n"
            f"[white]Проверен:[/white] {data['url']}\n\n"
            f"[dim]Такого юзернейма не существует в Telegram[/dim]",
            title="[red]РЕЗУЛЬТАТ[/red]",
            border_style="red",
            box=box.DOUBLE
        ))
        return

    table = Table(show_header=False, box=box.ROUNDED, border_style="green", padding=(0, 2))
    table.add_column("key", style="dim white", no_wrap=True)
    table.add_column("value", style="bold")

    table.add_row("Статус", "[green]✓ СУЩЕСТВУЕТ[/green]")
    table.add_row("Юзернейм", f"[cyan]@{data['username']}[/cyan]")
    table.add_row("Тип", f"[yellow]{data['type']}[/yellow]")

    if data["title"]:
        table.add_row("Имя / Название", data["title"])
    if data["description"]:
        desc = data["description"][:200] + ("..." if len(data["description"]) > 200 else "")
        table.add_row("Описание", desc)
    if data["photo"]:
        table.add_row("Аватар", f"[link={data['photo']}]открыть[/link]")

    table.add_row("URL", f"[link={data['url']}]{data['url']}[/link]")

    console.print()
    console.print(Panel(table, title="[bold green]РЕЗУЛЬТАТ[/bold green]", border_style="green", box=box.DOUBLE))

def main():
    banner()

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = console.input("[bold cyan]Введи юзернейм (без @) → [/bold cyan]")

    username = username.strip()
    if not username:
        console.print("[red]Пустой ввод.[/red]")
        return

    with console.status(f"[cyan]Проверяю @{username.lstrip('@')}...[/cyan]", spinner="dots"):
        time.sleep(0.4)
        data = check_username(username)

    render_result(data)
    console.print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Прервано.[/dim]")