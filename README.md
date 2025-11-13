# dock

A declarative macOS Dock configuration manager. Define your Dock setup in a YAML file and apply it consistently across machines.

## Features

- **Declarative Configuration**: Define your Dock apps and settings in a simple YAML file
- **Version Control Friendly**: Keep your Dock configuration in Git alongside your dotfiles
- **Idempotent**: Only makes changes when necessary to minimize Dock restarts
- **Dry Run Mode**: Preview changes before applying them
- **Backup & Restore**: Export your current Dock configuration to a file
- **Profile Support**: Manage multiple Dock configurations for different contexts
- **Shell Completions**: Bash and Zsh completion support included

## Installation

### Via Homebrew (Recommended)

```bash
brew install jamessawle/tap/dock
```

This will automatically install `dockutil` as a dependency.

### From Source

```bash
git clone https://github.com/jamessawle/dock.git
cd dock
make install
uv run dock --version
```

## Quick Start

1. Create a configuration file:

```bash
mkdir -p ~/.config/dock
cat > ~/.config/dock/config.yml << 'EOF'
apps:
  - Safari
  - Mail
  - Calendar

settings:
  autohide: true
  autohide_delay: 0.5
EOF
```

2. Apply the configuration:

```bash
dock reset
```

3. Your Dock will now match the configuration!

## Configuration File Format

The configuration file uses YAML format with three main sections:

### Complete Example

```yaml
apps:
  - Google Chrome
  - "Visual Studio Code"
  - Terminal
  - Slack
  - "System Settings"

downloads:
  preset: fan        # Options: classic, fan, list
  path: "~/Downloads"
  section: others    # Options: apps-left, apps-right, others

settings:
  autohide: true
  autohide_delay: 0.15  # Seconds, rounded to 2 decimals
```

### Apps Section

List the applications you want in your Dock, in order:

```yaml
apps:
  - Safari
  - Mail
  - "Visual Studio Code"  # Use quotes for names with spaces
  - Terminal
```

- Apps are added in the order specified
- Use the application name as it appears in `/Applications`
- Quote names that contain spaces or special characters
- Apps not in the list will be removed from the Dock

### Downloads Section

Configure the Downloads stack tile:

```yaml
downloads:
  preset: fan           # Display style: classic, fan, or list
  path: "~/Downloads"   # Path to the folder
  section: others       # Position: apps-left, apps-right, or others
```

Or disable the Downloads tile entirely:

```yaml
downloads: off
```

If omitted, the Downloads tile is left unchanged.

### Settings Section

Configure Dock system preferences:

```yaml
settings:
  autohide: true         # Auto-hide the Dock
  autohide_delay: 0.15   # Delay before showing (seconds)
```

Both settings are optional and default to `false` and `0.0` respectively.

## Commands

### `dock reset`

Apply Dock configuration from a file.

```bash
# Use default config discovery
dock reset

# Use specific config file
dock reset --file ~/my-dock.yml

# Use a profile
dock reset --profile work

# Preview changes without applying
dock reset --dry-run
```

**Options:**
- `--file, -f PATH`: Path to configuration file
- `--profile NAME`: Use profile from `~/.config/dock/profiles/NAME.yml`
- `--dry-run`: Show what would change without applying

### `dock backup`

Export current Dock configuration to a file.

```bash
# Backup to a file
dock backup --file ~/my-dock-backup.yml
```

**Options:**
- `--file, -f PATH`: Output file path (required)

The backup includes your current apps, downloads tile configuration, and settings. Default values are omitted to keep the output minimal.

### `dock show`

Display current Dock applications.

```bash
dock show
```

Outputs a simple list of application names currently in your Dock.

### `dock validate`

Validate a configuration file without applying changes.

```bash
# Validate default config
dock validate

# Validate specific file
dock validate --file ~/my-dock.yml

# Validate a profile
dock validate --profile work
```

**Options:**
- `--file, -f PATH`: Path to configuration file
- `--profile NAME`: Validate profile from `~/.config/dock/profiles/NAME.yml`

Checks for:
- Valid YAML syntax
- Required fields present
- Valid enum values
- Duplicate app names
- Path existence (for downloads)

## Configuration Discovery

When you run `dock reset` or `dock validate` without `--file`, the tool searches for a configuration file in this order:

1. `$DOCK_CONFIG` environment variable
2. `--profile NAME` → `~/.config/dock/profiles/NAME.yml`
3. `~/.config/dock/config.yml`
4. `/etc/dock/config.yml`

The first file found is used.

### Using Profiles

Profiles let you maintain multiple Dock configurations:

