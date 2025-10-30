#!/usr/bin/env bash

# Dock manipulation helpers.

# shellcheck shell=bash

dock_plan=()

read_defaults_value() {
	local domain="$1" key="$2"
	local out
	if out="$(defaults read "$domain" "$key" 2>/dev/null)"; then
		printf '%s' "$out"
	else
		printf ''
	fi
}

current_autohide_value() {
	local raw
	raw="$(read_defaults_value "com.apple.dock" "autohide")"
	local lowered
	lowered="$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]')"
	case "$lowered" in
	true | 1) echo "true" ;;
	*) echo "false" ;;
	esac
}

current_autohide_delay_value() {
	local raw
	raw="$(read_defaults_value "com.apple.dock" "autohide-delay")"
	[[ -z "$raw" ]] && raw="0"
	if declare -F round_with_trim >/dev/null; then
		round_with_trim "$raw" 2
	else
		printf '%s' "$raw"
	fi
}

add_app_command() {
	local app="$1" path
	path="$(app_path_for "$app")"
	if [[ -z "$path" ]]; then
		warn "App not found: $app"
		return 1
	fi
	printf "dockutil --add %q --no-restart" "$path"
}

build_preset_flags() {
	case "$1" in
	classic) echo "--view grid --display folder --sort dateadded" ;;
	fan) echo "--view fan --display stack --sort dateadded" ;;
	list) echo "--view list --display folder --sort name" ;;
	*) echo "--view grid --display folder --sort dateadded" ;;
	esac
}

add_downloads_command() {
	local flags target section
	flags="$(build_preset_flags "$dl_preset")"
	target="$dl_path"
	section="others"
	[[ "$dl_section" == apps-left || "$dl_section" == apps-right ]] && section="apps"
	printf "dockutil --add %q --section %s --no-restart %s" "$target" "$section" "$flags"
}

build_plan() {
	local apps=("$@") cmd
	dock_plan=()
	dock_plan+=("dockutil --remove all --no-restart")

	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "apps-left" ]]; then
		cmd="$(add_downloads_command)" && dock_plan+=("$cmd")
	fi

	local app
	for app in "${apps[@]}"; do
		if cmd="$(add_app_command "$app")"; then
			dock_plan+=("$cmd")
		fi
	done

	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "apps-right" ]]; then
		cmd="$(add_downloads_command)" && dock_plan+=("$cmd")
	fi
	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "others" ]]; then
		cmd="$(add_downloads_command)" && dock_plan+=("$cmd")
	fi

	if [[ "$settings_autohide" != "$(current_autohide_value)" ]]; then
		dock_plan+=("defaults write com.apple.dock autohide -bool $settings_autohide")
	fi

	if [[ "$settings_autohide_delay" != "$(current_autohide_delay_value)" ]]; then
		dock_plan+=("defaults write com.apple.dock autohide-delay -float $settings_autohide_delay")
	fi

	dock_plan+=("killall Dock")
}

print_plan() {
	local cmd
	for cmd in "${dock_plan[@]}"; do
		printf '[DRY-RUN] %s\n' "$cmd"
	done
}

execute_plan() {
	local cmd
	for cmd in "${dock_plan[@]}"; do
		if [[ "$cmd" == "killall Dock" ]]; then
			eval "$cmd" >/dev/null 2>&1 || true
		else
			eval "$cmd" >/dev/null 2>&1
		fi
	done
}
