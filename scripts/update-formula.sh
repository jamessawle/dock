#!/bin/bash
# Script to generate Formula/dock.rb from the template

set -e

# Parse arguments
RELEASE_MODE=false
LOCAL_MODE=false
if [[ "$1" == "--release" ]]; then
    RELEASE_MODE=true
elif [[ "$1" == "--local" ]]; then
    LOCAL_MODE=true
fi

echo "==> Generating Homebrew formula from template..."

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Version: $VERSION"

if [ "$LOCAL_MODE" = true ]; then
    # Local testing mode: build and use local tarball with file:// URL
    echo "Local testing mode: Building package for local testing..."
    uv build
    
    # Get the tarball path and calculate SHA256
    TARBALL_PATH="dist/dock_cli-${VERSION}.tar.gz"
    if [ ! -f "$TARBALL_PATH" ]; then
        echo "Error: Tarball not found at $TARBALL_PATH"
        exit 1
    fi
    
    SHA256=$(shasum -a 256 "$TARBALL_PATH" | cut -d' ' -f1)
    echo "SHA256: $SHA256"
    
    # Get absolute path for file:// URL
    TARBALL_ABSOLUTE_PATH="$(cd "$(dirname "$TARBALL_PATH")" && pwd)/$(basename "$TARBALL_PATH")"
    echo "Local tarball: $TARBALL_ABSOLUTE_PATH"
elif [ "$RELEASE_MODE" = true ]; then
    # Release mode: use GitHub release tarball
    echo "Release mode: Using GitHub release tarball"
    TARBALL_URL="https://github.com/jamessawle/dock/archive/refs/tags/v${VERSION}.tar.gz"
    
    echo "Waiting for release tarball to be available..."
    sleep 5
    for i in {1..12}; do
        if curl -f -I "$TARBALL_URL" > /dev/null 2>&1; then
            echo "Release tarball is available"
            break
        fi
        echo "Attempt $i: Tarball not yet available, waiting..."
        sleep 5
    done
    
    echo "Calculating SHA256 from GitHub release..."
    SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | cut -d' ' -f1)
    echo "SHA256: $SHA256"
else
    # Default mode: build and use local tarball
    echo "Default mode: Building package..."
    uv build
    
    # Get the tarball path and calculate SHA256
    TARBALL_PATH="dist/dock_cli-${VERSION}.tar.gz"
    if [ ! -f "$TARBALL_PATH" ]; then
        echo "Error: Tarball not found at $TARBALL_PATH"
        exit 1
    fi
    
    SHA256=$(shasum -a 256 "$TARBALL_PATH" | cut -d' ' -f1)
    echo "SHA256: $SHA256"
fi

# Get Python dependencies and their versions
echo "Fetching dependency information..."

# Build resource blocks from uv.lock
echo "Extracting dependencies from uv.lock..."

