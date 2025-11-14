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
FORMULA_NAME="dock-test"

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
    
    # Unlink test formula if linked
    if brew list "$FORMULA_NAME" &>/dev/null; then
        echo "  Unlinking ${FORMULA_NAME}..."
        brew unlink "$FORMULA_NAME" 2>/dev/null || true
        
        echo "  Uninstalling ${FORMULA_NAME}..."
        brew uninstall "$FORMULA_NAME" || true
    fi
    
    # Relink production dock if it exists
    if brew list dock &>/dev/null 2>&1; then
        echo "  Relinking production dock..."
        brew link dock 2>/dev/null || true
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
echo "  Testing as: ${FORMULA_NAME}"
echo ""

# Step 1: Build the package
echo_step "Building package..."
uv build
echo ""

# Step 2: Update formula for local testing
echo_step "Generating formula for local testing..."
./scripts/update-formula.sh --local
echo ""

# Step 3: Unlink production dock if installed
if brew list dock &>/dev/null 2>&1; then
    echo_step "Unlinking production dock to avoid conflicts..."
    brew unlink dock || true
    echo ""
fi

# Step 4: Create temporary tap
echo_step "Setting up temporary tap: ${TAP_FULL_NAME}"
if [ -d "$TAP_PATH" ]; then
    echo_warning "Tap already exists, removing it first..."
    brew untap "$TAP_FULL_NAME" || true
fi

mkdir -p "$TAP_PATH"
echo "  Created tap directory: $TAP_PATH"

# Copy formula to tap and rename class
cp Formula/dock.rb "$TAP_PATH/${FORMULA_NAME}.rb"
# Update the class name in the formula
sed -i.bak "s/class Dock </class DockTest </" "$TAP_PATH/${FORMULA_NAME}.rb"
rm "$TAP_PATH/${FORMULA_NAME}.rb.bak"
echo "  Copied formula to tap as ${FORMULA_NAME}.rb"
echo ""

# Step 5: Install from local tap
echo_step "Installing formula from local tap..."
# Install and show output in real-time
brew install "${TAP_FULL_NAME}/${FORMULA_NAME}"
echo ""

# Step 6: Link the test formula
echo_step "Linking test formula..."
if brew link "${FORMULA_NAME}"; then
    echo "  Linked successfully"
else
    echo_error "Link failed"
    exit 1
fi
echo ""

# Step 7: Run brew audit
echo_step "Running brew audit..."
if brew audit --strict "${TAP_FULL_NAME}/${FORMULA_NAME}"; then
    echo -e "${GREEN}✓${NC} Audit passed"
else
    echo_error "Audit failed"
    exit 1
fi
echo ""

# Step 8: Run brew test
echo_step "Running brew test..."
if brew test "${TAP_FULL_NAME}/${FORMULA_NAME}"; then
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
