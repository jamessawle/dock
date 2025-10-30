#!/usr/bin/env bash

# YAML validation and parsing helpers.

# shellcheck shell=bash

VALIDATION_ERRORS=()
CONFIG_NORMALIZED_JSON=""
CONFIG_DEFAULT_DOWNLOAD_PRESET="classic"
CONFIG_DEFAULT_DOWNLOAD_PATH="~/Downloads"
CONFIG_DEFAULT_DOWNLOAD_SECTION="others"

normalize_config_json() {
	local f="$1"
	yq -o=json '.downloads as $dl | {"apps": (.apps // []), "downloads": {"enabled": ($dl != "off"), "preset": (([$dl] | map(select(type == "!!map")) | .[0].preset) // "classic"), "path": (([$dl] | map(select(type == "!!map")) | .[0].path) // "~/Downloads"), "section": (([$dl] | map(select(type == "!!map")) | .[0].section) // "others")}}' "$f"
}

strip_config_defaults_yaml() {
	# Remove downloads keys that match defaults; drop the map entirely if empty.
	yq -P "
		del(.downloads.preset | select(. == \"$CONFIG_DEFAULT_DOWNLOAD_PRESET\")) |
		del(.downloads.path | select(. == \"$CONFIG_DEFAULT_DOWNLOAD_PATH\")) |
		del(.downloads.section | select(. == \"$CONFIG_DEFAULT_DOWNLOAD_SECTION\")) |
		del(.downloads | select(type == \"!!map\" and length == 0))
	"
}

add_validation_error() {
	VALIDATION_ERRORS+=("$1")
}

validate_yaml_config() {
	local f="$1"
	VALIDATION_ERRORS=()

	# Unknown top-level keys
	local unknown
	unknown="$(yq -r 'keys | map(select(. != "apps" and . != "downloads")) | .[]?' "$f" || true)"
	if [[ -n "$unknown" ]]; then
		add_validation_error "Unknown top-level key(s): ${unknown//$'\n'/, }"
	fi

	# apps: must be seq of strings if present
	if yq -e '.apps? != null' "$f" >/dev/null 2>&1; then
		if ! yq -e '.apps | type == "!!seq"' "$f" >/dev/null 2>&1; then
			add_validation_error ".apps must be a YAML list"
		else
			local nonstr_count
			nonstr_count="$(yq -r '.apps | map(select(type != "!!str")) | length' "$f" 2>/dev/null || echo 0)"
			if [[ "${nonstr_count:-0}" -gt 0 ]]; then
				add_validation_error "All .apps entries must be strings"
			fi
		fi
	fi

	# downloads: may be null/absent, "off", or map with allowed keys
	if yq -e '.downloads? != null' "$f" >/dev/null 2>&1; then
		if yq -e '.downloads == "off"' "$f" >/dev/null 2>&1; then
			: # ok
		else
			local downloads_is_map=0
			if yq -e '.downloads | type == "!!map"' "$f" >/dev/null 2>&1; then
				downloads_is_map=1
			else
				add_validation_error ".downloads must be a map or the string \"off\""
			fi
			if ((downloads_is_map)); then
				# unknown keys inside downloads
				local d_unknown
				d_unknown="$(yq -r '.downloads | keys | map(select(. != "preset" and . != "path" and . != "section")) | .[]?' "$f" 2>/dev/null || true)"
				if [[ -n "$d_unknown" ]]; then
					add_validation_error "Unknown .downloads key(s): ${d_unknown//$'\n'/, }"
				fi

				# preset constraint
				if yq -e '.downloads.preset? != null' "$f" >/dev/null 2>&1; then
					if ! yq -e '.downloads.preset | type == "!!str"' "$f" >/dev/null 2>&1; then
						add_validation_error ".downloads.preset must be a string"
					else
						local preset
						preset="$(yq -r '.downloads.preset // ""' "$f" 2>/dev/null || echo "")"
						if [[ -n "$preset" ]]; then
							case "$preset" in
							classic | fan | list) : ;;
							*) add_validation_error ".downloads.preset must be one of: classic, fan, list" ;;
							esac
						fi
					fi
				fi

				# section constraint
				if yq -e '.downloads.section? != null' "$f" >/dev/null 2>&1; then
					if ! yq -e '.downloads.section | type == "!!str"' "$f" >/dev/null 2>&1; then
						add_validation_error ".downloads.section must be a string"
					else
						local section
						section="$(yq -r '.downloads.section // ""' "$f" 2>/dev/null || echo "")"
						if [[ -n "$section" ]]; then
							case "$section" in
							apps-left | apps-right | others) : ;;
							*) add_validation_error ".downloads.section must be one of: apps-left, apps-right, others" ;;
							esac
						fi
					fi
				fi

				# path must be string if present
				if yq -e '.downloads.path? != null' "$f" >/dev/null 2>&1; then
					if ! yq -e '.downloads.path | type == "!!str"' "$f" >/dev/null 2>&1; then
						add_validation_error ".downloads.path must be a string"
					fi
				fi
			fi
		fi
	fi

	if ((${#VALIDATION_ERRORS[@]} == 0)); then
		CONFIG_NORMALIZED_JSON="$(normalize_config_json "$f")"
	else
		CONFIG_NORMALIZED_JSON=""
	fi

	((${#VALIDATION_ERRORS[@]} == 0))
}

load_yaml_config() {
	local f="$1"
	parsed_apps=()

	# strict validation first
	if ! validate_yaml_config "$f"; then
		local err
		for err in "${VALIDATION_ERRORS[@]}"; do
			warn "$err"
		done
		die "Invalid config: $f"
	fi

	local normalized="${CONFIG_NORMALIZED_JSON:-}"
	if [[ -z "$normalized" ]]; then
		normalized="$(normalize_config_json "$f")"
	fi

	local apps_out
	apps_out="$(printf '%s' "$normalized" | yq -p=json -r '.apps[]?' 2>/dev/null || true)"
	while IFS= read -r l; do [[ -n "$l" ]] && parsed_apps+=("$l"); done <<<"$apps_out"

	local dl_enabled_raw dl_preset_raw dl_path_raw dl_section_raw
	dl_enabled_raw="$(printf '%s' "$normalized" | yq -p=json -r '.downloads.enabled' 2>/dev/null || echo "true")"
	dl_preset_raw="$(printf '%s' "$normalized" | yq -p=json -r '.downloads.preset' 2>/dev/null || echo "classic")"
	dl_path_raw="$(printf '%s' "$normalized" | yq -p=json -r '.downloads.path' 2>/dev/null || echo "~/Downloads")"
	dl_section_raw="$(printf '%s' "$normalized" | yq -p=json -r '.downloads.section' 2>/dev/null || echo "others")"

	if [[ "$dl_enabled_raw" == "false" ]]; then
		dl_enabled=0
	else
		dl_enabled=1
	fi
	dl_preset="$dl_preset_raw"
	dl_path="${dl_path_raw/#\~/$HOME}"
	dl_section="$dl_section_raw"
}

build_preset_flags() {
	case "$1" in
	classic) echo "--view grid --display folder --sort dateadded" ;;
	fan) echo "--view fan --display stack --sort dateadded" ;;
	list) echo "--view list --display folder --sort name" ;;
	*) echo "--view grid --display folder --sort dateadded" ;;
	esac
}
