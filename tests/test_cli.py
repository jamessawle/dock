"""Minimal CLI tests - just argument parsing and service invocation."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from dock.cli import cli


class TestCLI:
    """Test CLI argument parsing and service invocation."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help message."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Manage macOS Dock" in result.output

    def test_cli_version(self, runner):
        """Test CLI version option."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0


class TestResetCLI:
    """Test reset command CLI."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_reset_invokes_service(self, runner, tmp_path):
        """Test that reset command invokes ResetService."""
        # Create a temp file so Click's path validation passes
        config_file = tmp_path / "config.yml"
        config_file.write_text("apps: []")

        with patch("dock.cli.ResetService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["reset", "--file", str(config_file)])

            # Verify service was instantiated and execute was called
            mock_service_class.assert_called_once()
            mock_service.execute.assert_called_once_with(
                file_path=str(config_file), profile=None, dry_run=False
            )

    def test_reset_with_profile_option(self, runner):
        """Test reset command with --profile option."""
        with patch("dock.cli.ResetService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["reset", "--profile", "work"])

            mock_service.execute.assert_called_once_with(
                file_path=None, profile="work", dry_run=False
            )

    def test_reset_with_dry_run_flag(self, runner):
        """Test reset command with --dry-run flag."""
        with patch("dock.cli.ResetService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["reset", "--dry-run"])

            mock_service.execute.assert_called_once_with(
                file_path=None, profile=None, dry_run=True
            )

    def test_reset_handles_service_exception(self, runner):
        """Test reset command handles service exceptions."""
        with patch("dock.cli.ResetService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.execute.side_effect = Exception("Test error")

            result = runner.invoke(cli, ["reset"])

            assert result.exit_code != 0
            assert "Error" in result.output


class TestBackupCLI:
    """Test backup command CLI."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_backup_invokes_service(self, runner):
        """Test that backup command invokes BackupService."""
        with patch("dock.cli.BackupService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["backup", "--file", "/fake/output.yml"])

            mock_service_class.assert_called_once()
            mock_service.execute.assert_called_once_with(file_path="/fake/output.yml")

    def test_backup_requires_file_option(self, runner):
        """Test backup command requires --file option."""
        result = runner.invoke(cli, ["backup"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()


class TestShowCLI:
    """Test show command CLI."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_show_invokes_service(self, runner):
        """Test that show command invokes ShowService."""
        with patch("dock.cli.ShowService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["show"])

            mock_service_class.assert_called_once()
            mock_service.execute.assert_called_once()


class TestValidateCLI:
    """Test validate command CLI."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_validate_invokes_service(self, runner, tmp_path):
        """Test that validate command invokes ValidateService."""
        # Create a temp file so Click's path validation passes
        config_file = tmp_path / "config.yml"
        config_file.write_text("apps: []")

        with patch("dock.cli.ValidateService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["validate", "--file", str(config_file)])

            mock_service_class.assert_called_once()
            mock_service.execute.assert_called_once_with(
                file_path=str(config_file), profile=None
            )

    def test_validate_with_profile_option(self, runner):
        """Test validate command with --profile option."""
        with patch("dock.cli.ValidateService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            runner.invoke(cli, ["validate", "--profile", "work"])

            mock_service.execute.assert_called_once_with(
                file_path=None, profile="work"
            )
