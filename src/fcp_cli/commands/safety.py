"""Safety command - check food safety information."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fcp_cli.services.fcp import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import demo_safe, run_async

app = typer.Typer()
console = Console()


@app.command("recalls")
@demo_safe
def check_recalls(
    foods: list[str] = typer.Argument(..., help="Food items to check for recalls"),
) -> None:
    """Check for food recalls on specified items.

    Examples:
        fcp safety recalls lettuce romaine
        fcp safety recalls chicken "ground beef"
        fcp safety recalls eggs
    """
    try:
        client = FcpClient()
        result = run_async(client.check_food_recalls(foods))

        recalls = result.get("recalls", [])
        if not recalls:
            console.print("[green]No recalls found for the specified items.[/green]")
            return

        for recall in recalls:
            title = recall.get("title", recall.get("product", "Unknown"))
            reason = recall.get("reason", recall.get("description", "No details"))
            date = recall.get("date", recall.get("recall_date", "-"))
            panel = Panel(
                f"[red]Reason:[/red] {reason}\n[yellow]Date:[/yellow] {date}",
                title=f"[bold red]{title}[/bold red]",
                border_style="red",
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


@app.command("interactions")
def check_interactions(
    foods: list[str] = typer.Argument(..., help="Food items to check"),
    medications: list[str] = typer.Option(
        ...,
        "--medication",
        "-m",
        help="Medications to check for interactions",
    ),
) -> None:
    """Check for drug-food interactions."""
    try:
        client = FcpClient()
        result = run_async(client.check_drug_interactions(foods, medications))

        interactions = result.get("interactions", [])
        if not interactions:
            console.print("[green]No interactions found.[/green]")
            return

        table = Table(title="Drug-Food Interactions")
        table.add_column("Food", style="cyan")
        table.add_column("Medication", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Details")

        for interaction in interactions:
            table.add_row(
                interaction.get("food", "-"),
                interaction.get("medication", "-"),
                interaction.get("severity", "-"),
                interaction.get("description", interaction.get("details", "-")),
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


@app.command("allergens")
def check_allergens(
    foods: list[str] = typer.Argument(..., help="Food items to check"),
    allergies: list[str] = typer.Option(
        ...,
        "--allergy",
        "-a",
        help="Your allergies to check against",
    ),
) -> None:
    """Check for allergen alerts in food items."""
    try:
        client = FcpClient()
        result = run_async(client.check_allergen_alerts(foods, allergies))

        alerts = result.get("alerts", [])
        if not alerts:
            console.print("[green]No allergen alerts found.[/green]")
            return

        for alert in alerts:
            food = alert.get("food", "Unknown")
            allergen = alert.get("allergen", "Unknown")
            confidence = alert.get("confidence", "Unknown")
            panel = Panel(
                f"[yellow]Allergen:[/yellow] {allergen}\n[cyan]Confidence:[/cyan] {confidence}",
                title=f"[bold red]Alert: {food}[/bold red]",
                border_style="red",
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


@app.command("restaurant")
def check_restaurant(
    name: str = typer.Argument(..., help="Name of the restaurant"),
    location: str = typer.Argument(..., help="City or address"),
) -> None:
    """Get safety and health inspection information for a restaurant."""
    try:
        client = FcpClient()
        result = run_async(client.get_restaurant_safety_info(name, location))

        name = result.get("restaurant_name", name)
        status = result.get("status", "Unknown")
        last_inspection = result.get("last_inspection_date", "Unknown")
        score = result.get("inspection_score", "N/A")
        violations = result.get("violations", [])

        content_parts = [
            f"[bold]Status:[/bold] {status}",
            f"[bold]Last Inspection:[/bold] {last_inspection}",
            f"[bold]Score:[/bold] {score}",
        ]

        if violations:
            content_parts.append("\n[bold red]Violations:[/bold red]")
            for v in violations:
                if isinstance(v, dict):
                    v_text = v.get("description", str(v))
                    v_critical = " [bold red](CRITICAL)[/bold red]" if v.get("is_critical") else ""
                    content_parts.append(f"  - {v_text}{v_critical}")
                else:
                    content_parts.append(f"  - {v}")

        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold blue]Safety Info: {name}[/bold blue]",
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
