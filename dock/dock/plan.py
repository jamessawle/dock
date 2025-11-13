"""Execution plan generator for dock changes."""

from dataclasses import dataclass
from typing import Literal

from dock.config.models import DownloadsConfig
from dock.dock.diff import DockDiff


@dataclass
class ExecutionStep:
    """Represents a single execution step."""

    action: Literal["remove_all", "add_app", "set_plist", "restart"]
    description: str
    command: str


class ExecutionPlan:
    """Generates execution plan from diff."""

    @staticmethod
    def generate_plan(diff: DockDiff, desired_apps: list[str]) -> list[ExecutionStep]:
        """
        Generate execution plan from diff.

        Args:
            diff: DockDiff containing changes.
            desired_apps: List of desired apps in order.

        Returns:
            List of ExecutionStep objects representing the plan.
        """
        steps: list[ExecutionStep] = []

        # Check if we need to modify apps
        has_reorder = any(change.action == "reorder" for change in diff.app_changes)
        has_app_changes = bool(diff.app_changes)

        if has_reorder:
            # Step 1: Remove all apps
            steps.append(
                ExecutionStep(
                    action="remove_all",
                    description="Remove all dock items",
                    command="dockutil --remove all --no-restart",
                )
            )

            # Step 2: Add all desired apps in order
            for position, app in enumerate(desired_apps, start=1):
                steps.append(
                    ExecutionStep(
                        action="add_app",
                        description=f"Add {app} at position {position}",
                        command=(
                            f"dockutil --add /Applications/{app}.app "
                            f"--position {position} --no-restart"
                        ),
                    )
                )
        elif has_app_changes:
            # Handle individual additions and removals
            for change in diff.app_changes:
                if change.action == "remove":
                    steps.append(
                        ExecutionStep(
                            action="add_app",
                            description=f"Remove {change.app_name}",
                            command=f"dockutil --remove '{change.app_name}' --no-restart",
                        )
                    )

            for change in diff.app_changes:
                if change.action == "add":
                    position_arg = (
                        f" --position {change.position}" if change.position else ""
                    )
                    steps.append(
                        ExecutionStep(
                            action="add_app",
                            description=f"Add {change.app_name}",
                            command=(
                                f"dockutil --add /Applications/{change.app_name}.app"
                                f"{position_arg} --no-restart"
                            ),
                        )
                    )

        # Handle downloads changes
        if diff.downloads_change is not None:
            if diff.downloads_change == "off":
                steps.append(
                    ExecutionStep(
                        action="add_app",
                        description="Remove Downloads folder",
                        command="dockutil --remove Downloads --no-restart",
                    )
                )
            elif isinstance(diff.downloads_change, DownloadsConfig):
                # Map preset to dockutil view and display options
                # classic = stack view, fan = fan view, list = list/grid view
                if diff.downloads_change.preset == "classic":
                    view = "auto"
                    display = "stack"
                elif diff.downloads_change.preset == "fan":
                    view = "fan"
                    display = "stack"
                else:  # list
                    view = "grid"
                    display = "folder"

                # Map section to dockutil section
                section_map = {
                    "apps-left": "left",
                    "apps-right": "right",
                    "others": "others",
                }
                section = section_map.get(diff.downloads_change.section, "others")

                steps.append(
                    ExecutionStep(
                        action="add_app",
                        description=(
                            f"Add Downloads folder (preset: {diff.downloads_change.preset})"
                        ),
                        command=(
                            f"dockutil --add '{diff.downloads_change.path}' "
                            f"--view {view} --display {display} "
                            f"--section {section} --no-restart"
                        ),
                    )
                )

        # Handle settings changes
        for setting_change in diff.setting_changes:
            if setting_change.setting_name == "autohide":
                value = "true" if setting_change.new_value else "false"
                steps.append(
                    ExecutionStep(
                        action="set_plist",
                        description=f"Set autohide to {value}",
                        command=f"defaults write com.apple.dock autohide -bool {value}",
                    )
                )
            elif setting_change.setting_name == "autohide_delay":
                steps.append(
                    ExecutionStep(
                        action="set_plist",
                        description=f"Set autohide delay to {setting_change.new_value}s",
                        command=(
                            f"defaults write com.apple.dock autohide-delay "
                            f"-float {setting_change.new_value}"
                        ),
                    )
                )

        # Final step: Restart dock
        if steps:
            steps.append(
                ExecutionStep(
                    action="restart",
                    description="Restart Dock to apply changes",
                    command="killall Dock",
                )
            )

        return steps
