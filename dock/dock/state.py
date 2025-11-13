"""Dock state reader for reading current dock configuration."""

from typing import Optional
from urllib.parse import urlparse

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.config.models import DockConfig, DownloadsConfig, SettingsConfig


class DockStateReader:
    """Reads current dock state."""

    def __init__(self, dockutil_cmd: DockutilCommand, plist_mgr: PlistManager):
        """
        Initialize DockStateReader.

        Args:
            dockutil_cmd: DockutilCommand instance for reading dock apps.
            plist_mgr: PlistManager instance for reading dock settings.
        """
        self.dockutil = dockutil_cmd
        self.plist = plist_mgr

    def read_current_apps(self) -> list[str]:
        """
        Get list of current dock apps.

        Returns:
            List of app names currently in the dock.
        """
        return self.dockutil.list_apps()

    def read_current_settings(self) -> SettingsConfig:
        """
        Get current dock settings from plist.

        Returns:
            SettingsConfig with current autohide and autohide_delay values.
        """
        autohide = self.plist.read_autohide()
        autohide_delay = self.plist.read_autohide_delay()

        return SettingsConfig(
            autohide=autohide,
            autohide_delay=autohide_delay
        )

    def read_current_downloads(self) -> Optional[DownloadsConfig]:
        """
        Get current downloads tile configuration.

        Returns:
            DownloadsConfig if downloads tile is present, None otherwise.
        """
        # Read persistent-others array from plist
        persistent_others = self.plist.read_value("persistent-others", [])

        # Find downloads tile
        downloads_tile = None
        for item in persistent_others:
            if item.get("tile-type") == "directory-tile":
                tile_data = item.get("tile-data", {})
                if tile_data.get("file-label") == "Downloads":
                    downloads_tile = tile_data
                    break

        if not downloads_tile:
            return None

        # Extract preset from displayas value
        # 0 = classic (stack), 1 = fan, 2 = list
        displayas = downloads_tile.get("displayas", 1)
        preset_map = {0: "classic", 1: "fan", 2: "list"}
        preset_str = preset_map.get(displayas, "fan")

        # Extract path from file-data
        file_data = downloads_tile.get("file-data", {})
        url_string = file_data.get("_CFURLString", "file:///Users/Downloads/")

        # Parse URL and convert to ~ notation
        parsed = urlparse(url_string)
        path = parsed.path.rstrip("/")  # Remove trailing slash
        if path.startswith("/Users/"):
            # Convert to ~ notation
            path = "~" + path[path.index("/", 7):]

        # Determine section (for now, assume others since it's in persistent-others)
        section_str = "others"

        # Type assertions for Literal types
        from typing import Literal, cast
        preset = cast(Literal["classic", "fan", "list"], preset_str)
        section = cast(Literal["apps-left", "apps-right", "others"], section_str)

        return DownloadsConfig(
            preset=preset,
            path=path,
            section=section
        )

    def read_full_state(self) -> DockConfig:
        """
        Read complete current dock state.

        Returns:
            DockConfig with current apps, settings, and downloads configuration.
        """
        apps = self.read_current_apps()
        settings = self.read_current_settings()
        downloads = self.read_current_downloads()

        return DockConfig(
            apps=apps,
            settings=settings,
            downloads=downloads
        )
