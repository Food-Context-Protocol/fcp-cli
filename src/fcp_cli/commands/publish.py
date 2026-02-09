"""Publish command - generate and manage content."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async

app = typer.Typer()
console = Console()


@app.command("generate")
def generate_content(
    content_type: str = typer.Argument(
        ...,
        help="Type of content to generate (blog, social, newsletter)",
    ),
    log_ids: list[str] = typer.Option(
        None,
        "--log",
        "-l",
        help="Food log IDs to include in content",
    ),
) -> None:
    """Generate publishable content from your food logs."""
    try:
        client = FcpClient()
        result = run_async(client.generate_content(content_type, log_ids))

        title = result.get("title", "Generated Content")
        content = result.get("content", result.get("body", ""))
        status = result.get("status", "draft")

        panel = Panel(
            content,
            title=f"[bold]{title}[/bold]",
            subtitle=f"[dim]Status: {status}[/dim]",
            border_style="blue",
        )
        console.print(panel)

        if result.get("id"):
            console.print(f"\n[dim]Draft ID: {result['id']}[/dim]")

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("drafts")
def list_drafts() -> None:
    """List content drafts."""
    try:
        client = FcpClient()
        drafts = run_async(client.get_drafts())

        if not drafts:
            console.print("[yellow]No drafts yet.[/yellow]")
            return

        table = Table(title="Content Drafts")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")

        for draft in drafts:
            table.add_row(
                draft.get("id", "-"),
                draft.get("title", "-"),
                draft.get("content_type", draft.get("type", "-")),
                draft.get("status", "-"),
            )

        console.print(table)

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("show")
def show_draft(
    draft_id: str = typer.Argument(..., help="ID of draft to view"),
) -> None:
    """View details of a specific draft."""
    try:
        client = FcpClient()
        draft = run_async(client.get_draft(draft_id))

        content_parts = []
        if draft.content:
            content_parts.append(draft.content)

        meta = []
        if draft.content_type:
            meta.append(f"Type: {draft.content_type}")
        if draft.status:
            meta.append(f"Status: {draft.status}")
        if draft.platforms:
            meta.append(f"Platforms: {', '.join(draft.platforms)}")

        if meta:
            content_parts.append(f"\n[dim]{' | '.join(meta)}[/dim]")

        content_parts.append(f"\n[dim]ID: {draft.id}[/dim]")

        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold]{draft.title}[/bold]",
            border_style="blue",
        )
        console.print(panel)

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("edit")
def edit_draft(
    draft_id: str = typer.Argument(..., help="ID of draft to edit"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    content: str | None = typer.Option(None, "--content", "-c", help="New content"),
    status: str | None = typer.Option(None, "--status", "-s", help="New status"),
) -> None:
    """Edit a draft."""
    if not any([title, content, status]):
        console.print("[yellow]No changes specified. Use --title, --content, or --status.[/yellow]")
        raise typer.Exit(0)

    try:
        client = FcpClient()
        draft = run_async(
            client.update_draft(
                draft_id=draft_id,
                title=title,
                content=content,
                status=status,
            )
        )

        console.print(
            Panel(
                f"[bold]Title:[/bold] {draft.title}\n[dim]ID: {draft.id}[/dim]",
                title="[green]Draft Updated[/green]",
                border_style="green",
            )
        )

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("delete")
def delete_draft(
    draft_id: str = typer.Argument(..., help="ID of draft to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a draft."""
    if not yes and not typer.confirm(f"Delete draft {draft_id}?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    try:
        client = FcpClient()
        run_async(client.delete_draft(draft_id))
        console.print(f"[green]Deleted draft {draft_id}.[/green]")

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("publish")
def publish_draft(
    draft_id: str = typer.Argument(..., help="ID of draft to publish"),
    platforms: list[str] = typer.Option(
        [],
        "--platform",
        "-p",
        help="Platform to publish to (can use multiple times)",
    ),
) -> None:
    """Publish a draft to platforms."""
    try:
        client = FcpClient()
        result = run_async(
            client.publish_draft(
                draft_id=draft_id,
                platforms=platforms or None,
            )
        )

        published_to = result.get("platforms", result.get("published_to", []))
        urls = result.get("external_urls", result.get("urls", {}))

        content_parts = ["[green]Successfully published![/green]"]
        if published_to:
            content_parts.append(f"\n[bold]Platforms:[/bold] {', '.join(published_to)}")
        if urls:
            content_parts.append("\n[bold]URLs:[/bold]")
            if isinstance(urls, dict):
                content_parts.extend(f"  {platform}: {url}" for platform, url in urls.items() if url)
            else:
                content_parts.append(f"  {urls}")

        console.print(
            Panel(
                "\n".join(content_parts),
                title="[bold]Published[/bold]",
                border_style="green",
            )
        )

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("published")
def list_published() -> None:
    """View published content."""
    try:
        client = FcpClient()
        published = run_async(client.get_published_content())

        if not published:
            console.print("[yellow]No published content yet.[/yellow]")
            return

        table = Table(title="Published Content")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Platform", style="yellow")
        table.add_column("Date", style="dim")

        for item in published:
            table.add_row(
                item.get("id", "-"),
                item.get("title", "-"),
                item.get("content_type", item.get("type", "-")),
                ", ".join(item.get("platforms", [])) if item.get("platforms") else "-",
                item.get("published_at", item.get("date", "-")),
            )

        console.print(table)

    except FcpConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        console.print("[dim]Is the FCP server running?[/dim]")
        raise typer.Exit(1) from e
    except FcpServerError as e:
        console.print(f"[red]Server error:[/red] {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e
