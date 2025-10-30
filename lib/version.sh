#!/usr/bin/env bash

# Version utilities extracted from the main dock script.

# shellcheck shell=bash

extract_version() {
	awk '{
    if (match($0, /[0-9]+(\.[0-9]+)+/)) { print substr($0, RSTART, RLENGTH); found=1; exit }
  } END { if (!found) print "0" }'
}

# vercomp a b -> 0 if equal, 1 if a>b, 2 if a<b
vercomp() {
	[[ "$1" == "$2" ]] && return 0

	local IFS=.
	local -a a b
	# Split versions into arrays using IFS safely
	read -r -a a <<<"$1"
	read -r -a b <<<"$2"

	local i
	local len=${#a[@]}
	((${#b[@]} > len)) && len=${#b[@]}

	for ((i = 0; i < len; i++)); do
		local x=${a[i]:-0} y=${b[i]:-0}
		((10#$x > 10#$y)) && return 1
		((10#$x < 10#$y)) && return 2
	done
	return 0
}

version_ge() {
	vercomp "$1" "$2"
	local rc=$?
	[[ $rc -eq 0 || $rc -eq 1 ]]
}
