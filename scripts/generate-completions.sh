#!/usr/bin/env bash
set -euo pipefail

# Generate shell completions for dock CLI
# This script should be run as part of the release process

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPLETIONS_DIR="$PROJECT_ROOT/completions"

echo "Generating shell completions..."

# Ensure completions directory exists
mkdir -p "$COMPLETIONS_DIR"

# Generate bash completion
echo "  - Generating bash completion..."
uv run env _DOCK_COMPLETE=bash_source dock > "$COMPLETIONS_DIR/dock.bash"

# Generate zsh completion
echo "  - Generating zsh completion..."
uv run env _DOCK_COMPLETE=zsh_source dock > "$COMPLETIONS_DIR/_dock"

echo "✓ Shell completions generated successfully"
echo "  - $COMPLETIONS_DIR/dock.bash"
echo "  - $COMPLETIONS_DIR/_dock"
