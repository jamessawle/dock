#!/bin/bash
# Script to help update the Homebrew formula with a new version

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"
URL="https://github.com/jamessawle/dock/archive/refs/tags/${TAG}.tar.gz"

echo "Calculating SHA256 for version ${VERSION}..."
echo "URL: ${URL}"
echo ""

# Download and calculate SHA256
SHA256=$(curl -sL "${URL}" | shasum -a 256 | cut -d' ' -f1)

if [ -z "$SHA256" ]; then
    echo "Error: Failed to calculate SHA256. Make sure the release exists on GitHub."
    exit 1
fi

echo "SHA256: ${SHA256}"
echo ""
echo "Update Formula/dock.rb with:"
echo "  url \"${URL}\""
echo "  sha256 \"${SHA256}\""
echo ""

# Optionally update the formula file automatically
read -p "Update Formula/dock.rb automatically? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -f "Formula/dock.rb" ]; then
        echo "Error: Formula/dock.rb not found"
        exit 1
    fi
    
    # Create backup
    cp Formula/dock.rb Formula/dock.rb.bak
    
    # Update version and SHA256
    sed -i.tmp "s|url \".*\"|url \"${URL}\"|" Formula/dock.rb
    sed -i.tmp "s|sha256 \".*\"|sha256 \"${SHA256}\"|" Formula/dock.rb
    rm Formula/dock.rb.tmp
    
    echo "Formula updated successfully!"
    echo "Backup saved to Formula/dock.rb.bak"
    echo ""
    echo "Next steps:"
    echo "1. Review the changes: git diff Formula/dock.rb"
    echo "2. Test locally: brew install --build-from-source ./Formula/dock.rb"
    echo "3. Run tests: brew test dock"
    echo "4. Copy to tap repo: cp Formula/dock.rb /path/to/homebrew-tap/Formula/"
fi
