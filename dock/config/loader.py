"""Configuration file loader with discovery logic."""

import os
from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    """Loads configuration files with discovery logic."""

    @staticmethod
    def discover_config_path(
        file_path: str | None,
        profile: str | None
    ) -> Path:
        """
        Discover config file path using priority:
        1. Explicit --file path
        2. --profile NAME → ~/.config/dock/profiles/NAME.yml
        3. $DOCK_CONFIG environment variable
        4. ~/.config/dock/config.yml
        5. /etc/dock/config.yml
        """
        # Priority 1: Explicit file path
        if file_path:
            return Path(file_path)

        # Priority 2: Profile
        if profile:
            home = Path.home()
            profiles_dir = home / ".config" / "dock" / "profiles"

            # Try .yml first, then .yaml
            profile_yml = profiles_dir / f"{profile}.yml"
            if profile_yml.exists():
                return profile_yml

            profile_yaml = profiles_dir / f"{profile}.yaml"
            if profile_yaml.exists():
                return profile_yaml

            # If profile specified but not found, return the expected path
            # (will fail later with FileNotFoundError)
            return profile_yml

        # Priority 3: Environment variable
        env_config = os.environ.get("DOCK_CONFIG")
        if env_config:
            env_path = Path(env_config)
            if env_path.exists():
                return env_path

        # Priority 4: User config
        home = Path.home()
        user_config = home / ".config" / "dock" / "config.yml"
        if user_config.exists():
            return user_config

        # Priority 5: System config
        system_config = Path("/etc/dock/config.yml")
        if system_config.exists():
            return system_config

        # No config found
        raise FileNotFoundError(
            "No configuration file found. Checked:\n"
            f"  - $DOCK_CONFIG environment variable\n"
            f"  - {user_config}\n"
            f"  - {system_config}"
        )

    @staticmethod
    def load_config(path: Path) -> dict[str, Any]:
        """Load and parse YAML config file."""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            content = f.read()

        # Handle empty files
        if not content.strip():
            return {}

        data = yaml.safe_load(content)

        # yaml.safe_load returns None for empty files
        if data is None:
            return {}

        # Ensure we got a dict
        if not isinstance(data, dict):
            raise ValueError(
                f"Configuration file must contain a YAML dictionary, "
                f"got {type(data).__name__}"
            )

        return data
