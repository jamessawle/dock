"""Wrapper for dockutil commands."""


from dock.adapters import CommandExecutor, SubprocessExecutor


class DockutilCommand:
    """Wrapper for dockutil commands."""

    def __init__(self, executor: CommandExecutor | None = None):
        """
        Initialize DockutilCommand.

        Args:
            executor: CommandExecutor instance for running commands.
                     Defaults to SubprocessExecutor if not provided.
        """
        self.executor = executor or SubprocessExecutor()

    def check_installed(self) -> bool:
        """
        Check if dockutil is installed.

        Returns:
            True if dockutil is available, False otherwise.
        """
        result = self.executor.execute(["which", "dockutil"], check=False)
        return bool(result.strip())

    def list_apps(self) -> list[str]:
        """
        List current dock apps.

        Returns:
            List of permanently docked app names (excludes recent/active apps and folders).
        """
        output = self.executor.execute(["dockutil", "--list"])
        if not output.strip():
            return []

        # Parse dockutil output - format is tab-separated:
        # AppName\tPath\tSection\tPlistPath\tBundleID
        apps = []
        for line in output.strip().split("\n"):
            if line.strip():
                # Split by tab and take the first field (app name)
                parts = line.split("\t")
                if len(parts) >= 3:
                    app_name = parts[0].strip()
                    section = parts[2].strip()
                    # Only include apps from persistentApps section
                    # Exclude recentApps (currently running but not permanent)
                    # Exclude persistentOthers (which includes Downloads folder)
                    if section == "persistentApps":
                        apps.append(app_name)
        return apps

    def add_app(self, app_name: str, position: int | None = None) -> None:
        """
        Add app to dock.

        Args:
            app_name: Name of the application to add.
            position: Optional position in dock (1-indexed).
        """
        app_path = f"/Applications/{app_name}.app"
        command = ["dockutil", "--add", app_path]

        if position is not None:
            command.extend(["--position", str(position)])

        command.append("--no-restart")
        self.executor.execute(command)

    def remove_app(self, app_name: str) -> None:
        """
        Remove app from dock.

        Args:
            app_name: Name of the application to remove.
        """
        command = ["dockutil", "--remove", app_name, "--no-restart"]
        self.executor.execute(command)

    def remove_all(self) -> None:
        """Remove all apps from dock."""
        command = ["dockutil", "--remove", "all", "--no-restart"]
        self.executor.execute(command)

    def add_folder(
        self,
        path: str,
        view: str = "auto",
        display: str = "stack",
        section: str = "others",
    ) -> None:
        """
        Add folder to dock.

        Args:
            path: Path to folder (e.g., ~/Downloads).
            view: View style (auto, fan, grid, list).
            display: Display style (stack, folder).
            section: Section to add to (left, right, others).
        """
        command = [
            "dockutil",
            "--add",
            path,
            "--view",
            view,
            "--display",
            display,
            "--section",
            section,
            "--no-restart",
        ]
        self.executor.execute(command)
