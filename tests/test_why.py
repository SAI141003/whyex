import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from why import find_matches, diagnose
from rules import RULES

REQUIRED_KEYS = {
    "id": str,
    "tags": list,
    "match": str,
    "title": str,
    "why": str,
    "fix": list,
}


def test_rules_load():
    assert len(RULES) == 144
    ids = [r["id"] for r in RULES]
    assert len(ids) == len(set(ids)), "duplicate rule ids"


def test_all_rule_regexes_compile():
    for r in RULES:
        try:
            re.compile(r["match"])
        except re.error as e:
            raise AssertionError("rule %r has invalid regex: %s" % (r["id"], e))


def test_rule_required_fields_and_unique_ids():
    seen = set()
    for r in RULES:
        for key, typ in REQUIRED_KEYS.items():
            assert key in r, "rule %r missing key %r" % (r.get("id", "?"), key)
            assert isinstance(r[key], typ), (
                "rule %r key %r should be %s, got %s"
                % (r.get("id", "?"), key, typ.__name__, type(r[key]).__name__)
            )
        assert r["id"] not in seen, "duplicate rule id %r" % r["id"]
        seen.add(r["id"])


SAMPLES = {
    "git-not-a-repo": "fatal: not a git repository",
    "git-push-rejected": "failed to push some refs to origin",
    "git-refspec": "error: src refspec main does not match any",
    "git-remote-exists": "remote origin already exists",
    "git-ssh-permission": "Permission denied (publickey)",
    "git-detached": "You are in 'detached HEAD' state",
    "git-divergent": "Pulling without specifying how to reconcile",
    "git-untracked-overwrite": "The following untracked working tree files would be overwritten",
    "py-modulenotfound": "ModuleNotFoundError: No module named 'requests'",
    "py-syntaxerror": "SyntaxError: invalid syntax",
    "py-indentation": "IndentationError: unexpected indent",
    "py-filenotfound": "FileNotFoundError: [Errno 2] No such file or directory: 'x'",
    "py-unicode": "UnicodeDecodeError: 'utf-8' codec can't decode",
    "py-pip-permission": "error: externally-managed-environment",
    "py-python-not-found": "python: command not found",
    "node-not-found": "node: command not found",
    "npm-not-found": "npm: command not found",
    "npm-eacces": "npm ERR! code EACCES",
    "npm-network": "npm ERR! code ECONNRESET",
    "node-cannot-find-module": "Cannot find module 'express'",
    "node-ebadengine": "EBADENGINE",
    "go-not-found": "go: command not found",
    "go-no-module": "go: cannot find main module",
    "cargo-not-found": "cargo: command not found",
    "rustc-error": "error[E0425] cannot find value `x` in this scope",
    "java-not-found": "java: command not found",
    "java-version": "UnsupportedClassVersionError",
    "ruby-bundle-permission": "Gem::FilePermissionError",
    "cc-fatal-include": "fatal error: 'foo.h' file not found",
    "cc-undefined-ref": "undefined reference to 'main'",
    "segfault": "Segmentation fault",
    "cmd-not-found": "gitblub: command not found",
    "permission-denied": "Permission denied",
    "no-space": "No space left on device",
    "port-in-use": "Error: listen EADDRINUSE: address already in use :::3000",
    "connection-refused": "Connection refused",
    "ssl-cert": "SSL certificate problem: self signed certificate",
    "zsh-no-matches": "zsh: no matches found: *.log",
    "bash-syntax-error": "syntax error near unexpected token `('",
    "docker-daemon": "Cannot connect to the Docker daemon",
    "docker-permission": "permission denied while trying to connect to the Docker daemon socket",

    "git-bad-revision": "fatal: bad revision",
    "git-bad-object": "fatal: bad object",
    "git-pathspec-no-match": "error: pathspec 'foo' did not match any file",
    "git-merge-in-progress": "You have unmerged paths",
    "git-lock-exists": "unable to create '.git/index.lock': File exists",
    "git-no-upstream": "The current branch main has no upstream branch",
    "git-unrelated-histories": "fatal: refusing to merge unrelated histories",
    "git-local-changes-overwritten": "Your local changes would be overwritten by checkout",
    "git-dubious-ownership": "detected dubious ownership of repository in /repo",
    "git-repo-not-found": "remote error: access denied or repository not found",
    "py-import-name": "ImportError: cannot import name 'foo' from 'bar'",
    "py-pip-no-version": "Could not find a version that satisfies the requirement foo",
    "py-pip-timeout": "pip._vendor.urllib3.exceptions.ReadTimeoutError: timed out",
    "py-venv-no-python": "venv: Command 'python3' not found",
    "py-asyncio-running": "asyncio.run() cannot be called from a running event loop",
    "py-mypy-error": "foo.py:10:5: error: Incompatible types",
    "py-recursion-error": "RecursionError: maximum recursion depth exceeded",
    "py-memory-error": "MemoryError",
    "py-json-decode": "json.decoder.JSONDecodeError: Expecting value",
    "py-value-error": "ValueError: invalid literal for int() with base 10: 'x'",
    "py-key-error": "KeyError: 'missing'",
    "py-index-error": "IndexError: list index out of range",
    "py-too-many-open-files": "OSError: [Errno 24] Too many open files",
    "node-tsc-2304": "error TS2304: Cannot find name 'foo'",
    "node-tsc-2322": "error TS2322: Type 'X' is not assignable to type 'Y'",
    "node-jest-no-module": "Cannot find module 'express' from 'src/app.js'",
    "node-eslint-noconfig": "ESLint couldn't find a configuration file",
    "node-webpack-resolve": "Module not found: Error: Can't resolve 'lodash'",
    "node-nodemon-crash": "App crashed - waiting for file changes",
    "node-unhandled-rejection": "UnhandledPromiseRejectionWarning: something",
    "node-err-require-esm": "Error [ERR_REQUIRE_ESM]: require() of ES Module",
    "node-npm-elifecycle": "npm ERR! code ELIFECYCLE",
    "docker-invalid-cmd": "docker: 'blah' is not a docker command",
    "docker-copy-not-found": "COPY failed: file not found in build context",
    "docker-push-denied": "denied: requested access to the resource is denied",
    "docker-pull-denied": "Error response from daemon: pull access denied",
    "docker-exec-not-found": 'exec: "ls" : executable file not found in $PATH',
    "k8s-not-found": "Error from server (NotFound): pods not found",
    "k8s-crashloop": "CrashLoopBackOff",
    "k8s-imagepull": "ImagePullBackOff",
    "k8s-forbidden": "Error from server (Forbidden): forbidden",
    "k8s-progress-deadline": 'deployment "x" exceeded its progress deadline',
    "kubectl-context": "Unable to connect to the server: the server is currently unable to handle the request",
    "go-panic-nil": "panic: runtime error: invalid memory address or nil pointer dereference",
    "go-panic-waitgroup": "panic: sync: negative WaitGroup counter",
    "go-type-mismatch": "cannot use x (type int) as type string in assignment",
    "go-undefined": "undefined: foo",
    "go-no-go-files": "no Go files in /app",
    "go-test-fail": "--- FAIL: TestFoo (0.00s)",
    "go-signal-killed": "signal: killed (exit status 137)",
    "go-checksum-mismatch": "checksum mismatch in go.sum",
    "rust-e0502": "error[E0502]: cannot borrow `x` as mutable more than once",
    "rust-e0599": "error[E0599]: no method named `foo` found for type `X`",
    "rust-e0382": "error[E0382]: borrow of moved value: `x`",
    "rust-e0716": "error[E0716]: temporary value dropped while borrowed",
    "rust-e0308": "error[E0308]: mismatched types expected `u32` found `u8`",
    "rust-unwrap-none": "called `Option::unwrap()` on a `None` value",
    "rust-no-macro": "error: cannot find macro `println` in this scope",
    "rust-cargo-no-package": "failed to select a version for the requirement serde",
    "java-classnotfound": "java.lang.ClassNotFoundException: com.example.Foo",
    "java-noclassdeffound": "java.lang.NoClassDefFoundError: com/example/Foo",
    "java-nosuchmethod": "java.lang.NoSuchMethodError: com.example.Foo.bar()",
    "java-oom": "java.lang.OutOfMemoryError: Java heap space",
    "java-javac-notfound": "javac: file not found: Main.java",
    "java-gradle-no-java": "Could not determine Java version using executable",
    "ruby-loaderror": "LoadError: cannot load such file -- sinatra",
    "ruby-gemfile-not-found": "Bundler::GemfileNotFound",
    "ruby-secret-key": "Missing `secret_key_base` for 'production' environment",
    "ruby-name-error": "NameError: uninitialized constant FOO",
    "cc-linker-symbol": "ld: symbol(s) not found for architecture x86_64",
    "cc-linker-failed": "clang: error: linker command failed with exit code 1",
    "cc-undeclared": "error: use of undeclared identifier 'foo'",
    "cc-expected-semi": "error: expected ';' after expression",
    "cc-double-free": "free(): double free detected in tcache 2",
    "cc-corrupted-top": "malloc(): corrupted top size",
    "shell-fish-unknown": "fish: Unknown command: foo",
    "shell-bad-substitution": "bash: ${x}: bad substitution",
    "shell-unexpected-eof": "syntax error: unexpected end of file",
    "shell-command-subst": "command substitution: line 1: unexpected EOF",
    "shell-bash-line": "bash: line 10: cd: No such file or directory",
    "net-ssh-timeout": "ssh: connect to host example.com port 22: Connection timed out",
    "net-dns": "Name or service not known",
    "net-curl-7": "curl: (7) Failed to connect to host",
    "net-curl-28": "curl: (28) Operation timed out after 3000 ms",
    "net-curl-60": "curl: (60) SSL certificate problem: self signed certificate",
    "net-econnreset": "Connection reset by peer",
    "net-502": "502 Bad Gateway",
    "net-504": "504 Gateway Timeout",
    "net-cors": "Access-Control-Allow-Origin header is missing",
    "db-postgres-refused": "psycopg2.OperationalError: connection refused",
    "db-mysql-access": "Access denied for user 'root'@'localhost'",
    "db-redis-refused": "redis.exceptions.ConnectionError: Error 61 connecting",
    "db-sqlite-locked": "database is locked",
    "db-mongo-network": "MongoNetworkError: connection refused",
    "sys-too-many-open": "Too many open files",
    "sys-killed": "Out of memory: Killed process 1234 (java)",
    "sys-readonly": "Read-only file system",
    "sys-no-route": "No route to host",
    "pm-apt-locate": "E: Unable to locate package foo",
    "pm-apt-lock": "E: Could not get lock /var/lib/dpkg/lock",
    "pm-brew-no-formula": "brew: No available formula with the name foo",
    "pm-yum-no-package": "No package foo available",
    "ci-gitlab-no-config": "Could not find .gitlab-ci.yml file",
}


