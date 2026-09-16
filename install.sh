#!/bin/sh
set -euo pipefail

PYTHON_MIN="3.7"

echo "======================================="
echo "  Installing whyex ..."
echo "  by Sai Koushik Yaganti"
echo "  https://github.com/SAI141003/whyex"
echo "======================================="

# --- Locate a python interpreter -------------------------------------------
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "Error: Python $PYTHON_MIN or newer was not found on your system."
  echo "Please install Python 3.7+ from https://www.python.org/downloads/"
  echo "or via your package manager (e.g. 'brew install python'), then re-run this installer."
  exit 1
fi

# --- Install ----------------------------------------------------------------
if command -v pipx >/dev/null 2>&1; then
  echo "pipx detected - installing 'whyex' into an isolated environment."
  pipx install whyex
else
  echo "Installing 'whyex' for the current user with pip."
  if ! "$PYTHON" -m pip install --user whyex; then
    echo "----------------------------------------------------------------"
    echo "Warning: the normal 'pip install --user' attempt failed."
    echo "Your Python may be externally managed (PEP 668). Retrying with"
    echo "'--break-system-packages'. This installs into your system Python"
    echo "and may conflict with OS packages - prefer a venv or pipx instead."
    echo "----------------------------------------------------------------"
    "$PYTHON" -m pip install --user --break-system-packages whyex
  fi
fi

echo ""
echo "Done! 'whyex' is installed."
echo ""
echo "Next steps:"
echo "  whyex --version     Verify the installation"
echo "  whyex init          Enable shell auto-explain (hook into your shell)"
echo "  whyex list          See everything 'why' knows how to diagnose"
echo ""
echo "Get started:"
echo "  whyex run <command>   Run a command and explain failures automatically"
echo "  whyex                 Explain the last failed command"
echo ""
echo "If 'whyex' is not on your PATH, ensure your user bin directory"
echo "(e.g. ~/.local/bin or \$(pipx environment)) is on your PATH."
