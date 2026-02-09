"""Log command - Add food entries."""

import asyncio
import base64
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from fcp_cli.services.fcp import (
    FcpClient,
    FcpConnectionError,
    FcpNotFoundError,
    FcpServerError,
)
from fcp_cli.utils import (
    ImageTooLargeError,
    InvalidImageError,
    auto_select_resolution,
    demo_safe,
    get_relative_time,
    read_image_as_base64,
    run_async,
    validate_limit,
    validate_resolution,
)

app = typer.Typer()
console = Console()


def _process_image_for_log(image: str, resolution: str | None) -> tuple[str, str]:
    """Process and validate image for food log.

    Args:
        image: Path to image file
        resolution: Resolution setting or None for auto

    Returns:
        Tuple of (image_base64, selected_resolution)

    Raises:
        FileNotFoundError: If image file not found
        ImageTooLargeError: If image exceeds size limit
        InvalidImageError: If image format is invalid
        ValueError: If resolution value is invalid
    """
    # Auto-select resolution if not specified
    if resolution is None:
        selected_resolution = auto_select_resolution(image)
    else:
        selected_resolution = validate_resolution(resolution)

    image_base64 = read_image_as_base64(image)
    return image_base64, selected_resolution


@app.command("add")
@demo_safe
def add(
    description: str = typer.Argument(..., help="Description of the food"),
    image: str | None = typer.Option(None, "--image", "-i", help="Path to food image"),
    meal_type: str | None = typer.Option(
        None,
        "--meal-type",
        "-m",
        help="Meal type (breakfast, lunch, dinner, snack)",
    ),
    resolution: str | None = typer.Option(
        None,
        "--res",
        "-r",
        help="Image resolution: low (fast/cheap), medium (balanced), high (detailed). Auto-detects if not specified.",
    ),
) -> None:
    """Add a new food log entry with AI-powered nutrition analysis.

    Examples:
        fcp log add "Tonkotsu Ramen" --meal-type dinner
        fcp log add "Margherita Pizza"
        fcp log add "Caesar Salad" --image salad.jpg --res high
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Adding food log...", total=None)

        try:
            client = FcpClient()
            image_base64 = None
            selected_resolution = None

            if image:
                try:
                    image_base64, selected_resolution = _process_image_for_log(image, resolution)
                    if resolution is None:
                        console.print(f"[dim]Auto-selected resolution: {selected_resolution}[/dim]")
                except FileNotFoundError as e:
                    console.print(f"[red]Error:[/red] {e}")
                    raise typer.Exit(1) from e
                except (ImageTooLargeError, InvalidImageError) as e:
                    console.print(f"[red]Error:[/red] {e}")
                    raise typer.Exit(1) from e
                except ValueError as e:
                    console.print(f"[red]Error:[/red] {e}")
                    raise typer.Exit(1) from e

            log = run_async(
                client.create_food_log(
                    dish_name=description,
                    description=description,
                    meal_type=meal_type,
                    image_base64=image_base64,
                )
            )

            # Display success
            panel_content = f"[bold]Dish:[/bold] {log.dish_name}"
            if log.meal_type:
                panel_content += f"\n[bold]Meal Type:[/bold] {log.meal_type}"
            if log.id:
                panel_content += f"\n[dim]ID: {log.id}[/dim]"

            console.print(
                Panel(
                    panel_content,
                    title="[green]Food Log Added[/green]",
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
        except httpx.HTTPStatusError as e:
            console.print(f"[red]HTTP error:[/red] {e.response.status_code}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Failed to add food log:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("nutrition")
def log_nutrition(
    description: str = typer.Argument(..., help="Description of the meal or nutrition info"),
    meal_type: str | None = typer.Option(None, "--meal-type", "-m", help="Meal type"),
    calories: int | None = typer.Option(None, "--calories", "-c", help="Calories (kcal)"),
    protein: int | None = typer.Option(None, "--protein", "-p", help="Protein (g)"),
    carbs: int | None = typer.Option(None, "--carbs", help="Carbohydrates (g)"),
    fat: int | None = typer.Option(None, "--fat", help="Fat (g)"),
) -> None:
    """Log a meal with detailed nutritional information."""
    # Validation
    for val, name in [(calories, "calories"), (protein, "protein"), (carbs, "carbs"), (fat, "fat")]:
        if val is not None and val < 0:
            console.print(f"[red]Error:[/red] {name.capitalize()} cannot be negative.")
            raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Logging nutrition...", total=None)

        try:
            client = FcpClient()
            log = run_async(
                client.log_meal(
                    description=description,
                    meal_type=meal_type,
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fat=fat,
                )
            )

            # Display success
            panel_content = f"[bold]Meal:[/bold] {log.dish_name}"
            if log.nutrition and (
                nutrition_parts := [
                    f"{key.capitalize()}: {val}" for key, val in log.nutrition.items() if val is not None
                ]
            ):
                panel_content += f"\n[bold]Nutrition:[/bold] {', '.join(nutrition_parts)}"

            console.print(
                Panel(
                    panel_content,
                    title="[green]Nutrition Logged[/green]",
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


@app.command("list")
def list_logs(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of entries to show", callback=validate_limit),
) -> None:
    """List recent food log entries."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching food logs...", total=None)

        try:
            client = FcpClient()
            logs = run_async(client.get_food_logs(limit=limit))

            if not logs:
                console.print("[yellow]No food logs found.[/yellow]")
                return

            # Create table
            table = Table(title=f"Recent Food Logs (showing {len(logs)})")
            table.add_column("Time", style="dim")
            table.add_column("Dish", style="bold")
            table.add_column("Type", style="cyan")
            table.add_column("ID", style="dim")

            for log in logs:
                time_str = ""
                if log.timestamp:
                    time_str = get_relative_time(log.timestamp)
                table.add_row(
                    time_str,
                    log.dish_name,
                    log.meal_type or "-",
                    log.id or "-",
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
            console.print(f"[red]Failed to fetch food logs:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("show")
def show_log(
    log_id: str = typer.Argument(..., help="ID of food log to view"),
) -> None:
    """View details of a specific food log entry."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching food log...", total=None)

        try:
            client = FcpClient()
            log = run_async(client.get_food_log(log_id))

            content_parts = [f"[bold]Dish:[/bold] {log.dish_name}"]
            if log.description:
                content_parts.append(f"[bold]Description:[/bold] {log.description}")
            if log.meal_type:
                content_parts.append(f"[bold]Meal Type:[/bold] {log.meal_type}")
            if log.timestamp:
                rel_time = get_relative_time(log.timestamp)
                content_parts.append(f"[bold]Time:[/bold] {log.timestamp.strftime('%Y-%m-%d %H:%M')} ({rel_time})")
            if log.ingredients:
                content_parts.append(f"[bold]Ingredients:[/bold] {', '.join(log.ingredients)}")
            if log.nutrition:
                nutrition_str = ", ".join(f"{k}: {v}" for k, v in log.nutrition.items())
                content_parts.append(f"[bold]Nutrition:[/bold] {nutrition_str}")
            content_parts.append(f"\n[dim]ID: {log.id}[/dim]")

            panel = Panel(
                "\n".join(content_parts),
                title="[bold]Food Log Details[/bold]",
                border_style="blue",
            )
            console.print(panel)

        except FcpNotFoundError as e:
            console.print(f"[red]Food log not found:[/red] {log_id}")
            raise typer.Exit(1) from e
        except FcpConnectionError as e:
            console.print(f"[red]Connection error:[/red] {e}")
            raise typer.Exit(1) from e
        except FcpServerError as e:
            console.print(f"[red]Server error:[/red] {e}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Failed to fetch food log:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("edit")
def edit_log(
    log_id: str = typer.Argument(..., help="ID of food log to edit"),
    dish_name: str | None = typer.Option(None, "--dish", "-d", help="New dish name"),
    description: str | None = typer.Option(None, "--desc", help="New description"),
    meal_type: str | None = typer.Option(
        None,
        "--meal-type",
        "-m",
        help="New meal type (breakfast, lunch, dinner, snack)",
    ),
) -> None:
    """Edit a food log entry."""
    if not any([dish_name, description, meal_type]):
        console.print("[yellow]No changes specified. Use --dish, --desc, or --meal-type.[/yellow]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Updating food log...", total=None)

        try:
            client = FcpClient()
            log = run_async(
                client.update_food_log(
                    log_id=log_id,
                    dish_name=dish_name,
                    description=description,
                    meal_type=meal_type,
                )
            )

            console.print(
                Panel(
                    f"[bold]Dish:[/bold] {log.dish_name}\n[dim]ID: {log.id}[/dim]",
                    title="[green]Food Log Updated[/green]",
                    border_style="green",
                )
            )

        except FcpNotFoundError as e:
            console.print(f"[red]Food log not found:[/red] {log_id}")
            raise typer.Exit(1) from e
        except FcpConnectionError as e:
            console.print(f"[red]Connection error:[/red] {e}")
            raise typer.Exit(1) from e
        except FcpServerError as e:
            console.print(f"[red]Server error:[/red] {e}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Failed to update food log:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("delete")
def delete_log(
    log_id: str = typer.Argument(..., help="ID of food log to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a food log entry."""
    if not yes and not typer.confirm(f"Delete food log {log_id}?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Deleting food log...", total=None)

        try:
            client = FcpClient()
            run_async(client.delete_food_log(log_id))
            console.print(f"[green]Deleted food log {log_id}.[/green]")

        except FcpNotFoundError as e:
            console.print(f"[red]Food log not found:[/red] {log_id}")
            raise typer.Exit(1) from e
        except FcpConnectionError as e:
            console.print(f"[red]Connection error:[/red] {e}")
            raise typer.Exit(1) from e
        except FcpServerError as e:
            console.print(f"[red]Server error:[/red] {e}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Failed to delete food log:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("menu")
def log_menu(
    image_path: Path = typer.Argument(..., help="Path to menu image"),
    restaurant_name: str | None = typer.Option(None, "--restaurant", "-n", help="Restaurant name"),
    resolution: str | None = typer.Option(
        None,
        "--res",
        "-r",
        help="Image resolution: low (fast/cheap), medium (balanced), high (detailed). Auto-detects if not specified.",
    ),
) -> None:
    """Scan a restaurant menu and list dishes."""
    if not image_path.exists():
        console.print(f"[red]Error:[/red] File not found: {image_path}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Analyzing menu...", total=None)

        try:
            # Auto-select resolution if not specified
            if resolution is None:
                selected_resolution = auto_select_resolution(str(image_path))
                console.print(f"[dim]Auto-selected resolution: {selected_resolution}[/dim]")
            else:
                selected_resolution = validate_resolution(resolution)

            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")

            client = FcpClient()
            result = run_async(client.parse_menu(image_base64, restaurant_name, selected_resolution))

            items = result.get("items", [])
            if not items:
                console.print("[yellow]No dishes found on menu.[/yellow]")
                return

            table = Table(title=f"Menu: {restaurant_name or 'Unknown'}")
            table.add_column("Dish", style="cyan")
            table.add_column("Price", style="green")
            table.add_column("Description", style="dim")

            for item in items:
                table.add_row(
                    str(item.get("name", "Unknown")),
                    str(item.get("price", "N/A")),
                    str(item.get("description", "")),
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("donate")
def log_donate(
    log_id: str = typer.Argument(..., help="Log ID to donate"),
    organization: str | None = typer.Option(None, "--org", help="Target organization"),
) -> None:
    """Pledge a surplus meal for donation."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Pledging donation...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.donate_meal(log_id, organization))
            message = result.get("message", "Donation pledged successfully.")
            console.print(f"[green]{message}[/green]")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("batch")
def log_batch(
    folder: Path = typer.Argument(..., help="Folder with meal images"),
    max_parallel: int = typer.Option(
        5,
        "--parallel",
        "-p",
        help="Max concurrent uploads (1-10)",
        min=1,
        max=10,
    ),
    resolution: str = typer.Option(
        "low",
        "--res",
        "-r",
        help="Image resolution: low (fast/cheap), medium (balanced), high (detailed)",
    ),
    meal_type: str | None = typer.Option(
        None,
        "--meal-type",
        "-m",
        help="Meal type for all images (breakfast, lunch, dinner, snack)",
    ),
) -> None:
    """Log multiple meals in parallel (BLAZING FAST).

    Examples:
        fcp log batch ./photos --parallel 5 --res low
        fcp log batch ~/meals --parallel 3 --res medium --meal-type lunch
    """
    # Validate inputs
    if not folder.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {folder}")
        raise typer.Exit(1)

    try:
        selected_resolution = validate_resolution(resolution)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Find images
    extensions = ["jpg", "jpeg", "png", "heic", "webp", "gif"]
    images = []
    for ext in extensions:
        images.extend(folder.glob(f"*.{ext}"))
        images.extend(folder.glob(f"*.{ext.upper()}"))

    if not images:
        console.print(f"[yellow]No images found in {folder}[/yellow]")
        return

    console.print(f"[cyan]Processing {len(images)} images with {max_parallel} parallel requests...[/cyan]")
    console.print(f"[dim]Resolution: {selected_resolution}[/dim]\n")

    # Run async batch processor
    results = asyncio.run(_batch_log_meals(images, max_parallel, selected_resolution, meal_type))

    # Show results
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count

    console.print()
    console.print(f"[green]✓ {success_count}/{len(images)} meals logged successfully[/green]")

    if failed_count > 0:
        console.print(f"[red]✗ {failed_count} failed[/red]")
        console.print("\n[yellow]Failed images:[/yellow]")
        for r in results:
            if not r["success"]:
                console.print(f"  • {r['image']}: {r['error']}")


async def _process_single_image(
    image: Path,
    meal_type: str | None,
    client: FcpClient | None = None,
) -> dict:
    """Process a single image and create food log.

    Args:
        image: Path to image file
        meal_type: Optional meal type
        client: Optional FcpClient instance (for testing)

    Returns:
        Result dictionary with success status
    """
    try:
        # Read image
        image_base64 = read_image_as_base64(str(image))

        # Create client if not provided
        if client is None:
            client = FcpClient()

        # Log meal
        await client.create_food_log(
            dish_name=image.stem,  # Use filename as dish name
            description=f"Logged from {image.name}",
            meal_type=meal_type,
            image_base64=image_base64,
        )

        return {
            "success": True,
            "image": image.name,
        }
    except Exception as e:
        return {
            "success": False,
            "image": image.name,
            "error": str(e),
        }


async def _batch_log_meals(
    images: list[Path],
    max_parallel: int,
    resolution: str,
    meal_type: str | None = None,
) -> list[dict]:
    """Process images in parallel with controlled concurrency.

    Args:
        images: List of image paths to process
        max_parallel: Maximum concurrent requests
        resolution: Image resolution (low/medium/high)
        meal_type: Optional meal type for all images

    Returns:
        List of result dictionaries with success status
    """
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_parallel)

    async def process_with_semaphore(image: Path) -> dict:
        """Process image with semaphore control."""
        async with semaphore:
            return await _process_single_image(image, meal_type)

    # Launch all tasks in parallel with progress bar
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task(f"Logging {len(images)} meals...", total=len(images))

        async def process_with_progress(image: Path) -> dict:
            """Process image and update progress."""
            result = await process_with_semaphore(image)
            progress.update(task_id, advance=1)
            return result

        # Launch all tasks
        tasks = [process_with_progress(img) for img in images]
        results = await asyncio.gather(*tasks)

    return results
