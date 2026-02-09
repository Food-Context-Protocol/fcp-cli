"""Recipes command - manage saved recipes."""

from enum import StrEnum
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fcp_cli.services import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import (
    ImageTooLargeError,
    InvalidImageError,
    auto_select_resolution,
    read_image_as_base64,
    run_async,
    validate_resolution,
)


class RecipeFilter(StrEnum):
    """Valid recipe filter types."""

    ALL = "all"
    FAVORITES = "favorites"
    ARCHIVED = "archived"


app = typer.Typer()
console = Console()


@app.command("list")
def list_recipes(
    filter_type: RecipeFilter = typer.Option(
        RecipeFilter.ALL,
        "--filter",
        "-f",
        help="Filter recipes: all, favorites, archived",
    ),
) -> None:
    """List saved recipes."""
    try:
        client = FcpClient()
        recipes = run_async(client.get_recipes_filtered(filter_type.value))

        if not recipes:
            msg = "No saved recipes yet."
            if filter_type == RecipeFilter.FAVORITES:
                msg = "No favorite recipes yet."
            elif filter_type == RecipeFilter.ARCHIVED:
                msg = "No archived recipes."
            console.print(f"[yellow]{msg}[/yellow]")
            return

        title = "Saved Recipes"
        if filter_type == RecipeFilter.FAVORITES:
            title = "Favorite Recipes"
        elif filter_type == RecipeFilter.ARCHIVED:
            title = "Archived Recipes"

        table = Table(title=title)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Servings", style="yellow")
        table.add_column("Status", style="dim")

        for recipe in recipes:
            status_parts = []
            if recipe.is_favorite:
                status_parts.append("★")
            if recipe.is_archived:
                status_parts.append("archived")
            table.add_row(
                recipe.id[:8] if recipe.id else "-",
                recipe.name,
                recipe.source or "-",
                str(recipe.servings) if recipe.servings else "-",
                " ".join(status_parts) if status_parts else "-",
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


@app.command("suggest")
def suggest_recipes(
    context: str | None = typer.Argument(None, help="Context (e.g. 'quick dinner', 'healthy')"),
    exclude_recent_days: int = typer.Option(3, "--exclude-recent", help="Exclude meals eaten in last N days"),
) -> None:
    """Get recipe suggestions based on your preferences."""
    try:
        client = FcpClient()
        suggestions = run_async(client.suggest_meals(context, exclude_recent_days))

        if not suggestions:
            console.print("[yellow]No suggestions found.[/yellow]")
            return

        table = Table(title="Recipe Suggestions")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Reason", style="white")

        for s in suggestions:
            table.add_row(s.name, s.meal_type or "-", s.reason or "-")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("extract")
def extract_recipe(
    image: Path = typer.Argument(..., help="Path to image of recipe or dish"),
    resolution: str | None = typer.Option(
        None,
        "--res",
        "-r",
        help="Image resolution: low (fast/cheap), medium (balanced), high (detailed). Auto-detects if not specified.",
    ),
) -> None:
    """Extract a recipe from an image."""
    try:
        # Auto-select resolution if not specified
        if resolution is None:
            selected_resolution = auto_select_resolution(str(image))
            console.print(f"[dim]Auto-selected resolution: {selected_resolution}[/dim]")
        else:
            selected_resolution = validate_resolution(resolution)

        image_base64 = read_image_as_base64(str(image))
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e
    except (ImageTooLargeError, InvalidImageError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e

    try:
        client = FcpClient()
        result = run_async(client.extract_recipe_from_image(image_base64, selected_resolution))

        name = result.get("name", result.get("recipe_name", "Extracted Recipe"))
        ingredients = result.get("ingredients", [])
        instructions = result.get("instructions", result.get("steps", []))
        servings = result.get("servings", "-")

        content_parts = []

        if ingredients:
            content_parts.append("[bold]Ingredients:[/bold]")
            for ing in ingredients:
                if isinstance(ing, dict):
                    content_parts.append(f"  - {ing.get('name', ing)}: {ing.get('amount', '')}")
                else:
                    content_parts.append(f"  - {ing}")

        if instructions:
            content_parts.append("\n[bold]Instructions:[/bold]")
            for i, step in enumerate(instructions, 1):
                if isinstance(step, dict):
                    content_parts.append(f"  {i}. {step.get('text', step)}")
                else:
                    content_parts.append(f"  {i}. {step}")

        content_parts.append(f"\n[dim]Servings: {servings}[/dim]")

        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold]{name}[/bold]",
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


@app.command("show")
def show_recipe(
    recipe_id: str = typer.Argument(..., help="ID of recipe to view"),
) -> None:
    """View details of a specific recipe."""
    try:
        client = FcpClient()
        recipe = run_async(client.get_recipe(recipe_id))

        content_parts = []

        if recipe.description:
            content_parts.append(f"{recipe.description}\n")

        if recipe.ingredients:
            content_parts.append("[bold]Ingredients:[/bold]")
            for ing in recipe.ingredients:
                if isinstance(ing, dict):
                    amount = ing.get("amount", "")
                    name = ing.get("name", ing.get("item", str(ing)))
                    content_parts.append(f"  - {amount} {name}".strip())
                else:
                    content_parts.append(f"  - {ing}")

        if recipe.instructions:
            content_parts.append("\n[bold]Instructions:[/bold]")
            for i, step in enumerate(recipe.instructions, 1):
                if isinstance(step, dict):
                    content_parts.append(f"  {i}. {step.get('text', str(step))}")
                else:
                    content_parts.append(f"  {i}. {step}")

        meta = []
        if recipe.servings:
            meta.append(f"Servings: {recipe.servings}")
        if recipe.prep_time:
            meta.append(f"Prep: {recipe.prep_time}")
        if recipe.cook_time:
            meta.append(f"Cook: {recipe.cook_time}")
        if recipe.source:
            meta.append(f"Source: {recipe.source}")
        if recipe.is_favorite:
            meta.append("[yellow]★ Favorite[/yellow]")
        if recipe.is_archived:
            meta.append("[dim]Archived[/dim]")

        if meta:
            content_parts.append(f"\n{' | '.join(meta)}")

        content_parts.append(f"\n[dim]ID: {recipe.id}[/dim]")

        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold]{recipe.name}[/bold]",
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


