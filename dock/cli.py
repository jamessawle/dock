"""CLI entry point for dock command."""

import sys
from typing import Optional

import click

from dock.services.backup_service import BackupService
from dock.services.reset_service import ResetService
from dock.services.show_service import ShowService
from dock.services.validate_service import ValidateService
from dock.utils.output import print_error


@click.group()
@click.version_option(version="0.2.0")
def cli() -> None:
    """Manage macOS Dock from YAML configuration."""
    pass


@cli.command()
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="Config file path"
)
@click.option("--profile", help="Profile name from ~/.config/dock/profiles/")
@click.option("--dry-run", is_flag=True, help="Show changes without applying")
def reset(file: Optional[str], profile: Optional[str], dry_run: bool) -> None:
    """Apply dock configuration from file."""
    try:
        service = ResetService()
        service.execute(file_path=file, profile=profile, dry_run=dry_run)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(), help="Output file path")
def backup(file: str) -> None:
    """Export current dock configuration to file."""
    try:
        service = BackupService()
        service.execute(file_path=file)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


@cli.command()
def show() -> None:
    """Display current dock configuration as YAML."""
    try:
        service = ShowService()
        service.execute()
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Config file path")
@click.option("--profile", help="Profile name from ~/.config/dock/profiles/")
def validate(file: Optional[str], profile: Optional[str]) -> None:
    """Validate configuration file."""
    try:
        service = ValidateService()
        service.execute(file_path=file, profile=profile)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
