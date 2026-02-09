"""Profile command - View taste profile."""

import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from fcp_cli.services.fcp import FcpClient, FcpConnectionError, FcpServerError
from fcp_cli.utils import run_async

app = typer.Typer()
console = Console()


def _format_list(items: list[str], max_items: int = 5) -> str:
    """Format a list of items for display."""
    if not items:
        return "[dim]None[/dim]"
    display_items = items[:max_items]
    result = ", ".join(display_items)
    if len(items) > max_items:
        result += f" (+{len(items) - max_items} more)"
    return result


@app.command("show")
def show() -> None:
    """Show your taste profile."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching taste profile...", total=None)

        try:
            client = FcpClient()
            profile = run_async(client.get_taste_profile())

            # Create info table
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Label", style="bold")
            table.add_column("Value")

            table.add_row(
                "Favorite Cuisines",
                _format_list(profile.favorite_cuisines),
            )
            table.add_row(
                "Preferred Ingredients",
                _format_list(profile.preferred_ingredients),
            )
            table.add_row(
                "Disliked Ingredients",
                _format_list(profile.disliked_ingredients),
            )
            table.add_row(
                "Dietary Restrictions",
                _format_list(profile.dietary_restrictions),
            )

            if profile.average_calories is not None:
                table.add_row(
                    "Average Calories",
                    f"{profile.average_calories:.0f} kcal/day",
                )

            # Display in panel
            console.print(
                Panel(
                    table,
                    title="[bold blue]Taste Profile[/bold blue]",
                    border_style="blue",
                )
            )

            # Show meal patterns if available
            if profile.meal_patterns:
                patterns_table = Table(
                    title="Meal Patterns",
                    show_header=True,
                )
                patterns_table.add_column("Pattern", style="bold")
                patterns_table.add_column("Value", style="cyan")

                for key, value in profile.meal_patterns.items():
                    patterns_table.add_row(key, str(value))

                console.print(patterns_table)

        except FcpConnectionError as e:
            console.print(f"[red]Connection error:[/red] {e}")
            console.print("[dim]Is the FCP server running?[/dim]")
            raise typer.Exit(1) from e
        except FcpServerError as e:
            console.print(f"[red]Server error:[/red] {e}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Failed to fetch profile:[/red] {e}")
            raise typer.Exit(1) from e


@app.command("stats")
def show_stats(
    period: str = typer.Option("month", "--period", "-p", help="Time period (week, month, year)"),
    group_by: str = typer.Option("meal_type", "--group-by", "-g", help="Group by (day, meal_type, cuisine)"),
) -> None:
    """View food statistics."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching statistics...", total=None)

        try:
            client = FcpClient()
            stats = run_async(client.get_food_stats(period=period, group_by=group_by))

            console.print(Panel(f"[bold]Food Stats ({period})[/bold]", style="cyan"))

            # Pretty print stats
            console.print_json(json.dumps(stats))

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


@app.command("report")
def generate_report(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
    focus: str | None = typer.Option(None, "--focus", "-f", help="Focus area (e.g., 'protein', 'IBS')"),
) -> None:
    """Generate a dietitian report."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Generating report...", total=None)

        try:
            client = FcpClient()
            report = run_async(client.get_dietitian_report(days=days, focus_area=focus))

            title = report.get("title", "Dietitian Report")
            content = report.get("content", report.get("report", ""))

            console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style="green"))

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


def _print_streak_encouragement(current_streak: int) -> None:
    """Print encouragement message based on streak length."""
    if current_streak == 0:
        console.print("\n[dim]Log a meal today to start your streak![/dim]")
        return
    if current_streak >= 7:
        console.print(f"\n[green]Amazing! You've logged for {current_streak} days straight![/green]")
        return
    if current_streak >= 3:
        console.print("\n[green]Great job! Keep the streak going![/green]")
        return


@app.command("streak")
def show_streak(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to check for streak"),
) -> None:
    """View your food logging streak."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Checking streak...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.get_streak(streak_days=days))

            current_streak = result.get("current_streak", result.get("streak", 0))
            best_streak = result.get("best_streak", result.get("longest_streak", current_streak))
            last_logged = result.get("last_logged", result.get("last_log_date"))

            # Create streak display
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Label", style="bold")
            table.add_column("Value", style="cyan")

            # Add flame emoji for streaks
            streak_display = f"🔥 {current_streak} days" if current_streak > 0 else "0 days"
            table.add_row("Current Streak", streak_display)
            table.add_row("Best Streak", f"⭐ {best_streak} days")
            if last_logged:
                table.add_row("Last Logged", str(last_logged))

            console.print(
                Panel(
                    table,
                    title="[bold yellow]Logging Streak[/bold yellow]",
                    border_style="yellow",
                )
            )

            # Encouragement message
            _print_streak_encouragement(current_streak)

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


