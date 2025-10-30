#!/usr/bin/env bash

# String/number helpers kept separate for reuse.

# shellcheck shell=bash

round_with_trim() {
	local raw="${1:-0}"
	local decimals="${2:-2}"
	local sign=""

	if [[ "$raw" == -* ]]; then
		sign="-"
		raw="${raw#-}"
	elif [[ "$raw" == +* ]]; then
		raw="${raw#+}"
	fi

	[[ -z "$raw" ]] && raw="0"
	[[ "$raw" == .* ]] && raw="0$raw"

	local scaled
	scaled=$(printf 'scale=0; (%s * (10^%d) + 0.5)/1\n' "$raw" "$decimals" | bc 2>/dev/null) || {
		printf "%s" "${sign}${raw}"
		return
	}

	if [[ "$sign" == "-" && "$scaled" != "0" ]]; then
		scaled="-$scaled"
	fi

	local rounded
	rounded=$(printf 'scale=%d; %s/(10^%d)\n' "$decimals" "$scaled" "$decimals" | bc)

	rounded=$(printf '%s' "$rounded" |
		sed -e 's/^\./0./' \
		    -e 's/-\./-0./' \
		    -e 's/[.]\([0-9]*[1-9]\)0*/.\1/' \
		    -e 's/[.]0*$//')

	[[ "$rounded" == "-0" ]] && rounded="0"
	printf "%s" "$rounded"
}
