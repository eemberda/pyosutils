# pywinutil

Windows utility CLI. Called from any terminal as `pywinutil`.

## Install

Make it callable globally from any terminal:

    pip install -e .

This registers the `pywinutil` command (via the Python `Scripts` directory, which is on PATH).

Alternatively, without installing, add this folder to your PATH and use the
`pywinutil.cmd` wrapper:

    pywinutil.cmd copy C:\data\docs D:\backup

## Usage

Copy a folder from one drive to another (destination parent folder):

    pywinutil copy D:\data\docs E:\backup

Copy a folder's contents directly into the destination (no subfolder):

    pywinutil copy D:\data\docs E:\backup --no-folder

Copy a single file to a specific destination file:

    pywinutil copy D:\data\docs\report.xlsx E:\backup\report.xlsx

### Resume (--continue)

If a copy is interrupted (disk unplugged, disconnect, crash), re-run with
`--continue` to resume. Files already fully copied are skipped; only missing
files are copied again.

    pywinutil copy D:\data\docs E:\backup --continue

State is stored in `pywinutil_copy_state.json`. Use `--state <dir>` to choose
where the state file lives (default: current directory):

    pywinutil copy D:\data\docs E:\backup --continue --state E:\backup\.pywinutil

> Note: within a single large file, copy resumes per-file only. A file that
> was still mid-copy when interrupted is re-copied from scratch.

Run `pywinutil copy --help` for all options.