"""Labels command - cottage food label generation."""

import typer
from rich.console import Console
from rich.panel import Panel

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async

app = typer.Typer()
console = Console()


@app.command("cottage")
def generate_cottage_label(
    product_name: str = typer.Argument(..., help="Name of the product"),
    ingredients: list[str] = typer.Argument(..., help="Ingredients in order of weight"),
    weight: str | None = typer.Option(None, "--weight", "-w", help="Net weight (e.g., '12 oz (340g)')"),
    business_name: str | None = typer.Option(None, "--business", "-b", help="Business name"),
    address: str | None = typer.Option(None, "--address", "-a", help="Business address"),
    refrigerated: bool = typer.Option(False, "--refrigerated", "-r", help="Product requires refrigeration"),
) -> None:
    """Generate a cottage food product label."""
    try:
        client = FcpClient()
        label = run_async(
            client.generate_cottage_label(
                product_name=product_name,
                ingredients=ingredients,
                net_weight=weight,
                business_name=business_name,
                business_address=address,
                is_refrigerated=refrigerated,
            )
        )

        content_parts = [
            f"[bold]Product:[/bold] {label.product_name}",
            f"\n[bold]Ingredients:[/bold]\n  {', '.join(label.ingredients)}",
        ]

        if label.allergen_warnings:
            content_parts.append(f"\n[yellow]Contains:[/yellow] {', '.join(label.allergen_warnings)}")

        if label.weight:
            content_parts.append(f"\n[bold]Net Weight:[/bold] {label.weight}")

        if label.producer_info:
            content_parts.append(f"\n[bold]Produced by:[/bold] {label.producer_info}")

        if label.warnings:
            content_parts.append("\n[yellow]Warnings:[/yellow]")
            content_parts.extend(f"  - {warning}" for warning in label.warnings)
        if label.regulatory_notes:
            content_parts.append("\n[dim]Regulatory Notes:[/dim]")
            content_parts.extend(f"  - {note}" for note in label.regulatory_notes)
        if label.label_text:
            content_parts.append(f"\n[dim]---[/dim]\n{label.label_text}")

        panel = Panel(
            "\n".join(content_parts),
            title="[bold]Cottage Food Label[/bold]",
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
