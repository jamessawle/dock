"""Tests for plist manager."""

import plistlib
from pathlib import Path

import pytest

from dock.adapters.plist import PlistManager


class TestPlistManager:
    """Tests for PlistManager."""

    @pytest.fixture
    def temp_plist(self, tmp_path: Path) -> Path:
        """Create a temporary plist file for testing."""
        plist_file = tmp_path / "test.plist"
        test_data = {
            "autohide": True,
            "autohide-delay": 0.5,
            "magnification": False,
            "tilesize": 48,
        }
        with open(plist_file, "wb") as f:
            plistlib.dump(test_data, f)
        return plist_file

    def test_read_plist_returns_dict(self, temp_plist: Path) -> None:
        """Test read_plist returns dictionary of plist contents."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_plist()

        assert isinstance(result, dict)
        assert result["autohide"] is True
        assert result["autohide-delay"] == 0.5
        assert result["magnification"] is False
        assert result["tilesize"] == 48

    def test_write_plist_saves_data(self, tmp_path: Path) -> None:
        """Test write_plist saves data to file."""
        plist_file = tmp_path / "new.plist"
        manager = PlistManager()
        manager.DOCK_PLIST = plist_file

        test_data = {
            "autohide": False,
            "autohide-delay": 1.0,
        }
        manager.write_plist(test_data)

        # Read back and verify
        with open(plist_file, "rb") as f:
            saved_data = plistlib.load(f)

        assert saved_data == test_data

    def test_read_value_returns_existing_key(self, temp_plist: Path) -> None:
        """Test read_value returns value for existing key."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_value("autohide")

        assert result is True

    def test_read_value_returns_default_for_missing_key(self, temp_plist: Path) -> None:
        """Test read_value returns default for missing key."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_value("nonexistent", default="default_value")

        assert result == "default_value"

    def test_read_value_returns_none_for_missing_key_no_default(
        self, temp_plist: Path
    ) -> None:
        """Test read_value returns None when key missing and no default."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_value("nonexistent")

        assert result is None

    def test_write_value_updates_existing_key(self, temp_plist: Path) -> None:
        """Test write_value updates existing key."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        manager.write_value("autohide", False)

        # Read back and verify
        result = manager.read_value("autohide")
        assert result is False

    def test_write_value_adds_new_key(self, temp_plist: Path) -> None:
        """Test write_value adds new key."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        manager.write_value("new_key", "new_value")

        # Read back and verify
        result = manager.read_value("new_key")
        assert result == "new_value"

    def test_read_autohide_returns_boolean(self, temp_plist: Path) -> None:
        """Test read_autohide returns boolean value."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_autohide()

        assert result is True

    def test_read_autohide_returns_false_when_missing(self, tmp_path: Path) -> None:
        """Test read_autohide returns False when key is missing."""
        plist_file = tmp_path / "minimal.plist"
        with open(plist_file, "wb") as f:
            plistlib.dump({}, f)

        manager = PlistManager()
        manager.DOCK_PLIST = plist_file

        result = manager.read_autohide()

        assert result is False

    def test_write_autohide_sets_value(self, temp_plist: Path) -> None:
        """Test write_autohide sets autohide value."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        manager.write_autohide(False)

        result = manager.read_autohide()
        assert result is False

    def test_read_autohide_delay_returns_float(self, temp_plist: Path) -> None:
        """Test read_autohide_delay returns float value."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        result = manager.read_autohide_delay()

        assert result == 0.5

    def test_read_autohide_delay_returns_zero_when_missing(self, tmp_path: Path) -> None:
        """Test read_autohide_delay returns 0.0 when key is missing."""
        plist_file = tmp_path / "minimal.plist"
        with open(plist_file, "wb") as f:
            plistlib.dump({}, f)

        manager = PlistManager()
        manager.DOCK_PLIST = plist_file

        result = manager.read_autohide_delay()

        assert result == 0.0

    def test_write_autohide_delay_sets_value(self, temp_plist: Path) -> None:
        """Test write_autohide_delay sets delay value."""
        manager = PlistManager()
        manager.DOCK_PLIST = temp_plist

        manager.write_autohide_delay(1.5)

        result = manager.read_autohide_delay()
        assert result == 1.5

    def test_read_plist_raises_error_for_nonexistent_file(self, tmp_path: Path) -> None:
        """Test read_plist raises FileNotFoundError for missing file."""
        manager = PlistManager()
        manager.DOCK_PLIST = tmp_path / "nonexistent.plist"

        with pytest.raises(FileNotFoundError):
            manager.read_plist()

    def test_write_plist_handles_various_types(self, tmp_path: Path) -> None:
        """Test write_plist handles various data types."""
        plist_file = tmp_path / "types.plist"
        manager = PlistManager()
        manager.DOCK_PLIST = plist_file

        test_data = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        manager.write_plist(test_data)

        # Read back and verify
        result = manager.read_plist()
        assert result == test_data