def test_each_rule_matches_a_sample():
    rule_ids = {r["id"] for r in RULES}
    assert set(SAMPLES) == rule_ids, (
        "SAMPLES must cover exactly the rule ids; missing=%s extra=%s"
        % (sorted(rule_ids - set(SAMPLES)), sorted(set(SAMPLES) - rule_ids))
    )
    for rid, text in SAMPLES.items():
        rule, m, others = find_matches(text)
        assert rule is not None, "no rule matched sample for %r: %r" % (rid, text)
        assert rule["id"] == rid, (
            "sample for %r matched %r instead (text=%r)"
            % (rid, rule["id"], text)
        )


# ---- existing tests (kept) ----

def test_git_not_repo():
    text = "fatal: not a git repository (or any of the parent directories): .git"
    rule, m, others = find_matches(text)
    assert rule is not None
    assert rule["id"] == "git-not-a-repo"


def test_module_not_found():
    text = "ModuleNotFoundError: No module named 'requests'"
    rule, m, others = find_matches(text)
    assert rule is not None
    assert rule["id"] == "py-modulenotfound"
    assert m.group("mod") == "requests"


def test_port_in_use():
    text = "Error: listen EADDRINUSE: address already in use :::3000"
    rule, m, others = find_matches(text)
    assert rule is not None
    assert rule["id"] == "port-in-use"


