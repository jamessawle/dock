# Requirements Document

## Introduction

This document specifies the requirements for `dock`, a CLI tool that enables users to declaratively manage their macOS Dock settings through a YAML configuration file. The tool provides a unified interface for controlling both Dock applications (via dockutil) and Dock system preferences (via PlistBuddy).

## Glossary

- **dock**: The CLI tool that reads configuration files and applies dock settings
- **Configuration_File**: A YAML file containing dock application names and system preference settings
- **Dock_Application**: An application name that appears in the macOS Dock apps section
- **Dock_Settings**: System-level settings for the Dock (e.g., autohide, autohide_delay)
- **Downloads_Tile**: The Downloads stack configuration in the Dock
- **dockutil**: External command-line utility for managing Dock applications
- **PlistBuddy**: macOS built-in utility for reading and writing property list files
- **Dock_State**: The current configuration of applications and preferences in the macOS Dock
- **reset_command**: The command that reads a Configuration_File and applies settings to the Dock
- **backup_command**: The command that reads the current Dock_State and outputs a Configuration_File
- **show_command**: The command that displays current Dock application names
- **validate_command**: The command that validates a Configuration_File without applying changes

## Configuration File Structure

The Configuration_File SHALL use YAML format with the following structure:

```yaml
apps:
  - Google Chrome
  - "Visual Studio Code"
  - "System Settings"

downloads:
  preset: classic      # classic | fan | list
  path: "~/Downloads"
  section: others      # apps-left | apps-right | others
  # or: downloads: off

settings:
  autohide: true       # true | false
  autohide_delay: 0.15 # seconds; rounded to 2 decimals
```

## Command Structure

The dock tool SHALL support the following commands:

1. **reset**: Apply configuration from a file to the Dock
   - Usage: `dock reset [--file PATH] [--profile NAME] [--dry-run]`
   - Config discovery order: `$DOCK_CONFIG` env var, `--profile NAME` (uses `~/.config/dock/profiles/NAME.yml`), `~/.config/dock/config.yml`, `/etc/dock/config.yml`

2. **backup**: Export current Dock configuration to a file
   - Usage: `dock backup --file PATH`
   - Writes current Dock state as YAML to specified file

3. **show**: Display current Dock app names
   - Usage: `dock show`
   - Prints list of current apps in the Dock

4. **validate**: Validate configuration file
   - Usage: `dock validate [--file PATH] [--profile NAME]`
   - Checks config syntax and structure without making changes

## Requirements

### Requirement 1

**User Story:** As a macOS user, I want to define my Dock configuration in a YAML file, so that I can version control and reproduce my Dock setup across machines

#### Acceptance Criteria

1. WHEN the user invokes the reset_command, THE dock tool SHALL read a YAML Configuration_File using config discovery
2. THE dock tool SHALL check for Configuration_File in the following order: `$DOCK_CONFIG` environment variable, `--profile NAME` path, `~/.config/dock/config.yml`, `/etc/dock/config.yml`
3. WHEN the user provides the --file option, THE dock tool SHALL use that path instead of config discovery
4. WHEN the user provides the --profile option, THE dock tool SHALL use `~/.config/dock/profiles/NAME.yml` or `~/.config/dock/profiles/NAME.yaml`
5. WHEN the Configuration_File contains syntax errors, THE dock tool SHALL display a descriptive error message and exit with a non-zero status code

### Requirement 2

**User Story:** As a macOS user, I want to specify which applications appear in my Dock using simple app names, so that I can maintain a consistent set of applications

#### Acceptance Criteria

1. WHEN the reset_command is invoked, THE dock tool SHALL invoke dockutil to add Dock_Applications specified in the apps section of the Configuration_File
2. THE dock tool SHALL invoke dockutil to remove Dock_Applications not specified in the apps section
3. THE dock tool SHALL preserve the order of Dock_Applications as defined in the apps section
4. THE dock tool SHALL accept application names as strings in the apps list (e.g., "Google Chrome", "Visual Studio Code")
5. WHEN a specified Dock_Application cannot be found, THE dock tool SHALL log a warning and continue processing remaining applications

