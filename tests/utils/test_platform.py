"""Tests for platform detection utilities."""

import pytest


def test_is_macos_on_darwin(mocker):
    """Test is_macos() returns True on macOS."""
    mocker.patch("platform.system", return_value="Darwin")

    from dock.utils.platform import is_macos

    assert is_macos() is True


def test_is_macos_on_linux(mocker):
    """Test is_macos() returns False on Linux."""
    mocker.patch("platform.system", return_value="Linux")

    from dock.utils.platform import is_macos

    assert is_macos() is False


def test_is_macos_on_windows(mocker):
    """Test is_macos() returns False on Windows."""
    mocker.patch("platform.system", return_value="Windows")

    from dock.utils.platform import is_macos

    assert is_macos() is False


def test_require_macos_on_darwin(mocker):
    """Test require_macos() does not raise on macOS."""
    mocker.patch("platform.system", return_value="Darwin")

    from dock.utils.platform import require_macos

    # Should not raise
    require_macos()


def test_require_macos_on_linux(mocker):
    """Test require_macos() raises error on Linux."""
    mocker.patch("platform.system", return_value="Linux")

    from dock.utils.platform import require_macos

    with pytest.raises(RuntimeError, match="This tool requires macOS"):
        require_macos()


def test_require_macos_on_windows(mocker):
    """Test require_macos() raises error on Windows."""
    mocker.patch("platform.system", return_value="Windows")

    from dock.utils.platform import require_macos

    with pytest.raises(RuntimeError, match="This tool requires macOS"):
        require_macos()
