"""Service for backup command business logic."""

from pathlib import Path

import yaml

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.config.converter import converter
from dock.dock.state import DockStateReader
from dock.utils.output import print_success


class BackupService:
    """Service for backing up dock configuration."""

    def execute(self, file_path: str) -> None:
        """
        Execute the backup command.

        Args:
            file_path: Path to output file.

        Raises:
            Exception: If backup fails.
        """
        # Initialize command wrappers
        dockutil = DockutilCommand()
        plist_mgr = PlistManager()

        # Read current state
        state_reader = DockStateReader(dockutil, plist_mgr)
        current_state = state_reader.read_full_state()

        # Convert to dict
        config_dict = converter.unstructure(current_state)

        # Write to file
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        print_success(f"Dock configuration backed up to: {output_path}")
