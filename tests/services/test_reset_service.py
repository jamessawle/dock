"""Tests for ResetService."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from dock.config.models import DockConfig
from dock.dock.diff import DockDiff
from dock.services.reset_service import ResetService


class TestResetService:
    """Tests for ResetService business logic."""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file."""
        config_file = tmp_path / "config.yml"
        config_data = {
            "apps": ["Safari", "Mail", "Calendar"],
            "settings": {"autohide": True, "autohide_delay": 0.5},
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return config_file

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies."""
        with patch("dock.services.reset_service.require_macos"), \
             patch("dock.services.reset_service.ConfigLoader") as mock_loader, \
             patch("dock.services.reset_service.converter") as mock_converter, \
             patch("dock.services.reset_service.ConfigValidator") as mock_validator, \
             patch("dock.services.reset_service.DockStateReader") as mock_state_reader, \
             patch("dock.services.reset_service.DiffCalculator") as mock_diff_calc, \
             patch("dock.services.reset_service.DockExecutor") as mock_executor, \
             patch("dock.services.reset_service.ExecutionPlan") as mock_plan, \
             patch("dock.services.reset_service.DockutilCommand") as mock_dockutil, \
             patch("dock.services.reset_service.PlistManager") as mock_plist, \
             patch("dock.services.reset_service.print_success") as mock_print_success, \
             patch("dock.services.reset_service.print_error") as mock_print_error, \
             patch("dock.services.reset_service.print_warning") as mock_print_warning, \
             patch("dock.services.reset_service.print_info") as mock_print_info, \
             patch("dock.services.reset_service.print_execution_plan") as mock_print_plan:

            # Setup mock returns - need to mock the instance methods
            mock_loader_instance = Mock()
            mock_loader.return_value = mock_loader_instance
            mock_loader_instance.discover_config_path.return_value = Path("/fake/config.yml")
            mock_loader_instance.load_config.return_value = {
                "apps": ["Safari", "Mail"],
                "settings": {"autohide": True},
            }

            mock_config_instance = Mock(spec=DockConfig)
            mock_config_instance.apps = ["Safari", "Mail"]
            mock_converter.structure.return_value = mock_config_instance

            mock_validator_instance = Mock()
            mock_validator.return_value = mock_validator_instance
            mock_validator_instance.validate_config.return_value = []

            mock_plan.generate_plan.return_value = []

            mock_state_reader_instance = Mock()
            mock_state_reader.return_value = mock_state_reader_instance
            mock_state_reader_instance.read_full_state.return_value = Mock(spec=DockConfig)

            mock_diff_result = Mock(spec=DockDiff)
            mock_diff_result.has_changes.return_value = True
            mock_diff_result.app_changes = []
            mock_diff_result.setting_changes = []
            mock_diff_result.downloads_change = None

            mock_diff_calc_instance = Mock()
            mock_diff_calc.return_value = mock_diff_calc_instance
            mock_diff_calc_instance.calculate_diff.return_value = mock_diff_result

            mock_executor_instance = Mock()
            mock_executor.return_value = mock_executor_instance
            mock_executor_instance.apply_diff.return_value = True

            mock_dockutil_instance = Mock()
            mock_dockutil.return_value = mock_dockutil_instance
            mock_dockutil_instance.check_installed.return_value = True

            yield {
                "loader": mock_loader,
                "converter": mock_converter,
                "validator": mock_validator,
                "state_reader": mock_state_reader,
                "diff_calc": mock_diff_calc,
                "executor": mock_executor,
                "dockutil": mock_dockutil,
                "plist": mock_plist,
                "print_success": mock_print_success,
                "print_error": mock_print_error,
                "print_warning": mock_print_warning,
                "print_info": mock_print_info,
                "print_plan": mock_print_plan,
            }

    def test_execute_with_valid_config(self, temp_config_file, mock_dependencies):
        """Test execute with valid config file."""
        service = ResetService()
        service.execute(file_path=str(temp_config_file), profile=None, dry_run=False)

        # Verify success message was printed
        mock_dependencies["print_success"].assert_called()

    def test_execute_with_dry_run(self, temp_config_file, mock_dependencies):
        """Test execute with dry-run flag."""
        service = ResetService()
        service.execute(file_path=str(temp_config_file), profile=None, dry_run=True)

        # Verify execution plan was printed
        mock_dependencies["print_plan"].assert_called()
        # Verify executor was NOT called in dry-run mode
        mock_dependencies["executor"].assert_not_called()

    def test_execute_with_profile(self, mock_dependencies):
        """Test execute with profile option."""
        service = ResetService()
        service.execute(file_path=None, profile="work", dry_run=False)

        # Verify the command attempted to load a profile
        assert mock_dependencies["loader"].return_value.discover_config_path.called

    def test_execute_with_missing_dockutil(self, temp_config_file, mock_dependencies):
        """Test execute when dockutil is not installed."""
        mock_dependencies["dockutil"].return_value.check_installed.return_value = False

        service = ResetService()
        with pytest.raises(SystemExit):
            service.execute(file_path=str(temp_config_file), profile=None, dry_run=False)

    def test_execute_with_validation_warnings(self, temp_config_file, mock_dependencies):
        """Test execute displays validation warnings."""
        mock_dependencies["validator"].return_value.validate_config.return_value = [
            "Duplicate app name found: Safari",
            "Downloads path does not exist: ~/NonExistent",
        ]

        service = ResetService()
        service.execute(file_path=str(temp_config_file), profile=None, dry_run=False)

        # Should still succeed
        mock_dependencies["print_success"].assert_called()

    def test_execute_with_no_changes_needed(self, temp_config_file, mock_dependencies):
        """Test execute when no changes are needed."""
        (
            mock_dependencies["diff_calc"]
            .return_value.calculate_diff.return_value.has_changes.return_value
        ) = False

        service = ResetService()
        with pytest.raises(SystemExit) as exc_info:
            service.execute(file_path=str(temp_config_file), profile=None, dry_run=False)

        assert exc_info.value.code == 0
        mock_dependencies["print_success"].assert_called()

    def test_execute_on_non_macos_platform(self, temp_config_file):
        """Test execute fails on non-macOS platform."""
        with patch("dock.services.reset_service.require_macos") as mock_require:
            mock_require.side_effect = RuntimeError("This tool requires macOS")

            service = ResetService()
            with pytest.raises(RuntimeError):
                service.execute(file_path=str(temp_config_file), profile=None, dry_run=False)

    def test_execute_with_missing_config_file(self, mock_dependencies):
        """Test execute when config file doesn't exist."""
        (
            mock_dependencies["loader"]
            .return_value.discover_config_path.side_effect
        ) = FileNotFoundError("No configuration file found")

        service = ResetService()
        with pytest.raises(FileNotFoundError):
            service.execute(file_path=None, profile=None, dry_run=False)

    def test_execute_with_invalid_yaml(self, tmp_path, mock_dependencies):
        """Test execute with invalid YAML config."""
        invalid_config = tmp_path / "invalid.yml"
        with open(invalid_config, "w") as f:
            f.write("invalid: yaml: content:")

        (
            mock_dependencies["loader"].return_value.load_config.side_effect
        ) = yaml.YAMLError("Invalid YAML")

        service = ResetService()
        with pytest.raises(yaml.YAMLError):
            service.execute(file_path=str(invalid_config), profile=None, dry_run=False)
