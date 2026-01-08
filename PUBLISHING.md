# MahkrabCLI cheat sheet (dev, install, release)

This project publishes the Python distribution `mahkrab` and installs the command `mk` via `[project.scripts]`.

## Quick facts

- End users should prefer `pipx install mahkrab` (isolated + puts `mk` on `PATH`).
- `pip install mahkrab` is best inside a virtual environment.
- Ubuntu/Debian may block system-wide `pip install` (PEP 668 “externally-managed-environment”); use `pipx` or a venv.
- PyPI requires a new `version` for every upload (no overwriting).

## Install (fresh computer)

### A) `pipx` (recommended for end users)

Install pipx:
- **Ubuntu/WSL2**: `sudo apt update && sudo apt install -y pipx && pipx ensurepath`
- **macOS**: `brew install pipx && pipx ensurepath`
- **Windows** (PowerShell): `py -m pip install --user pipx` then `py -m pipx ensurepath`

Install Mahkrab:
- `pipx install mahkrab`
- Verify: `mk -h` and `mk --version`

Upgrade later:
- `pipx upgrade mahkrab`

### B) `pip` inside a venv (recommended for development/testing)

Create and use a venv:
- **Linux/macOS**:
  - `python3 -m venv .venv`
  - `. .venv/bin/activate`
- **Windows**:
  - `py -m venv .venv`
  - `.venv\Scripts\activate`

Install and verify:
- `python -m pip install -U pip`
- `python -m pip install mahkrab`
- `mk -h`
- `mk --version`

Upgrade later:
- `python -m pip install -U mahkrab`

### C) `pip` without a venv (not recommended)

This varies by OS and can fail on Ubuntu/Debian (PEP 668).

If you *must*:
- `python3 -m pip install --user mahkrab`
- Ensure your user scripts directory is on `PATH` (otherwise `mk` won’t be found).

## Uninstall / cleanup

### Uninstall a `pipx` install

- `pipx uninstall mahkrab`
- (Optional) remove all pipx environments: `pipx uninstall-all`

### Uninstall a venv-based install

Inside the venv:
- `pip uninstall mahkrab`

Remove the venv entirely (fastest “clean slate”):
- `deactivate` (if active)
- `rm -rf .venv` (Linux/macOS) or delete the `.venv` folder (Windows)

### Uninstall a `pip --user` install

- `python3 -m pip uninstall mahkrab`

## Test installs (prove what a user will see)

### Test PyPI install with a completely fresh temporary venv (recommended)

Linux/macOS:
- `python3 -m venv /tmp/mk-pypi-test`
- `. /tmp/mk-pypi-test/bin/activate`
- `python -m pip install -U pip`
- `python -m pip install mahkrab`
- `mk --version`
- `mk -h`
- `deactivate && rm -rf /tmp/mk-pypi-test`

Windows (PowerShell):
- `py -m venv $env:TEMP\mk-pypi-test`
- `& $env:TEMP\mk-pypi-test\Scripts\Activate.ps1`
- `py -m pip install -U pip`
- `py -m pip install mahkrab`
- `mk --version`
- `mk -h`
- `deactivate` then delete `$env:TEMP\mk-pypi-test`

### Test `pipx` install (clean)

- `pipx uninstall mahkrab 2>/dev/null || true`
- `pipx install mahkrab`
- `mk --version`
- `mk -h`

## Day-to-day development (editable installs)

### Editable install in a venv (recommended)

From repo root (has `pyproject.toml`):
- `python3 -m venv .venv`
- `. .venv/bin/activate`
- `python -m pip install -U pip`
- `python -m pip install -e .`

Now edits in your repo are reflected immediately when running:
- `mk ...` (uses the venv entrypoint)

If you change packaging metadata (entry points, dependencies), reinstall:
- `python -m pip install -e . --upgrade`

### Editable install with `pipx` (optional)

This is handy if you want a global-ish `mk` while still developing from the repo:
- `pipx install -e .`

Edits in the repo should reflect immediately because pipx points at your local path.

If you later want the published version instead:
- `pipx uninstall mahkrab`
- `pipx install mahkrab`

## Release to PyPI (production)

### Before you upload

- Ensure `pyproject.toml` `version` is bumped (PyPI rejects re-uploads of the same version).
- Clean old build artifacts so you only upload the new version:
  - `rm -rf dist build *.egg-info src/*.egg-info`

### Release using a venv (recommended; avoids PEP 668 issues)

From repo root:
- `. .venv/bin/activate` (or create it if you don’t have one)
- `python -m pip install -U pip build twine`
- `python -m build`
- `python -m twine upload dist/*`
  - Username: `__token__`
  - Password: your **PyPI** token (not TestPyPI)

### Release “without a venv” (practical alternatives)

On PEP-668 systems, the safest “no venv” approach is to use `pipx run` (ephemeral envs):
- `pipx run build`
- `pipx run twine upload dist/*`

You can also install `build`/`twine` into your user site-packages on some systems:
- `python3 -m pip install --user -U build twine`
- `python3 -m build`
- `python3 -m twine upload dist/*`

### After you upload

Verify like a new user (temporary venv):
- `python3 -m venv /tmp/mk-verify && . /tmp/mk-verify/bin/activate`
- `python -m pip install -U pip`
- `python -m pip install -U mahkrab`
- `mk --version`
- `deactivate && rm -rf /tmp/mk-verify`

Tell users to upgrade:
- `pipx upgrade mahkrab`
- or `pip install -U mahkrab` (in their venv)

## When to use TestPyPI (and how)

Use TestPyPI when you want to verify packaging/metadata/installability *without* affecting real users.

Upload to TestPyPI:
- `python -m twine upload --repository testpypi dist/*`

Install from TestPyPI with `pip` (fresh venv recommended):
- `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mahkrab`

Install from TestPyPI with `pipx`:
- `pipx install --pip-args="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple" mahkrab`

Notes:
- Tokens are not interchangeable: TestPyPI tokens work only on TestPyPI; PyPI tokens work only on PyPI.
- TestPyPI is not permanent storage; projects/accounts can be wiped occasionally.

