"""Suggest command - meal suggestions."""

import typer
from rich.console import Console
from rich.panel import Panel

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import demo_safe, run_async

app = typer.Typer()
console = Console()


@app.command("meals")
@demo_safe
def suggest_meals(
    context: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context for suggestions (e.g., 'date night', 'quick lunch', 'healthy')",
    ),
    exclude_days: int = typer.Option(
        3,
        "--exclude-days",
        "-e",
        help="Exclude meals from the last N days",
    ),
) -> None:
    """Get personalized meal suggestions based on your eating history.

    Examples:
        fcp suggest meals --context "japanese cuisine"
        fcp suggest meals --context "date night"
        fcp suggest meals --context "quick healthy lunch" --exclude-days 7
    """
    try:
        client = FcpClient()
        suggestions = run_async(
            client.suggest_meals(
                context=context,
                exclude_recent_days=exclude_days,
            )
        )

        if not suggestions:
            console.print("[yellow]No suggestions available.[/yellow]")
            return

        for suggestion in suggestions:
            content_parts = []
            if suggestion.description:
                content_parts.append(suggestion.description)
            if suggestion.meal_type:
                content_parts.append(f"\n[bold]Type:[/bold] {suggestion.meal_type}")
            if suggestion.venue:
                content_parts.append(f"[bold]Venue:[/bold] {suggestion.venue}")
            if suggestion.reason:
                content_parts.append(f"\n[dim]Why: {suggestion.reason}[/dim]")
            if suggestion.ingredients_needed:
                content_parts.append(f"\n[bold]Ingredients needed:[/bold] {', '.join(suggestion.ingredients_needed)}")
            if suggestion.prep_time:
                content_parts.append(f"[bold]Prep time:[/bold] {suggestion.prep_time}")
            if suggestion.match_score is not None:
                content_parts.append(f"[bold]Match score:[/bold] {suggestion.match_score:.0%}")

            panel = Panel(
                "\n".join(content_parts) if content_parts else "No details available",
                title=f"[bold]{suggestion.name}[/bold]",
                border_style="green",
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
