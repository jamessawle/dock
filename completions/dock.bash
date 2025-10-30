# bash completion for dock
# To use: source this file or place it in your bash-completion directory.

_dock_completion() {
	local cur prev
	if declare -F _init_completion >/dev/null 2>&1; then
		_init_completion -n = || return
		cur=${cur:-${COMP_WORDS[COMP_CWORD]}}
		prev=${COMP_WORDS[COMP_CWORD - 1]}
	else
		cur=${COMP_WORDS[COMP_CWORD]}
		prev=${COMP_WORDS[COMP_CWORD - 1]}
	fi

	case "$prev" in
	--file | -f)
		COMPREPLY=($(compgen -f -- "$cur"))
		return
		;;
	--profile)
		local profiles_dir="$HOME/.config/dock/profiles"
		if [[ -d "$profiles_dir" ]]; then
			local profiles=()
			while IFS= read -r -d '' file; do
				file=${file##*/}
				file=${file%.*}
				profiles+=("$file")
			done < <(find "$profiles_dir" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) -print0 2>/dev/null)
			if [[ ${#profiles[@]} -gt 0 ]]; then
				local profile_list
				profile_list=$(printf '%s\n' "${profiles[@]}")
				COMPREPLY=($(compgen -W "$profile_list" -- "$cur"))
				return
			fi
		fi
		COMPREPLY=($(compgen -f -- "$cur"))
		return
		;;
	esac

	if [[ $cur == -* ]]; then
		local opts="--dry-run --file -f --profile --help -h --version"
		COMPREPLY=($(compgen -W "$opts" -- "$cur"))
		return
	fi

	local commands="reset show validate backup"
	local cmd=""
	for word in "${COMP_WORDS[@]:1}"; do
		if [[ $word != -* ]]; then
			cmd=$word
			break
		fi
	done

	if [[ -z $cmd ]]; then
		COMPREPLY=($(compgen -W "$commands" -- "$cur"))
		return
	fi

	local cmd_opts="--dry-run --file -f --profile --help -h --version"
	case $cmd in
	reset | show | validate | backup)
		COMPREPLY=($(compgen -W "$cmd_opts" -- "$cur"))
		;;
	esac
}

complete -F _dock_completion dock
