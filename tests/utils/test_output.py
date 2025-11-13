"""Tests for output formatting utilities."""

from dock.config.models import DownloadsConfig
from dock.dock.diff import AppChange, DockDiff, SettingChange


def test_print_success(mocker):
    """Test print_success() outputs green text."""
    mock_secho = mocker.patch("click.secho")

    from dock.utils.output import print_success

    print_success("Operation completed")

    mock_secho.assert_called_once_with("✓ Operation completed", fg="green")


def test_print_error(mocker):
    """Test print_error() outputs red text to stderr."""
    mock_secho = mocker.patch("click.secho")

    from dock.utils.output import print_error

    print_error("Something went wrong")

    mock_secho.assert_called_once_with("✗ Something went wrong", fg="red", err=True)


def test_print_warning(mocker):
    """Test print_warning() outputs yellow text."""
    mock_secho = mocker.patch("click.secho")

    from dock.utils.output import print_warning

    print_warning("This is a warning")

    mock_secho.assert_called_once_with("⚠ This is a warning", fg="yellow")


def test_print_info(mocker):
    """Test print_info() outputs plain text."""
    mock_echo = mocker.patch("click.echo")

    from dock.utils.output import print_info

    print_info("Information message")

    mock_echo.assert_called_once_with("  Information message")


def test_print_diff_with_app_changes(mocker, capsys):
    """Test print_diff() formats app changes correctly."""
    mock_echo = mocker.patch("click.echo")
    mock_print_info = mocker.patch("dock.utils.output.print_info")

    from dock.utils.output import print_diff

    diff = DockDiff(
        app_changes=[
            AppChange(action="add", app_name="Safari", position=1),
            AppChange(action="remove", app_name="Mail"),
        ],
        setting_changes=[],
        downloads_change=None,
    )

    print_diff(diff)

    # Check that echo was called for the section header
    assert mock_echo.call_count >= 1
    assert any("App changes" in str(call) for call in mock_echo.call_args_list)

    # Check that print_info was called for each change
    assert mock_print_info.call_count == 2


def test_print_diff_with_setting_changes(mocker):
    """Test print_diff() formats setting changes correctly."""
    mock_echo = mocker.patch("click.echo")
    mock_print_info = mocker.patch("dock.utils.output.print_info")

    from dock.utils.output import print_diff

    diff = DockDiff(
        app_changes=[],
        setting_changes=[
            SettingChange(setting_name="autohide", old_value=False, new_value=True),
            SettingChange(setting_name="autohide_delay", old_value=0.0, new_value=0.5),
        ],
        downloads_change=None,
    )

    print_diff(diff)

    # Check that echo was called for the section header
    assert mock_echo.call_count >= 1
    assert any("Setting changes" in str(call) for call in mock_echo.call_args_list)

    # Check that print_info was called for each change
    assert mock_print_info.call_count == 2


def test_print_diff_with_downloads_change(mocker):
    """Test print_diff() formats downloads changes correctly."""
    mock_echo = mocker.patch("click.echo")
    mocker.patch("dock.utils.output.print_info")

    from dock.utils.output import print_diff

    downloads = DownloadsConfig(preset="fan", path="~/Downloads", section="others")
    diff = DockDiff(
        app_changes=[],
        setting_changes=[],
        downloads_change=downloads,
    )

    print_diff(diff)

    # Check that echo was called for the section header
    assert mock_echo.call_count >= 1
    assert any("Downloads" in str(call) for call in mock_echo.call_args_list)


def test_print_diff_with_downloads_off(mocker):
    """Test print_diff() formats downloads removal correctly."""
    mock_echo = mocker.patch("click.echo")
    mocker.patch("dock.utils.output.print_info")

    from dock.utils.output import print_diff

    diff = DockDiff(
        app_changes=[],
        setting_changes=[],
        downloads_change="off",
    )

    print_diff(diff)

    # Check that echo was called for the section header
    assert mock_echo.call_count >= 1
    assert any("Downloads" in str(call) for call in mock_echo.call_args_list)


def test_print_diff_dry_run_mode(mocker):
    """Test print_diff() includes dry-run prefix."""
    mock_echo = mocker.patch("click.echo")

    from dock.utils.output import print_diff

    diff = DockDiff(
        app_changes=[AppChange(action="add", app_name="Safari", position=1)],
        setting_changes=[],
        downloads_change=None,
    )

    print_diff(diff, dry_run=True)

    # Check that at least one call includes the dry-run prefix
    assert any("[DRY RUN]" in str(call) for call in mock_echo.call_args_list)


def test_print_diff_no_changes(mocker):
    """Test print_diff() with no changes."""
    mock_echo = mocker.patch("click.echo")

    from dock.utils.output import print_diff

    diff = DockDiff(
        app_changes=[],
        setting_changes=[],
        downloads_change=None,
    )

    print_diff(diff)

    # Should not print anything for empty diff
    assert mock_echo.call_count == 0
