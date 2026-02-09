"""Research command - AI-powered food research."""

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from fcp_cli.utils import demo_safe, run_async

app = typer.Typer()
console = Console()


@app.command("ask")
@demo_safe
def ask(
    question: str = typer.Argument(..., help="Research question about food/nutrition"),
) -> None:
    """
    Ask a food research question using AI deep research.

    Examples:
        fcp research ask "What are the health benefits of fermented foods?"
        fcp research ask "How does cooking method affect nutrient retention?"
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Researching...", total=None)

        try:
            # Local import to reduce CLI startup time (lazy loading pydantic-ai)
            from fcp_cli.agents import ResearchAgent

            agent = ResearchAgent()
            result = run_async(agent.research(question))

            # Build output panels
            summary_panel = Panel(
                result.summary,
                title="[bold]Summary[/bold]",
                border_style="green",
            )

            key_points_text = "\n".join(f"• {point}" for point in result.key_points)
            points_panel = Panel(
                key_points_text,
                title="[bold]Key Points[/bold]",
                border_style="blue",
            )

            meta_text = f"Sources: {result.sources_consulted} | Confidence: {result.confidence}"
            meta_panel = Panel(
                meta_text,
                title="[bold]Metadata[/bold]",
                border_style="dim",
            )

            # Group and display
            output = Group(summary_panel, points_panel, meta_panel)
            console.print(Panel(output, title=f"[bold]Research: {question}[/bold]"))

        except Exception as e:
            console.print(f"[red]Research failed:[/red] {e}")
            raise typer.Exit(1) from e
