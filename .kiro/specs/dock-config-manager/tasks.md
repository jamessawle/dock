# Implementation Plan

- [x] 1. Set up project structure and development environment
  - Create project directory structure with dock/, tests/, and completions/ folders
  - Initialize uv project with pyproject.toml and .python-version
  - Create Makefile with common development tasks (install, test, lint, type-check, format, ci)
  - Add .gitignore for Python projects
  - Add MIT LICENSE file
  - Set up pytest configuration in pyproject.toml
  - _Requirements: 13.5, 15.1_

- [x] 2. Implement configuration models with TDD
- [x] 2.1 Write tests for Pydantic configuration models
  - Write tests for SettingsConfig validation (autohide, autohide_delay rounding)
  - Write tests for DownloadsConfig validation (preset, path, section enums)
  - Write tests for DockConfig validation (apps list, optional fields)
  - Write tests for invalid configurations
  - _Requirements: 13.1, 13.4_

- [x] 2.2 Implement Pydantic models to pass tests
  - Create SettingsConfig model with autohide and autohide_delay fields
  - Create DownloadsConfig model with preset, path, and section fields
  - Create DockConfig model with apps, downloads, and settings fields
  - Add validators for autohide_delay rounding and enum values
  - _Requirements: 1.5, 3.2, 3.3, 4.3, 4.4, 4.5_

- [x] 2.3 Write tests for configuration file loader
  - Write tests for config discovery priority order
  - Write tests for YAML parsing with valid and invalid files
  - Write tests for environment variable handling
  - Write tests for profile path resolution
  - Write tests for file not found scenarios
  - _Requirements: 13.1_

- [x] 2.4 Implement configuration loader to pass tests
  - Create ConfigLoader.discover_config_path() implementing priority order
  - Create ConfigLoader.load_config() to read and parse YAML files
  - Handle environment variable $DOCK_CONFIG
  - Handle --profile option to load from ~/.config/dock/profiles/
  - Handle default paths ~/.config/dock/config.yml and /etc/dock/config.yml
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.5 Write tests for configuration validator
  - Write tests for duplicate app name detection
  - Write tests for downloads path validation
  - Write tests for warning message generation
  - _Requirements: 13.4_

- [x] 2.6 Implement configuration validator to pass tests
  - Create ConfigValidator.validate_config() to check for warnings
  - Check for duplicate app names
  - Validate downloads path exists when specified
  - Return list of validation warnings
  - _Requirements: 11.2, 11.3, 13.4_

- [x] 3. Implement command execution abstractions with TDD
- [x] 3.1 Write tests for command executor interface
  - Write tests for SubprocessExecutor with mocked subprocess
  - Write tests for command output capture
  - Write tests for error handling
  - _Requirements: 13.2_

- [x] 3.2 Implement command executor to pass tests
  - Create CommandExecutor abstract base class with execute() method
  - Create SubprocessExecutor implementation using subprocess.run()
  - Handle command output capture and error checking
  - _Requirements: 13.2, 13.3_

- [x] 3.3 Write tests for dockutil command wrapper
  - Write tests for check_installed() with mocked executor
  - Write tests for list_apps() parsing dockutil output
  - Write tests for add_app() command generation
  - Write tests for remove_app() command generation
  - Write tests for remove_all() command generation
  - _Requirements: 13.2, 13.3_

- [x] 3.4 Implement dockutil wrapper to pass tests
  - Create DockutilCommand class with CommandExecutor dependency injection
  - Implement check_installed() to verify dockutil is available
  - Implement list_apps() to parse dockutil output
  - Implement add_app() to add applications to dock
  - Implement remove_app() to remove applications from dock
  - Implement remove_all() to clear all dock apps
  - _Requirements: 2.1, 2.2, 7.1, 9.2, 10.1_

