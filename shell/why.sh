# why shell integration — auto-explain failed commands.
# Usage: `whyex <command>` runs the command, captures output, and explains on failure.
#        `whyex list|explain|run|fix|contribute|init|config|...` delegates to the whyex binary.

_whyex_exec() {
    _wx_bin="$(command -v whyex 2>/dev/null)"
    if [ -n "$_wx_bin" ] && [ -x "$_wx_bin" ]; then
        command whyex "$@"
    else
        python3 -m why "$@"
    fi
}

whyex() {
    case "$1" in
        run|explain|list|fix|contribute|init|config|-v|--version|--help|"")
            _whyex_exec "$@"
            ;;
        *)
            "$@" > "$HOME/.why/last_output.txt" 2>&1
            local code=$?
            cat "$HOME/.why/last_output.txt"
            if [ "$code" -ne 0 ]; then
                _whyex_exec explain < "$HOME/.why/last_output.txt"
            fi
            return "$code"
            ;;
    esac
}
