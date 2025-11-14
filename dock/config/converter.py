"""Cattrs converter for configuration models."""

from typing import Any, Literal

import cattrs
from cattrs.gen import make_dict_structure_fn, override

from dock.config.models import DockConfig, DownloadsConfig, SettingsConfig


def create_converter() -> cattrs.Converter:
    """
    Create a configured cattrs converter for dock configuration.

    Returns:
        Configured converter instance.
    """
    converter = cattrs.Converter()

    # Configure DownloadsConfig to handle dict input
    converter.register_structure_hook(
        DownloadsConfig,
        make_dict_structure_fn(
            DownloadsConfig,
            converter,
            preset=override(omit_if_default=False),
            path=override(omit_if_default=False),
            section=override(omit_if_default=False),
        ),
    )

    # Configure SettingsConfig to handle dict input
    converter.register_structure_hook(
        SettingsConfig,
        make_dict_structure_fn(
            SettingsConfig,
            converter,
            autohide=override(omit_if_default=False),
            autohide_delay=override(omit_if_default=False),
        ),
    )

    # Configure DockConfig to handle the union type for downloads
    def structure_dock_config(data: dict[str, Any], _: type) -> DockConfig:
        """Structure DockConfig with special handling for downloads field."""
        apps = data.get("apps", [])
        settings_data = data.get("settings", {})
        downloads_data = data.get("downloads")

        # Structure settings
        settings = converter.structure(settings_data, SettingsConfig)

        # Handle downloads field
        downloads: Literal["off"] | DownloadsConfig | None
        if downloads_data == "off":
            downloads = "off"
        elif downloads_data is None:
            downloads = DownloadsConfig()
        elif isinstance(downloads_data, dict):
            downloads = converter.structure(downloads_data, DownloadsConfig)
        elif isinstance(downloads_data, DownloadsConfig):
            downloads = downloads_data
        else:
            raise ValueError(f"Invalid downloads value: {downloads_data}")

        return DockConfig(apps=apps, downloads=downloads, settings=settings)

    converter.register_structure_hook(DockConfig, structure_dock_config)

    return converter


# Global converter instance
converter = create_converter()
