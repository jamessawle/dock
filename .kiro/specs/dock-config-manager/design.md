# Design Document

## Overview

The `dock` tool is a Python-based CLI application that manages macOS Dock configuration through declarative YAML files. The tool provides a clean abstraction over `dockutil` (for managing dock apps) and Python's `plistlib` (for managing dock preferences), enabling users to version control their Dock setup and apply it consistently across machines.

### Technology Stack

- **Language**: Python 3.9+
- **Package Manager**: uv (for fast dependency management and Python version management)
- **CLI Framework**: Click (provides command routing, option parsing, and help generation)
- **YAML Parsing**: PyYAML (standard library for YAML handling)
- **Plist Handling**: plistlib (Python built-in for reading/writing plists)
- **Subprocess Management**: Python's built-in `subprocess` module (only for dockutil)
- **Testing**: pytest with pytest-mock for unit tests
- **Packaging**: setuptools with entry points for CLI installation
- **Type Checking**: mypy for static type analysis
- **Linting**: ruff for fast Python linting

### Design Principles

1. **Separation of Concerns**: Configuration parsing, validation, state comparison, and execution are separate modules
2. **Testability**: All external command execution is abstracted behind interfaces that can be mocked
3. **Idempotency**: Only apply changes when necessary to minimize Dock restarts
4. **Clear Feedback**: Provide detailed output about what changes will be or were made
5. **Error Resilience**: Handle errors gracefully and continue processing when possible

## Architecture

### Module Structure

```
dock/
├── __init__.py
├── __main__.py              # Entry point for python -m dock
├── cli.py                   # Click command definitions
├── config/
│   ├── __init__.py
│   ├── loader.py            # Config file discovery and loading
│   ├── models.py            # Pydantic models for config structure
│   └── validator.py         # Config validation logic
├── dock/
│   ├── __init__.py
│   ├── state.py             # Current dock state reading
│   ├── diff.py              # Comparing desired vs current state
│   └── executor.py          # Applying changes to dock
├── commands/
│   ├── __init__.py
│   ├── dockutil.py          # dockutil command wrapper
│   └── plist.py             # plist file reading/writing using plistlib
└── utils/
    ├── __init__.py
    ├── platform.py          # Platform detection
    └── output.py            # Formatted output helpers
```

### Data Flow

```
User Command
    ↓
CLI Layer (cli.py)
    ↓
Config Loader (config/loader.py) → Config Model (config/models.py)
    ↓
Validator (config/validator.py)
    ↓
State Reader (dock/state.py) → Current State
    ↓
Diff Calculator (dock/diff.py) → Change Set
    ↓
Executor (dock/executor.py) → Command Wrappers (commands/)
    ↓
System Commands (dockutil) / Plist Files (plistlib)
```

## Components and Interfaces

### 1. CLI Layer (`cli.py`)

The CLI layer uses Click to define commands and handle user input.

```python
@click.group()
@click.version_option()
def cli():
    """Manage macOS Dock from YAML configuration."""
    pass

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Config file path')
@click.option('--profile', help='Profile name from ~/.config/dock/profiles/')
@click.option('--dry-run', is_flag=True, help='Show changes without applying')
def reset(file, profile, dry_run):
    """Apply dock configuration from file."""
    pass

@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(), help='Output file path')
def backup(file):
    """Export current dock configuration to file."""
    pass

@cli.command()
def show():
    """Display current dock app names."""
    pass

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Config file path')
@click.option('--profile', help='Profile name from ~/.config/dock/profiles/')
def validate(file, profile):
    """Validate configuration file."""
    pass
```

### 2. Configuration Module (`config/`)

#### Config Loader (`config/loader.py`)

Handles config file discovery and loading.

```python
class ConfigLoader:
    """Loads configuration files with discovery logic."""
    
    @staticmethod
    def discover_config_path(file_path: Optional[str], profile: Optional[str]) -> Path:
        """
        Discover config file path using priority:
        1. Explicit --file path
        2. --profile NAME → ~/.config/dock/profiles/NAME.yml
        3. $DOCK_CONFIG environment variable
        4. ~/.config/dock/config.yml
        5. /etc/dock/config.yml
        """
        pass
    
    @staticmethod
    def load_config(path: Path) -> Dict[str, Any]:
        """Load and parse YAML config file."""
        pass
```