@app.command("lifetime")
def show_lifetime_stats() -> None:
    """View lifetime food logging statistics."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching lifetime stats...", total=None)

        try:
            client = FcpClient()
            stats = run_async(client.get_lifetime_stats())

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Label", style="bold")
            table.add_column("Value", style="cyan")

            # Common stat keys
            total_meals = stats.get("total_meals", stats.get("meals_logged", 0))
            unique_dishes = stats.get("unique_dishes", stats.get("unique_foods", 0))
            days_logged = stats.get("days_logged", stats.get("active_days", 0))
            first_log = stats.get("first_log", stats.get("member_since"))
            favorite_cuisine = stats.get("favorite_cuisine", stats.get("top_cuisine"))
            avg_meals_per_day = stats.get("avg_meals_per_day", stats.get("average_daily_meals"))

            table.add_row("Total Meals Logged", str(total_meals))
            table.add_row("Unique Dishes", str(unique_dishes))
            table.add_row("Days Active", str(days_logged))
            if first_log:
                table.add_row("Member Since", str(first_log))
            if favorite_cuisine:
                table.add_row("Favorite Cuisine", favorite_cuisine)
            if avg_meals_per_day:
                table.add_row("Avg Meals/Day", f"{float(avg_meals_per_day):.1f}")

            console.print(
                Panel(
                    table,
                    title="[bold magenta]Lifetime Statistics[/bold magenta]",
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


@app.command("nutrition")
def show_nutrition(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
) -> None:
    """View detailed nutrition breakdown."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Analyzing nutrition...", total=None)

        try:
            client = FcpClient()
            result = run_async(client.get_nutrition_analytics(days=days))

            if summary := result.get("summary", result.get("totals", {})):
                table = Table(title=f"Nutrition Summary ({days} days)")
                table.add_column("Nutrient", style="bold")
                table.add_column("Daily Average", style="cyan")
                table.add_column("Total", style="green")

                nutrients = ["calories", "protein", "carbs", "fat", "fiber", "sodium"]
                units = {"calories": "kcal", "protein": "g", "carbs": "g", "fat": "g", "fiber": "g", "sodium": "mg"}

                for nutrient in nutrients:
                    avg = summary.get(f"avg_{nutrient}", summary.get(f"{nutrient}_avg"))
                    total = summary.get(f"total_{nutrient}", summary.get(nutrient))
                    if avg is not None or total is not None:
                        unit = units.get(nutrient, "")
                        avg_str = f"{float(avg):.1f} {unit}" if avg is not None else "-"
                        total_str = f"{float(total):.1f} {unit}" if total is not None else "-"
                        table.add_row(nutrient.capitalize(), avg_str, total_str)

                console.print(table)

            if breakdown := result.get("breakdown", result.get("by_day", [])):
                console.print("\n[bold]Daily Breakdown:[/bold]")
                for item in breakdown[:10]:  # Limit to 10 items
                    label = item.get("label", item.get("date", "Unknown"))
                    calories = item.get("calories", 0)
                    console.print(f"  {label}: {calories} kcal")

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
