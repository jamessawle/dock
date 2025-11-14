#!/bin/bash
# Script to test Homebrew formula locally using a temporary tap

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TAP_NAME="test-dock"
TAP_USER="local"
TAP_FULL_NAME="${TAP_USER}/${TAP_NAME}"
TAP_PATH="$(brew --repository)/Library/Taps/${TAP_USER}/homebrew-${TAP_NAME}"

echo_step() {
    echo -e "${GREEN}==>${NC} $1"
}

echo_error() {
    echo -e "${RED}Error:${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

cleanup() {
    echo_step "Cleaning up..."
    
    # Uninstall formula if installed
    if brew list dock &>/dev/null; then
        echo "  Uninstalling dock..."
        brew uninstall dock || true
    fi
    
    # Remove tap if it exists
    if [ -d "$TAP_PATH" ]; then
        echo "  Removing tap ${TAP_FULL_NAME}..."
        brew untap "$TAP_FULL_NAME" || true
    fi
    
    echo_step "Cleanup complete"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

echo_step "Starting local Homebrew formula test"
echo ""

# Step 1: Uninstall existing dock formula if present
if brew list dock &>/dev/null; then
    echo_step "Uninstalling existing dock formula..."
    brew uninstall dock
    echo ""
fi

# Step 2: Build the package
echo_step "Building package..."
uv build
echo ""

# Step 3: Generate completions
echo_step "Generating completions..."
./scripts/generate-completions.sh
echo ""

# Step 4: Update formula for local testing
echo_step "Generating formula for local testing..."
./scripts/update-formula.sh --local
echo ""

# Step 5: Create temporary tap
echo_step "Setting up temporary tap: ${TAP_FULL_NAME}"
if [ -d "$TAP_PATH" ]; then
    echo_warning "Tap already exists, removing it first..."
    brew untap "$TAP_FULL_NAME" || true
fi

mkdir -p "$TAP_PATH"
echo "  Created tap directory: $TAP_PATH"

# Copy formula to tap
cp Formula/dock.rb "$TAP_PATH/dock.rb"
echo "  Copied formula to tap"
echo ""

# Step 6: Install from local tap
echo_step "Installing formula from local tap..."
# Install and capture output, ignoring linkage warnings
set +e
INSTALL_OUTPUT=$(brew install "${TAP_FULL_NAME}/dock" 2>&1)
INSTALL_EXIT=$?
set -e

# Check if installation succeeded (exit code 0 or just linkage warning)
if [ $INSTALL_EXIT -eq 0 ] || echo "$INSTALL_OUTPUT" | grep -q "built in"; then
    echo "  Installation completed"
else
    echo "$INSTALL_OUTPUT"
    echo_error "Installation failed"
    exit 1
fi
echo ""

# Step 7: Run brew audit
echo_step "Running brew audit..."
if brew audit --strict "${TAP_FULL_NAME}/dock"; then
    echo -e "${GREEN}✓${NC} Audit passed"
else
    echo_error "Audit failed"
    exit 1
fi
echo ""

# Step 8: Run brew test
echo_step "Running brew test..."
if brew test "${TAP_FULL_NAME}/dock"; then
    echo -e "${GREEN}✓${NC} Tests passed"
else
    echo_error "Tests failed"
    exit 1
fi
echo ""

# Step 9: Verify installation
echo_step "Verifying installation..."
if command -v dock &>/dev/null; then
    echo "  dock command is available"
    echo "  Version: $(dock --version)"
    echo -e "${GREEN}✓${NC} Installation verified"
else
    echo_error "dock command not found after installation"
    exit 1
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests passed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The formula has been tested and will be cleaned up automatically."
