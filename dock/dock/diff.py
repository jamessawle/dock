"""Dock diff calculator for comparing desired vs current state."""

from dataclasses import dataclass
from typing import Any, Literal

from dock.config.models import DockConfig, DownloadsConfig, SettingsConfig


@dataclass
class AppChange:
    """Represents a change to dock apps."""

    action: Literal["add", "remove", "reorder"]
    app_name: str
    position: int | None = None


@dataclass
class SettingChange:
    """Represents a change to dock settings."""

    setting_name: str
    old_value: Any
    new_value: Any


@dataclass
class DockDiff:
    """Complete set of changes needed."""

    app_changes: list[AppChange]
    setting_changes: list[SettingChange]
    downloads_change: Literal["off"] | DownloadsConfig | None

    def has_changes(self) -> bool:
        """
        Check if any changes are needed.

        Returns:
            True if any changes exist, False otherwise.
        """
        return bool(
            self.app_changes
            or self.setting_changes
            or self.downloads_change is not None
        )


class DiffCalculator:
    """Calculates differences between desired and current state."""

    @staticmethod
    def calculate_diff(desired: DockConfig, current: DockConfig) -> DockDiff:
        """
        Calculate what changes are needed.

        Args:
            desired: Desired dock configuration.
            current: Current dock configuration.

        Returns:
            DockDiff containing all necessary changes.
        """
        app_changes = DiffCalculator._calculate_app_changes(
            desired.apps, current.apps
        )
        setting_changes = DiffCalculator._calculate_setting_changes(
            desired.settings, current.settings
        )
        downloads_change = DiffCalculator._calculate_downloads_change(
            desired.downloads, current.downloads
        )

        return DockDiff(
            app_changes=app_changes,
            setting_changes=setting_changes,
            downloads_change=downloads_change,
        )

    @staticmethod
    def _calculate_app_changes(
        desired_apps: list[str], current_apps: list[str]
    ) -> list[AppChange]:
        """
        Determine app additions, removals, and reordering.

        When reordering is needed, dockutil requires removing all apps
        and re-adding them in the correct order.

        Args:
            desired_apps: List of desired app names.
            current_apps: List of current app names.

        Returns:
            List of AppChange objects representing necessary changes.
        """
        changes: list[AppChange] = []

        # Check if the apps are in the same order (ignoring additions/removals)
        # Get the common apps in the order they appear in current
        current_set = set(current_apps)
        desired_set = set(desired_apps)
        common_apps = [app for app in desired_apps if app in current_set]
        current_common = [app for app in current_apps if app in desired_set]

        needs_reorder = common_apps != current_common

        if needs_reorder:
            # If reordering is needed, we need to remove all and re-add all
            # First, mark all current apps for removal
            for app in current_apps:
                changes.append(AppChange(action="reorder", app_name=app))

            # Then, add all desired apps in the correct order
            for position, app in enumerate(desired_apps, start=1):
                changes.append(
                    AppChange(action="add", app_name=app, position=position)
                )
        else:
            # No reordering needed - just handle additions and removals
            # Find apps to remove (in current but not in desired)
            for app in current_apps:
                if app not in desired_apps:
                    changes.append(AppChange(action="remove", app_name=app))

            # Find apps to add (in desired but not in current)
            for position, app in enumerate(desired_apps, start=1):
                if app not in current_apps:
                    changes.append(
                        AppChange(action="add", app_name=app, position=position)
                    )

        return changes

    @staticmethod
    def _calculate_setting_changes(
        desired_settings: SettingsConfig, current_settings: SettingsConfig
    ) -> list[SettingChange]:
        """
        Calculate setting changes.

        Args:
            desired_settings: Desired SettingsConfig.
            current_settings: Current SettingsConfig.

        Returns:
            List of SettingChange objects.
        """
        changes: list[SettingChange] = []

        # Check autohide
        if desired_settings.autohide != current_settings.autohide:
            changes.append(
                SettingChange(
                    setting_name="autohide",
                    old_value=current_settings.autohide,
                    new_value=desired_settings.autohide,
                )
            )

        # Check autohide_delay
        if desired_settings.autohide_delay != current_settings.autohide_delay:
            changes.append(
                SettingChange(
                    setting_name="autohide_delay",
                    old_value=current_settings.autohide_delay,
                    new_value=desired_settings.autohide_delay,
                )
            )

        return changes

    @staticmethod
    def _calculate_downloads_change(
        desired_downloads: Literal["off"] | DownloadsConfig | None,
        current_downloads: Literal["off"] | DownloadsConfig | None
    ) -> Literal["off"] | DownloadsConfig | None:
        """
        Calculate downloads tile changes.

        Args:
            desired_downloads: Desired downloads configuration.
            current_downloads: Current downloads configuration.

        Returns:
            "off" if downloads should be removed,
            DownloadsConfig if downloads should be added/modified,
            None if no change needed.
        """
        # If desired is "off" and current exists, remove it
        if desired_downloads == "off" and current_downloads is not None:
            return "off"

        # If desired is None and current exists, no change (keep current)
        if desired_downloads is None:
            return None

        # If desired is "off" and current is None, no change needed
        if desired_downloads == "off" and current_downloads is None:
            return None

        # If desired is a config and current is None, add it
        if isinstance(desired_downloads, DownloadsConfig) and current_downloads is None:
            return desired_downloads

        # If both are configs, check if they differ
        if isinstance(desired_downloads, DownloadsConfig) and isinstance(
            current_downloads, DownloadsConfig
        ):
            if (
                desired_downloads.preset != current_downloads.preset
                or desired_downloads.path != current_downloads.path
                or desired_downloads.section != current_downloads.section
            ):
                return desired_downloads

        return None
