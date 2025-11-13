"""Platform detection utilities."""

import platform


def is_macos() -> bool:
    """
    Check if running on macOS.

    Returns:
        True if running on macOS (Darwin), False otherwise.
    """
    return platform.system() == "Darwin"


def require_macos() -> None:
    """
    Raise error if not on macOS.

    Raises:
        RuntimeError: If not running on macOS.
    """
    if not is_macos():
        raise RuntimeError("This tool requires macOS")
