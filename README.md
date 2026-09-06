# pyosutil

Utility CLI for filesystems and drives. Called from any terminal as `pyosutil`.

Currently provides a `copy` command that copies files/folders between drives
(any drives or locations) with resume support for interrupted copies.

## Requirements

- **Python 3.9+** on Windows (works on other OSes too)
  - Check: `python --version`
- **pip** (bundled with Python)
  - Check: `pip --version`
- **Git** (only needed to clone the repository, optional)

No third-party Python packages are required — the tool uses only the standard
library.

### Installing Python (if not already installed)

If `python --version` shows nothing or errors, install Python first:

1. Download the installer from <https://www.python.org/downloads/>.
2. Run the installer and **check the box `Add python.exe to PATH`** before
   clicking Install.
3. Reopen your terminal so the new PATH takes effect.
4. Verify: `python --version` and `pip --version`.

> On Windows your package manager can also install Python, e.g.
> `winget install Python.Python.3.12`. Any version 3.9+ works.

## Getting Started

Clone the repository and install it:

    git clone https://github.com/eemberda/pyosutils.git
    cd pyosutils
    pip install -e .

This registers the `pyosutil` command globally (via Python's `Scripts`
directory, which is on PATH). Reopen the terminal and verify it works:

    pyosutil --help

> If `pyosutil` is not recognized, your Python `Scripts` directory may not be
> on PATH. Find it with `python -c "import sys; print(sys.prefix + '\\Scripts')"`
> and add it to your PATH, then reopen the terminal.

### Alternative install (no pip install)

If you don't want to install the package, you can still call it globally:

1. Clone or copy this folder (must keep `pyosutil.py` and `pyosutil.cmd` together).
2. Add this folder to your PATH (Environment Variables > Path).
3. Reopen the terminal and run `pyosutil` as usual.

## Usage

Copy a folder from one drive to another (destination parent folder):

    pyosutil copy D:\data\docs E:\backup

Copy a folder's contents directly into the destination (no subfolder):

    pyosutil copy D:\data\docs E:\backup --no-folder

Copy a single file to a specific destination file:

    pyosutil copy D:\data\docs\report.xlsx E:\backup\report.xlsx

### Resume (--continue)

If a copy is interrupted (disk unplugged, disconnect, crash), re-run with
`--continue` to resume. Files already fully copied are skipped; only missing
or incomplete files are copied again.

    pyosutil copy D:\data\docs E:\backup --continue

State is stored in `pyosutil_copy_state.json`. Use `--state <dir>` to choose
where the state file lives (default: current directory):

    pyosutil copy D:\data\docs E:\backup --continue --state E:\backup\.pyosutil

> Note: within a single large file, copy resumes per-file only. A file that
> was still mid-copy when interrupted is re-copied from scratch.

Run `pyosutil copy --help` for all options.