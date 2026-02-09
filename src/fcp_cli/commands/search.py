"""Search command - Search food logs."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from fcp_cli.services.fcp import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import demo_safe, get_relative_time, parse_date_string, run_async, validate_limit

app = typer.Typer()
console = Console()


def _format_log_timestamp(timestamp) -> str:
    """Format log timestamp, returning empty string if None."""
    if timestamp:
        return get_relative_time(timestamp)
    return ""


@app.command("query")
@demo_safe
def query(
    query: str = typer.Argument(..., help="Search query (natural language)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum results", callback=validate_limit),
) -> None:
    """Search food logs using natural language queries.

    Examples:
        fcp search query "ramen from this week"
        fcp search query "high protein meals"
        fcp search query "what did I eat yesterday" --limit 5
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Searching...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.search_meals(query=query, limit=limit))

            if not result.logs:
                console.print(
                    Panel(
                        f"No results found for: [bold]{query}[/bold]",
                        title="[yellow]No Results[/yellow]",
                        border_style="yellow",
                    )
                )
                return

            # Create table
            table = Table(title=f"Search Results for '{query}' ({result.total} found)")
            table.add_column("Time", style="dim")
            table.add_column("Dish", style="bold")
            table.add_column("Description", style="dim", max_width=40)
            table.add_column("Type", style="cyan")

            for log in result.logs:
                time_str = _format_log_timestamp(log.timestamp)
                description = log.description or "-"
                if len(description) > 40:
                    description = f"{description[:37]}..."

                table.add_row(
                    time_str,
                    log.dish_name,
                    description,
                    log.meal_type or "-",
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
            console.print(f"[red]Search failed:[/red] {e}")
            raise typer.Exit(1) from e


def _validate_date(value: str) -> str:
    """Validate and parse date parameter."""
    try:
        # Parse to validate, then return ISO format
        parsed = parse_date_string(value)
        return parsed.strftime("%Y-%m-%d")
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


@app.command("by-date")
def by_date(
    date: str = typer.Argument(..., help="Date to search (YYYY-MM-DD, today, yesterday, or -N for days ago)"),
    end_date: str | None = typer.Option(None, "--to", "-t", help="End date for range search"),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum results", callback=validate_limit),
) -> None:
    """Search food logs by date or date range."""
    # Validate dates
    try:
        start = _validate_date(date)
        end = _validate_date(end_date) if end_date else None
    except typer.BadParameter as e:
        console.print(f"[red]Invalid date:[/red] {e}")
        raise typer.Exit(1) from e

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Searching by date...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.search_meals_by_date(start_date=start, end_date=end, limit=limit))

            if not result.logs:
                date_desc = f"{start} to {end}" if end else start
                console.print(
                    Panel(
                        f"No food logs found for: [bold]{date_desc}[/bold]",
                        title="[yellow]No Results[/yellow]",
                        border_style="yellow",
                    )
                )
                return

            # Create table
            date_desc = f"{start} to {end}" if end else start
            table = Table(title=f"Food Logs for {date_desc} ({result.total} found)")
            table.add_column("Time", style="dim")
            table.add_column("Dish", style="bold")
            table.add_column("Description", style="dim", max_width=40)
            table.add_column("Type", style="cyan")

            for log in result.logs:
                time_str = _format_log_timestamp(log.timestamp)
                description = log.description or "-"
                if len(description) > 40:
                    description = f"{description[:37]}..."

                table.add_row(
                    time_str,
                    log.dish_name,
                    description,
                    log.meal_type or "-",
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
            console.print(f"[red]Search failed:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("barcode")
def lookup_barcode(
    barcode: str = typer.Argument(..., help="Product barcode (UPC, EAN, etc.)"),
) -> None:
    """Look up food product information by barcode.

    Scan or enter a product barcode to get nutritional information.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Looking up barcode...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.lookup_product_by_barcode(barcode))

            if not result or result.get("error"):
                console.print(
                    Panel(
                        f"Product not found for barcode: [bold]{barcode}[/bold]",
                        title="[yellow]Not Found[/yellow]",
                        border_style="yellow",
                    )
                )
                return

            # Extract product information
            name = result.get("name", result.get("product_name", "Unknown Product"))
            brand = result.get("brand", result.get("manufacturer", ""))
            nutrition = result.get("nutrition", result.get("nutritional_info", {}))
            serving_size = result.get("serving_size", result.get("serving", ""))
            ingredients = result.get("ingredients", "")

            # Build content
            content_parts = []
            if brand:
                content_parts.append(f"[bold]Brand:[/bold] {brand}")
            if serving_size:
                content_parts.append(f"[bold]Serving Size:[/bold] {serving_size}")

            if nutrition:
                content_parts.append("\n[bold]Nutrition Facts:[/bold]")
                nutrients = ["calories", "protein", "carbs", "carbohydrates", "fat", "fiber", "sugar", "sodium"]
                units = {
                    "calories": "kcal",
                    "protein": "g",
                    "carbs": "g",
                    "carbohydrates": "g",
                    "fat": "g",
                    "fiber": "g",
                    "sugar": "g",
                    "sodium": "mg",
                }
                for nutrient in nutrients:
                    value = nutrition.get(nutrient)
                    if value is not None:
                        unit = units.get(nutrient, "")
                        display_name = "Carbs" if nutrient == "carbohydrates" else nutrient.capitalize()
                        content_parts.append(f"  {display_name}: {value}{unit}")

            if ingredients and isinstance(ingredients, str):
                # Truncate long ingredients list
                if len(ingredients) > 200:
                    ingredients = f"{ingredients[:197]}..."
                content_parts.append(f"\n[bold]Ingredients:[/bold]\n[dim]{ingredients}[/dim]")

            content_parts.append(f"\n[dim]Barcode: {barcode}[/dim]")

            panel = Panel(
                "\n".join(content_parts),
                title=f"[bold cyan]{name}[/bold cyan]",
                border_style="cyan",
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
            console.print(f"[red]Barcode lookup failed:[/red] {e}")
            raise typer.Exit(1) from e
