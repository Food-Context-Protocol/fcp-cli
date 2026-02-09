"""Pantry command - manage pantry items."""

from enum import StrEnum

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import (
    ImageTooLargeError,
    InvalidImageError,
    read_image_as_base64,
    run_async,
)


class PantryCategory(StrEnum):
    """Valid pantry item categories."""

    PRODUCE = "produce"
    DAIRY = "dairy"
    PROTEINS = "proteins"
    GRAINS = "grains"
    FROZEN = "frozen"
    CANNED = "canned"
    CONDIMENTS = "condiments"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    OTHER = "other"


class StorageLocation(StrEnum):
    """Valid storage locations."""

    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"


app = typer.Typer()
console = Console()


@app.command("list")
def list_pantry() -> None:
    """List all items in your pantry."""
    try:
        client = FcpClient()
        items = run_async(client.get_user_pantry())

        if not items:
            console.print("[yellow]Your pantry is empty.[/yellow]")
            return

        table = Table(title="Pantry Items")
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", style="green")
        table.add_column("Expiry", style="yellow")

        for item in items:
            name = item.get("name", item.get("item_name", "Unknown"))
            quantity = str(item.get("quantity", "-"))
            expiry = item.get("expiry_date", item.get("expiration", "-"))
            table.add_row(name, quantity, expiry)

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


@app.command("add")
def add_item(
    items: list[str] = typer.Argument(..., help="Items to add (e.g., 'eggs' 'milk' 'bread')"),
) -> None:
    """Add items to your pantry."""
    try:
        client = FcpClient()
        items_payload = [{"name": item} for item in items]
        run_async(client.add_to_pantry(items_payload))
        console.print(f"[green]Added {len(items)} item(s) to pantry.[/green]")

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


@app.command("expiring")
def check_expiring() -> None:
    """Check for expiring items in your pantry."""
    try:
        client = FcpClient()
        result = run_async(client.check_pantry_expiry())

        expiring = result.get("expiring", result.get("items", []))
        if not expiring:
            console.print("[green]No items expiring soon.[/green]")
            return

        table = Table(title="Expiring Items")
        table.add_column("Item", style="cyan")
        table.add_column("Expires", style="red")

        for item in expiring:
            name = item.get("name", item.get("item_name", "Unknown"))
            expiry = item.get("expiry_date", item.get("expiration", "-"))
            table.add_row(name, expiry)

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


@app.command("suggest")
def suggest_meals() -> None:
    """Get meal suggestions based on pantry items."""
    try:
        client = FcpClient()
        result = run_async(client.get_pantry_suggestions())

        suggestions = result.get("suggestions", [])
        if not suggestions:
            console.print("[yellow]No suggestions available.[/yellow]")
            return

        for i, suggestion in enumerate(suggestions, 1):
            title = suggestion.get("name", suggestion.get("title", f"Suggestion {i}"))
            desc = suggestion.get("description", "")
            panel = Panel(desc, title=f"[bold]{title}[/bold]", border_style="green")
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


@app.command("update")
def update_item(
    item_id: str = typer.Argument(..., help="ID of pantry item to update"),
    quantity: str | None = typer.Option(None, "--qty", "-q", help="New quantity"),
    category: PantryCategory | None = typer.Option(None, "--category", "-c", help="Category"),
    location: StorageLocation | None = typer.Option(None, "--location", "-l", help="Storage location"),
    expiration: str | None = typer.Option(None, "--expires", "-e", help="Expiration date (YYYY-MM-DD)"),
) -> None:
    """Update a pantry item."""
    if not any([quantity, category, location, expiration]):
        console.print("[yellow]No changes specified. Use --qty, --category, --location, or --expires.[/yellow]")
        raise typer.Exit(0)

    try:
        client = FcpClient()
        item = run_async(
            client.update_pantry_item(
                item_id=item_id,
                quantity=quantity,
                category=category.value if category else None,
                storage_location=location.value if location else None,
                expiration_date=expiration,
            )
        )

        console.print(
            Panel(
                f"[bold]Item:[/bold] {item.name}\n[dim]ID: {item.id}[/dim]",
                title="[green]Pantry Item Updated[/green]",
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
def delete_item(
    item_id: str = typer.Argument(..., help="ID of pantry item to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a pantry item."""
    if not yes and not typer.confirm(f"Delete pantry item {item_id}?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    try:
        client = FcpClient()
        run_async(client.delete_pantry_item(item_id))
        console.print(f"[green]Deleted pantry item {item_id}.[/green]")

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


@app.command("receipt")
def parse_receipt(
    image: str = typer.Argument(..., help="Path to receipt image"),
) -> None:
    """Parse a receipt image and add items to pantry."""
    # Validate image file first
    try:
        image_base64 = read_image_as_base64(image)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e
    except (ImageTooLargeError, InvalidImageError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Parsing receipt...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.parse_receipt(image_base64))

            items = result.get("items", [])
            if not items:
                console.print("[yellow]No items found in receipt.[/yellow]")
                return

            table = Table(title="Receipt Items")
            table.add_column("Item", style="cyan")
            table.add_column("Quantity", style="green")
            table.add_column("Price", style="yellow")

            for item in items:
                name = item.get("name", item.get("description", "Unknown"))
                qty = str(item.get("quantity", 1))
                price = str(item.get("price", "-"))
                table.add_row(name, qty, price)

            console.print(table)

            if typer.confirm("Add these items to pantry?"):
                run_async(client.add_to_pantry(items))
                console.print(f"[green]Added {len(items)} items to pantry.[/green]")

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


@app.command("use")
def use_items(
    items: list[str] = typer.Argument(..., help="Items to use/deduct (e.g., 'eggs' 'milk')"),
    quantity: str | None = typer.Option(None, "--qty", "-q", help="Quantity to deduct (applies to all items)"),
) -> None:
    """Use/deduct items from your pantry.

    Mark items as used when cooking. Items will be deducted from inventory.
    """
    try:
        client = FcpClient()
        items_payload = [{"name": item, "quantity": quantity or "1"} for item in items]
        result = run_async(client.deduct_from_pantry(items_payload))

        deducted = result.get("deducted", result.get("items", []))
        not_found = result.get("not_found", [])

        if deducted:
            console.print(f"[green]Used {len(deducted)} item(s) from pantry.[/green]")
            for item in deducted:
                name = item.get("name", item)
                remaining = item.get("remaining", item.get("quantity_remaining"))
                if remaining is not None:
                    console.print(f"  - {name}: {remaining} remaining")
                else:
                    console.print(f"  - {name}")

        if not_found:
            console.print("\n[yellow]Not found in pantry:[/yellow]")
            for item in not_found:
                name = item if isinstance(item, str) else item.get("name", item)
                console.print(f"  - {name}")

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
