"""Configuration models for dock."""

from typing import Literal

import attrs


def _validate_autohide(
    instance: SettingsConfig, attribute: attrs.Attribute[bool], value: bool
) -> None:
    """Validate autohide is a boolean."""
    if not isinstance(value, bool):
        raise TypeError(f"autohide must be a boolean, got {type(value).__name__}")


def _validate_autohide_delay(
    instance: SettingsConfig, attribute: attrs.Attribute[float], value: float
) -> None:
    """Validate autohide_delay is non-negative."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"autohide_delay must be a number, got {type(value).__name__}")
    if value < 0:
        raise ValueError("autohide_delay must be non-negative")


@attrs.define
class SettingsConfig:
    """Dock settings configuration."""

    autohide: bool = attrs.field(default=False, validator=_validate_autohide)
    autohide_delay: float = attrs.field(default=0.0, validator=_validate_autohide_delay)

    def __attrs_post_init__(self) -> None:
        """Round autohide_delay to 2 decimals after initialization."""
        object.__setattr__(self, "autohide_delay", round(self.autohide_delay, 2))


@attrs.define
class DownloadsConfig:
    """Downloads tile configuration."""

    preset: Literal["classic", "fan", "list"] = "classic"
    path: str = "~/Downloads"
    section: Literal["apps-left", "apps-right", "others"] = "others"


def _validate_apps(
    instance: DockConfig, attribute: attrs.Attribute[list[str]], value: list[str]
) -> None:
    """Validate apps is a list."""
    if not isinstance(value, list):
        raise TypeError(f"apps must be a list, got {type(value).__name__}")


@attrs.define
class DockConfig:
    """Complete dock configuration."""

    apps: list[str] = attrs.field(factory=list, validator=_validate_apps)
    downloads: Literal["off"] | DownloadsConfig | None = attrs.field(factory=DownloadsConfig)
    settings: SettingsConfig = attrs.field(factory=SettingsConfig)
