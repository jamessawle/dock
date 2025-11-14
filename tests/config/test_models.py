"""Tests for configuration models."""

import pytest


class TestSettingsConfig:
    """Tests for SettingsConfig model."""

    def test_settings_config_defaults(self):
        """Test SettingsConfig with default values."""
        from dock.config.models import SettingsConfig

        config = SettingsConfig()
        assert config.autohide is False
        assert config.autohide_delay == 0.0

    def test_settings_config_with_values(self):
        """Test SettingsConfig with explicit values."""
        from dock.config.models import SettingsConfig

        config = SettingsConfig(autohide=True, autohide_delay=0.5)
        assert config.autohide is True
        assert config.autohide_delay == 0.5

    def test_autohide_delay_rounding(self):
        """Test that autohide_delay is rounded to 2 decimals."""
        from dock.config.models import SettingsConfig

        config = SettingsConfig(autohide_delay=0.123456)
        assert config.autohide_delay == 0.12

        config = SettingsConfig(autohide_delay=0.156)
        assert config.autohide_delay == 0.16

    def test_autohide_delay_negative_invalid(self):
        """Test that negative autohide_delay is invalid."""
        from dock.config.models import SettingsConfig

        with pytest.raises(ValueError):
            SettingsConfig(autohide_delay=-0.5)

    def test_autohide_invalid_type(self):
        """Test that invalid autohide type raises error."""
        from dock.config.models import SettingsConfig

        with pytest.raises(TypeError):
            SettingsConfig(autohide="not a boolean")


class TestDownloadsConfig:
    """Tests for DownloadsConfig model."""

    def test_downloads_config_with_defaults(self):
        """Test DownloadsConfig with default values."""
        from dock.config.models import DownloadsConfig

        config = DownloadsConfig(preset="classic")
        assert config.preset == "classic"
        assert config.path == "~/Downloads"
        assert config.section == "others"

    def test_downloads_config_all_fields(self):
        """Test DownloadsConfig with all fields specified."""
        from dock.config.models import DownloadsConfig

        config = DownloadsConfig(
            preset="fan",
            path="~/Documents",
            section="apps-right"
        )
        assert config.preset == "fan"
        assert config.path == "~/Documents"
        assert config.section == "apps-right"

    def test_downloads_preset_valid_values(self):
        """Test that all valid preset values are accepted."""
        from dock.config.models import DownloadsConfig

        for preset in ["classic", "fan", "list"]:
            config = DownloadsConfig(preset=preset)
            assert config.preset == preset

    def test_downloads_preset_invalid_value(self):
        """Test that invalid preset value raises error."""
        from dock.config.converter import converter
        from dock.config.models import DownloadsConfig

        with pytest.raises(Exception):  # cattrs raises various exceptions for invalid literals
            converter.structure({"preset": "invalid"}, DownloadsConfig)

    def test_downloads_section_valid_values(self):
        """Test that all valid section values are accepted."""
        from dock.config.models import DownloadsConfig

        for section in ["apps-left", "apps-right", "others"]:
            config = DownloadsConfig(preset="classic", section=section)
            assert config.section == section

    def test_downloads_section_invalid_value(self):
        """Test that invalid section value raises error."""
        from dock.config.converter import converter
        from dock.config.models import DownloadsConfig

        with pytest.raises(Exception):  # cattrs raises various exceptions for invalid literals
            converter.structure({"preset": "classic", "section": "invalid"}, DownloadsConfig)


class TestDockConfig:
    """Tests for DockConfig model."""

    def test_dock_config_minimal(self):
        """Test DockConfig with minimal configuration."""
        from dock.config.models import DockConfig, DownloadsConfig

        config = DockConfig()
        assert config.apps == []
        # Downloads should default to classic preset
        assert isinstance(config.downloads, DownloadsConfig)
        assert config.downloads.preset == "classic"
        assert config.downloads.path == "~/Downloads"
        assert config.downloads.section == "others"
        assert config.settings.autohide is False
        assert config.settings.autohide_delay == 0.0

    def test_dock_config_with_apps(self):
        """Test DockConfig with apps list."""
        from dock.config.models import DockConfig

        config = DockConfig(apps=["Safari", "Mail", "System Settings"])
        assert config.apps == ["Safari", "Mail", "System Settings"]

    def test_dock_config_with_downloads_object(self):
        """Test DockConfig with downloads configuration object."""
        from dock.config.models import DockConfig, DownloadsConfig

        downloads = DownloadsConfig(preset="fan", path="~/Documents")
        config = DockConfig(downloads=downloads)
        assert config.downloads.preset == "fan"
        assert config.downloads.path == "~/Documents"

    def test_dock_config_with_downloads_dict(self):
        """Test DockConfig with downloads as dict."""
        from dock.config.converter import converter
        from dock.config.models import DockConfig

        config = converter.structure(
            {"downloads": {"preset": "list", "path": "~/Desktop"}}, DockConfig
        )
        assert config.downloads.preset == "list"
        assert config.downloads.path == "~/Desktop"

    def test_dock_config_with_downloads_off(self):
        """Test DockConfig with downloads set to 'off'."""
        from dock.config.models import DockConfig

        config = DockConfig(downloads="off")
        assert config.downloads == "off"

    def test_dock_config_with_settings(self):
        """Test DockConfig with settings configuration."""
        from dock.config.converter import converter
        from dock.config.models import DockConfig

        config = converter.structure(
            {"settings": {"autohide": True, "autohide_delay": 0.25}}, DockConfig
        )
        assert config.settings.autohide is True
        assert config.settings.autohide_delay == 0.25

    def test_dock_config_complete(self):
        """Test DockConfig with all fields."""
        from dock.config.converter import converter
        from dock.config.models import DockConfig

        config = converter.structure(
            {
                "apps": ["Safari", "Mail"],
                "downloads": {"preset": "classic", "path": "~/Downloads"},
                "settings": {"autohide": True, "autohide_delay": 0.15},
            },
            DockConfig,
        )
        assert len(config.apps) == 2
        assert config.downloads.preset == "classic"
        assert config.settings.autohide is True
        assert config.settings.autohide_delay == 0.15

    def test_dock_config_invalid_apps_type(self):
        """Test that invalid apps type raises error."""
        from dock.config.converter import converter
        from dock.config.models import DockConfig

        with pytest.raises(Exception):
            converter.structure({"apps": "not a list"}, DockConfig)

    def test_dock_config_invalid_downloads_type(self):
        """Test that invalid downloads type raises error."""
        from dock.config.converter import converter
        from dock.config.models import DockConfig

        with pytest.raises(Exception):
            converter.structure({"downloads": 123}, DockConfig)
