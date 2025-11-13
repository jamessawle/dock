"""Service for reset command business logic."""

import sys

import click
from pydantic import ValidationError

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.config.loader import ConfigLoader
from dock.config.models import DockConfig
from dock.config.validator import ConfigValidator
from dock.dock.diff import DiffCalculator
from dock.dock.executor import DockExecutor
from dock.dock.plan import ExecutionPlan
from dock.dock.state import DockStateReader
from dock.utils.output import (
    print_error,
    print_execution_plan,
    print_info,
    print_success,
    print_warning,
)
from dock.utils.platform import require_macos


class ResetService:
    """Service for applying dock configuration."""

    def execute(
        self, file_path: str | None, profile: str | None, dry_run: bool
    ) -> None:
        """
        Execute the reset command.

        Args:
            file_path: Optional path to config file.
            profile: Optional profile name.
            dry_run: Whether to run in dry-run mode.

        Raises:
            RuntimeError: If not running on macOS.
            FileNotFoundError: If config file not found.
            yaml.YAMLError: If config file is invalid YAML.
            ValidationError: If config validation fails.
        """
        # Check platform
        require_macos()

        # Initialize command wrappers
        dockutil = DockutilCommand()
        plist_mgr = PlistManager()

        # Check if dockutil is installed
        if not dockutil.check_installed():
            print_error("dockutil is not installed")
            print_info("Install with: brew install dockutil")
            sys.exit(1)

        # Discover and load config
        loader = ConfigLoader()
        config_path = loader.discover_config_path(file_path, profile)
        click.echo(f"Loading configuration from: {config_path}")

        config_data = loader.load_config(config_path)

        # Parse and validate config
        try:
            config = DockConfig.model_validate(config_data)
        except ValidationError as e:
            print_error("Configuration validation failed:")
            for error in e.errors():
                loc = " -> ".join(str(item) for item in error["loc"])
                print_info(f"  {loc}: {error['msg']}")
            sys.exit(1)

        # Run semantic validation
        validator = ConfigValidator()
        warnings = validator.validate_config(config)
        if warnings:
            for warning in warnings:
                print_warning(warning)

        # Read current state
        state_reader = DockStateReader(dockutil, plist_mgr)
        current_state = state_reader.read_full_state()

        # Calculate diff
        diff_calc = DiffCalculator()
        diff = diff_calc.calculate_diff(config, current_state)

        # Check if changes are needed
        if not diff.has_changes():
            print_success("Dock is already in desired state. No changes needed.")
            sys.exit(0)

        # Generate and display execution plan
        plan = ExecutionPlan.generate_plan(diff, config.apps)
        print_execution_plan(plan, dry_run=dry_run)

        # Apply changes (unless dry-run)
        if not dry_run:
            executor = DockExecutor(dockutil, plist_mgr, dry_run=False)
            changes_made = executor.apply_diff(diff)
        else:
            changes_made = True

        if dry_run:
            click.echo()  # Add newline before message
            click.echo("Dry run complete. No changes were made.")
        elif changes_made:
            click.echo()  # Add newline before message
            print_success("Dock configuration applied successfully!")
        else:
            print_success("No changes were needed.")
