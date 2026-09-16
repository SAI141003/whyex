# Release / Distribution Checklist

Package: `whyex` · version `0.1.0` · repo `https://github.com/SAI141003/whyex` · license MIT

## 1. Create the GitHub repository

- [ ] Push this project to `https://github.com/SAI141003/whyex`.
- [ ] Confirm workflows are enabled (Actions tab).

## 2. PyPI via Trusted Publishing (no tokens)

One-time setup:

- [ ] On PyPI, go to *Account settings → Publishing → Add a new pending publisher*.
- [ ] Fill in: PyPI project name `whyex`, owner `SAI141003`, repository `whyex`,
      workflow name `release.yml`, environment `pypi`.

Publish:

- [ ] Tag and push:
      ```sh
      git tag v0.1.0 && git push origin v0.1.0
      ```
- [ ] The `Release` action builds sdist + wheel and publishes to PyPI via
      OIDC (`id-token: write`) — no API token needed.

Manual fallback (token-based):

```sh
python -m pip install -U build twine
python -m build
python -m twine upload --repository pypi dist/*   # uses PYPI_API_TOKEN
```

Set `PYPI_API_TOKEN` in your shell or export it before uploading.

## 3. Post-publish verification

```sh
python3 -m venv /tmp/whyex-check && source /tmp/whyex-check/bin/activate
pip install whyex
whyex --version
whyex explain "fatal: not a git repository"
deactivate
```

All three commands must succeed and the explain output must show a fix hint.

## 4. Homebrew tap

- [ ] Compute the release tarball checksum:
      ```sh
      curl -L https://github.com/SAI141003/whyex/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256
      ```
- [ ] Replace `REPLACE_WITH_RELEASE_SHA256` in `homebrew/why.rb` with that value.
- [ ] Create tap repo `https://github.com/SAI141003/homebrew-whyex` containing
      `Formula/whyex.rb` (copy of the updated `homebrew/why.rb`; rename class if desired).
- [ ] Verify install from a clean machine:
      ```sh
      brew install SAI141003/whyex/whyex
      whyex --version
      ```

## 5. Binaries

- [ ] The `Binaries` workflow runs automatically on tag `v*`: builds one-file
      executables on macOS and Ubuntu with PyInstaller and attaches
      `dist/whyex*` artifacts to the GitHub Release.
- [ ] Check the Release page for the built `whyex-*` assets after the run finishes.