RESOURCES=$(python3 << 'PYTHON_SCRIPT'
import re

# Get direct dependencies from pyproject.toml
with open('pyproject.toml') as f:
    content = f.read()
    match = re.search(r'dependencies = \[(.*?)\]', content, re.DOTALL)
    direct_deps = set()
    if match:
        deps = re.findall(r'"([^"]+)"', match.group(1))
        for dep in deps:
            # Extract package name (remove version constraints)
            pkg_name = re.split(r'[>=<]', dep)[0]
            direct_deps.add(pkg_name.lower())

# Parse uv.lock to get all packages
with open('uv.lock') as f:
    content = f.read()
    
all_packages = {}
package_deps = {}
current_package = None
current_deps = []

for line in content.split('\n'):
    if line.startswith('[[package]]'):
        if current_package:
            package_deps[current_package['name'].lower()] = current_deps
        current_package = {}
        current_deps = []
    elif current_package is not None:
        if line.startswith('name = '):
            current_package['name'] = line.split('"')[1]
        elif line.startswith('version = '):
            current_package['version'] = line.split('"')[1]
        elif 'sdist = {' in line:
            # Extract URL and hash from sdist line
            url_match = re.search(r'url = "([^"]+)"', line)
            hash_match = re.search(r'hash = "sha256:([^"]+)"', line)
            if url_match and hash_match:
                current_package['url'] = url_match.group(1)
                current_package['sha256'] = hash_match.group(1)
                all_packages[current_package['name'].lower()] = current_package
        elif line.strip().startswith('{ name = ') and 'dependencies' in content[max(0, content.find(line)-200):content.find(line)]:
            # This is a dependency line
            dep_name = re.search(r'name = "([^"]+)"', line)
            if dep_name:
                current_deps.append(dep_name.group(1).lower())

if current_package:
    package_deps[current_package['name'].lower()] = current_deps

# Find all runtime dependencies (direct + transitive, excluding dev)
def get_all_deps(pkg_name, visited=None):
    if visited is None:
        visited = set()
    if pkg_name in visited or pkg_name == 'dock-cli':
        return visited
    visited.add(pkg_name)
    for dep in package_deps.get(pkg_name, []):
        get_all_deps(dep, visited)
    return visited

runtime_deps = set()
for dep in direct_deps:
    runtime_deps.update(get_all_deps(dep))

# Generate resource blocks for runtime dependencies only
packages = {name: all_packages[name] for name in runtime_deps if name in all_packages}

resources = ""
for name in sorted(packages.keys()):
    pkg = packages[name]
    resources += f'  resource "{name}" do\n'
    resources += f'    url "{pkg["url"]}"\n'
    resources += f'    sha256 "{pkg["sha256"]}"\n'
    resources += f'  end\n\n'

print(resources, end='')
PYTHON_SCRIPT
)

echo "Found $(echo "$RESOURCES" | grep -c 'resource') dependencies"

# Copy template to Formula/dock.rb
cp Formula/dock.rb.tmpl Formula/dock.rb

# Get current directory for local mode
REPO_PATH="$(pwd)"

# Replace placeholders
sed -i.bak "s/PLACEHOLDER_VERSION_UPDATE_BEFORE_PUBLISHING/${VERSION}/g" Formula/dock.rb

if [ "$LOCAL_MODE" = true ]; then
    # For local testing, use file:// URL to local tarball
    sed -i.bak "s|PLACEHOLDER_URL_LINE|url \"file://${TARBALL_ABSOLUTE_PATH}\"|g" Formula/dock.rb
    sed -i.bak "s|PLACEHOLDER_SHA256_LINE|sha256 \"${SHA256}\"|g" Formula/dock.rb
    sed -i.bak "s|PLACEHOLDER_HEAD_LINE|head \"https://github.com/jamessawle/dock.git\", branch: \"main\"|g" Formula/dock.rb
else
    # For release/default mode, use actual url and sha256
    sed -i.bak "s|PLACEHOLDER_URL_LINE|url \"https://github.com/jamessawle/dock/archive/refs/tags/v${VERSION}.tar.gz\"|g" Formula/dock.rb
    sed -i.bak "s|PLACEHOLDER_SHA256_LINE|sha256 \"${SHA256}\"|g" Formula/dock.rb
    sed -i.bak "s|PLACEHOLDER_HEAD_LINE|head \"https://github.com/jamessawle/dock.git\", branch: \"main\"|g" Formula/dock.rb
fi

rm Formula/dock.rb.bak

# Replace dependencies placeholder using Python (handles multiline properly)
python3 << PYTHON_SCRIPT
with open('Formula/dock.rb', 'r') as f:
    content = f.read()

resources = """$RESOURCES"""
content = content.replace('  PLACEHOLDER_DEPENDENCIES_UPDATE_BEFORE_PUBLISHING', resources.rstrip())

with open('Formula/dock.rb', 'w') as f:
    f.write(content)
PYTHON_SCRIPT

echo ""
echo "✓ Formula generated successfully at Formula/dock.rb"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff Formula/dock.rb"
echo "2. Test the formula: ./scripts/test-formula.sh"