- [x] 3.5 Write tests for plist manager
  - Write tests for read_plist() and write_plist() with temporary files
  - Write tests for read_value() and write_value()
  - Write tests for read_autohide() and write_autohide()
  - Write tests for read_autohide_delay() and write_autohide_delay()
  - Write tests for file I/O error handling
  - _Requirements: 13.2, 13.3_

- [x] 3.6 Implement plist manager to pass tests
  - Create PlistManager class with read_plist() and write_plist() methods
  - Implement read_value() and write_value() for generic plist access
  - Implement read_autohide() and write_autohide() for autohide setting
  - Implement read_autohide_delay() and write_autohide_delay() for delay setting
  - Handle file I/O errors gracefully
  - _Requirements: 3.1, 3.2, 3.3, 9.3_

- [x] 4. Implement dock state reading and comparison with TDD
- [x] 4.1 Write tests for dock state reader
  - Write tests for read_current_apps() with mocked dockutil
  - Write tests for read_current_settings() with mocked plist manager
  - Write tests for read_current_downloads() with mocked plist manager
  - Write tests for read_full_state() returning complete DockConfig
  - _Requirements: 13.1_

- [x] 4.2 Implement dock state reader to pass tests
  - Create DockStateReader class with dockutil and plist manager dependencies
  - Implement read_current_apps() to get current dock applications
  - Implement read_current_settings() to get current settings from plist
  - Implement read_current_downloads() to get downloads tile configuration
  - Implement read_full_state() to return complete DockConfig
  - _Requirements: 5.2, 9.1, 12.1, 12.3_

- [x] 4.3 Write tests for diff calculator
  - Write tests for app additions, removals, and reordering scenarios
  - Write tests for setting changes detection
  - Write tests for downloads tile changes
  - Write tests for no changes scenario
  - Write tests for has_changes() method
  - _Requirements: 13.1_

- [x] 4.4 Implement diff calculator to pass tests
  - Create AppChange, SettingChange, and DockDiff dataclasses
  - Create DiffCalculator.calculate_diff() to compare desired vs current state
  - Implement _calculate_app_changes() to determine additions, removals, and reordering
  - Implement setting comparison logic
  - Implement downloads tile comparison logic
  - Add has_changes() method to DockDiff
  - _Requirements: 5.1, 5.2, 12.1, 12.2, 12.3, 12.4_

- [x] 5. Implement dock executor with TDD
- [x] 5.1 Write tests for dock executor
  - Write tests for apply_diff() with mocked dependencies
  - Write tests for _apply_app_changes() command execution
  - Write tests for _apply_setting_changes() plist modifications
  - Write tests for _restart_dock() only when changes made
  - Write tests for dry-run mode (no actual execution)
  - _Requirements: 13.2_

- [x] 5.2 Implement dock executor to pass tests
  - Create DockExecutor class with dockutil, plist manager, and dry_run flag
  - Implement apply_diff() method to orchestrate all changes
  - Implement _apply_app_changes() to add/remove apps via dockutil
  - Implement _apply_setting_changes() to modify plist values
  - Implement _restart_dock() to restart Dock process using killall
  - Only restart dock when changes were actually made
  - Display planned changes without executing commands when dry_run=True
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 5.3, 5.4, 8.1, 8.2, 8.3, 8.4, 8.5, 12.2, 12.4, 12.5_

- [x] 6. Implement utility modules with TDD
- [x] 6.1 Write tests for platform detection
  - Write tests for is_macos() on different platforms
  - Write tests for require_macos() raising error on non-macOS
  - _Requirements: 13.1_

- [x] 6.2 Implement platform detection to pass tests
  - Create is_macos() function to check platform
  - Create require_macos() function to raise error if not on macOS
  - _Requirements: 7.4_

- [x] 6.3 Write tests for output formatting helpers
  - Write tests for colored output functions
  - Write tests for print_diff() formatting
  - _Requirements: 13.1_

