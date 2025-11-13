"""Manages dock plist file operations."""

import plistlib
from pathlib import Path
from typing import Any


class PlistManager:
    """Manages dock plist file operations."""

    DOCK_PLIST = Path.home() / "Library/Preferences/com.apple.dock.plist"

    def read_plist(self) -> dict[str, Any]:
        """
        Read entire dock plist file.

        Returns:
            Dictionary containing plist data.

        Raises:
            FileNotFoundError: If plist file doesn't exist.
        """
        with open(self.DOCK_PLIST, "rb") as f:
            data = plistlib.load(f)
            # plistlib.load returns Any, but we know it's a dict for dock plist
            assert isinstance(data, dict)
            return data

    def write_plist(self, data: dict[str, Any]) -> None:
        """
        Write entire dock plist file.

        Args:
            data: Dictionary to write to plist file.
        """
        with open(self.DOCK_PLIST, "wb") as f:
            plistlib.dump(data, f)

    def read_value(self, key: str, default: Any = None) -> Any:
        """
        Read specific value from dock plist.

        Args:
            key: Plist key to read.
            default: Default value if key doesn't exist.

        Returns:
            Value for the key, or default if key doesn't exist.
        """
        plist = self.read_plist()
        return plist.get(key, default)

    def write_value(self, key: str, value: Any) -> None:
        """
        Write specific value to dock plist.

        Args:
            key: Plist key to write.
            value: Value to write.
        """
        plist = self.read_plist()
        plist[key] = value
        self.write_plist(plist)

    def read_autohide(self) -> bool:
        """
        Read autohide setting.

        Returns:
            True if autohide is enabled, False otherwise.
        """
        value = self.read_value("autohide", False)
        assert isinstance(value, bool)
        return value

    def write_autohide(self, enabled: bool) -> None:
        """
        Write autohide setting.

        Args:
            enabled: Whether to enable autohide.
        """
        self.write_value("autohide", enabled)

    def read_autohide_delay(self) -> float:
        """
        Read autohide delay.

        Returns:
            Autohide delay in seconds.
        """
        value = self.read_value("autohide-delay", 0.0)
        # Convert to float if it's an int or float
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0

    def write_autohide_delay(self, delay: float) -> None:
        """
        Write autohide delay.

        Args:
            delay: Autohide delay in seconds.
        """
        self.write_value("autohide-delay", delay)
