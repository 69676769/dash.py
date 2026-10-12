# -*- coding: utf-8 -*-
import sys
import os
import time
import json
import random
import hashlib
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich import box

console = Console()

# ============ НАСТРОЙКИ АВТООБНОВЛЕНИЯ ============
RAW_URL = "https://raw.githubusercontent.com/69676769/dash.py/main/dash.py"
LOCAL_FILE = os.path.expanduser("~/dash.py")
VERSION = "1.0"

BANNER = r"""
  ███████╗███╗   ██╗ ██████╗ ███████╗███████╗██████╗ 
  ██╔════╝████╗  ██║██╔═══██╗██╔════╝██╔════╝██╔══██╗
  ███████╗██╔██╗ ██║██║   ██║███████╗█████╗  ██████╔╝
  ╚════██║██║╚██╗██║██║   ██║╚════██║██╔══╝  ██╔══██╗
  ███████║██║ ╚████║╚██████╔╝███████║███████╗██║  ██║
  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝
"""


def banner():
    console.clear()
    console.print(Align.center(Panel(Text(BANNER, style="bold red"), border_style="red", box=box.DOUBLE)))
    console.print(Align.center(f"[dim]SNOSER DASHBOARD // v{VERSION} // iSH Edition[/dim]\n"))


def auto_update():
    console.print("[dim]Проверяю обновления с GitHub...[/dim]")
    try:
        r = subprocess.run(
            ["busybox", "wget", "-q", "-O", "-", RAW_URL],
            capture_output=True, timeout=30
        )
        if r.returncode != 0:
            console.print("[yellow]Не удалось проверить обновления. Продолжаю с локальной версией.[/yellow]\n")
            return

        remote_code = r.stdout.decode("utf-8", errors="ignore")

        if not os.path.exists(LOCAL_FILE):
            console.print("[yellow]Локальный файл не найден.[/yellow]\n")
            return

        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            local_code = f.read()

        remote_hash = hashlib.md5(remote_code.encode()).hexdigest()
        local_hash = hashlib.md5(local_code.encode()).hexdigest()

        if remote_hash != local_hash:
            console.print("[green]✓ Найдена новая версия. Обновляю...[/green]")
            with open(LOCAL_FILE, "w", encoding="utf-8") as f:
                f.write(remote_code)
            console.print("[green]✓ Обновлено. Перезапусти скрипт.[/green]\n")
            sys.exit(0)
        else:
            console.print("[green]✓ Версия актуальна.[/green]\n")

    except Exception as e:
        console.print(f"[yellow]Ошибка автообновления: {e}[/yellow]\n")


def fake_snos(username, threads=10, count=100):
    """Визуальная имитация процесса сноса."""
    stats = {
        "target": f"@{username}",
        "threads": threads,
        "total": count,
        "sent": 0,
        "success": 0,
        "failed": 0,
        "started": datetime.now().strftime("%H:%M:%S"),
    }

    console.print(Panel(
        f"[bold red]ЦЕЛЬ:[/bold red] {stats['target']}\n"
        f"[bold]Потоков:[/bold] {threads}\n"
        f"[bold]Всего жалоб:[/bold] {count}\n"
        f"[bold]Старт:[/bold] {stats['started']}",
        title="[bold red]ЗАПУСК СНОСА[/bold red]",
        border_style="red",
        box=box.DOUBLE
    ))
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[red]Отправка жалоб...", total=count)

        for i in range(count):
            time.sleep(random.uniform(0.03, 0.12))
            stats["sent"] += 1

            if random.random() > 0.85:
                stats["success"] += 1
                color = "green"
                mark = "✓"
            else:
                stats["failed"] += 1
                color = "red"
                mark = "✗"

            progress.update(
                task,
                advance=1,
                description=f"[red]Жалоба {stats['sent']}/{count} [{color}]{mark}[/{color}]"
            )

    console.print()

    result_table = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
    result_table.add_column("k", style="dim white")
    result_table.add_column("v", style="bold")

    result_table.add_row("Цель", f"[cyan]{stats['target']}[/cyan]")
    result_table.add_row("Отправлено", str(stats["total"]))
    result_table.add_row("Успех", f"[green]{stats['success']}[/green]")
    result_table.add_row("Провал", f"[red]{stats['failed']}[/red]")
    result_table.add_row("Эффективность", f"[yellow]{round(stats['success']/stats['total']*100, 1)}%[/yellow]")
    result_table.add_row("Статус", "[red]СНОС ЗАВЕРШЁН[/red]")

    console.print(Panel(result_table, title="[bold red]РЕЗУЛЬТАТ[/bold red]", border_style="red", box=box.DOUBLE))

    # Сохранение лога
    os.makedirs(os.path.expanduser("~/snos_logs"), exist_ok=True)
    log_path = os.path.expanduser(f"~/snos_logs/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    console.print(f"\n[dim]Лог сохранён: {log_path}[/dim]")


def menu():
    console.print("\n[bold red]═══ ГЛАВНОЕ МЕНЮ ═══[/bold red]")
    console.print("[1] [red]СНОС[/red] — запустить процесс")
    console.print("[2] Показать логи")
    console.print("[3] Проверить обновления")
    console.print("[4] Выход\n")


def show_logs():
    log_dir = os.path.expanduser("~/snos_logs")
    if not os.path.exists(log_dir):
        console.print("[yellow]Логов пока нет.[/yellow]")
        return
    files = sorted(os.listdir(log_dir))
    if not files:
        console.print("[yellow]Логов нет.[/yellow]")
        return
    for f in files[-10:]:
        console.print(f"[dim]{f}[/dim]")


def main():
    banner()
    auto_update()

    target = None

    while True:
        if target is None:
            target = Prompt.ask("[bold cyan]Введи юзернейм цели (без @)[/bold cyan]").lstrip("@").strip()
            if not target:
                continue

        menu()
        choice = Prompt.ask("[bold yellow]Выбор[/bold yellow]", choices=["1", "2", "3", "4"])

        if choice == "1":
            threads = Prompt.ask("[cyan]Потоков[/cyan]", default="10")
            count = Prompt.ask("[cyan]Всего жалоб[/cyan]", default="100")
            try:
                fake_snos(target, int(threads), int(count))
            except ValueError:
                console.print("[red]Неверное число.[/red]")

        elif choice == "2":
            show_logs()

        elif choice == "3":
            auto_update()

        elif choice == "4":
            console.print("[dim]Выход.[/dim]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Прервано.[/dim]")