- [x] 6.4 Implement output helpers to pass tests
  - Create print_success(), print_error(), print_warning(), print_info() functions
  - Create print_diff() function to display DockDiff in readable format
  - Use click.secho for colored output
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. Implement CLI commands with integration tests
- [x] 7.1 Write integration tests for reset command
  - Write tests for reset with valid config file
  - Write tests for reset with --dry-run flag
  - Write tests for reset with --profile option
  - Write tests for config discovery order
  - Write tests for error scenarios (missing dockutil, invalid config, etc.)
  - _Requirements: 13.1, 13.5_

- [x] 7.2 Implement reset command to pass tests
  - Create cli() group with version option
  - Create reset() command with --file, --profile, and --dry-run options
  - Implement config loading, validation, state reading, diff calculation, and execution
  - Add platform check at start of command
  - Display clear output about changes being made
  - Handle errors gracefully with appropriate exit codes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 5.1, 6.1, 6.5, 7.1, 7.2, 7.3, 7.5, 2.5, 8.1_

- [x] 7.3 Write integration tests for backup command
  - Write tests for backup with --file option
  - Write tests for YAML output format
  - Write tests for omitting default values
  - Write tests for error scenarios
  - _Requirements: 13.1, 13.5_

- [x] 7.4 Implement backup command to pass tests
  - Create backup() command with required --file option
  - Read current dock state using DockStateReader
  - Format state as YAML using PyYAML
  - Omit default values to keep output minimal
  - Write YAML to specified file path
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 7.5 Write integration tests for show command
  - Write tests for show command output format
  - Write tests for error scenarios
  - _Requirements: 13.1, 13.5_

- [x] 7.6 Implement show command to pass tests
  - Create show() command with no options
  - Read current apps using dockutil
  - Display app names in simple list format
  - Exit with status code 0
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 7.7 Write integration tests for validate command
  - Write tests for validate with valid config
  - Write tests for validate with invalid config
  - Write tests for validation warnings
  - Write tests for --profile option
  - _Requirements: 13.1, 13.5_

- [x] 7.8 Implement validate command to pass tests
  - Create validate() command with --file and --profile options
  - Load configuration using ConfigLoader
  - Parse and validate using Pydantic models
  - Run ConfigValidator checks
  - Display success message or error details
  - Exit with appropriate status code
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 8. Create entry points and packaging
- [x] 8.1 Set up package entry point
  - Create __main__.py for python -m dock support
  - Configure [project.scripts] in pyproject.toml for dock command
  - Test that dock command works after installation
  - _Requirements: 15.4_

- [x] 8.2 Generate shell completions
  - Create completions/ directory
  - Generate Bash completion file using Click's completion support
  - Generate Zsh completion file using Click's completion support
  - Add completions generation to Makefile
  - Test completions work in both shells
  - _Requirements: 15.3_

- [x] 9. Set up CI/CD with GitHub Actions
- [x] 9.1 Create CI workflow
  - Write .github/workflows/ci.yml
  - Set up uv with astral-sh/setup-uv action
  - Run linting with ruff
  - Run type checking with mypy
  - Run tests with pytest
  - Build package with uv build
  - Run on push and pull_request events
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 9.2 Create release workflow
  - Write .github/workflows/release.yml
  - Trigger on version tags (v*)
  - Run full CI checks
  - Build distribution packages
  - Create GitHub release with artifacts
  - _Requirements: 14.5_

- [x] 10. Create Homebrew formula
- [x] 10.1 Write Homebrew formula for tap
  - Create formula file for jamessawle/homebrew-tap
  - Specify dockutil as dependency
  - Use virtualenv_install_with_resources for Python dependencies
  - Include completion file installation
  - Add test block to verify installation
  - Test formula installation locally
  - _Requirements: 15.1, 15.2, 15.5_

- [x] 11. Write documentation
- [x] 11.1 Create comprehensive README
  - Document installation via Homebrew
  - Explain configuration file format with examples
  - Document all commands (reset, backup, show, validate)
  - Explain config discovery order
  - Provide troubleshooting section
  - Include development setup instructions
  - _Requirements: 15.3_