#### Config Models (`config/models.py`)

Uses Pydantic for data validation and type safety.

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Union

class DownloadsConfig(BaseModel):
    """Downloads tile configuration."""
    preset: Literal['classic', 'fan', 'list']
    path: str = "~/Downloads"
    section: Literal['apps-left', 'apps-right', 'others'] = 'others'

class SettingsConfig(BaseModel):
    """Dock settings configuration."""
    autohide: bool = False
    autohide_delay: float = Field(default=0.0, ge=0)
    
    @validator('autohide_delay')
    def round_delay(cls, v):
        """Round autohide_delay to 2 decimals."""
        return round(v, 2)

class DockConfig(BaseModel):
    """Complete dock configuration."""
    apps: List[str] = Field(default_factory=list)
    downloads: Union[Literal['off'], DownloadsConfig, None] = None
    settings: SettingsConfig = Field(default_factory=SettingsConfig)
```

#### Config Validator (`config/validator.py`)

Additional validation beyond Pydantic models.

```python
class ConfigValidator:
    """Validates configuration semantics."""
    
    @staticmethod
    def validate_config(config: DockConfig) -> List[str]:
        """
        Validate configuration and return list of warnings.
        - Check if app names are reasonable
        - Validate paths exist (for downloads)
        - Check for duplicate apps
        """
        pass
```

### 3. Dock State Module (`dock/`)

#### State Reader (`dock/state.py`)

Reads current Dock configuration.

```python
class DockStateReader:
    """Reads current dock state."""
    
    def __init__(self, dockutil_cmd: DockutilCommand, plist_mgr: PlistManager):
        self.dockutil = dockutil_cmd
        self.plist = plist_mgr
    
    def read_current_apps(self) -> List[str]:
        """Get list of current dock apps."""
        pass
    
    def read_current_settings(self) -> SettingsConfig:
        """Get current dock settings from plist."""
        pass
    
    def read_current_downloads(self) -> Optional[DownloadsConfig]:
        """Get current downloads tile configuration."""
        pass
    
    def read_full_state(self) -> DockConfig:
        """Read complete current dock state."""
        pass
```

#### Diff Calculator (`dock/diff.py`)

Compares desired and current state.

```python
@dataclass
class AppChange:
    """Represents a change to dock apps."""
    action: Literal['add', 'remove', 'reorder']
    app_name: str
    position: Optional[int] = None

@dataclass
class SettingChange:
    """Represents a change to dock settings."""
    setting_name: str
    old_value: Any
    new_value: Any

@dataclass
class DockDiff:
    """Complete set of changes needed."""
    app_changes: List[AppChange]
    setting_changes: List[SettingChange]
    downloads_change: Optional[DownloadsConfig]
    
    def has_changes(self) -> bool:
        """Check if any changes are needed."""
        return bool(self.app_changes or self.setting_changes or self.downloads_change)

class DiffCalculator:
    """Calculates differences between desired and current state."""
    
    @staticmethod
    def calculate_diff(desired: DockConfig, current: DockConfig) -> DockDiff:
        """Calculate what changes are needed."""
        pass
    
    @staticmethod
    def _calculate_app_changes(desired_apps: List[str], current_apps: List[str]) -> List[AppChange]:
        """Determine app additions, removals, and reordering."""
        pass
```

#### Executor (`dock/executor.py`)

Applies changes to the Dock.

```python
class DockExecutor:
    """Executes dock changes."""
    
    def __init__(self, dockutil_cmd: DockutilCommand, plist_mgr: PlistManager, dry_run: bool = False):
        self.dockutil = dockutil_cmd
        self.plist = plist_mgr
        self.dry_run = dry_run
    
    def apply_diff(self, diff: DockDiff) -> bool:
        """
        Apply changes from diff.
        Returns True if changes were made, False otherwise.
        """
        pass
    
    def _apply_app_changes(self, changes: List[AppChange]) -> None:
        """Apply app additions, removals, and reordering."""
        pass
    
    def _apply_setting_changes(self, changes: List[SettingChange]) -> None:
        """Apply settings changes via plistlib."""
        pass
    
    def _restart_dock(self) -> None:
        """Restart Dock process."""
        pass
