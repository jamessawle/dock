"""Dock executor for applying changes."""

import subprocess
from typing import TYPE_CHECKING

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.dock.diff import AppChange, DockDiff, SettingChange

if TYPE_CHECKING:
    from dock.config.models import DownloadsConfig


class DockExecutor:
    """Executes dock changes."""

    def __init__(
        self,
        dockutil_cmd: DockutilCommand,
        plist_mgr: PlistManager,
        dry_run: bool = False
    ):
        """
        Initialize DockExecutor.

        Args:
            dockutil_cmd: DockutilCommand instance for managing dock apps.
            plist_mgr: PlistManager instance for managing dock settings.
            dry_run: If True, display changes without executing them.
        """
        self.dockutil = dockutil_cmd
        self.plist = plist_mgr
        self.dry_run = dry_run

    def apply_diff(self, diff: DockDiff) -> bool:
        """
        Apply changes from diff.

        Args:
            diff: DockDiff containing changes to apply.

        Returns:
            True if changes were made (or would be made in dry-run),
            False if no changes needed.
        """
        if not diff.has_changes():
            return False

        if self.dry_run:
            # In dry-run mode, just indicate changes would be made
            return True

        # Apply app changes
        if diff.app_changes:
            self._apply_app_changes(diff.app_changes)

        # Apply setting changes
        if diff.setting_changes:
            self._apply_setting_changes(diff.setting_changes)

        # Apply downloads changes
        if diff.downloads_change is not None:
            self._apply_downloads_change(diff.downloads_change)

        # Restart dock to apply changes
        self._restart_dock()

        return True

    def _apply_app_changes(self, changes: list[AppChange]) -> None:
        """
        Apply app additions, removals, and reordering.

        When reordering is needed, dockutil requires removing all apps
        and re-adding them in the correct order.

        Args:
            changes: List of AppChange objects to apply.
        """
        # Check if there are any reorder operations
        has_reorder = any(change.action == "reorder" for change in changes)

        # If reordering is needed, remove all apps first
        if has_reorder:
            self.dockutil.remove_all()
            # Then add all apps back in the correct order
            # Get all "add" changes sorted by position
            add_changes = [c for c in changes if c.action == "add"]
            add_changes.sort(key=lambda c: c.position or 0)
            for change in add_changes:
                self.dockutil.add_app(change.app_name, change.position)
        else:
            # No reordering - process removals first, then additions
            for change in changes:
                if change.action == "remove":
                    self.dockutil.remove_app(change.app_name)

            for change in changes:
                if change.action == "add":
                    self.dockutil.add_app(change.app_name, change.position)

    def _apply_setting_changes(self, changes: list[SettingChange]) -> None:
        """
        Apply settings changes via plist.

        Args:
            changes: List of SettingChange objects to apply.
        """
        for change in changes:
            if change.setting_name == "autohide":
                self.plist.write_autohide(change.new_value)
            elif change.setting_name == "autohide_delay":
                self.plist.write_autohide_delay(change.new_value)

    def _apply_downloads_change(
        self, downloads_change: str | DownloadsConfig
    ) -> None:
        """
        Apply downloads tile changes.

        Args:
            downloads_change: Either "off" to remove downloads,
                            or DownloadsConfig to add/modify downloads tile.
        """
        from dock.config.models import DownloadsConfig

        if downloads_change == "off":
            # Remove Downloads folder
            self.dockutil.remove_app("Downloads")
        elif isinstance(downloads_change, DownloadsConfig):
            # Map preset to dockutil view and display options
            if downloads_change.preset == "classic":
                view = "auto"
                display = "stack"
            elif downloads_change.preset == "fan":
                view = "fan"
                display = "stack"
            else:  # list
                view = "grid"
                display = "folder"

            # Map section
            section_map = {
                "apps-left": "left",
                "apps-right": "right",
                "others": "others",
            }
            section = section_map.get(downloads_change.section, "others")

            # Add Downloads folder
            self.dockutil.add_folder(
                path=downloads_change.path,
                view=view,
                display=display,
                section=section,
            )

    def _restart_dock(self) -> None:
        """Restart Dock process using killall."""
        try:
            subprocess.run(
                ['killall', 'Dock'],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # Ignore errors - dock might already be restarting
            pass
