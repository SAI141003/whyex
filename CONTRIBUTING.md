# Contributing to whyex

Thanks for helping improve **whyex**.

`whyex` turns raw error messages into plain-English diagnoses and fixes.  
Its value grows with every diagnostic rule — so **rules are the main contribution**.

- **Author / maintainer:** Sai Koushik Yaganti ([@SAI141003](https://github.com/SAI141003))
- **Command / package:** `whyex`
- **Python:** 3.7+ · **Runtime dependencies:** none (keep it that way)
- **License:** MIT
- **Tests:** `make test` or `python3 -m pytest -q`

## Quick start

```bash
git clone https://github.com/SAI141003/whyex.git
cd whyex
pip install -e .
make test
```

All tests should pass before you change anything.

## Adding a diagnostic rule

Rules live in `rules.py` as plain dicts. Append yours to the list:

```python
{
    "id": "py-modulenotfound",
    "tags": ["python", "imports"],
    "match": r"ModuleNotFoundError: No module named ['\"]?(?P<mod>[^'\"]+)",
    "title": "Missing Python package: {mod}",
    "why": (
        "Python cannot find the module in the interpreter that ran the script. "
        "Usually the package was never installed there, or the wrong "
        "virtualenv/interpreter is active."
    ),
    "fix": [
        "Install with the active interpreter: python -m pip install {mod}",
        "Still failing? Check which env is active: which python",
    ],
    # Optional:
    "severity": "error",
    "remediation": "python -m pip install <package>",
    "priority": 2,
}
```

**Required keys:** `id`, `tags`, `match`, `title`, `why`, `fix`.

### Naming the id

- kebab-case, prefixed by area: `py-…`, `node-…`, `k8s-…`, `docker-…`, `git-…`
- Name the condition, not a vague symptom
- Grep `rules.py` first — duplicate ids fail CI

### Choosing tags

Lowercase. Reuse existing tags when possible. Two or three is enough.

### Writing the match regex

Matching sorts by `(priority, len(match))` descending — **specific beats generic**.

- Anchor on stable phrases from real output
- Skip volatile bits (absolute paths, versions, hostnames)
- Prefer long precise patterns over short catch-alls
- Use `"priority": 2` only when a broader existing rule would otherwise win

### Writing title, why, fix

- `title`: one line stating the problem as the user sees it
- `why`: root cause and typical trigger
- `fix`: 1–4 ordered steps with copy-pasteable commands

## Using `whyex contribute`

```bash
whyex contribute \
  --error "ECONNREFUSED 127.0.0.1:6379" \
  --title "Redis is unreachable" \
  --why "Nothing is listening on the configured Redis port." \
  --fix "Start redis-server, then retry the app."
```

This writes a literal-match rule into `contrib_rules.py`. Before opening a PR:

1. Move the finished rule into `rules.py`
2. Tighten `match` into a proper regex
3. Remove it from `contrib_rules.py`
4. Add a `SAMPLES` entry in `tests/test_why.py`

## Optional: auto-fix remediation

Add `remediation` only when one shell command cleanly fixes the problem:

- Safe and non-destructive
- Never `rm -rf`, force pushes, or data deletion
- Placeholders like `<package>` are never auto-executed

## Testing

```bash
python3 -m pytest -q
```

## PR checklist

- [ ] Id is new, kebab-case, area-prefixed
- [ ] `match` regex compiles
- [ ] `SAMPLES` entry added; tests green
- [ ] `title` / `why` / `fix` are clear
- [ ] No new runtime dependencies

Questions? Open an issue or contact the maintainer:

- GitHub: [@SAI141003](https://github.com/SAI141003)
- Email: saiyaganti14@gmail.com
