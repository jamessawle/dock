"""Tests for dock executor."""

import subprocess
from unittest.mock import Mock

import pytest

from dock.adapters.dockutil import DockutilCommand
from dock.adapters.plist import PlistManager
from dock.dock.diff import AppChange, DockDiff, SettingChange
from dock.dock.executor import DockExecutor


class TestDockExecutor:
    """Tests for DockExecutor."""

    @pytest.fixture
    def mock_dockutil(self) -> Mock:
        """Create mock DockutilCommand."""
        return Mock(spec=DockutilCommand)

    @pytest.fixture
    def mock_plist(self) -> Mock:
        """Create mock PlistManager."""
        return Mock(spec=PlistManager)

    @pytest.fixture
    def executor(self, mock_dockutil: Mock, mock_plist: Mock) -> DockExecutor:
        """Create DockExecutor with mocked dependencies."""
        return DockExecutor(mock_dockutil, mock_plist, dry_run=False)

    @pytest.fixture
    def dry_run_executor(self, mock_dockutil: Mock, mock_plist: Mock) -> DockExecutor:
        """Create DockExecutor in dry-run mode."""
        return DockExecutor(mock_dockutil, mock_plist, dry_run=True)

    def test_apply_diff_with_no_changes(
        self, executor: DockExecutor, mock_dockutil: Mock, mock_plist: Mock
    ) -> None:
        """Test apply_diff with no changes returns False."""
        diff = DockDiff(
            app_changes=[],
            setting_changes=[],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is False
        mock_dockutil.remove_app.assert_not_called()
        mock_dockutil.add_app.assert_not_called()
        mock_plist.write_autohide.assert_not_called()
        mock_plist.write_autohide_delay.assert_not_called()

    def test_apply_diff_with_app_additions(
        self, executor: DockExecutor, mock_dockutil: Mock
    ) -> None:
        """Test apply_diff adds apps correctly."""
        diff = DockDiff(
            app_changes=[
                AppChange(action="add", app_name="Safari", position=1),
                AppChange(action="add", app_name="Mail", position=2),
            ],
            setting_changes=[],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is True
        assert mock_dockutil.add_app.call_count == 2
        mock_dockutil.add_app.assert_any_call("Safari", 1)
        mock_dockutil.add_app.assert_any_call("Mail", 2)

    def test_apply_diff_with_app_removals(
        self, executor: DockExecutor, mock_dockutil: Mock
    ) -> None:
        """Test apply_diff removes apps correctly."""
        diff = DockDiff(
            app_changes=[
                AppChange(action="remove", app_name="Calendar"),
                AppChange(action="remove", app_name="Notes"),
            ],
            setting_changes=[],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is True
        assert mock_dockutil.remove_app.call_count == 2
        mock_dockutil.remove_app.assert_any_call("Calendar")
        mock_dockutil.remove_app.assert_any_call("Notes")

    def test_apply_diff_with_app_reordering(
        self, executor: DockExecutor, mock_dockutil: Mock
    ) -> None:
        """Test apply_diff handles reordering (remove then add)."""
        diff = DockDiff(
            app_changes=[
                AppChange(action="remove", app_name="Safari"),
                AppChange(action="add", app_name="Safari", position=3),
            ],
            setting_changes=[],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is True
        mock_dockutil.remove_app.assert_called_once_with("Safari")
        mock_dockutil.add_app.assert_called_once_with("Safari", 3)

    def test_apply_diff_with_setting_changes(
        self, executor: DockExecutor, mock_plist: Mock
    ) -> None:
        """Test apply_diff modifies settings correctly."""
        diff = DockDiff(
            app_changes=[],
            setting_changes=[
                SettingChange(setting_name="autohide", old_value=False, new_value=True),
                SettingChange(setting_name="autohide_delay", old_value=0.0, new_value=0.5),
            ],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is True
        mock_plist.write_autohide.assert_called_once_with(True)
        mock_plist.write_autohide_delay.assert_called_once_with(0.5)

    def test_apply_diff_with_mixed_changes(
        self, executor: DockExecutor, mock_dockutil: Mock, mock_plist: Mock, mocker
    ) -> None:
        """Test apply_diff with both app and setting changes."""
        mock_restart = mocker.patch.object(executor, '_restart_dock')

        diff = DockDiff(
            app_changes=[
                AppChange(action="add", app_name="Safari", position=1),
            ],
            setting_changes=[
                SettingChange(setting_name="autohide", old_value=False, new_value=True),
            ],
            downloads_change=None
        )

        result = executor.apply_diff(diff)

        assert result is True
        mock_dockutil.add_app.assert_called_once_with("Safari", 1)
        mock_plist.write_autohide.assert_called_once_with(True)
        mock_restart.assert_called_once()

    def test_apply_diff_restarts_dock_when_changes_made(
        self, executor: DockExecutor, mock_dockutil: Mock, mocker
    ) -> None:
        """Test apply_diff restarts dock only when changes are made."""
        mock_restart = mocker.patch.object(executor, '_restart_dock')

        diff = DockDiff(
            app_changes=[
                AppChange(action="add", app_name="Safari", position=1),
            ],
            setting_changes=[],
            downloads_change=None
        )

        executor.apply_diff(diff)

        mock_restart.assert_called_once()

    def test_apply_diff_does_not_restart_dock_when_no_changes(
        self, executor: DockExecutor, mocker
    ) -> None:
        """Test apply_diff does not restart dock when no changes."""
        mock_restart = mocker.patch.object(executor, '_restart_dock')

        diff = DockDiff(
            app_changes=[],
            setting_changes=[],
            downloads_change=None
        )

        executor.apply_diff(diff)

        mock_restart.assert_not_called()

    def test_apply_diff_in_dry_run_mode(
        self, dry_run_executor: DockExecutor, mock_dockutil: Mock, mock_plist: Mock, mocker
    ) -> None:
        """Test apply_diff in dry-run mode does not execute commands."""
        mock_restart = mocker.patch.object(dry_run_executor, '_restart_dock')

        diff = DockDiff(
            app_changes=[
                AppChange(action="add", app_name="Safari", position=1),
                AppChange(action="remove", app_name="Mail"),
            ],
            setting_changes=[
                SettingChange(setting_name="autohide", old_value=False, new_value=True),
            ],
            downloads_change=None
        )

        result = dry_run_executor.apply_diff(diff)

        # Should return True to indicate changes would be made
        assert result is True

        # But should not execute any commands
        mock_dockutil.add_app.assert_not_called()
        mock_dockutil.remove_app.assert_not_called()
        mock_plist.write_autohide.assert_not_called()
        mock_restart.assert_not_called()

    def test_apply_app_changes_processes_removals_before_additions(
        self, executor: DockExecutor, mock_dockutil: Mock
    ) -> None:
        """Test _apply_app_changes processes removals before additions."""
        changes = [
            AppChange(action="add", app_name="Safari", position=1),
            AppChange(action="remove", app_name="Mail"),
            AppChange(action="add", app_name="Calendar", position=2),
        ]

        executor._apply_app_changes(changes)

        # Verify removals happen before additions
        calls = mock_dockutil.method_calls
        remove_indices = [i for i, c in enumerate(calls) if c[0] == 'remove_app']
        add_indices = [i for i, c in enumerate(calls) if c[0] == 'add_app']

        if remove_indices and add_indices:
            assert max(remove_indices) < min(add_indices)

    def test_apply_setting_changes_handles_autohide(
        self, executor: DockExecutor, mock_plist: Mock
    ) -> None:
        """Test _apply_setting_changes handles autohide setting."""
        changes = [
            SettingChange(setting_name="autohide", old_value=False, new_value=True),
        ]

        executor._apply_setting_changes(changes)

        mock_plist.write_autohide.assert_called_once_with(True)

    def test_apply_setting_changes_handles_autohide_delay(
        self, executor: DockExecutor, mock_plist: Mock
    ) -> None:
        """Test _apply_setting_changes handles autohide_delay setting."""
        changes = [
            SettingChange(setting_name="autohide_delay", old_value=0.0, new_value=0.5),
        ]

        executor._apply_setting_changes(changes)

        mock_plist.write_autohide_delay.assert_called_once_with(0.5)

    def test_apply_setting_changes_handles_multiple_settings(
        self, executor: DockExecutor, mock_plist: Mock
    ) -> None:
        """Test _apply_setting_changes handles multiple settings."""
        changes = [
            SettingChange(setting_name="autohide", old_value=False, new_value=True),
            SettingChange(setting_name="autohide_delay", old_value=0.0, new_value=0.5),
        ]

        executor._apply_setting_changes(changes)

        mock_plist.write_autohide.assert_called_once_with(True)
        mock_plist.write_autohide_delay.assert_called_once_with(0.5)

    def test_restart_dock_calls_killall(self, executor: DockExecutor, mocker) -> None:
        """Test _restart_dock calls killall Dock."""
        mock_run = mocker.patch('subprocess.run')

        executor._restart_dock()

        mock_run.assert_called_once_with(
            ['killall', 'Dock'],
            check=True,
            capture_output=True
        )

    def test_restart_dock_handles_errors(self, executor: DockExecutor, mocker) -> None:
        """Test _restart_dock handles subprocess errors gracefully."""
        mock_run = mocker.patch(
            'subprocess.run',
            side_effect=subprocess.CalledProcessError(1, 'killall')
        )

        # Should not raise exception
        executor._restart_dock()

        mock_run.assert_called_once()
