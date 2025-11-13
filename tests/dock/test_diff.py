"""Tests for dock diff calculator."""


from dock.config.models import DockConfig, DownloadsConfig, SettingsConfig
from dock.dock.diff import AppChange, DiffCalculator, DockDiff, SettingChange


class TestDiffCalculator:
    """Tests for DiffCalculator."""

    def test_calculate_diff_with_app_additions(self) -> None:
        """Test calculate_diff detects app additions."""
        current = DockConfig(apps=["Safari", "Mail"])
        desired = DockConfig(apps=["Safari", "Mail", "Calendar"])

        diff = DiffCalculator.calculate_diff(desired, current)

        assert len(diff.app_changes) == 1
        assert diff.app_changes[0].action == "add"
        assert diff.app_changes[0].app_name == "Calendar"
        assert diff.app_changes[0].position == 3

    def test_calculate_diff_with_app_removals(self) -> None:
        """Test calculate_diff detects app removals."""
        current = DockConfig(apps=["Safari", "Mail", "Calendar"])
        desired = DockConfig(apps=["Safari", "Mail"])

        diff = DiffCalculator.calculate_diff(desired, current)

        assert len(diff.app_changes) == 1
        assert diff.app_changes[0].action == "remove"
        assert diff.app_changes[0].app_name == "Calendar"

    def test_calculate_diff_with_app_reordering(self) -> None:
        """Test calculate_diff detects app reordering."""
        current = DockConfig(apps=["Safari", "Mail", "Calendar"])
        desired = DockConfig(apps=["Mail", "Safari", "Calendar"])

        diff = DiffCalculator.calculate_diff(desired, current)

        # Should detect reordering as remove + add operations
        assert len(diff.app_changes) > 0
        assert diff.has_changes()

    def test_calculate_diff_with_multiple_app_changes(self) -> None:
        """Test calculate_diff handles multiple app changes."""
        current = DockConfig(apps=["Safari", "Mail"])
        desired = DockConfig(apps=["Mail", "Calendar", "Notes"])

        diff = DiffCalculator.calculate_diff(desired, current)

        # Should detect removal of Safari and additions of Calendar and Notes
        assert len(diff.app_changes) >= 2
        assert diff.has_changes()

    def test_calculate_diff_with_no_app_changes(self) -> None:
        """Test calculate_diff returns empty when apps are identical."""
        current = DockConfig(apps=["Safari", "Mail", "Calendar"])
        desired = DockConfig(apps=["Safari", "Mail", "Calendar"])

        diff = DiffCalculator.calculate_diff(desired, current)

        assert len(diff.app_changes) == 0

    def test_calculate_diff_with_setting_changes(self) -> None:
        """Test calculate_diff detects setting changes."""
        current = DockConfig(
            apps=[],
            settings=SettingsConfig(autohide=False, autohide_delay=0.0)
        )
        desired = DockConfig(
            apps=[],
            settings=SettingsConfig(autohide=True, autohide_delay=0.5)
        )

        diff = DiffCalculator.calculate_diff(desired, current)

        assert len(diff.setting_changes) == 2

        autohide_change = next(c for c in diff.setting_changes if c.setting_name == "autohide")
        assert autohide_change.old_value is False
        assert autohide_change.new_value is True

        delay_change = next(c for c in diff.setting_changes if c.setting_name == "autohide_delay")
        assert delay_change.old_value == 0.0
        assert delay_change.new_value == 0.5

    def test_calculate_diff_with_no_setting_changes(self) -> None:
        """Test calculate_diff returns empty when settings are identical."""
        current = DockConfig(
            apps=[],
            settings=SettingsConfig(autohide=True, autohide_delay=0.5)
        )
        desired = DockConfig(
            apps=[],
            settings=SettingsConfig(autohide=True, autohide_delay=0.5)
        )

        diff = DiffCalculator.calculate_diff(desired, current)

        assert len(diff.setting_changes) == 0

    def test_calculate_diff_with_downloads_tile_addition(self) -> None:
        """Test calculate_diff detects downloads tile addition."""
        current = DockConfig(apps=[], downloads=None)
        desired = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )

        diff = DiffCalculator.calculate_diff(desired, current)

        assert diff.downloads_change is not None
        assert diff.downloads_change.preset == "fan"

    def test_calculate_diff_with_downloads_tile_removal(self) -> None:
        """Test calculate_diff detects downloads tile removal."""
        current = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )
        desired = DockConfig(apps=[], downloads="off")

        diff = DiffCalculator.calculate_diff(desired, current)

        assert diff.downloads_change == "off"

    def test_calculate_diff_with_downloads_tile_modification(self) -> None:
        """Test calculate_diff detects downloads tile modifications."""
        current = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )
        desired = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="list", path="~/Documents", section="others")
        )

        diff = DiffCalculator.calculate_diff(desired, current)

        assert diff.downloads_change is not None
        assert isinstance(diff.downloads_change, DownloadsConfig)
        assert diff.downloads_change.preset == "list"
        assert diff.downloads_change.path == "~/Documents"

    def test_calculate_diff_with_no_downloads_changes(self) -> None:
        """Test calculate_diff returns None when downloads are identical."""
        current = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )
        desired = DockConfig(
            apps=[],
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )

        diff = DiffCalculator.calculate_diff(desired, current)

        assert diff.downloads_change is None

    def test_calculate_diff_with_no_changes(self) -> None:
        """Test calculate_diff with completely identical configs."""
        config = DockConfig(
            apps=["Safari", "Mail"],
            settings=SettingsConfig(autohide=True, autohide_delay=0.5),
            downloads=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )

        diff = DiffCalculator.calculate_diff(config, config)

        assert len(diff.app_changes) == 0
        assert len(diff.setting_changes) == 0
        assert diff.downloads_change is None
        assert not diff.has_changes()

    def test_has_changes_returns_true_with_app_changes(self) -> None:
        """Test has_changes returns True when app changes exist."""
        diff = DockDiff(
            app_changes=[AppChange(action="add", app_name="Safari", position=1)],
            setting_changes=[],
            downloads_change=None
        )

        assert diff.has_changes() is True

    def test_has_changes_returns_true_with_setting_changes(self) -> None:
        """Test has_changes returns True when setting changes exist."""
        diff = DockDiff(
            app_changes=[],
            setting_changes=[
                SettingChange(setting_name="autohide", old_value=False, new_value=True)
            ],
            downloads_change=None
        )

        assert diff.has_changes() is True

    def test_has_changes_returns_true_with_downloads_changes(self) -> None:
        """Test has_changes returns True when downloads changes exist."""
        diff = DockDiff(
            app_changes=[],
            setting_changes=[],
            downloads_change=DownloadsConfig(preset="fan", path="~/Downloads", section="others")
        )

        assert diff.has_changes() is True

    def test_has_changes_returns_false_with_no_changes(self) -> None:
        """Test has_changes returns False when no changes exist."""
        diff = DockDiff(
            app_changes=[],
            setting_changes=[],
            downloads_change=None
        )

        assert diff.has_changes() is False

    def test_calculate_app_changes_with_additions_at_end(self) -> None:
        """Test _calculate_app_changes adds new apps at the end."""
        desired_apps = ["Safari", "Mail", "Calendar"]
        current_apps = ["Safari", "Mail"]

        changes = DiffCalculator._calculate_app_changes(desired_apps, current_apps)

        additions = [c for c in changes if c.action == "add"]
        assert len(additions) == 1
        assert additions[0].app_name == "Calendar"
        assert additions[0].position == 3

    def test_calculate_app_changes_with_removals(self) -> None:
        """Test _calculate_app_changes removes apps not in desired list."""
        desired_apps = ["Safari"]
        current_apps = ["Safari", "Mail", "Calendar"]

        changes = DiffCalculator._calculate_app_changes(desired_apps, current_apps)

        removals = [c for c in changes if c.action == "remove"]
        assert len(removals) == 2
        removed_names = {c.app_name for c in removals}
        assert "Mail" in removed_names
        assert "Calendar" in removed_names

    def test_calculate_app_changes_with_reordering(self) -> None:
        """Test _calculate_app_changes handles reordering."""
        desired_apps = ["Calendar", "Safari", "Mail"]
        current_apps = ["Safari", "Mail", "Calendar"]

        changes = DiffCalculator._calculate_app_changes(desired_apps, current_apps)

        # Reordering should result in remove and add operations
        assert len(changes) > 0

    def test_calculate_app_changes_with_empty_current(self) -> None:
        """Test _calculate_app_changes with empty current apps."""
        desired_apps = ["Safari", "Mail"]
        current_apps = []

        changes = DiffCalculator._calculate_app_changes(desired_apps, current_apps)

        additions = [c for c in changes if c.action == "add"]
        assert len(additions) == 2
        assert additions[0].app_name == "Safari"
        assert additions[0].position == 1
        assert additions[1].app_name == "Mail"
        assert additions[1].position == 2

    def test_calculate_app_changes_with_empty_desired(self) -> None:
        """Test _calculate_app_changes with empty desired apps."""
        desired_apps = []
        current_apps = ["Safari", "Mail"]

        changes = DiffCalculator._calculate_app_changes(desired_apps, current_apps)

        removals = [c for c in changes if c.action == "remove"]
        assert len(removals) == 2
