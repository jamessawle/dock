#!/usr/bin/env bash

# Dock manipulation helpers.

# shellcheck shell=bash

dock_plan=()

add_app_command() {
	local app="$1" path
	path="$(app_path_for "$app")"
	if [[ -z "$path" ]]; then
		warn "App not found: $app"
		return 1
	fi
	printf "dockutil --add %q --no-restart" "$path"
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