```

### 4. Command Wrappers (`commands/`)

#### Dockutil Wrapper (`commands/dockutil.py`)

Abstracts dockutil command execution.

```python
class DockutilCommand:
    """Wrapper for dockutil commands."""
    
    def __init__(self, executor: Optional[CommandExecutor] = None):
        self.executor = executor or SubprocessExecutor()
    
    def check_installed(self) -> bool:
        """Check if dockutil is installed."""
        pass
    
    def list_apps(self) -> List[str]:
        """List current dock apps."""
        pass
    
    def add_app(self, app_name: str, position: Optional[int] = None) -> None:
        """Add app to dock."""
        pass
    
    def remove_app(self, app_name: str) -> None:
        """Remove app from dock."""
        pass
    
    def remove_all(self) -> None:
        """Remove all apps from dock."""
        pass
```

#### Plist Manager (`commands/plist.py`)

Manages dock plist file using Python's plistlib.

```python
import plistlib
from pathlib import Path
from typing import Any, Dict

class PlistManager:
    """Manages dock plist file operations."""
    
    DOCK_PLIST = Path.home() / "Library/Preferences/com.apple.dock.plist"
    
    def read_plist(self) -> Dict[str, Any]:
        """Read entire dock plist file."""
        with open(self.DOCK_PLIST, 'rb') as f:
            return plistlib.load(f)
    
    def write_plist(self, data: Dict[str, Any]) -> None:
        """Write entire dock plist file."""
        with open(self.DOCK_PLIST, 'wb') as f:
            plistlib.dump(data, f)
    
    def read_value(self, key: str, default: Any = None) -> Any:
        """Read specific value from dock plist."""
        plist = self.read_plist()
        return plist.get(key, default)
    
    def write_value(self, key: str, value: Any) -> None:
        """Write specific value to dock plist."""
        plist = self.read_plist()
        plist[key] = value
        self.write_plist(plist)
    
    def read_autohide(self) -> bool:
        """Read autohide setting."""
        return self.read_value('autohide', False)
    
    def write_autohide(self, enabled: bool) -> None:
        """Write autohide setting."""
        self.write_value('autohide', enabled)
    
    def read_autohide_delay(self) -> float:
        """Read autohide delay."""
        return self.read_value('autohide-delay', 0.0)
    
    def write_autohide_delay(self, delay: float) -> None:
        """Write autohide delay."""
        self.write_value('autohide-delay', delay)
```

#### Command Executor Interface (`commands/__init__.py`)

Abstraction for command execution (enables testing).

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class CommandExecutor(ABC):
    """Abstract interface for executing system commands."""
    
    @abstractmethod
    def execute(self, command: List[str], check: bool = True) -> str:
        """Execute command and return stdout."""
        pass

class SubprocessExecutor(CommandExecutor):
    """Real command executor using subprocess."""
    
    def execute(self, command: List[str], check: bool = True) -> str:
        """Execute command using subprocess."""
        import subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout
```

### 5. Utilities (`utils/`)

#### Platform Detection (`utils/platform.py`)

```python
def is_macos() -> bool:
    """Check if running on macOS."""
    import platform
    return platform.system() == 'Darwin'

def require_macos() -> None:
    """Raise error if not on macOS."""
    if not is_macos():
        raise RuntimeError("This tool requires macOS")
```

#### Output Helpers (`utils/output.py`)

```python
import click

def print_success(message: str) -> None:
    """Print success message in green."""
    click.secho(f"✓ {message}", fg='green')

def print_error(message: str) -> None:
    """Print error message in red."""
    click.secho(f"✗ {message}", fg='red', err=True)

def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    click.secho(f"⚠ {message}", fg='yellow')

def print_info(message: str) -> None:
    """Print info message."""
    click.echo(f"  {message}")

def print_diff(diff: DockDiff, dry_run: bool = False) -> None:
    """Print formatted diff output."""
    prefix = "[DRY RUN] " if dry_run else ""
    
    if diff.app_changes:
        click.echo(f"\n{prefix}App changes:")
        for change in diff.app_changes:
            if change.action == 'add':
                print_info(f"+ Add: {change.app_name}")
            elif change.action == 'remove':
                print_info(f"- Remove: {change.app_name}")
    
    if diff.setting_changes:
        click.echo(f"\n{prefix}Setting changes:")
        for change in diff.setting_changes:
            print_info(f"  {change.setting_name}: {change.old_value} → {change.new_value}")
```

## Data Models

### Configuration File Format