@app.command("save")
def save_recipe(
    name: str = typer.Argument(..., help="Name of the recipe"),
    ingredients: list[str] = typer.Option([], "--ingredient", "-i", help="Ingredient (can use multiple times)"),
    instructions: list[str] = typer.Option([], "--step", "-s", help="Instruction step (can use multiple times)"),
    servings: int | None = typer.Option(None, "--servings", help="Number of servings"),
    source: str | None = typer.Option(None, "--source", help="Recipe source"),
) -> None:
    """Save a new recipe manually."""
    try:
        client = FcpClient()
        recipe = run_async(
            client.create_recipe(
                name=name,
                ingredients=ingredients or None,
                instructions=instructions or None,
                servings=servings,
                source=source or "manual",
            )
        )

        console.print(
            Panel(
                f"[bold]Name:[/bold] {recipe.name}\n[dim]ID: {recipe.id}[/dim]",
                title="[green]Recipe Saved[/green]",
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


@app.command("favorite")
def toggle_favorite(
    recipe_id: str = typer.Argument(..., help="ID of recipe"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove from favorites"),
) -> None:
    """Add or remove a recipe from favorites."""
    try:
        client = FcpClient()
        recipe = run_async(
            client.update_recipe(
                recipe_id=recipe_id,
                is_favorite=not remove,
            )
        )

        action = "removed from" if remove else "added to"
        console.print(f"[green]{recipe.name} {action} favorites.[/green]")

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


@app.command("archive")
def toggle_archive(
    recipe_id: str = typer.Argument(..., help="ID of recipe"),
    restore: bool = typer.Option(False, "--restore", "-r", help="Restore from archive"),
) -> None:
    """Archive or restore a recipe."""
    try:
        client = FcpClient()
        recipe = run_async(
            client.update_recipe(
                recipe_id=recipe_id,
                is_archived=not restore,
            )
        )

        action = "restored from" if restore else "moved to"
        console.print(f"[green]{recipe.name} {action} archive.[/green]")

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
def delete_recipe(
    recipe_id: str = typer.Argument(..., help="ID of recipe to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a recipe."""
    if not yes and not typer.confirm(f"Delete recipe {recipe_id}?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    try:
        client = FcpClient()
        run_async(client.delete_recipe(recipe_id))
        console.print(f"[green]Deleted recipe {recipe_id}.[/green]")

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


@app.command("scale")
def scale_recipe(
    recipe_id: str = typer.Argument(..., help="ID of recipe to scale"),
    servings: int = typer.Argument(..., help="Target number of servings"),
) -> None:
    """Scale a recipe to a new number of servings."""
    try:
        client = FcpClient()
        recipe = run_async(client.scale_recipe(recipe_id, servings))

        console.print(
            Panel(
                f"[bold]Scaled to {recipe.servings} servings[/bold]",
                title=f"[green]{recipe.name}[/green]",
                border_style="green",
            )
        )

        if recipe.ingredients:
            console.print("[bold]Ingredients:[/bold]")
            for ing in recipe.ingredients:
                if isinstance(ing, dict):
                    amount = ing.get("amount", "")
                    name = ing.get("name", ing.get("item", str(ing)))
                    console.print(f"  - {amount} {name}".strip())
                else:
                    console.print(f"  - {ing}")

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


@app.command("standardize")
def standardize_recipe(
    text: str = typer.Argument(..., help="Raw recipe text to standardize"),
) -> None:
    """Convert unstructured recipe text into a structured format."""
    try:
        client = FcpClient()
        recipe = run_async(client.standardize_recipe(text))

        console.print(
            Panel(
                f"[bold]Name:[/bold] {recipe.name}\n[dim]Standardized[/dim]",
                title="[green]Recipe Standardized[/green]",
                border_style="green",
            )
        )

        if recipe.ingredients:
            console.print("[bold]Ingredients:[/bold]")
            for ing in recipe.ingredients:
                if isinstance(ing, dict):
                    amount = ing.get("amount", "")
                    name = ing.get("name", ing.get("item", str(ing)))
                    console.print(f"  - {amount} {name}".strip())
                else:
                    console.print(f"  - {ing}")

        if recipe.instructions:
            console.print("\n[bold]Instructions:[/bold]")
            for i, step in enumerate(recipe.instructions, 1):
                console.print(f"  {i}. {step}")

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


class Difficulty(StrEnum):
    """Valid recipe difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MealType(StrEnum):
    """Valid meal types."""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


@app.command("generate")
def generate_recipe(
    ingredients: list[str] = typer.Option(
        [], "--ingredient", "-i", help="Available ingredient (can use multiple times)"
    ),
    cuisine: str | None = typer.Option(None, "--cuisine", "-c", help="Desired cuisine type (e.g., Italian, Asian)"),
    dietary: list[str] = typer.Option([], "--dietary", "-d", help="Dietary restriction (can use multiple times)"),
    meal_type: MealType | None = typer.Option(None, "--meal", "-m", help="Meal type (breakfast, lunch, dinner, snack)"),
    difficulty: Difficulty | None = typer.Option(None, "--difficulty", help="Difficulty level (easy, medium, hard)"),
) -> None:
    """Generate a recipe using AI based on your preferences."""
    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Generating recipe...", total=None)

        try:
            client = FcpClient()
            recipe = run_async(
                client.generate_recipe(
                    ingredients=ingredients or None,
                    cuisine=cuisine,
                    dietary_restrictions=dietary or None,
                    meal_type=meal_type.value if meal_type else None,
                    difficulty=difficulty.value if difficulty else None,
                )
            )

            content_parts = []

            if recipe.description:
                content_parts.append(f"{recipe.description}\n")

            if recipe.ingredients:
                content_parts.append("[bold]Ingredients:[/bold]")
                for ing in recipe.ingredients:
                    if isinstance(ing, dict):
                        amount = ing.get("amount", "")
                        name = ing.get("name", ing.get("item", str(ing)))
                        content_parts.append(f"  - {amount} {name}".strip())
                    else:
                        content_parts.append(f"  - {ing}")

            if recipe.instructions:
                content_parts.append("\n[bold]Instructions:[/bold]")
                for i, step in enumerate(recipe.instructions, 1):
                    if isinstance(step, dict):
                        content_parts.append(f"  {i}. {step.get('text', str(step))}")
                    else:
                        content_parts.append(f"  {i}. {step}")

            meta = []
            if recipe.servings:
                meta.append(f"Servings: {recipe.servings}")
            if recipe.prep_time:
                meta.append(f"Prep: {recipe.prep_time}")
            if recipe.cook_time:
                meta.append(f"Cook: {recipe.cook_time}")

            if meta:
                content_parts.append(f"\n{' | '.join(meta)}")

            panel = Panel(
                "\n".join(content_parts),
                title=f"[bold green]🍳 {recipe.name}[/bold green]",
                subtitle="[dim]AI Generated[/dim]",
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
