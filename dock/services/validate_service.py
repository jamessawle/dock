"""Service for validate command business logic."""

import sys

from cattrs.errors import ClassValidationError

from dock.config.converter import converter
from dock.config.loader import ConfigLoader
from dock.config.models import DockConfig
from dock.config.validator import ConfigValidator
from dock.utils.output import print_error, print_info, print_success, print_warning


class ValidateService:
    """Service for validating dock configuration."""

    def execute(self, file_path: str | None, profile: str | None) -> None:
        """
        Execute the validate command.

        Args:
            file_path: Optional path to config file.
            profile: Optional profile name.

        Raises:
            FileNotFoundError: If config file not found.
            yaml.YAMLError: If config file is invalid YAML.
            ValidationError: If config validation fails.
        """
        # Discover and load config
        loader = ConfigLoader()
        config_path = loader.discover_config_path(file_path, profile)
        print_info(f"Validating configuration: {config_path}")

        config_data = loader.load_config(config_path)

        # Parse and validate config
        try:
            config = converter.structure(config_data, DockConfig)
        except (ClassValidationError, ValueError, TypeError) as e:
            print_error("Configuration validation failed:")
            if isinstance(e, ClassValidationError):
                for exc in e.exceptions:
                    print_info(f"  {exc}")
            else:
                print_info(f"  {e}")
            sys.exit(1)

        # Run semantic validation
        validator = ConfigValidator()
        warnings = validator.validate_config(config)

        if warnings:
            for warning in warnings:
                print_warning(warning)

        print_success("Configuration is valid!")
