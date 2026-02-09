"""Taste command - Taste Buddy dietary compatibility checker."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async

app = typer.Typer()
console = Console()


@app.command("check")
def check_compatibility(
    dish_name: str = typer.Argument(..., help="Name of the dish to check"),
    ingredients: list[str] = typer.Option(
        [],
        "--ingredient",
        "-i",
        help="Ingredient to check (can use multiple times)",
    ),
    allergies: list[str] = typer.Option(
        [],
        "--allergy",
        "-a",
        help="Allergy to check against (can use multiple times)",
    ),
    diets: list[str] = typer.Option(
        [],
        "--diet",
        "-d",
        help="Dietary restriction (can use multiple times)",
    ),
) -> None:
    """Check if a dish is compatible with your dietary restrictions."""
    try:
        client = FcpClient()
        result = run_async(
            client.check_taste_buddy(
                dish_name=dish_name,
                ingredients=ingredients or None,
                user_allergies=allergies or None,
                user_diet=diets or None,
            )
        )

        # Determine overall status
        if result.is_safe and result.is_compliant:
            status = "[green]Safe & Compliant[/green]"
            border = "green"
        elif result.is_safe:
            status = "[yellow]Safe but has diet conflicts[/yellow]"
            border = "yellow"
        else:
            status = "[red]Not Safe[/red]"
            border = "red"

        content_parts = [f"[bold]Status:[/bold] {status}"]

        if result.detected_allergens:
            content_parts.append(f"\n[red]Detected Allergens:[/red] {', '.join(result.detected_allergens)}")

        if result.diet_conflicts:
            content_parts.append(f"\n[yellow]Diet Conflicts:[/yellow] {', '.join(result.diet_conflicts)}")

        if result.warnings:
            content_parts.append("\n[yellow]Warnings:[/yellow]")
            content_parts.extend(f"  - {warning}" for warning in result.warnings)
        if result.modifications:
            content_parts.append("\n[cyan]Suggested Modifications:[/cyan]")
            content_parts.extend(f"  - {mod}" for mod in result.modifications)
        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold]Taste Buddy: {dish_name}[/bold]",
            border_style=border,
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


@app.command("pairings")
def get_pairings(
    ingredient: str = typer.Argument(..., help="Ingredient to find pairings for"),
    count: int = typer.Option(5, "--count", "-c", help="Number of pairings to return"),
) -> None:
    """Get flavor pairings for an ingredient."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(f"Finding pairings for {ingredient}...", total=None)

        try:
            client = FcpClient()
            pairings = run_async(client.get_flavor_pairings(ingredient, count))

            if not pairings:
                console.print(f"[yellow]No pairings found for {ingredient}.[/yellow]")
                return

            # Format pairings - handle both dict and string formats
            pairing_lines = []
            for p in pairings:
                if isinstance(p, dict):
                    name = p.get("name", "Unknown")
                    reason = p.get("reason", "")
                    flavor = p.get("flavor_profile", "")
                    line = f"[bold cyan]{name}[/bold cyan]"
                    if flavor:
                        line += f" [dim]({flavor})[/dim]"
                    if reason:
                        line += f"\n  [dim]{reason}[/dim]"
                    pairing_lines.append(line)
                else:
                    pairing_lines.append(f"[cyan]{p}[/cyan]")

            console.print(
                Panel(
                    "\n\n".join(pairing_lines),
                    title=f"[bold]Flavor Pairings: {ingredient}[/bold]",
                    border_style="magenta",
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
