#!/usr/bin/env bash

# Dock manipulation helpers.

# shellcheck shell=bash

add_app() {
	local app="$1" path
	path="$(app_path_for "$app")"
	if [[ -z "$path" ]]; then
		warn "App not found: $app"
		return 1
	fi
	if [[ "$DRY_RUN" -eq 1 ]]; then
		printf "[DRY-RUN] dockutil --add %q --no-restart\n" "$path"
	else
		dockutil --add "$path" --no-restart >/dev/null 2>&1
	fi
}

add_downloads() {
	[[ "$dl_enabled" -eq 1 ]] || return 0
	local flags target esc_target section
	flags="$(build_preset_flags "$dl_preset")"
	target="$dl_path"
	esc_target="$(printf '%q' "$target")"
	section="others"
	[[ "$dl_section" == apps-left || "$dl_section" == apps-right ]] && section="apps"

	if [[ "$DRY_RUN" -eq 1 ]]; then
		echo "[DRY-RUN] dockutil --add $esc_target --section $section --no-restart $flags"
	else
		# shellcheck disable=SC2086
		dockutil --add "$target" --section "$section" --no-restart $flags >/dev/null 2>&1
	fi
}

reset_dock() {
	local apps=("$@")
	if [[ "$DRY_RUN" -eq 1 ]]; then
		echo "[DRY-RUN] dockutil --remove all --no-restart"
	else
		dockutil --remove all --no-restart >/dev/null 2>&1
	fi

	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "apps-left" ]]; then
		add_downloads
	fi
	local a
	for a in "${apps[@]}"; do add_app "$a"; done
	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "apps-right" ]]; then
		add_downloads
	fi
	if [[ "$dl_enabled" -eq 1 && "$dl_section" == "others" ]]; then
		add_downloads
	fi

	if [[ "$DRY_RUN" -eq 1 ]]; then
		echo "[DRY-RUN] killall Dock"
	else
		killall Dock 2>/dev/null || true
	fi
}
