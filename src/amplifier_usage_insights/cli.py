"""CLI commands for amplifier-usage-insights."""

from datetime import datetime, timedelta
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .insights import InsightsEngine, format_conversational_response
from .metrics import calculate_weekly_metrics, get_week_start
from .parser import SessionParser
from .storage import MetricsDB

app = typer.Typer(
    name="amplifier-insights",
    help="Conversational insights about your AI collaboration effectiveness",
)
console = Console()


def get_db_path() -> Path:
    """Get the default database path."""
    return Path.home() / ".amplifier-usage-insights" / "metrics.db"


def get_projects_dir() -> Path:
    """Get the default Amplifier projects directory."""
    return Path.home() / ".amplifier" / "projects"


@app.command()
def init() -> None:
    """
    Initialize the insights database.

    Creates ~/.amplifier-usage-insights/metrics.db and sets up schema.
    Safe to run multiple times - will not overwrite existing data.
    """
    db_path = get_db_path()

    console.print(f"[bold]Initializing database at:[/bold] {db_path}")

    # MetricsDB.__init__ automatically creates schema
    MetricsDB(db_path)

    console.print("[green]✓[/green] Database initialized successfully")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Run [cyan]amplifier-insights refresh[/cyan] to scan your sessions")
    console.print("  2. Run [cyan]amplifier-insights show[/cyan] to see your insights")


@app.command()
def refresh() -> None:
    """
    Scan Amplifier sessions and update metrics.

    Scans ~/.amplifier/projects/ for sessions, parses them, and updates
    the metrics database with latest data.
    """
    db_path = get_db_path()
    projects_dir = get_projects_dir()

    if not projects_dir.exists():
        console.print(f"[red]Error:[/red] Amplifier projects directory not found: {projects_dir}")
        console.print("Make sure you have Amplifier installed and have run some sessions.")
        raise typer.Exit(1)

    console.print(f"[bold]Scanning sessions in:[/bold] {projects_dir}")

    # Initialize parser and database
    parser = SessionParser()
    db = MetricsDB(db_path)

    # Find all sessions
    session_dirs = parser.find_sessions(projects_dir)
    total_sessions = len(session_dirs)

    if total_sessions == 0:
        console.print("[yellow]No sessions found.[/yellow]")
        console.print("Run some Amplifier sessions first!")
        raise typer.Exit(0)

    console.print(f"Found {total_sessions} sessions. Processing...")

    # Process each session
    processed = 0
    errors = 0

    with console.status("[bold green]Processing sessions...") as status:
        for session_dir in session_dirs:
            try:
                session = parser.parse_session(session_dir)
                db.save_session(session)
                processed += 1

                if processed % 10 == 0:
                    status.update(f"[bold green]Processed {processed}/{total_sessions}...")
            except Exception as e:
                errors += 1
                console.print(f"[yellow]Warning:[/yellow] Failed to parse {session_dir.name}: {e}")

    console.print(f"\n[green]✓[/green] Processed {processed} sessions")
    if errors > 0:
        console.print(f"[yellow]⚠[/yellow]  {errors} sessions failed to parse")

    # Compute weekly metrics for recent weeks
    console.print("\n[bold]Computing weekly metrics...[/bold]")

    now = datetime.now()
    weeks_to_compute = 4  # Last 4 weeks

    for i in range(weeks_to_compute):
        week_start = get_week_start(now - timedelta(days=7 * i))
        metrics = calculate_weekly_metrics(db, week_start)
        db.save_weekly_metrics(metrics)

    console.print(f"[green]✓[/green] Computed metrics for last {weeks_to_compute} weeks")
    console.print(
        "\n[bold green]All done![/bold green] Run [cyan]amplifier-insights show[/cyan] to see your insights."
    )


