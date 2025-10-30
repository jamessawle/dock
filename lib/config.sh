#!/usr/bin/env bash

# YAML validation and parsing helpers.

# shellcheck shell=bash

validate_yaml_config() {
	local f="$1"

	# Unknown top-level keys
	local unknown
	unknown="$(yq -r 'keys | map(select(. != "apps" and . != "downloads")) | .[]?' "$f" || true)"
	if [[ -n "$unknown" ]]; then
		die "Invalid config: unknown top-level key(s): ${unknown//$'\n'/, }"
	fi

	# apps: must be seq of strings if present
	if yq -e '.apps? != null' "$f" >/dev/null 2>&1; then
		yq -e '.apps | type == "!!seq"' "$f" >/dev/null 2>&1 ||
			die "Invalid config: .apps must be a YAML list"
		local nonstr_count
		nonstr_count="$(yq -r '.apps | map(select(type != "!!str")) | length' "$f")"
		if [[ "${nonstr_count:-0}" -gt 0 ]]; then
			die "Invalid config: all .apps entries must be strings"
		fi
	fi

	# downloads: may be null/absent, "off", or map with allowed keys
	if yq -e '.downloads? != null' "$f" >/dev/null 2>&1; then
		if yq -e '.downloads == "off"' "$f" >/dev/null 2>&1; then
			: # ok
		else
			yq -e '.downloads | type == "!!map"' "$f" >/dev/null 2>&1 ||
				die "Invalid config: .downloads must be a map or the string \"off\""
			# unknown keys inside downloads
			local d_unknown
			d_unknown="$(yq -r '.downloads | keys | map(select(. != "preset" and . != "path" and . != "section")) | .[]?' "$f" || true)"
			[[ -n "$d_unknown" ]] && die "Invalid config: unknown .downloads key(s): ${d_unknown//$'\n'/, }"

			# preset constraint
			if yq -e '.downloads.preset? != null' "$f" >/dev/null 2>&1; then
				yq -e '.downloads.preset | type == "!!str"' "$f" >/dev/null 2>&1 ||
					die "Invalid config: .downloads.preset must be a string"
				local preset
				preset="$(yq -r '.downloads.preset' "$f")"
				case "$preset" in
				classic | fan | list) : ;;
				*) die "Invalid config: .downloads.preset must be one of: classic, fan, list" ;;
				esac
			fi

			# section constraint
			if yq -e '.downloads.section? != null' "$f" >/dev/null 2>&1; then
				yq -e '.downloads.section | type == "!!str"' "$f" >/dev/null 2>&1 ||
					die "Invalid config: .downloads.section must be a string"
				local section
				section="$(yq -r '.downloads.section' "$f")"
				case "$section" in
				apps-left | apps-right | others) : ;;
				*) die "Invalid config: .downloads.section must be one of: apps-left, apps-right, others" ;;
				esac
			fi

			# path must be string if present
			if yq -e '.downloads.path? != null' "$f" >/dev/null 2>&1; then
				yq -e '.downloads.path | type == "!!str"' "$f" >/dev/null 2>&1 ||
					die "Invalid config: .downloads.path must be a string"
			fi
		fi
	fi
}

load_yaml_config() {
	local f="$1"
	parsed_apps=()

	# strict validation first
	validate_yaml_config "$f"

	local out
	out="$(yq -r '.apps // [] | .[]' "$f" 2>/dev/null || true)"
	while IFS= read -r l; do [[ -n "$l" ]] && parsed_apps+=("$l"); done <<<"$out"

	local raw
	raw="$(yq -r '.downloads // ""' "$f" 2>/dev/null || true)"
	if [[ "$raw" == "off" ]]; then
		dl_enabled=0
		dl_preset="classic"
		dl_path="${HOME}/Downloads"
		dl_section="others"
		return 0
	fi
	if yq -e '.downloads | type == "!!map"' "$f" >/dev/null 2>&1; then
		dl_preset="$(yq -r '.downloads.preset // "classic"' "$f")"
		dl_path="$(yq -r '.downloads.path // "~/" + "Downloads"' "$f")"
		dl_path="${dl_path/#\~/$HOME}"
		dl_section="$(yq -r '.downloads.section // "others"' "$f")"
	fi
}

build_preset_flags() {
	case "$1" in
	classic) echo "--view grid --display folder --sort dateadded" ;;
	fan) echo "--view fan --display stack --sort dateadded" ;;
	list) echo "--view list --display folder --sort name" ;;
	*) echo "--view grid --display folder --sort dateadded" ;;
	esac
}
