#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""whyex - explains the last error and shows how to fix it.

Created by Sai Koushik Yaganti (https://github.com/SAI141003).

Works offline, zero dependencies, language-agnostic. Point it at any error
from any stack (git, Python, Node, Go, Rust, Java, shell, Docker, network...)
and it tells you what happened and the exact fix.
"""
import sys
import os
import re
import json
import argparse
import subprocess

from rules import RULES, ALL_TAGS

_contrib_env = os.environ.get("WHYEX_CONTRIB_FILE")
_contrib_path = _contrib_env or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "contrib_rules.py"
)

try:
    if _contrib_env:
        if os.path.exists(_contrib_env):
            import importlib.util
            _cspec = importlib.util.spec_from_file_location("contrib_rules", _contrib_env)
            _cmod = importlib.util.module_from_spec(_cspec)
            _cspec.loader.exec_module(_cmod)
            CONTRIB_RULES = list(getattr(_cmod, "CONTRIB_RULES", []))
        else:
            CONTRIB_RULES = []
    else:
        from contrib_rules import CONTRIB_RULES  # noqa: F401
        CONTRIB_RULES = list(CONTRIB_RULES)
except Exception:
    CONTRIB_RULES = []

RULES = list(RULES) + list(CONTRIB_RULES)
ALL_TAGS = sorted({t for r in RULES for t in r.get("tags", [])})

APP = "whyex"
VERSION = "0.1.0"
CONFIG_DIR = os.path.expanduser(os.environ.get("WHY_CONFIG_DIR", "~/.why"))
LAST_OUTPUT = os.path.join(CONFIG_DIR, "last_output.txt")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

SHELL_FUNCTIONS = """# why shell integration — auto-explain failed commands.
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
"""

SHELL_RC_SNIPPET = (
    "\n# why shell integration (added by `why init`)\n"
    '[ -f "$HOME/.why/why.sh" ] && . "$HOME/.why/why.sh"\n'
)

SHELL_HOOK_MARKER = "# why shell integration"


def _detect_rc_file():
    home = os.path.expanduser("~")
    shell = os.environ.get("SHELL", "")
    zshrc = os.path.join(home, ".zshrc")
    if shell.endswith("zsh") or os.path.exists(zshrc):
        return zshrc
    bashrc = os.path.join(home, ".bashrc")
    if os.path.exists(bashrc):
        return bashrc
    if sys.platform == "darwin":
        bash_profile = os.path.join(home, ".bash_profile")
        if os.path.exists(bash_profile):
            return bash_profile
    return bashrc

USE_COLOR = sys.stdout.isatty()


def _c(code, s):
    if not USE_COLOR:
        return s
    return "\033[" + str(code) + "m" + s + "\033[0m"


RED = lambda s: _c(31, s)
GREEN = lambda s: _c(32, s)
YELLOW = lambda s: _c(33, s)
CYAN = lambda s: _c(36, s)
BOLD = lambda s: _c(1, s)
DIM = lambda s: _c(2, s)


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def safe_format(template, groups):
    try:
        return template.format(**groups)
    except Exception:
        return template


def find_matches(text):
    scored = []
    for rule in RULES:
        try:
            m = re.search(rule["match"], text, re.IGNORECASE | re.DOTALL)
        except re.error:
            m = None
        if m:
            scored.append((rule.get("priority", 1), len(rule["match"]), rule, m))
    if not scored:
        return None, None, []
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best_priority, best_score, best_rule, best_match = scored[0]
    others = [r for _, _, r, _ in scored[1:] if r["id"] != best_rule["id"]]
    seen = set()
    deduped = []
    for r in others:
        if r["id"] not in seen:
            seen.add(r["id"])
            deduped.append(r)
    return best_rule, best_match, deduped[:3]


def _compute_confidence(rule):
    if rule.get("priority", 1) >= 2:
        return "high"
    if len(rule.get("match", "")) >= 40:
        return "high"
    if len(rule.get("match", "")) >= 20:
        return "medium"
    return "low"


def _fill_groups(groups):
    cmd_val = groups.get("cmd")
    if not cmd_val:
        for alt in ("cmd2", "cmd3"):
            if groups.get(alt):
                cmd_val = groups[alt]
                break
    if cmd_val:
        groups["cmd"] = cmd_val
    return groups


def _build_result(text):
    text = (text or "").strip()
    if not text:
        return None

    best_rule, best_match, others = find_matches(text)

    if best_rule is None:
        return {
            "matched": False,
            "rule_id": None,
            "title": None,
            "severity": None,
            "confidence": None,
            "tags": [],
            "why": "This error isn't in the offline knowledge base yet.",
            "fix": [],
            "remediation": None,
        }

    severity = best_rule.get("severity", "error")
    confidence = _compute_confidence(best_rule)
    tags = list(best_rule.get("tags", []))

    groups = _fill_groups(best_match.groupdict() if best_match else {})
    title = safe_format(best_rule.get("title", "Error"), groups)
    why = safe_format(best_rule.get("why", ""), groups)
    fix = [safe_format(step, groups) for step in best_rule.get("fix", [])]
    remediation = best_rule.get("remediation")

    return {
        "matched": True,
        "rule_id": best_rule["id"],
        "title": title,
        "severity": severity,
        "confidence": confidence,
        "tags": tags,
        "why": why,
        "fix": fix,
        "remediation": remediation,
        "_others": others,
        "_match": best_match,
    }


def diagnose(text, as_json=False):
    result = _build_result(text)
    if result is None:
        print(YELLOW("Nothing to diagnose. Pipe an error in, run `whyex run <cmd>`, "
                     "or pass text: `whyex explain \"error text\"`."))
        return 1

    if as_json:
        out = dict(result)
        out.pop("_others", None)
        out.pop("_match", None)
        print(json.dumps(out))
        return 0

    return _print_pretty(result)


def _print_pretty(result):
    if not result["matched"]:
        print(CYAN("whyex") + " . " + YELLOW("no known rule matched this error"))
        print(DIM("-" * 50))
        print(result["why"])
        print("Tip: " + BOLD("whyex list") + " to see covered errors, or contribute a rule.")
        return 0

    others = result.get("_others", [])
    tags = result["tags"]
    print(CYAN("whyex") + " . " + BOLD("diagnosing"))
    print(DIM("-" * 50))
    print(RED("x") + " " + BOLD(result["title"]) + "  " + DIM("(" + ", ".join(tags) + ")"))
    print(DIM("severity: " + result["severity"] + " · confidence: " + result["confidence"]))
    if result["why"]:
        print()
        print(wrap(result["why"], indent="  "))
    if result["fix"]:
        print()
        print(GREEN("OK How to fix:"))
        for i, step in enumerate(result["fix"], 1):
            lines = wrap(step, indent="     ").split("\n")
            print("  " + str(i) + ". " + lines[0].lstrip())
            for cont in lines[1:]:
                print(cont)
    if others:
        print()
        print(DIM("Possibly related: ") +
              ", ".join(BOLD(r.get("title", r["id"])) for r in others))
    return 0


def wrap(text, indent="", width=78):
    out = []
    for line in text.split("\n"):
        if not line:
            out.append("")
            continue
        words = line.split(" ")
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > width and cur:
                out.append(indent + cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        out.append(indent + cur)
    return "\n".join(out)


def _resolve_text(args):
    text = " ".join(getattr(args, "text", []) or []).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()
    if not text and os.path.exists(LAST_OUTPUT):
        with open(LAST_OUTPUT, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    return text


def cmd_run(args):
    remainder = args.command
    if not remainder:
        print(RED("usage: whyex run <command...>"))
        return 2
    try:
        proc = subprocess.run(
            remainder,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
        )
    except FileNotFoundError:
        return diagnose("command not found: " + remainder[0], as_json=args.json)
    out = proc.stdout or ""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(LAST_OUTPUT, "w", encoding="utf-8") as f:
        f.write(out)
    if not getattr(args, "json", False):
        sys.stdout.write(out)
    if proc.returncode != 0:
        if not out.strip():
            msg = ("Command exited with code %d but produced no output to diagnose."
                   % proc.returncode)
            if args.json:
                print(json.dumps({"matched": False, "exit_code": proc.returncode,
                                  "why": msg}))
            else:
                print(YELLOW(msg))
            return proc.returncode
        diagnose(out, as_json=args.json)
    return proc.returncode


def cmd_explain(args):
    text = _resolve_text(args)
    return diagnose(text, as_json=args.json)


def cmd_fix(args):
    text = _resolve_text(args)
    result = _build_result(text)
    if result is None:
        print(YELLOW("Nothing to diagnose. Pipe an error in, run `whyex run <cmd>`, "
                     "or pass text: `whyex explain \"error text\"`."))
        return 1
    if not result["matched"]:
        print(CYAN("whyex") + " . " + YELLOW("no rule matched — nothing to auto-fix"))
        return 0
    _print_pretty(result)
    raw_remediation = result.get("remediation") or None
    if not raw_remediation:
        print("No automated fix available for this error — see the steps above.")
        return 0
    m = result.get("_match")
    groups = _fill_groups(m.groupdict()) if m is not None else {}
    groups = {k: v for k, v in groups.items() if v is not None}
    remediation = safe_format(raw_remediation, groups) or None
    if not remediation:
        print("No automated fix available for this error — see the steps above.")
        return 0
    if "<" in remediation or "{" in remediation:
        print(YELLOW("This fix contains <placeholders> — edit them first, then run:"))
        print("  " + remediation)
        return 0
    print(remediation)
    if not args.yes:
        try:
            ans = input("Run this command? [y/N] ")
        except EOFError:
            ans = ""
        if ans.strip().lower() not in ("y", "yes"):
            return 0
    proc = subprocess.run(remediation, shell=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.write(proc.stdout or "")
    if proc.stderr and proc.stderr != proc.stdout:
        sys.stderr.write(proc.stderr)
    print("exit code: %d" % proc.returncode)
    return 0


def _slugify(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "rule"


def _write_contrib_rules(path, rules):
    import pprint
    content = "CONTRIB_RULES = " + pprint.pformat(rules, indent=4, width=100) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def cmd_contribute(args):
    error = args.error
    title = args.title
    why = args.why
    fix_list = list(args.fix or [])
    raw_tags = args.tags or "shell"
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()] or ["shell"]

    base_id = args.id or _slugify(title)
    existing_ids = {r["id"] for r in RULES}
    rid = base_id
    if rid in existing_ids:
        i = 2
        while ("%s-%d" % (base_id, i)) in existing_ids:
            i += 1
        rid = "%s-%d" % (base_id, i)

    rule = {
        "id": rid,
        "tags": tags,
        "match": re.escape(error),
        "title": title,
        "why": why,
        "fix": fix_list,
        "severity": "error",
        "remediation": None,
    }

    CONTRIB_RULES.append(rule)
    _write_contrib_rules(_contrib_path, CONTRIB_RULES)
    RULES.append(rule)

    print(GREEN("OK") + " added rule " + BOLD(rid))
    print("Run `python3 -m pytest -q` to validate, then open a PR.")
    return 0


def cmd_list(args):
    by_tag = {}
    for r in RULES:
        for t in r.get("tags", []):
            by_tag.setdefault(t, []).append(r)
    for tag in sorted(by_tag):
        print(CYAN(tag) + " (" + str(len(by_tag[tag])) + ")")
        for r in by_tag[tag]:
            print("  - " + r["id"] + " \u2014 " + r.get("title", r["id"]))
    print()
    print(BOLD("Total: " + str(len(RULES)) + " rules across "
               + str(len(by_tag)) + " categories"))
    return 0


def cmd_init(args):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        save_config({})

    hook_written = False
    rc_updated = False
    rc_backed_up = False
    rc_path = None
    hook_path = None
    if not getattr(args, "no_shell", False):
        hook_path = os.path.join(CONFIG_DIR, "why.sh")
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(SHELL_FUNCTIONS)
        hook_written = True
        rc_path = _detect_rc_file()
        try:
            with open(rc_path, "r", encoding="utf-8") as f:
                rc_content = f.read()
        except FileNotFoundError:
            rc_content = ""
        if SHELL_HOOK_MARKER not in rc_content:
            if rc_content:
                with open(rc_path + ".why.bak", "w", encoding="utf-8") as f:
                    f.write(rc_content)
                rc_backed_up = True
            with open(rc_path, "a", encoding="utf-8") as f:
                f.write(SHELL_RC_SNIPPET)
            rc_updated = True

    print(GREEN("OK") + " " + APP + " initialized at " + CONFIG_DIR)
    if hook_written:
        print()
        print(BOLD("Shell integration installed:"))
        print("  hook written to: " + hook_path)
        if rc_updated:
            print("  appended to:     " + rc_path)
            if rc_backed_up:
                print("  backup saved:    " + rc_path + ".why.bak")
            print()
            print("  `whyex <command>` now auto-explains failures in new shells.")
            print("  To undo: delete the appended lines from " + rc_path +
                  ((" and restore " + rc_path + ".why.bak") if rc_backed_up
                   else "") + ".")
        else:
            print("  NOTE: " + rc_path + " already contains whyex integration; skipped.")
    print()
    print(BOLD("Quick start:"))
    print("  whyex run npm test        # run a command and auto-explain failures")
    print("  make 2>&1 | whyex         # explain piped output")
    print("  whyex explain \"error...\"   # explain literal text")
    print("  whyex list                # see everything it can diagnose")
    print()
    return 0


def cmd_config(args):
    cfg = load_config()
    if args.set:
        for item in args.set:
            if "=" not in item:
                print(RED("invalid --set '" + item + "', expected key=value"))
                return 2
            k, v = item.split("=", 1)
            cfg[k.strip()] = v.strip()
        save_config(cfg)
        print(GREEN("OK") + " saved " + str(len(args.set)) + " key(s) to " + CONFIG_FILE)
        return 0
    if args.get:
        print(cfg.get(args.get, ""))
        return 0
    print(json.dumps(cfg, indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="whyex",
        description="Explain the last error and show how to fix it (offline).",
    )
    p.add_argument("-v", "--version", action="version",
                   version=APP + " " + VERSION)
    sub = p.add_subparsers(dest="cmd")

    pr = sub.add_parser("run", help="run a command and explain if it fails")
    pr.add_argument("command", nargs=argparse.REMAINDER,
                    help="the command to run")
    pr.add_argument("--json", action="store_true",
                    help="emit structured JSON instead of pretty text")

    pe = sub.add_parser("explain", help="explain text / piped / last run")
    pe.add_argument("text", nargs="*")
    pe.add_argument("--json", action="store_true",
                    help="emit structured JSON instead of pretty text")

    sub.add_parser("list", help="list diagnostic rules by category")
    pi = sub.add_parser("init", help="initialize config")
    pi.add_argument("--no-shell", action="store_true",
                    help="skip installing the shell hook")
    pc = sub.add_parser("config", help="get/set config values")
    pc.add_argument("--set", action="append")
    pc.add_argument("--get", nargs="?")

    pf = sub.add_parser("fix", help="safely run an automated fix for an error")
    pf.add_argument("text", nargs="*")
    pf.add_argument("-y", "--yes", action="store_true",
                    help="run the remediation without prompting")

    pcontrib = sub.add_parser("contribute",
                              help="scaffold a new rule from a pasted error")
    pcontrib.add_argument("--error", required=True,
                          help="the literal error text that should match")
    pcontrib.add_argument("--title", required=True,
                          help="human-readable title for the rule")
    pcontrib.add_argument("--why", required=True,
                          help="explanation of what the error means")
    pcontrib.add_argument("--fix", required=True, action="append",
                          help="a fix step (repeatable)")
    pcontrib.add_argument("--tags", default="shell",
                          help="comma-separated tags (default: shell)")
    pcontrib.add_argument("--id", default=None,
                          help="explicit rule id (default: slugified title)")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    KNOWN = {"run", "explain", "list", "init", "config", "fix", "contribute"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        return diagnose(" ".join(argv))

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "explain":
        return cmd_explain(args)
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "config":
        return cmd_config(args)
    if args.cmd == "fix":
        return cmd_fix(args)
    if args.cmd == "contribute":
        return cmd_contribute(args)

    if not sys.stdin.isatty():
        return diagnose(sys.stdin.read())
    if os.path.exists(LAST_OUTPUT):
        with open(LAST_OUTPUT, "r", encoding="utf-8", errors="replace") as f:
            return diagnose(f.read())
    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(141)
    except KeyboardInterrupt:
        sys.exit(130)