```yaml
apps:
  - Google Chrome
  - "Visual Studio Code"
  - "System Settings"

downloads:
  preset: classic
  path: "~/Downloads"
  section: others

settings:
  autohide: true
  autohide_delay: 0.15
```

### Internal State Representation

The `DockConfig` Pydantic model represents both the configuration file and the current dock state, enabling easy comparison.

## Error Handling

### Error Categories

1. **Configuration Errors**: Invalid YAML, missing required fields, invalid values
   - Action: Display clear error message and exit with code 1
   
2. **Dependency Errors**: dockutil not installed, wrong version
   - Action: Display installation instructions and exit with code 1
   
3. **Permission Errors**: Cannot modify dock plist
   - Action: Display error message suggesting permissions check
   
4. **Application Not Found**: App name in config doesn't exist
   - Action: Log warning and continue with other apps
   
5. **Command Execution Errors**: dockutil or PlistBuddy command fails
   - Action: Log error and continue with remaining operations when possible

### Error Handling Strategy

```python
class DockError(Exception):
    """Base exception for dock tool."""
    pass

class ConfigError(DockError):
    """Configuration-related errors."""
    pass

class DependencyError(DockError):
    """Missing or incompatible dependencies."""
    pass

class ExecutionError(DockError):
    """Command execution failures."""
    pass
```

## Testing Strategy

### Unit Tests

Test each module in isolation using mocks:

1. **Config Loading**: Test file discovery, YAML parsing, validation
2. **Plist Manager**: Test reading/writing plist files with temporary test files
3. **State Reading**: Mock dockutil output and plist data, verify parsing
4. **Diff Calculation**: Test various scenarios (additions, removals, reordering)
5. **Execution**: Mock command execution and plist operations, verify correct calls
6. **CLI**: Test command routing and option parsing

### Integration Tests

Test end-to-end flows with mocked system commands:

1. **Reset Command**: Load config → calculate diff → apply changes
2. **Backup Command**: Read state → format YAML → write file
3. **Validate Command**: Load config → validate → report errors
4. **Show Command**: Read apps → display list

### Test Fixtures

```python
# tests/fixtures/configs.py
VALID_CONFIG = """
apps:
  - Safari
  - Mail
settings:
  autohide: true
"""

INVALID_CONFIG = """
apps:
  - Safari
settings:
  autohide: "not a boolean"
"""

# tests/fixtures/dockutil_output.py
DOCKUTIL_LIST_OUTPUT = """
Safari
Mail
System Settings
"""
```

### Mocking Strategy

Use `pytest-mock` to mock command execution and file operations:

```python
def test_list_apps(mocker):
    mock_executor = mocker.Mock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Safari\nMail\n"
    
    dockutil = DockutilCommand(executor=mock_executor)
    apps = dockutil.list_apps()
    
    assert apps == ['Safari', 'Mail']
    mock_executor.execute.assert_called_once()

def test_read_autohide(tmp_path):
    # Create temporary plist file for testing
    test_plist = tmp_path / "com.apple.dock.plist"
    plist_data = {'autohide': True, 'autohide-delay': 0.5}
    with open(test_plist, 'wb') as f:
        plistlib.dump(plist_data, f)
    
    plist_mgr = PlistManager()
    plist_mgr.DOCK_PLIST = test_plist
    
    assert plist_mgr.read_autohide() is True
    assert plist_mgr.read_autohide_delay() == 0.5
```

## Packaging and Distribution

### Project Structure

```
dock/
├── pyproject.toml           # Project metadata and dependencies (uv format)
├── uv.lock                  # Locked dependencies
├── .python-version          # Python version for uv
├── README.md
├── LICENSE
├── Makefile                 # Common development tasks
├── completions/             # Pre-generated shell completions
│   ├── dock.bash
│   └── _dock
├── .github/
│   └── workflows/
│       ├── ci.yml           # Run tests, linting
│       └── release.yml      # Build and release
├── dock/                    # Source code
│   └── ...
└── tests/                   # Test suite
    └── ...
```

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "dock-cli"
version = "1.0.0"
description = "Manage macOS Dock from YAML configuration"
authors = [{name = "James Sawle"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.scripts]
dock = "dock.cli:cli"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "pytest-mock>=3.10",
    "mypy>=1.0",
    "ruff>=0.1.0",
    "types-pyyaml>=6.0",
]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
strict = true
```

### .python-version

```
3.11
```

### Makefile

```makefile
.PHONY: install test lint type-check format ci completions

