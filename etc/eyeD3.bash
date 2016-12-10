# bash-completion for 'eyeD3'

unset __EYED3_COMPLETION_LONG_OPT

function _eyeD3_completion()
{
    [[ -e `which eyeD3 2> /dev/null` ]] || return 0

    # Variables to hold the current word and possible matches
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local opts=()

    case "${cur}" in
        -*)
            if [[ -z "${__EYED3_COMPLETION_LONG_OPT}" ]]; then
                export __EYED3_COMPLETION_LONG_OPT=$(
                    eyeD3 --help | egrep -o " \-[A-Za-z0-9_\.\-]+\=?" | sort -u)
            fi
            opts="${__EYED3_COMPLETION_LONG_OPT}"
            ;;

        *)
            ;;
    esac

    # Set possible completions
    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
}

complete -o default -o nospace  -F _eyeD3_completion eyeD3

alias eyeD3-fixup='eyeD3 -P fixup'
alias eyeD3-stats='eyeD3 -P stats'
alias eyeD3-art='eyeD3 -P art'
