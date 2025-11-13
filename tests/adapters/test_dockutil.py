"""Tests for dockutil command wrapper."""

from unittest.mock import Mock

from dock.adapters import CommandExecutor
from dock.adapters.dockutil import DockutilCommand


class TestDockutilCommand:
    """Tests for DockutilCommand wrapper."""

    def test_check_installed_returns_true_when_available(self) -> None:
        """Test check_installed returns True when dockutil is available."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = "/usr/local/bin/dockutil\n"

        dockutil = DockutilCommand(executor=mock_executor)
        result = dockutil.check_installed()

        assert result is True
        mock_executor.execute.assert_called_once_with(
            ["which", "dockutil"],
            check=False
        )

    def test_check_installed_returns_false_when_not_available(self) -> None:
        """Test check_installed returns False when dockutil is not found."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        result = dockutil.check_installed()

        assert result is False

    def test_list_apps_parses_dockutil_output(self) -> None:
        """Test list_apps correctly parses dockutil output."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "Safari\tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
            "Mail\tfile:///Applications/Mail.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.mail\n"
            "System Settings\tfile:///System/Applications/System%20Settings.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.systempreferences\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)
        apps = dockutil.list_apps()

        assert apps == ["Safari", "Mail", "System Settings"]
        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--list"]
        )

    def test_list_apps_handles_empty_dock(self) -> None:
        """Test list_apps returns empty list for empty dock."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        apps = dockutil.list_apps()

        assert apps == []

    def test_list_apps_strips_whitespace(self) -> None:
        """Test list_apps strips whitespace from app names."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "  Safari  \tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
            "Mail\tfile:///Applications/Mail.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.mail\n"
            "  System Settings\tfile:///System/Applications/System%20Settings.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.systempreferences\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)
        apps = dockutil.list_apps()

        assert apps == ["Safari", "Mail", "System Settings"]

    def test_list_apps_excludes_persistent_others(self) -> None:
        """Test list_apps excludes items from persistentOthers section like Downloads folder."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = (
            "Safari\tfile:///Applications/Safari.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.Safari\n"
            "Mail\tfile:///Applications/Mail.app/\tpersistentApps\t/Users/test/Library/Preferences/com.apple.dock.plist\tcom.apple.mail\n"
            "Downloads\tfile:///Users/test/Downloads/\tpersistentOthers\t/Users/test/Library/Preferences/com.apple.dock.plist\t\n"
        )

        dockutil = DockutilCommand(executor=mock_executor)
        apps = dockutil.list_apps()

        # Should only include apps, not Downloads folder
        assert apps == ["Safari", "Mail"]
        assert "Downloads" not in apps

    def test_add_app_without_position(self) -> None:
        """Test add_app generates correct command without position."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.add_app("Safari")

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--add", "/Applications/Safari.app", "--no-restart"]
        )

    def test_add_app_with_position(self) -> None:
        """Test add_app generates correct command with position."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.add_app("Safari", position=3)

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--add", "/Applications/Safari.app", "--position", "3", "--no-restart"]
        )

    def test_add_app_handles_app_with_spaces(self) -> None:
        """Test add_app handles app names with spaces."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.add_app("Visual Studio Code")

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--add", "/Applications/Visual Studio Code.app", "--no-restart"]
        )

    def test_remove_app_generates_correct_command(self) -> None:
        """Test remove_app generates correct command."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.remove_app("Safari")

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--remove", "Safari", "--no-restart"]
        )

    def test_remove_app_handles_app_with_spaces(self) -> None:
        """Test remove_app handles app names with spaces."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.remove_app("Visual Studio Code")

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--remove", "Visual Studio Code", "--no-restart"]
        )

    def test_remove_all_generates_correct_command(self) -> None:
        """Test remove_all generates correct command."""
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute.return_value = ""

        dockutil = DockutilCommand(executor=mock_executor)
        dockutil.remove_all()

        mock_executor.execute.assert_called_once_with(
            ["dockutil", "--remove", "all", "--no-restart"]
        )

    def test_uses_default_executor_when_none_provided(self) -> None:
        """Test DockutilCommand uses SubprocessExecutor by default."""
        dockutil = DockutilCommand()

        assert dockutil.executor is not None
        from dock.adapters import SubprocessExecutor
        assert isinstance(dockutil.executor, SubprocessExecutor)
