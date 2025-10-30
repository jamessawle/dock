#!/usr/bin/env bash

# Dock snapshot and backup helpers.

# shellcheck shell=bash

_decode_file_url() {
	local s="$1"
	s="${s#file://}"
	s="${s%/}"
	s="${s//%20/ }"
	printf "%s" "$s"
}

_pb() { /usr/libexec/PlistBuddy -c "Print :$2" "$1" 2>/dev/null | sed 's/^ *//;s/ *$//'; }

_pb_count() {
	local out
	out="$(/usr/libexec/PlistBuddy -c "Print :$2" "$1" 2>/dev/null || true)"
	if [[ -z "$out" ]]; then
		echo 0
		return
	fi
	echo "$out" | awk 'BEGIN{n=0} /^    Dict {/ {n++} END{print n}'
}

generate_snapshot_yaml() {
	local plist="$HOME/Library/Preferences/com.apple.dock.plist"

	# Apps
	local apps=() a_count idx label url
	a_count="$(_pb_count "$plist" "persistent-apps")"
	for ((idx = 0; idx < a_count; idx++)); do
		label="$(_pb "$plist" "persistent-apps:$idx:tile-data:file-label")"
		url="$(_pb "$plist" "persistent-apps:$idx:tile-data:file-data:_CFURLString")"
		if [[ -n "$url" && "$url" == *".app"* && -n "$label" ]]; then apps+=("$label"); fi
	done

	# Downloads
	local dl_path_found="" dl_section_found=""
	local o_count oidx olabel ourl
	o_count="$(_pb_count "$plist" "persistent-others")"
	for ((oidx = 0; oidx < o_count; oidx++)); do
		olabel="$(_pb "$plist" "persistent-others:$oidx:tile-data:file-label")"
		ourl="$(_pb "$plist" "persistent-others:$oidx:tile-data:file-data:_CFURLString")"
		if [[ "$olabel" == "Downloads" || "$ourl" == *"/Downloads/"* || "$ourl" == *"/Downloads" ]]; then
			dl_path_found="$ourl"
			dl_section_found="others"
			break
		fi
	done
	if [[ -z "$dl_path_found" ]]; then
		for ((idx = 0; idx < a_count; idx++)); do
			label="$(_pb "$plist" "persistent-apps:$idx:tile-data:file-label")"
			url="$(_pb "$plist" "persistent-apps:$idx:tile-data:file-data:_CFURLString")"
			if [[ -n "$url" && "$url" != *".app"* && ("$label" == "Downloads" || "$url" == *"/Downloads/"* || "$url" == *"/Downloads") ]]; then
				dl_path_found="$url"
				if ((idx == 0)); then dl_section_found="apps-left"; else dl_section_found="apps-right"; fi
				break
			fi
		done
	fi
	local norm_dl=""
	if [[ -n "$dl_path_found" ]]; then
		norm_dl="$(_decode_file_url "$dl_path_found")"
		if [[ "$norm_dl" == "$HOME/Downloads" ]]; then
			# Produce a literal tilde path for YAML output, without relying on tilde expansion
			norm_dl="~${norm_dl#"$HOME"}"
		fi
	fi

	# Emit YAML
	echo "apps:"
	if [[ ${#apps[@]} -gt 0 ]]; then
		local a
		for a in "${apps[@]}"; do printf '  - %s\n' "$a"; done
	fi
	if [[ -n "$dl_section_found" && -n "$norm_dl" ]]; then
		cat <<EOF
downloads:
  preset: classic
  path: "$norm_dl"
  section: $dl_section_found
EOF
	else
		echo "downloads: off"
	fi
}

backup_to_file() {
	local out="$1"
	[[ -n "$out" ]] || die "backup requires --file PATH"
	local dir
	dir="$(dirname "$out")"
	[[ -d "$dir" ]] || mkdir -p "$dir"
	generate_snapshot_yaml >"$out"
	log "wrote snapshot to $out"
}
