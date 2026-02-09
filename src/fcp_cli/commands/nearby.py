"""Nearby command - find nearby food venues."""

from enum import StrEnum

import typer
from rich.console import Console
from rich.table import Table

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async, validate_latitude_callback, validate_longitude_callback


class VenueType(StrEnum):
    """Valid venue types."""

    RESTAURANT = "restaurant"
    CAFE = "cafe"
    GROCERY = "grocery"
    BAKERY = "bakery"
    FOOD_TRUCK = "food_truck"


app = typer.Typer()
console = Console()


def _validate_optional_latitude(value: float | None) -> float | None:
    """Validate latitude if provided."""
    return None if value is None else validate_latitude_callback(value)


def _validate_optional_longitude(value: float | None) -> float | None:
    """Validate longitude if provided."""
    return None if value is None else validate_longitude_callback(value)


@app.command("venues")
def find_venues(
    latitude: float | None = typer.Option(
        None, "--lat", help="Your latitude (-90 to 90)", callback=_validate_optional_latitude
    ),
    longitude: float | None = typer.Option(
        None, "--lon", help="Your longitude (-180 to 180)", callback=_validate_optional_longitude
    ),
    location: str | None = typer.Option(None, "--location", "-l", help="City or address (e.g., 'San Francisco, CA')"),
    venue_type: VenueType | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Venue type (restaurant, cafe, grocery, bakery, food_truck)",
    ),
    radius: int = typer.Option(
        2000,
        "--radius",
        "-r",
        help="Search radius in meters",
    ),
) -> None:
    """Find nearby food venues.

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
        venues, resolved_location = run_async(
            client.find_nearby_venues(
                latitude=latitude,
                longitude=longitude,
                location=location,
                venue_type=venue_type.value if venue_type else None,
                radius=radius,
            )
        )

        if not venues:
            console.print("[yellow]No venues found nearby.[/yellow]")
            return

        # Show resolved location if address was geocoded
        title = "Nearby Venues"
        if resolved_location and location:
            title = f"Nearby Venues in {resolved_location}"

        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Distance", style="yellow")
        table.add_column("Rating")
        table.add_column("Address", style="dim")

        for venue in venues:
            rating = f"{venue.rating:.1f}" if venue.rating else "-"
            table.add_row(
                venue.name,
                venue.venue_type or "-",
                venue.distance or "-",
                rating,
                venue.address or "-",
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
