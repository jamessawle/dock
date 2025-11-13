#!/bin/bash
# Script to test the Homebrew formula locally

set -e

FORMULA_PATH="Formula/dock.rb"

if [ ! -f "$FORMULA_PATH" ]; then
    echo "Error: Formula not found at $FORMULA_PATH"
    exit 1
fi

echo "Testing Homebrew formula for dock..."
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed"
    exit 1
fi

# Check if dockutil is installed (required dependency)
if ! brew list dockutil &> /dev/null; then
    echo "Warning: dockutil is not installed. Installing it first..."
    brew install dockutil
fi

echo "Step 1: Installing from local formula..."
brew install --build-from-source "./$FORMULA_PATH"

echo ""
echo "Step 2: Verifying installation..."

# Test that the command exists
if ! command -v dock &> /dev/null; then
    echo "Error: dock command not found after installation"
    exit 1
fi

# Test version flag
echo "Testing: dock --version"
dock --version

# Test help flag
echo ""
echo "Testing: dock --help"
dock --help | head -n 5

# Test completions are installed
echo ""
echo "Checking shell completions..."
BASH_COMPLETION="$(brew --prefix)/share/bash-completion/completions/dock"
ZSH_COMPLETION="$(brew --prefix)/share/zsh/site-functions/_dock"

if [ -f "$BASH_COMPLETION" ]; then
    echo "✓ Bash completion installed at $BASH_COMPLETION"
else
    echo "✗ Bash completion not found at $BASH_COMPLETION"
fi

if [ -f "$ZSH_COMPLETION" ]; then
    echo "✓ Zsh completion installed at $ZSH_COMPLETION"
else
    echo "✗ Zsh completion not found at $ZSH_COMPLETION"
fi

echo ""
echo "Step 3: Running formula test block..."
brew test dock

echo ""
echo "Step 4: Testing validate command..."
cat > /tmp/test-dock-config.yml << 'EOF'
apps:
  - Safari
  - Mail
settings:
  autohide: false
  autohide_delay: 0.0
EOF

dock validate --file /tmp/test-dock-config.yml

echo ""
echo "✓ All tests passed!"
echo ""
echo "To uninstall: brew uninstall dock"