install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check dock/ tests/

type-check:
	uv run mypy dock/

format:
	uv run ruff format dock/ tests/

ci: lint type-check test

completions:
	uv run _DOCK_COMPLETE=bash_source dock > completions/dock.bash
	uv run _DOCK_COMPLETE=zsh_source dock > completions/_dock
```

### Homebrew Formula

The formula will be published to `https://github.com/jamessawle/homebrew-tap`:

```ruby
class Dock < Formula
  include Language::Python::Virtualenv

  desc "Manage macOS Dock from YAML configuration"
  homepage "https://github.com/jamessawle/dock"
  url "https://github.com/jamessawle/dock/archive/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.11"
  depends_on "dockutil"

  resource "click" do
    url "https://files.pythonhosted.org/packages/..."
    sha256 "..."
  end

  # Additional resources...

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/dock", "--version"
  end
end
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync
      - name: Run linting
        run: uv run ruff check dock/ tests/
      - name: Run type checking
        run: uv run mypy dock/
      - name: Run tests
        run: uv run pytest tests/ -v
      - name: Build package
        run: uv build
```

#### Release Workflow (`.github/workflows/release.yml`)

Runs on version tags:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync
      - name: Run CI checks
        run: make ci
      - name: Build package
        run: uv build
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
      - name: Update Homebrew tap
        # Custom step to update formula in homebrew-tap repo
        run: |
          # Script to update formula with new version and SHA256
```

## Implementation Notes

### Handling App Names vs Paths

The tool accepts simple app names (e.g., "Google Chrome") rather than full paths. The implementation will:

1. Use dockutil's ability to find apps by name
2. Let dockutil handle the path resolution
3. If dockutil can't find an app, log a warning and continue

### Idempotency Implementation

To minimize Dock restarts:

1. Read current state before making changes
2. Calculate precise diff of what needs to change
3. Only execute commands for actual differences
4. Only restart Dock if changes were made

### Downloads Tile Handling

The downloads tile configuration maps to specific dockutil and plist commands:

- `preset`: Maps to view style in plist
- `path`: The folder path for the stack
- `section`: Position in dock (persistent-apps vs persistent-others)

### Settings Mapping

Settings map to plist keys in `~/Library/Preferences/com.apple.dock.plist`:

- `autohide` → `autohide` (boolean)
- `autohide_delay` → `autohide-delay` (float)

Python's `plistlib` handles the binary plist format automatically, reading and writing the file directly without needing external tools.

## Shell Completions

### Click Shell Completion

Click provides built-in shell completion support that needs to be activated by the user. The tool will support both Bash and Zsh completions.

#### Implementation

Add completion support to the CLI:

```python
# dock/cli.py
import click

# Enable shell completion
@click.group()
@click.version_option()
def cli():
    """Manage macOS Dock from YAML configuration."""
    pass
```

#### Installation Instructions

Users can enable completions with:

**Bash:**
```bash
_DOCK_COMPLETE=bash_source dock > ~/.dock-complete.bash
echo 'source ~/.dock-complete.bash' >> ~/.bashrc
```

**Zsh:**
```bash
_DOCK_COMPLETE=zsh_source dock > ~/.dock-complete.zsh
echo 'source ~/.dock-complete.zsh' >> ~/.zshrc
```

#### Homebrew Integration

The Homebrew formula will include completion files that are automatically installed:

```ruby
def install
  virtualenv_install_with_resources
  
  # Generate and install completions
  bash_completion.install "completions/dock.bash" => "dock"
  zsh_completion.install "completions/_dock"
end
```

We'll pre-generate completion files and include them in the repository:

```bash
# Generate completion files during development
_DOCK_COMPLETE=bash_source dock > completions/dock.bash
_DOCK_COMPLETE=zsh_source dock > completions/_dock
```

This matches the existing tool's approach where Homebrew installs completions automatically.

## Future Enhancements

Potential features for future versions:

1. Support for more dock preferences (magnification, tile size, position)
2. Support for spacers and special items
3. Backup/restore with timestamps
4. Diff command to compare config vs current state
5. Interactive mode for building configs
6. Dynamic completion for app names (complete from installed apps)
