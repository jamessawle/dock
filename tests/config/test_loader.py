"""Tests for configuration file loader."""

from pathlib import Path

import pytest
import yaml


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_config_valid_yaml(self, tmp_path):
        """Test loading a valid YAML configuration file."""
        from dock.config.loader import ConfigLoader

        config_file = tmp_path / "config.yml"
        config_data = {
            "apps": ["Safari", "Mail"],
            "settings": {"autohide": True, "autohide_delay": 0.5}
        }
        config_file.write_text(yaml.dump(config_data))

        result = ConfigLoader.load_config(config_file)
        assert result["apps"] == ["Safari", "Mail"]
        assert result["settings"]["autohide"] is True
        assert result["settings"]["autohide_delay"] == 0.5

    def test_load_config_empty_file(self, tmp_path):
        """Test loading an empty YAML file."""
        from dock.config.loader import ConfigLoader

        config_file = tmp_path / "config.yml"
        config_file.write_text("")

        result = ConfigLoader.load_config(config_file)
        assert result == {} or result is None

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading an invalid YAML file raises error."""
        from dock.config.loader import ConfigLoader

        config_file = tmp_path / "config.yml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            ConfigLoader.load_config(config_file)

    def test_load_config_file_not_found(self, tmp_path):
        """Test loading non-existent file raises error."""
        from dock.config.loader import ConfigLoader

        config_file = tmp_path / "nonexistent.yml"

        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_config(config_file)

    def test_discover_config_path_explicit_file(self, tmp_path):
        """Test that explicit --file path takes highest priority."""
        from dock.config.loader import ConfigLoader

        explicit_file = tmp_path / "explicit.yml"
        explicit_file.write_text("apps: []")

        result = ConfigLoader.discover_config_path(
            file_path=str(explicit_file),
            profile=None
        )
        assert result == explicit_file

    def test_discover_config_path_profile(self, tmp_path, monkeypatch):
        """Test that --profile option resolves to profiles directory."""
        from dock.config.loader import ConfigLoader

        # Mock home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        profiles_dir = tmp_path / ".config" / "dock" / "profiles"
        profiles_dir.mkdir(parents=True)
        profile_file = profiles_dir / "work.yml"
        profile_file.write_text("apps: []")

        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile="work"
        )
        assert result == profile_file

    def test_discover_config_path_profile_yaml_extension(self, tmp_path, monkeypatch):
        """Test that --profile option works with .yaml extension."""
        from dock.config.loader import ConfigLoader

        # Mock home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        profiles_dir = tmp_path / ".config" / "dock" / "profiles"
        profiles_dir.mkdir(parents=True)
        profile_file = profiles_dir / "work.yaml"
        profile_file.write_text("apps: []")

        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile="work"
        )
        assert result == profile_file

    def test_discover_config_path_env_variable(self, tmp_path, monkeypatch):
        """Test that $DOCK_CONFIG environment variable is used."""
        from dock.config.loader import ConfigLoader

        env_file = tmp_path / "env_config.yml"
        env_file.write_text("apps: []")

        monkeypatch.setenv("DOCK_CONFIG", str(env_file))

        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile=None
        )
        assert result == env_file

    def test_discover_config_path_user_config(self, tmp_path, monkeypatch):
        """Test that ~/.config/dock/config.yml is used as default."""
        from dock.config.loader import ConfigLoader

        # Mock home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config_dir = tmp_path / ".config" / "dock"
        config_dir.mkdir(parents=True)
        user_config = config_dir / "config.yml"
        user_config.write_text("apps: []")

        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile=None
        )
        assert result == user_config

    def test_discover_config_path_system_config(self, tmp_path, monkeypatch):
        """Test that /etc/dock/config.yml is used as fallback."""
        from dock.config.loader import ConfigLoader

        # Mock home directory to not have config
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nonexistent")

        # Create system config
        system_config = Path("/etc/dock/config.yml")

        # We can't actually create /etc/dock/config.yml in tests,
        # so we'll mock the existence check
        def mock_exists(self):
            if str(self) == "/etc/dock/config.yml":
                return True
            return False

        monkeypatch.setattr(Path, "exists", mock_exists)

        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile=None
        )
        assert result == system_config

    def test_discover_config_path_priority_order(self, tmp_path, monkeypatch):
        """Test that config discovery follows correct priority order."""
        from dock.config.loader import ConfigLoader

        # Setup: create all possible config locations
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Create user config
        config_dir = tmp_path / ".config" / "dock"
        config_dir.mkdir(parents=True)
        user_config = config_dir / "config.yml"
        user_config.write_text("apps: []")

        # Create env config
        env_file = tmp_path / "env_config.yml"
        env_file.write_text("apps: []")
        monkeypatch.setenv("DOCK_CONFIG", str(env_file))

        # Create profile
        profiles_dir = config_dir / "profiles"
        profiles_dir.mkdir()
        profile_file = profiles_dir / "test.yml"
        profile_file.write_text("apps: []")

        # Create explicit file
        explicit_file = tmp_path / "explicit.yml"
        explicit_file.write_text("apps: []")

        # Test priority: explicit file > profile > env > user config

        # 1. Explicit file wins over everything
        result = ConfigLoader.discover_config_path(
            file_path=str(explicit_file),
            profile="test"
        )
        assert result == explicit_file

        # 2. Profile wins over env and user config
        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile="test"
        )
        assert result == profile_file

        # 3. Env wins over user config
        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile=None
        )
        assert result == env_file

        # 4. User config is used when nothing else specified
        monkeypatch.delenv("DOCK_CONFIG")
        result = ConfigLoader.discover_config_path(
            file_path=None,
            profile=None
        )
        assert result == user_config

    def test_discover_config_path_no_config_found(self, tmp_path, monkeypatch):
        """Test that error is raised when no config file is found."""
        from dock.config.loader import ConfigLoader

        # Mock home directory to not have config
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nonexistent")

        # Ensure no env variable
        monkeypatch.delenv("DOCK_CONFIG", raising=False)

        with pytest.raises(FileNotFoundError):
            ConfigLoader.discover_config_path(
                file_path=None,
                profile=None
            )
