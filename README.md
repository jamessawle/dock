# dock — macOS Dock Manager

Minimal, predictable Dock management from a YAML config. Dry-run shows the exact `dockutil` commands that would run.

> **macOS only.** Requires `dockutil >= 3.0.0` and `yq >= 4.0.0`.

## Install

### Homebrew (recommended)

    brew tap jamessawle/tap
    brew install dock

Homebrew installs Bash and Zsh completions automatically. Open a new shell (or run `compinit`) to pick them up.

### Manual

    # Dependencies
    brew install dockutil yq

    # Install the script
    curl -fsSL https://raw.githubusercontent.com/jamessawle/dock/v0.1.0/dock -o /usr/local/bin/dock
    chmod +x /usr/local/bin/dock

Grab completions manually when not using Homebrew:

```bash
# Bash
curl -fsSL https://raw.githubusercontent.com/jamessawle/dock/main/completions/dock.bash -o /usr/local/etc/bash_completion.d/dock

# Zsh
curl -fsSL https://raw.githubusercontent.com/jamessawle/dock/main/completions/_dock -o ~/.zfunc/_dock
echo 'fpath=(~/.zfunc $fpath)' >> ~/.zshrc   # once
```

## Quick start

Create a config:

    # ~/.config/dock/config.yml
    apps:
      - Google Chrome
      - "Visual Studio Code"
      - "System Settings"
    downloads:
      preset: classic      # classic | fan | list
      path: "~/Downloads"
      section: others      # apps-left | apps-right | others

Then:

    dock validate
    dock --dry-run reset    # preview exact dockutil commands
    dock reset              # apply changes

## Commands

    reset     Reset Dock from a config file (or via discovery)
    show      Print current Dock app names (apps section)
    validate  Validate config and print the planned actions; no changes
    backup    Write current Dock as YAML (requires --file)

### Common options

    --dry-run          Show what would be done without changes
    --file, -f PATH    Config to use (reset/validate) or write (backup)
    --profile NAME     Use ~/.config/dock/profiles/NAME.(yml|yaml) if --file not set
    --version          Print version
    -h, --help         Show help

## Config discovery

When `--file` isn’t provided, discovery checks—in order:

1. `$DOCK_CONFIG` (if set and points to a file)  
2. `--profile NAME` → `~/.config/dock/profiles/NAME.yml|yaml`  
3. Standard locations:
   - `~/.config/dock/config.yml|yaml`
   - `/etc/dock/config.yml|yaml`

## Downloads tile

Configure the “Downloads” stack or turn it off:

    downloads: off
    # or
    downloads:
      preset: classic|fan|list
      path: "~/Downloads"
      section: apps-left|apps-right|others

## Examples

Preview then apply a profile:

    dock --profile work validate
    dock --profile work --dry-run reset
    dock --profile work reset

Backup current Dock to YAML:

    dock backup --file ~/.config/dock/snapshots/$(hostname)-dock.yml

Show current Dock apps:

    dock show

## Development

Install local Git hooks so commits run the full CI check:

    make hooks

The pre-commit hook runs `make ci` and stops the commit if formatting, linting, or tests fail. Set `SKIP_MAKE_CI=1` when committing to bypass the check in exceptional cases.

## Requirements

- macOS
- `dockutil >= 3.0.0` (Homebrew: `brew install dockutil`)
- `yq >= 4.0.0` (Homebrew: `brew install yq`)

## Versioning & releases

Tag versions in the script repo:

    git tag v0.1.0
    git push origin v0.1.0

Your Homebrew formula will point to the tag archive and a fixed `sha256`.

## Troubleshooting

- **“dockutil missing” / “yq missing”** → `brew install dockutil yq`
- **“dockutil >= 3.0.0 required”** → `brew upgrade dockutil`
- **No config found** → pass `--file`, use `--profile`, or create `~/.config/dock/config.yml`
- **Nothing happens** → try without `--dry-run`, or run `killall Dock`

## License

MIT — see [LICENSE](./LICENSE).  
Add an SPDX header to the script if you like:

    # SPDX-License-Identifier: MIT