```bash
# Create profiles directory
mkdir -p ~/.config/dock/profiles

# Create work profile
cat > ~/.config/dock/profiles/work.yml << 'EOF'
apps:
  - Slack
  - "Microsoft Teams"
  - "Visual Studio Code"
settings:
  autohide: false
EOF

# Create personal profile
cat > ~/.config/dock/profiles/personal.yml << 'EOF'
apps:
  - Safari
  - Mail
  - Music
settings:
  autohide: true
EOF

# Switch between profiles
dock reset --profile work
dock reset --profile personal
```

### Environment Variable

Set `DOCK_CONFIG` to always use a specific configuration:

```bash
export DOCK_CONFIG=~/dotfiles/dock.yml
dock reset
```

Add to your shell profile (`~/.zshrc` or `~/.bashrc`) to make it permanent.

## Troubleshooting

### "dockutil not found"

The tool requires `dockutil` to manage Dock applications.

**Solution:**
```bash
brew install dockutil
```

### "This tool requires macOS"

The tool only works on macOS as it manages the macOS Dock.

**Solution:** Run the tool on a macOS system.

### "Application not found" warnings

If an app name in your config doesn't match an installed application, you'll see a warning.

**Solution:**
- Check the exact name in `/Applications`
- Use quotes for names with spaces: `"Visual Studio Code"`
- Ensure the app is installed before running `dock reset`

### Changes not taking effect

The Dock should restart automatically after changes, but sometimes it needs a manual restart.

**Solution:**
```bash
killall Dock
```

### Permission errors

If you get permission errors when modifying the Dock plist:

**Solution:**
- Ensure you're running as your user (not root)
- Check that `~/Library/Preferences/com.apple.dock.plist` is writable
- Try: `chmod 644 ~/Library/Preferences/com.apple.dock.plist`

### Configuration validation fails

Use `dock validate` to check your configuration for errors:

```bash
dock validate --file ~/my-dock.yml
```

Common issues:
- Invalid YAML syntax (check indentation)
- Invalid enum values (check preset, section options)
- Duplicate app names
- Missing required fields

### Dry run shows unexpected changes

Use `--dry-run` to preview changes before applying:

```bash
dock reset --dry-run
```

This helps you verify the configuration will do what you expect.

## Examples

### Minimal Configuration

Just set the apps, use defaults for everything else:

```yaml
apps:
  - Safari
  - Mail
  - Calendar
```

### Auto-hide Dock with Fast Reveal

```yaml
apps:
  - Safari
  - Terminal

settings:
  autohide: true
  autohide_delay: 0.0  # Instant reveal
```

### Work Setup with Downloads Tile

```yaml
apps:
  - Slack
  - "Microsoft Teams"
  - "Visual Studio Code"
  - Terminal
  - "Google Chrome"

downloads:
  preset: list
  path: "~/Downloads"
  section: others

settings:
  autohide: false
```

### Minimal Dock (No Downloads Tile)

```yaml
apps:
  - Safari
  - Terminal

downloads: off

settings:
  autohide: true
  autohide_delay: 0.5
```

## Development

### Setup

Requirements:
- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

```bash
# Clone the repository
git clone https://github.com/jamessawle/dock.git
cd dock

# Install dependencies
make install

# Run the tool in development
uv run dock --version
```

### Development Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Run type checking
make type-check

# Format code
make format

# Run all CI checks (lint + type-check + test)
make ci

# Generate shell completions (automatically generated during release)
make completions
```

### Project Structure

```
dock/
├── dock/                    # Source code
│   ├── cli.py              # CLI commands
│   ├── config/             # Configuration loading and validation
│   ├── dock/               # Dock state and execution
│   ├── adapters/           # External command wrappers
│   ├── services/           # High-level service layer
│   └── utils/              # Utilities
├── tests/                   # Test suite
├── Formula/                 # Homebrew formula
├── completions/            # Shell completions
└── pyproject.toml          # Project configuration
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/config/test_loader.py -v

# Run with coverage
uv run pytest --cov=dock tests/
```

### Code Quality

The project uses:
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **pytest**: Testing framework

All checks run automatically in CI on pull requests.

## Homebrew Formula

The Homebrew formula is located in `Formula/dock.rb` and automatically published to [jamessawle/homebrew-tap](https://github.com/jamessawle/homebrew-tap).

### Releasing a New Version

The formula is automatically updated when you push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will:
- Run all CI checks
- Create a GitHub release
- Update the Homebrew formula with the new version
- Push the updated formula to the tap repository

### Testing the Formula Locally

```bash
# Test the formula before releasing
./scripts/test-formula.sh

# Or manually
brew install --build-from-source ./Formula/dock.rb
brew test dock
brew uninstall dock
```

See [Formula/PUBLISHING_CHECKLIST.md](Formula/PUBLISHING_CHECKLIST.md) for the complete release checklist.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make ci` to ensure all checks pass
5. Submit a pull request

## License

MIT