def test_no_match_returns_none():
    rule, m, others = find_matches("everything is fine, build succeeded")
    assert rule is None


def test_diagnose_runs(capsys):
    rc = diagnose("fatal: not a git repository")
    out = capsys.readouterr().out
    assert rc == 0
    assert "repository" in out.lower()


def test_cmd_not_found_named():
    text = "gitblub: command not found"
    rule, m, others = find_matches(text)
    assert rule is not None
    assert rule["id"] == "cmd-not-found"
    assert m.group("cmd") == "gitblub"


def test_cmd_not_found_title_no_none(capsys):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        diagnose("gitblub: command not found")
    assert "None" not in buf.getvalue()


def test_init_installs_shell_hook(monkeypatch):
    import types
    import tempfile
    import importlib
    import subprocess

    tmp = tempfile.mkdtemp()
    monkeypatch.setenv("HOME", tmp)
    monkeypatch.setenv("WHY_CONFIG_DIR", os.path.join(tmp, ".why"))
    monkeypatch.delenv("SHELL", raising=False)

    import why
    importlib.reload(why)
    args = types.SimpleNamespace(no_shell=False)
    why.cmd_init(args)

    hook = os.path.join(tmp, ".why", "why.sh")
    assert os.path.exists(hook), "shell hook not written"

    rc_path = why._detect_rc_file()
    with open(rc_path, "r", encoding="utf-8") as f:
        rc_content = f.read()
    assert "# why shell integration" in rc_content, "rc missing marker"

    subprocess.run(["bash", "-n", hook], check=True)
    import shutil
    if shutil.which("zsh"):
        subprocess.run(["zsh", "-n", hook], check=True)


