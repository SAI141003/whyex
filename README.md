# whyex

**Your terminal errors, explained in plain English — instantly, offline.**

![whyex demo](docs/demo.png)

**Author:** [Sai Koushik Yaganti](https://github.com/SAI141003) · **License:** MIT  
**Repo:** https://github.com/SAI141003/whyex

[![CI](https://github.com/SAI141003/whyex/actions/workflows/ci.yml/badge.svg)](https://github.com/SAI141003/whyex/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

---

## What is whyex?

`whyex` is a small command-line tool that **reads an error message from your terminal** and tells you:

1. **What** went wrong  
2. **Why** it happened  
3. **How** to fix it (exact commands)

It works **offline**. No API key. No ChatGPT. No copying errors into Google.  
It uses a curated set of **144 rules** for common failures across git, Python, Node, Docker, and more.

Think of it as a pocket guide that lives inside your terminal.

---

## What problem does it solve?

If you write code, you’ve lived this loop:

1. You run a command (`git push`, `npm install`, `python app.py`, `docker build`…)  
2. It fails with a cryptic message  
3. You leave the terminal, open a browser, search Stack Overflow  
4. You skim 3–4 answers that almost match  
5. You come back and try something  
6. Ten minutes are gone — often for an error you’ve seen before

**whyex short-circuits that loop.**

When the same class of error shows up again — missing package, not a git repo, port already in use, Docker daemon down — you stay in the terminal and get a clear explanation plus a fix in seconds.

### Who it’s for

- Students learning to code who don’t know what `ModuleNotFoundError` means yet  
- Developers who hit the same git / npm / Docker errors every week  
- Anyone who wants a fast, private answer without pasting logs into an AI chat  
- People on planes, locked-down machines, or offline environments

### What it’s *not*

- Not an AI model — it only explains errors it knows (144 rules today)  
- Not a debugger for bugs in *your* application logic  
- Not a replacement for reading docs when something is truly new

If it doesn’t recognize an error, it stays quiet instead of guessing.

---

## How to use it in daily life

Here are the everyday workflows:

### A) You just got an error — paste it

```bash
whyex explain "ModuleNotFoundError: No module named 'requests'"
```

```bash
whyex explain "fatal: not a git repository"
```

```bash
whyex explain "Error: listen EADDRINUSE: address already in use :::3000"
```

**When to use:** you already see the red text and want a plain-English answer now.

---

### B) You’re about to run something that might fail

```bash
whyex run npm test
whyex run python app.py
whyex run git push
```

**When to use:** tests, builds, deploys — if it fails, whyex explains automatically.

---

### C) Your build already dumped a wall of logs

```bash
make 2>&1 | whyex
npm install 2>&1 | whyex
docker compose up 2>&1 | whyex
```

**When to use:** long output where the real error is buried in the log.

---

### D) You want it to suggest (and optionally run) the fix

```bash
whyex fix "fatal: not a git repository"
```

whyex shows the diagnosis, prints something like `git init`, then asks:

```text
Run this command? [y/N]
```

Nothing runs unless you say yes.  
**When to use:** common, safe fixes you’re happy to confirm.

---

### E) Make every failed command explain itself (optional)

```bash
whyex init
```

Open a **new** terminal, then:

```bash
whyex npm test
whyex python script.py
```

If the command fails, whyex explains it automatically.  
**When to use:** you want this as a daily habit in your shell.

---

## Install (one time)

```bash
git clone https://github.com/SAI141003/whyex.git
cd whyex
pip install -e .
whyex --version
```

> After PyPI publish: `pip install whyex` or `pipx install whyex`.

Requires **Python 3.7+**.

---

## Command cheat sheet

| What you want | Command |
|---------------|---------|
| Explain a pasted error | `whyex explain "error text"` |
| Run a command + explain on fail | `whyex run <command>` |
| Explain piped logs | `cmd 2>&1 \| whyex` |
| Diagnose + offer a fix | `whyex fix "error text"` |
| JSON for tools / CI | `whyex explain --json "..."` |
| See all known errors | `whyex list` |
| Turn on shell auto-explain | `whyex init` |

---

## Real examples

**Missing Python package**

```bash
whyex explain "ModuleNotFoundError: No module named 'requests'"
```

→ Explains the active environment is missing `requests`, and shows how to install it with the right `python -m pip`.

**Not inside a git repo**

```bash
whyex explain "fatal: not a git repository"
```

→ Explains you’re outside a `.git` folder, and suggests `git init` or `cd` into the project.

**Port already in use**

```bash
whyex explain "Error: listen EADDRINUSE: address already in use :::3000"
```

→ Explains another process owns port 3000, and shows how to find/kill it or change the port.

---

## What it covers today

**144 rules** across **27 categories**, including:

| Area | Everyday errors |
|------|-----------------|
| Git | not a repo, push rejected, detached HEAD, SSH key issues |
| Python | ModuleNotFoundError, SyntaxError, pip / venv problems |
| Node / npm | missing modules, permission errors, engine mismatches |
| Go / Rust / Java / Ruby | missing toolchain, compile / panic / gem errors |
| C / C++ | missing headers, linker errors, segfaults |
| Docker / Kubernetes | daemon down, CrashLoopBackOff, ImagePullBackOff |
| Shell / network / DB | command not found, SSL, Postgres/Redis connection refused |

---

## How it works (simple)

1. **Capture** the error text  
2. **Match** it against the rule book (specific patterns win over vague ones)  
3. **Explain** with severity + confidence + numbered fixes  
4. **Optionally fix** — only after you confirm  

No telemetry. Nothing leaves your machine.

---

## Contribute a new error

Hit something whyex doesn’t know yet?

```bash
whyex contribute \
  --error "WeirdError: boom" \
  --title "Weird Boom" \
  --why "The foo service is down." \
  --fix "restart foo"
```

Then open a PR. Guide: [CONTRIBUTING.md](CONTRIBUTING.md)

```bash
make test
```

---

## Author

**Sai Koushik Yaganti**  
GitHub: [@SAI141003](https://github.com/SAI141003)  
LinkedIn: [saikoushikyaganti](https://www.linkedin.com/in/saikoushikyaganti/)  
Email: saiyaganti14@gmail.com

---

## License

MIT — see [LICENSE](LICENSE).