@app.command()
def status() -> None:
    """
    Show database stats and current metrics summary.

    Displays:
    - Total sessions stored
    - Date range of sessions
    - Total tool calls
    - Most recent week's summary
    """
    db_path = get_db_path()

    if not db_path.exists():
        console.print("[red]Error:[/red] Database not initialized.")
        console.print("Run [cyan]amplifier-insights init[/cyan] first.")
        raise typer.Exit(1)

    db = MetricsDB(db_path)

    # Get basic stats
    total_sessions = db.get_session_count()

    if total_sessions == 0:
        console.print("[yellow]No sessions in database.[/yellow]")
        console.print("Run [cyan]amplifier-insights refresh[/cyan] to scan your sessions.")
        raise typer.Exit(0)

    # Display stats
    console.print("[bold]Database Status:[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    table.add_row("Total Sessions", str(total_sessions))

    tool_summary = db.get_tool_usage_summary()
    total_tool_calls = sum(tool_summary.values())
    table.add_row("Total Tool Calls", str(total_tool_calls))
    table.add_row("Unique Tools", str(len(tool_summary)))

    console.print(table)

    # Show top tools
    console.print("\n[bold]Top 5 Tools:[/bold]")
    sorted_tools = sorted(tool_summary.items(), key=lambda x: x[1], reverse=True)
    for i, (tool_name, count) in enumerate(sorted_tools[:5], 1):
        pct = (count / total_tool_calls * 100) if total_tool_calls > 0 else 0
        console.print(f"  {i}. {tool_name}: {count} calls ({pct:.0f}%)")

    # Show current week summary
    now = datetime.now()
    week_start = get_week_start(now)
    current_week = db.get_weekly_metrics(week_start)

    if current_week and current_week.session_count > 0:
        console.print(f"\n[bold]This Week ({week_start.strftime('%Y-%m-%d')}):[/bold]")
        console.print(f"  Sessions: {current_week.session_count}")
        console.print(
            f"  Duration: {current_week.total_duration_seconds // 3600}h {(current_week.total_duration_seconds % 3600) // 60}m"
        )
        console.print(f"  Delegation ratio: {current_week.delegation_ratio * 100:.0f}%")
        console.print(f"  Error rate: {current_week.error_rate * 100:.0f}%")


@app.command()
def show(
    query: str = typer.Argument(
        "weekly", help="What to show: 'weekly', 'tools', 'growth', or natural language query"
    ),
) -> None:
    """
    Show insights based on your query.

    Examples:
        amplifier-insights show weekly
        amplifier-insights show tools
        amplifier-insights show growth
        amplifier-insights show "How am I doing?"
    """
    db_path = get_db_path()

    if not db_path.exists():
        console.print("[red]Error:[/red] Database not initialized.")
        console.print("Run [cyan]amplifier-insights init[/cyan] first.")
        raise typer.Exit(1)

    engine = InsightsEngine(db_path)

    # Route query
    query_lower = query.lower()

    if query_lower in ["weekly", "summary", "week"]:
        # Weekly summary
        data = engine.query_weekly_summary()
        response = format_conversational_response(data)
        console.print(response)

    elif query_lower in ["tools", "tool"]:
        # Tool usage
        tool_data = engine.query_tool_usage()

        console.print("\n[bold]📊 Your Tool Usage:[/bold]\n")

        total_calls = tool_data["total_calls"]
        unique_tools = tool_data["unique_tools"]
        top_tools = tool_data["top_tools"]

        console.print(f"Total tool calls: {total_calls}")
        console.print(f"Unique tools: {unique_tools}\n")
        console.print("[bold]Top Tools:[/bold]")

        if isinstance(top_tools, list):
            for i, (tool_name, count) in enumerate(top_tools[:10], 1):
                pct = (
                    (count / total_calls * 100)
                    if isinstance(total_calls, int) and total_calls > 0
                    else 0
                )
                console.print(f"  {i}. {tool_name}: {count} calls ({pct:.0f}%)")

    elif query_lower in ["growth", "improve", "progress"]:
        # Growth tracking
        growth_data = engine.query_growth()

        console.print("\n[bold]📈 Your Growth:[/bold]\n")
        console.print(f"Current week: {growth_data['current_week_sessions']} sessions")
        console.print(f"Previous week: {growth_data['previous_week_sessions']} sessions")
        console.print(f"Change: {growth_data['sessions_change']}")
        console.print(f"\nDelegation change: {growth_data['delegation_change']}")
        console.print(f"Tool diversity change: {growth_data['tools_change']}")
        console.print(f"Error rate change: {growth_data['error_change']}")

        trend = growth_data["trend"]
        trend_str = trend.capitalize() if isinstance(trend, str) else "Unknown"
        console.print(f"\n[bold]Trend:[/bold] {trend_str}")

    else:
        # Natural language query - use weekly summary
        data = engine.query_weekly_summary()
        response = format_conversational_response(data)
        console.print(response)


if __name__ == "__main__":
    app()
