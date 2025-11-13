# Homebrew Formula for dock

This directory contains the Homebrew formula for the `dock` CLI tool.

## Automated Publishing

The formula is **automatically updated** when you push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will handle:
- Calculating the SHA256 hash
- Updating the formula
- Publishing to [jamessawle/homebrew-tap](https://github.com/jamessawle/homebrew-tap)

## Testing Locally

Test the formula before releasing:

```bash
# Run the test script
./scripts/test-formula.sh

# Or manually
brew install --build-from-source ./Formula/dock.rb
brew test dock
dock --version
brew uninstall dock
```

## Manual Updates

If you need to update the formula manually:

```bash
# Calculate SHA256 and update formula
./scripts/update-formula.sh 1.0.0

# Test locally
./scripts/test-formula.sh

# Copy to tap repository
cp Formula/dock.rb /path/to/homebrew-tap/Formula/dock.rb
```

## Documentation

- **[PUBLISHING_CHECKLIST.md](PUBLISHING_CHECKLIST.md)**: Step-by-step release checklist
- **[README.md](../README.md)**: Main project documentation with Homebrew section

## Formula Structure

The formula (`dock.rb`) includes:

- **Dependencies**: Python 3.11 and dockutil
- **Python Resources**: All required packages (click, pyyaml, pydantic, etc.)
- **Completions**: Pre-generated Bash and Zsh completions
- **Tests**: Verification that the tool installs and runs correctly

## Initial Setup (One-Time)

1. Create the tap repository on GitHub: `homebrew-tap`
2. Add `HOMEBREW_TAP_TOKEN` secret to this repository's settings
3. Copy the initial formula to the tap repository

See [HOMEBREW.md](../HOMEBREW.md) for detailed setup instructions.
