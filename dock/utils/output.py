"""Output formatting utilities."""

from typing import TYPE_CHECKING

import click

from dock.config.models import DownloadsConfig
from dock.dock.diff import DockDiff

if TYPE_CHECKING:
    from dock.dock.plan import ExecutionStep


def print_success(message: str) -> None:
    """
    Print success message in green.

    Args:
        message: Success message to display.
    """
    click.secho(f"✓ {message}", fg="green")


def print_error(message: str) -> None:
    """
    Print error message in red to stderr.

    Args:
        message: Error message to display.
    """
    click.secho(f"✗ {message}", fg="red", err=True)


def print_warning(message: str) -> None:
    """
    Print warning message in yellow.

    Args:
        message: Warning message to display.
    """
    click.secho(f"⚠ {message}", fg="yellow")


def print_info(message: str) -> None:
    """
    Print info message.

    Args:
        message: Info message to display.
    """
    click.echo(f"  {message}")


def print_diff(diff: DockDiff, dry_run: bool = False) -> None:
    """
    Print formatted diff output.

    Args:
        diff: DockDiff containing changes to display.
        dry_run: Whether this is a dry-run (adds prefix to output).
    """
    prefix = "[DRY RUN] " if dry_run else ""

    # Print app changes
    if diff.app_changes:
        click.echo(f"\n{prefix}App changes:")
        for change in diff.app_changes:
            if change.action == "add":
                print_info(f"+ Add: {change.app_name}")
            elif change.action == "remove":
                print_info(f"- Remove: {change.app_name}")
            elif change.action == "reorder":
                print_info(f"↻ Reorder: {change.app_name}")

    # Print setting changes
    if diff.setting_changes:
        click.echo(f"\n{prefix}Setting changes:")
        for setting_change in diff.setting_changes:
            print_info(
                f"  {setting_change.setting_name}: "
                f"{setting_change.old_value} → {setting_change.new_value}"
            )

    # Print downloads changes
    if diff.downloads_change is not None:
        click.echo(f"\n{prefix}Downloads tile:")
        if diff.downloads_change == "off":
            print_info("  Remove downloads tile")
        elif isinstance(diff.downloads_change, DownloadsConfig):
            print_info(f"  Preset: {diff.downloads_change.preset}")
            print_info(f"  Path: {diff.downloads_change.path}")
            print_info(f"  Section: {diff.downloads_change.section}")


def print_execution_plan(steps: list["ExecutionStep"], dry_run: bool = False) -> None:
    """
    Print execution plan showing actual commands that will be run.

    Args:
        steps: List of ExecutionStep objects.
        dry_run: Whether this is a dry-run.
    """
    if not steps:
        return

    header = "Execution plan (dry-run):" if dry_run else "Executing commands:"
    click.echo(f"\n{header}")

    for step in steps:
        click.secho(f"$ {step.command}", fg="cyan")
