"""Tests for dock state reader."""

from unittest.mock import Mock

from dock.adapters import CommandExecutor
from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.config.models import DockConfig, DownloadsConfig, SettingsConfig
from dock.dock.state import DockStateReader


class TestDockStateReader:
    """Tests for DockStateReader."""

    def test_read_current_apps_with_mocked_dockutil(self) -> None:
        """Test read_current_apps returns list from dockutil."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "Safari\tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
            "Mail\tfile:///Applications/Mail.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.mail\n"
            "System Settings\tfile:///System/Applications/System%20Settings.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.systempreferences\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)
        plist_mgr = Mock(spec=PlistManager)

        reader = DockStateReader(dockutil, plist_mgr)
        apps = reader.read_current_apps()

        assert apps == ["Safari", "Mail", "System Settings"]

    def test_read_current_apps_handles_empty_dock(self) -> None:
        """Test read_current_apps handles empty dock."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        plist_mgr = Mock(spec=PlistManager)

        reader = DockStateReader(dockutil, plist_mgr)
        apps = reader.read_current_apps()

        assert apps == []

    def test_read_current_settings_with_mocked_plist(self) -> None:
        """Test read_current_settings returns SettingsConfig from plist."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_autohide.return_value = True
        plist_mgr.read_autohide_delay.return_value = 0.5

        reader = DockStateReader(dockutil, plist_mgr)
        settings = reader.read_current_settings()

        assert isinstance(settings, SettingsConfig)
        assert settings.autohide is True
        assert settings.autohide_delay == 0.5

    def test_read_current_settings_with_defaults(self) -> None:
        """Test read_current_settings returns defaults when not set."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_autohide.return_value = False
        plist_mgr.read_autohide_delay.return_value = 0.0

        reader = DockStateReader(dockutil, plist_mgr)
        settings = reader.read_current_settings()

        assert isinstance(settings, SettingsConfig)
        assert settings.autohide is False
        assert settings.autohide_delay == 0.0

    def test_read_current_downloads_with_mocked_plist(self) -> None:
        """Test read_current_downloads returns DownloadsConfig from plist."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_value.side_effect = lambda key, default=None: {
            "persistent-others": [
                {
                    "tile-data": {
                        "file-label": "Downloads",
                        "file-data": {"_CFURLString": "file:///Users/test/Downloads/"},
                        "displayas": 1,
                    },
                    "tile-type": "directory-tile",
                }
            ],
        }.get(key, default)

        reader = DockStateReader(dockutil, plist_mgr)
        downloads = reader.read_current_downloads()

        assert isinstance(downloads, DownloadsConfig)
        assert downloads.preset == "fan"
        assert downloads.path == "~/Downloads"
        assert downloads.section == "others"

    def test_read_current_downloads_returns_none_when_not_present(self) -> None:
        """Test read_current_downloads returns None when downloads tile not present."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_value.return_value = []

        reader = DockStateReader(dockutil, plist_mgr)
        downloads = reader.read_current_downloads()

        assert downloads is None

    def test_read_current_downloads_handles_classic_preset(self) -> None:
        """Test read_current_downloads correctly identifies classic preset."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_value.side_effect = lambda key, default=None: {
            "persistent-others": [
                {
                    "tile-data": {
                        "file-label": "Downloads",
                        "file-data": {"_CFURLString": "file:///Users/test/Downloads/"},
                        "displayas": 0,
                    },
                    "tile-type": "directory-tile",
                }
            ],
        }.get(key, default)

        reader = DockStateReader(dockutil, plist_mgr)
        downloads = reader.read_current_downloads()

        assert downloads is not None
        assert downloads.preset == "classic"

    def test_read_current_downloads_handles_list_preset(self) -> None:
        """Test read_current_downloads correctly identifies list preset."""
        mock_executor = Mock(spec=CommandExecutor)
        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_value.side_effect = lambda key, default=None: {
            "persistent-others": [
                {
                    "tile-data": {
                        "file-label": "Downloads",
                        "file-data": {"_CFURLString": "file:///Users/test/Downloads/"},
                        "displayas": 2,
                    },
                    "tile-type": "directory-tile",
                }
            ],
        }.get(key, default)

        reader = DockStateReader(dockutil, plist_mgr)
        downloads = reader.read_current_downloads()

        assert downloads is not None
        assert downloads.preset == "list"

    def test_read_full_state_returns_complete_dock_config(self) -> None:
        """Test read_full_state returns complete DockConfig."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "Safari\tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
            "Mail\tfile:///Applications/Mail.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.mail\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_autohide.return_value = True
        plist_mgr.read_autohide_delay.return_value = 0.25
        plist_mgr.read_value.side_effect = lambda key, default=None: {
            "persistent-others": [
                {
                    "tile-data": {
                        "file-label": "Downloads",
                        "file-data": {"_CFURLString": "file:///Users/test/Downloads/"},
                        "displayas": 1,
                    },
                    "tile-type": "directory-tile",
                }
            ],
        }.get(key, default)

        reader = DockStateReader(dockutil, plist_mgr)
        config = reader.read_full_state()

        assert isinstance(config, DockConfig)
        assert config.apps == ["Safari", "Mail"]
        assert config.settings.autohide is True
        assert config.settings.autohide_delay == 0.25
        assert isinstance(config.downloads, DownloadsConfig)
        assert config.downloads.preset == "fan"

    def test_read_full_state_with_no_downloads(self) -> None:
        """Test read_full_state handles missing downloads tile."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "Safari\tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)

        plist_mgr = Mock(spec=PlistManager)
        plist_mgr.read_autohide.return_value = False
        plist_mgr.read_autohide_delay.return_value = 0.0
        plist_mgr.read_value.return_value = []

        reader = DockStateReader(dockutil, plist_mgr)
        config = reader.read_full_state()

        assert isinstance(config, DockConfig)
        assert config.apps == ["Safari"]
        assert config.settings.autohide is False
        assert config.downloads is None
