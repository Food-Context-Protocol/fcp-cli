"""FCP CLI - Main entry point."""

import typer
from rich.console import Console

from fcp_cli import __version__
from fcp_cli.commands import (
    discover,
    labels,
    log,
    nearby,
    pantry,
    profile,
    publish,
    recipes,
    research,
    safety,
    search,
    suggest,
    taste,
)
from fcp_cli.services.logfire_service import configure_logfire

# Initialize Logfire for structured logging/tracing
configure_logfire()

app = typer.Typer(
    name="fcp",
    help="FCP CLI - Log and analyze your meals from the command line.",
    no_args_is_help=True,
)

console = Console()

# Register subcommands
app.add_typer(log.app, name="log", help="Log food entries")
app.add_typer(search.app, name="search", help="Search your food logs")
app.add_typer(profile.app, name="profile", help="View your taste profile")
app.add_typer(research.app, name="research", help="AI-powered food research")
app.add_typer(pantry.app, name="pantry", help="Manage your pantry")
app.add_typer(safety.app, name="safety", help="Check food safety information")
app.add_typer(discover.app, name="discover", help="Food discovery and recommendations")
app.add_typer(recipes.app, name="recipes", help="Manage saved recipes")
app.add_typer(publish.app, name="publish", help="Generate and manage content")
app.add_typer(suggest.app, name="suggest", help="Get meal suggestions")
app.add_typer(taste.app, name="taste", help="Taste Buddy dietary compatibility")
app.add_typer(labels.app, name="labels", help="Generate food labels")
app.add_typer(nearby.app, name="nearby", help="Find nearby food venues")


@app.command()
def version() -> None:
    """Show the CLI version."""
    console.print(f"[bold]FCP CLI[/bold] v{__version__}")


@app.callback()
def main() -> None:
    """FCP CLI - Log and analyze your meals from the command line."""
    pass


if __name__ == "__main__":
    app()