### Requirement 3

**User Story:** As a macOS user, I want to configure Dock system settings through the same configuration file, so that I can manage all Dock settings in one place

#### Acceptance Criteria

1. WHEN the reset_command is invoked, THE dock tool SHALL invoke PlistBuddy to modify Dock_Settings in the com.apple.dock plist file
2. THE dock tool SHALL support configuration of autohide setting with boolean values in the settings section
3. THE dock tool SHALL support configuration of autohide_delay setting with numeric values rounded to 2 decimals in the settings section
4. WHEN the settings section is omitted, THE dock tool SHALL use default values (autohide: false, autohide_delay: 0)
5. WHEN a Dock_Settings value is invalid, THE dock tool SHALL display an error message and skip that setting while continuing with others

### Requirement 4

**User Story:** As a macOS user, I want to configure the Downloads tile in my Dock, so that I can customize or disable it

#### Acceptance Criteria

1. WHEN the reset_command is invoked, THE dock tool SHALL configure the Downloads_Tile based on the downloads section
2. THE dock tool SHALL support setting downloads to "off" to disable the Downloads_Tile
3. THE dock tool SHALL support configuring Downloads_Tile preset with values classic, fan, or list
4. THE dock tool SHALL support configuring Downloads_Tile path as a string
5. THE dock tool SHALL support configuring Downloads_Tile section with values apps-left, apps-right, or others

### Requirement 5

**User Story:** As a macOS user, I want the tool to apply my configuration idempotently, so that I can run it multiple times without unintended side effects

#### Acceptance Criteria

1. WHEN the current Dock_State matches the Configuration_File, THE dock tool SHALL make no changes to the Dock
2. THE dock tool SHALL detect differences between the current Dock_State and the Configuration_File before making changes
3. THE dock tool SHALL only invoke dockutil and PlistBuddy commands when changes are necessary
4. THE dock tool SHALL restart the Dock process only when changes have been applied

### Requirement 6

**User Story:** As a macOS user, I want clear feedback about what changes are being made, so that I can understand what the tool is doing

#### Acceptance Criteria

1. THE dock tool SHALL display a summary of planned changes before applying them
2. WHEN adding a Dock_Application, THE dock tool SHALL log the application name
3. WHEN removing a Dock_Application, THE dock tool SHALL log the application name
4. WHEN modifying Dock_Settings, THE dock tool SHALL log the setting name and new value
5. WHEN all operations complete successfully, THE dock tool SHALL display a success message and exit with status code 0

### Requirement 7

**User Story:** As a macOS user, I want to handle errors gracefully, so that I can understand and fix configuration issues

#### Acceptance Criteria

1. WHEN dockutil is not installed, THE dock tool SHALL display an error message with installation instructions and exit with a non-zero status code
2. WHEN PlistBuddy commands fail, THE dock tool SHALL log the error and continue with remaining operations
3. WHEN the Configuration_File cannot be read, THE dock tool SHALL display a descriptive error message and exit with a non-zero status code
4. THE dock tool SHALL validate that it is running on macOS before attempting any operations
5. WHEN insufficient permissions prevent Dock modifications, THE dock tool SHALL display an appropriate error message

### Requirement 8

**User Story:** As a macOS user, I want to preview changes before applying them, so that I can verify the tool will do what I expect

#### Acceptance Criteria

1. WHEN the user invokes the reset_command with the --dry-run flag, THE dock tool SHALL display all planned changes without modifying the Dock_State
2. THE dock tool SHALL show which Dock_Applications would be added in dry-run mode
3. THE dock tool SHALL show which Dock_Applications would be removed in dry-run mode
4. THE dock tool SHALL show which Dock_Settings would be modified in dry-run mode
5. WHEN running in dry-run mode, THE dock tool SHALL exit with status code 0 without invoking dockutil or PlistBuddy