# ---- quality feature tests (added) ----

import subprocess
import tempfile
import json as _json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(args, stdin=None, workdir=None, env=None):
    return subprocess.run(
        [sys.executable, os.path.join(REPO, "why.py")] + args,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=workdir or REPO,
        env=env,
    )


def test_json_output():
    proc = _run(["explain", "--json",
                 "ModuleNotFoundError: No module named 'requests'"])
    assert proc.returncode == 0, proc.stdout
    data = _json.loads(proc.stdout)
    assert data["rule_id"] == "py-modulenotfound"
    assert data["matched"] is True
    assert isinstance(data["fix"], list)
    assert "severity" in data
    assert "confidence" in data
    assert data["remediation"] is None


def test_severity_confidence_pretty():
    proc = _run(["explain", "ModuleNotFoundError: No module named 'requests'"])
    assert proc.returncode == 0, proc.stdout
    out = proc.stdout
    assert "confidence:" in out
    assert "severity:" in out


def test_fix_subcommand_no_exec():
    tmp = tempfile.mkdtemp()
    try:
        proc = _run(["fix", "fatal: not a git repository"],
                    stdin="n\n", workdir=tmp)
        assert proc.returncode == 0, proc.stdout
        assert "git init" in proc.stdout
        assert not os.path.exists(os.path.join(tmp, ".git"))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_contribute_temp():
    tmpf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    tmpf.close()
    tmp_path = tmpf.name
    try:
        env = dict(os.environ)
        env["WHYEX_CONTRIB_FILE"] = tmp_path
        proc = _run(
            ["contribute",
             "--error", "WeirdError: boom",
             "--title", "Weird Boom",
             "--why", "x",
             "--fix", "do thing"],
            env=env,
        )
        assert proc.returncode == 0, proc.stdout

        with open(tmp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Weird Boom" in content

        pytest_env = dict(os.environ)
        pytest_env.pop("WHYEX_CONTRIB_FILE", None)
        check = subprocess.run(
            ["python3", "-m", "pytest", "-q", "-k", "not contribute"],
            cwd=REPO,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=pytest_env,
        )
        assert check.returncode == 0, check.stdout
    finally:
        os.unlink(tmp_path)

# ---- regression tests (bug hunts) ----

def test_init_hook_has_functions_not_selfsource(monkeypatch):
    import types
    import tempfile
    import importlib

    tmp = tempfile.mkdtemp()
    monkeypatch.setenv("HOME", tmp)
    monkeypatch.setenv("WHY_CONFIG_DIR", os.path.join(tmp, ".why"))
    monkeypatch.delenv("SHELL", raising=False)

    import why
    importlib.reload(why)
    args = types.SimpleNamespace(no_shell=False)
    why.cmd_init(args)

    hook_path = os.path.join(tmp, ".why", "why.sh")
    with open(hook_path, "r", encoding="utf-8") as f:
        hook_content = f.read()
    assert "whyex()" in hook_content, "hook missing whyex() definition"
    assert '&& . "$HOME/.why/why.sh"' not in hook_content, "hook must not self-source"

    rc_path = why._detect_rc_file()
    with open(rc_path, "r", encoding="utf-8") as f:
        rc_content = f.read()
    assert "# why shell integration" in rc_content, "rc missing marker"
    assert '. "$HOME/.why/why.sh"' in rc_content, "rc missing source line"


def test_fix_formats_captured_port():
    proc = _run(["fix", "Error: address already in use :::3000"],
                stdin="n\n")
    assert proc.returncode == 0, proc.stdout
    assert ":3000" in proc.stdout
    assert "{port}" not in proc.stdout


def test_fix_unresolved_template_is_manual():
    proc = _run(["fix", "OSError: [Errno 98] Address already in use"], stdin="")
    assert proc.returncode == 0, proc.stdout
    assert "<placeholders>" not in proc.stdout or "no rule matched" in proc.stdout
    assert "Run this command?" not in proc.stdout

    proc = _run(["fix", "Error: listen EADDRINUSE: address already in use"], stdin="")
    assert proc.returncode == 0, proc.stdout
    assert "<placeholders>" in proc.stdout
    assert "{port}" in proc.stdout
    assert "Run this command?" not in proc.stdout


def test_run_json_is_pure():
    proc = _run(["run", "--json", "sh", "-c", "echo boom; exit 3"])
    assert proc.returncode == 3, proc.stdout
    stripped = proc.stdout.strip()
    assert len(stripped.splitlines()) == 1, proc.stdout
    data = _json.loads(stripped)
    assert isinstance(data, dict)
