"""Service for show command business logic."""


import click
import yaml

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.dock.state import DockStateReader
from dock.utils.output import print_info


class ShowService:
    """Service for displaying current dock configuration."""

    def execute(self) -> None:
        """
        Execute the show command.

        Raises:
            Exception: If reading dock state fails.
        """
        # Initialize command wrappers
        dockutil = DockutilCommand()
        plist_mgr = PlistManager()

        # Read current state
        state_reader = DockStateReader(dockutil, plist_mgr)
        current_state = state_reader.read_full_state()

        # Convert to dict and remove default values
        config_dict = current_state.model_dump(
            exclude_defaults=True, exclude_none=True
        )

        # Print header
        print_info("Current dock configuration:")
        click.echo()

        # Output as YAML to stdout
        yaml_output = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
        click.echo(yaml_output)
