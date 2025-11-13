"""Pydantic models for dock configuration."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SettingsConfig(BaseModel):
    """Dock settings configuration."""

    autohide: bool = False
    autohide_delay: float = Field(default=0.0, ge=0)

    @field_validator("autohide_delay")
    @classmethod
    def round_delay(cls, v: float) -> float:
        """Round autohide_delay to 2 decimals."""
        return round(v, 2)


class DownloadsConfig(BaseModel):
    """Downloads tile configuration."""

    preset: Literal["classic", "fan", "list"] = "classic"
    path: str = "~/Downloads"
    section: Literal["apps-left", "apps-right", "others"] = "others"


class DockConfig(BaseModel):
    """Complete dock configuration."""

    apps: list[str] = Field(default_factory=list)
    downloads: Literal["off"] | DownloadsConfig | None = Field(
        default_factory=lambda: DownloadsConfig()
    )
    settings: SettingsConfig = Field(default_factory=SettingsConfig)
