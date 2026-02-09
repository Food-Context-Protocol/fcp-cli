"""Discover command - food discovery and recommendations."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async, validate_latitude_callback, validate_longitude_callback

app = typer.Typer()
console = Console()


def _validate_optional_latitude(value: float | None) -> float | None:
    """Validate latitude if provided."""
    return None if value is None else validate_latitude_callback(value)


def _validate_optional_longitude(value: float | None) -> float | None:
    """Validate longitude if provided."""
    return None if value is None else validate_longitude_callback(value)


@app.command("food")
def discover_food() -> None:
    """Get daily food discovery insights."""
    try:
        client = FcpClient()
        result = run_async(client.discover_food())

        insight = result.get("insight")
        discoveries = result.get("discoveries", result.get("items", []))

        if not discoveries and not insight:
            console.print("[yellow]No discoveries available today.[/yellow]")
            return

        if insight:
            console.print(Panel(insight, title="[bold]Daily Food Insight[/bold]", border_style="green"))

        for item in discoveries:
            title = item.get("name", item.get("title", "Discovery"))
            desc = item.get("description", "")
            category = item.get("category", "")
            header = f"[bold]{title}[/bold]" + (f" ({category})" if category else "")
            panel = Panel(desc, title=header, border_style="green")
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


@app.command("restaurants")
def discover_restaurants(
    latitude: float | None = typer.Option(
        None, "--lat", help="Your latitude (-90 to 90)", callback=_validate_optional_latitude
    ),
    longitude: float | None = typer.Option(
        None, "--lon", help="Your longitude (-180 to 180)", callback=_validate_optional_longitude
    ),
    location: str | None = typer.Option(None, "--location", "-l", help="City or address (e.g., 'San Francisco, CA')"),
) -> None:
    """Discover nearby restaurants based on your preferences.

    Location can be specified via coordinates (--lat/--lon) or address (--location).
    If both are provided, coordinates take precedence.
    """
    # Validate that either coordinates or location is provided
    has_coords = latitude is not None and longitude is not None
    has_location = location is not None

    if not has_coords and not has_location:
        console.print("[red]Error:[/red] Please provide either --lat/--lon or --location")
        raise typer.Exit(1)

    if (latitude is not None) != (longitude is not None):
        console.print("[red]Error:[/red] Both --lat and --lon must be provided together")
        raise typer.Exit(1)

    try:
        client = FcpClient()
        result, resolved_location = run_async(
            client.discover_restaurants(
                latitude=latitude,
                longitude=longitude,
                location=location,
            )
        )

        restaurants = result.get("restaurants", result.get("results", []))
        if not restaurants:
            console.print("[yellow]No restaurant recommendations found.[/yellow]")
            return

        # Show resolved location if address was geocoded
        title = "Restaurant Recommendations"
        if resolved_location and location:
            title = f"Restaurant Recommendations in {resolved_location}"

        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Cuisine", style="green")
        table.add_column("Rating", style="yellow")
        table.add_column("Distance")

        for restaurant in restaurants:
            table.add_row(
                restaurant.get("name", "-"),
                restaurant.get("cuisine", restaurant.get("type", "-")),
                str(restaurant.get("rating", "-")),
                restaurant.get("distance", "-"),
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


@app.command("recipes")
def discover_recipes(
    ingredients: list[str] = typer.Argument(..., help="Ingredients you have available"),
) -> None:
    """Discover recipes based on available ingredients."""
    try:
        client = FcpClient()
        result = run_async(client.discover_recipes(ingredients))

        recipes = result.get("recipes", result.get("suggestions", []))
        if not recipes:
            console.print("[yellow]No recipe suggestions found.[/yellow]")
            return

        for recipe in recipes:
            title = recipe.get("name", recipe.get("title", "Recipe"))
            desc = recipe.get("description", "")
            time = recipe.get("cook_time", recipe.get("time", ""))
            difficulty = recipe.get("difficulty", "")
            meta = []
            if time:
                meta.append(f"Time: {time}")
            if difficulty:
                meta.append(f"Difficulty: {difficulty}")
            content = desc + ("\n" + " | ".join(meta) if meta else "")
            panel = Panel(content, title=f"[bold]{title}[/bold]", border_style="blue")
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


@app.command("trends")
def show_trends(
    region: str | None = typer.Option(None, "--region", "-r", help="Region to get trends for"),
    cuisine: str | None = typer.Option(None, "--cuisine", "-c", help="Cuisine focus"),
) -> None:
    """Show current food trends."""
    try:
        client = FcpClient()
        result = run_async(client.get_food_trends(region=region, cuisine_focus=cuisine))

        trends = result.get("trends", [])
        if not trends:
            console.print("[yellow]No trends available.[/yellow]")
            return

        table = Table(title="Food Trends")
        table.add_column("Trend", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Popularity", style="yellow")

        for trend in trends:
            table.add_row(
                trend.get("name", "-"),
                trend.get("description", "-"),
                trend.get("popularity", trend.get("score", "-")),
            )

        console.print(table)

        if sources := result.get("sources", []):
            console.print("\n[dim]Sources:[/dim]")
            for source in sources:
                title = source.get("title", "Source")
                url = source.get("url", "")
                console.print(f"  - {title}: {url}")

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


@app.command("tip")
def show_tip() -> None:
    """Get a random food tip."""
    try:
        client = FcpClient()
        result = run_async(client.get_random_tip())

        tip = result.get("tip", result.get("text", result.get("content", "")))
        tip_title = result.get("tip_title", "")
        category = result.get("category", "")
        source = result.get("source", "")

        if not tip:
            console.print("[yellow]No tip available.[/yellow]")
            return

        # Build display title
        base_title = tip_title or "Food Tip"
        display_title = f"[bold]{base_title}[/bold]{f' ({category})' if category else ''}"

        # Build content with source attribution if available
        content_parts = [tip]
        if source:
            content_parts.append(f"[dim]Source: {source}[/dim]")
        content = "\n\n".join(content_parts)

        panel = Panel(content, title=display_title, border_style="cyan")
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
