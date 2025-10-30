#!/usr/bin/env bash

# Environment and discovery helpers split out of the main dock script.

# shellcheck shell=bash

ensure_macos() { [[ "$(uname -s)" == "Darwin" ]] || die "This tool supports macOS only."; }

ensure_dockutil() {
	command -v dockutil >/dev/null 2>&1 || die "dockutil missing (brew install dockutil)."
	local v
	v="$(dockutil --version 2>/dev/null | extract_version | tr -d '\r\n')"
	version_ge "$v" "3.0.0" || die "dockutil >= 3.0.0 required, found $v"
}

ensure_yq() {
	command -v yq >/dev/null 2>&1 || die "yq missing (brew install yq)."
	local v
	v="$(yq --version 2>/dev/null | extract_version | tr -d '\r\n')"
	version_ge "$v" "4.0.0" || die "yq >= 4.0.0 required, found $v"
}

find_config() {
	# Discovery priority when --file not given:
	# 1) $DOCK_CONFIG (env), 2) --profile NAME, 3) standard locations
	if [[ -n "$DOCK_CONFIG" && -f "$DOCK_CONFIG" ]]; then
		printf "%s" "$DOCK_CONFIG"
		return 0
	fi
	if [[ -n "$PROFILE" ]]; then
		local base="$HOME/.config/dock/profiles/${PROFILE}"
		for ext in yml yaml; do [[ -f "${base}.${ext}" ]] && {
			printf "%s" "${base}.${ext}"
			return 0
		}; done
	fi
	for f in "$HOME/.config/dock/config.yml" "$HOME/.config/dock/config.yaml" "/etc/dock/config.yml" "/etc/dock/config.yaml"; do
		[[ -f "$f" ]] && {
			printf "%s" "$f"
			return 0
		}
	done
	return 1
}

app_path_for() {
	local name="$1"
	# Absolute .app path
	if [[ "$name" == /*.app && -e "$name" ]]; then
		printf "%s" "$name"
		return 0
	fi
	# Bundle ID
	if [[ "$name" == bundle:* ]]; then
		local bid="${name#bundle:}" path
		path="$(mdfind "kMDItemCFBundleIdentifier == '$bid'" | head -n1 || true)"
		[[ -n "$path" && -e "$path" ]] && {
			printf "%s" "$path"
			return 0
		}
	fi
	# Typical locations
	local p
	for p in "/Applications/${name}.app" "$HOME/Applications/${name}.app" "/System/Applications/${name}.app" "/Applications/Utilities/${name}.app"; do
		[[ -e "$p" ]] && {
			printf "%s" "$p"
			return 0
		}
	done
	# Spotlight by display name
	local sp
	sp="$(mdfind "kMDItemDisplayName == '$name'" | head -n1 || true)"
	[[ -n "$sp" && -e "$sp" ]] && {
		printf "%s" "$sp"
		return 0
	}
	printf ""
}
