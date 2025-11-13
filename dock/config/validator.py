"""Configuration validator for semantic checks."""

from pathlib import Path

from dock.config.models import DockConfig, DownloadsConfig


class ConfigValidator:
    """Validates configuration semantics."""

    @staticmethod
    def validate_config(config: DockConfig) -> list[str]:
        """
        Validate configuration and return list of warnings.
        - Check for duplicate app names
        - Validate downloads path exists (when specified)
        """
        warnings: list[str] = []

        # Check for duplicate app names
        seen_apps = set()
        for app in config.apps:
            if app in seen_apps:
                warnings.append(f"Duplicate app name found: {app}")
            seen_apps.add(app)

        # Validate downloads path if specified
        if isinstance(config.downloads, DownloadsConfig):
            path_str = config.downloads.path
            # Expand ~ to home directory
            expanded_path = Path(path_str).expanduser()

            if not expanded_path.exists():
                warnings.append(
                    f"Downloads path does not exist: {path_str}"
                )

        return warnings
