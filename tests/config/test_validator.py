"""Tests for configuration validator."""

from pathlib import Path


class TestConfigValidator:
    """Tests for ConfigValidator class."""

    def test_validate_config_no_warnings(self):
        """Test validation with a valid configuration."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(
            apps=["Safari", "Mail", "System Settings"],
            settings={"autohide": True}
        )

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_duplicate_apps(self):
        """Test that duplicate app names generate warnings."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(
            apps=["Safari", "Mail", "Safari", "System Settings"]
        )

        warnings = ConfigValidator.validate_config(config)
        assert len(warnings) == 1
        assert "duplicate" in warnings[0].lower()
        assert "Safari" in warnings[0]

    def test_validate_config_multiple_duplicates(self):
        """Test that multiple duplicate app names generate separate warnings."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(
            apps=["Safari", "Mail", "Safari", "Mail", "System Settings"]
        )

        warnings = ConfigValidator.validate_config(config)
        assert len(warnings) == 2
        # Check that both duplicates are mentioned
        warning_text = " ".join(warnings)
        assert "Safari" in warning_text
        assert "Mail" in warning_text

    def test_validate_config_downloads_path_exists(self, tmp_path):
        """Test that existing downloads path generates no warning."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        # Create a test directory
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        config = DockConfig(
            apps=["Safari"],
            downloads={"preset": "classic", "path": str(downloads_dir)}
        )

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_downloads_path_not_exists(self, tmp_path):
        """Test that non-existent downloads path generates warning."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        nonexistent_path = tmp_path / "NonexistentFolder"

        config = DockConfig(
            apps=["Safari"],
            downloads={"preset": "classic", "path": str(nonexistent_path)}
        )

        warnings = ConfigValidator.validate_config(config)
        assert len(warnings) == 1
        assert "path" in warnings[0].lower() or "exist" in warnings[0].lower()
        assert str(nonexistent_path) in warnings[0]

    def test_validate_config_downloads_path_with_tilde(self, monkeypatch, tmp_path):
        """Test that downloads path with ~ is expanded correctly."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        # Mock home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create Downloads in mocked home
        downloads_dir = tmp_path / "Downloads"
        downloads_dir.mkdir()

        config = DockConfig(
            apps=["Safari"],
            downloads={"preset": "classic", "path": "~/Downloads"}
        )

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_downloads_off_no_warning(self):
        """Test that downloads='off' generates no warnings."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(
            apps=["Safari"],
            downloads="off"
        )

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_downloads_none_no_warning(self):
        """Test that downloads=None generates no warnings."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(
            apps=["Safari"],
            downloads=None
        )

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_empty_apps_list(self):
        """Test that empty apps list is valid."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        config = DockConfig(apps=[])

        warnings = ConfigValidator.validate_config(config)
        assert warnings == []

    def test_validate_config_combined_warnings(self, tmp_path):
        """Test that multiple validation issues generate multiple warnings."""
        from dock.config.models import DockConfig
        from dock.config.validator import ConfigValidator

        nonexistent_path = tmp_path / "NonexistentFolder"

        config = DockConfig(
            apps=["Safari", "Mail", "Safari"],
            downloads={"preset": "classic", "path": str(nonexistent_path)}
        )

        warnings = ConfigValidator.validate_config(config)
        assert len(warnings) == 2

        # Check for duplicate app warning
        assert any("duplicate" in w.lower() for w in warnings)

        # Check for path warning
        assert any("path" in w.lower() or "exist" in w.lower() for w in warnings)