### Requirement 9

**User Story:** As a macOS user, I want to export my current Dock configuration to a file, so that I can capture my current setup or migrate to a new machine

#### Acceptance Criteria

1. WHEN the user invokes the backup_command with the --file option, THE dock tool SHALL read the current Dock_State
2. THE dock tool SHALL query dockutil to retrieve the list of current Dock_Applications
3. THE dock tool SHALL query PlistBuddy to retrieve current Dock_Settings values
4. THE dock tool SHALL format the current Dock_State as a valid YAML Configuration_File
5. THE dock tool SHALL write the YAML Configuration_File to the path specified by the --file option
6. THE dock tool SHALL omit default values from the output to keep configs minimal

### Requirement 10

**User Story:** As a macOS user, I want to view my current Dock apps, so that I can see what is currently configured

#### Acceptance Criteria

1. WHEN the user invokes the show_command, THE dock tool SHALL query dockutil to retrieve the list of current Dock_Applications
2. THE dock tool SHALL display the application names in the apps section format
3. THE dock tool SHALL exit with status code 0 after displaying the list

### Requirement 11

**User Story:** As a macOS user, I want to validate my configuration file, so that I can check for errors before applying changes

#### Acceptance Criteria

1. WHEN the user invokes the validate_command, THE dock tool SHALL read and parse the Configuration_File
2. THE dock tool SHALL check the YAML syntax and structure
3. THE dock tool SHALL validate that all required fields are present
4. WHEN validation succeeds, THE dock tool SHALL display a success message and exit with status code 0
5. WHEN validation fails, THE dock tool SHALL display descriptive error messages and exit with a non-zero status code

### Requirement 12

**User Story:** As a macOS user, I want the tool to minimize unnecessary Dock restarts, so that I can avoid screen flicker and interruptions

#### Acceptance Criteria

1. THE dock tool SHALL compare each Dock_Application in the Configuration_File with the current Dock_State
2. THE dock tool SHALL only add or remove Dock_Applications that differ from the current Dock_State
3. THE dock tool SHALL compare each Dock_Settings value in the Configuration_File with the current value in the plist
4. THE dock tool SHALL only modify Dock_Settings values that differ from the current values
5. WHEN no changes are required, THE dock tool SHALL not restart the Dock process

### Requirement 13

**User Story:** As a developer, I want the tool to have a testable architecture, so that I can verify functionality and prevent regressions

#### Acceptance Criteria

1. THE dock tool SHALL separate configuration parsing logic from system command execution
2. THE dock tool SHALL use dependency injection or similar patterns to allow mocking of external command execution
3. THE dock tool SHALL provide interfaces or abstractions for dockutil and PlistBuddy interactions
4. THE dock tool SHALL validate configuration data independently from applying changes
5. THE dock tool SHALL structure code into modules with clear responsibilities (configuration, validation, execution, output)

### Requirement 14

**User Story:** As a developer, I want automated CI/CD processes, so that I can ensure code quality and streamline releases

#### Acceptance Criteria

1. THE dock tool repository SHALL include a GitHub Actions workflow for continuous integration
2. THE GitHub Actions workflow SHALL run tests on each pull request
3. THE GitHub Actions workflow SHALL run linting and type checking on each pull request
4. THE GitHub Actions workflow SHALL build the tool on each pull request
5. THE dock tool repository SHALL include a GitHub Actions workflow for releasing new versions

### Requirement 15

**User Story:** As a macOS user, I want to install the tool via Homebrew, so that I can easily manage installation and updates

#### Acceptance Criteria

1. THE dock tool SHALL be packaged for distribution via Homebrew
2. THE dock tool SHALL be published to the tap at https://github.com/jamessawle/homebrew-tap
3. THE dock tool repository SHALL include documentation for installing via Homebrew
4. THE dock tool SHALL include version information accessible via a --version flag
5. THE Homebrew formula SHALL specify dockutil as a dependency
