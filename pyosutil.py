#!/usr/bin/env python3
"""pyosutil - utility CLI for filesystems and drives.

Currently provides:
  copy  - copy files/folders across drives with resume support.
"""

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path


STATE_FILE = "pyosutil_copy_state.json"
CHUNK_BUF_SIZE = 1024 * 1024  # 1 MiB


def _size(path):
    try:
        return os.stat(path).st_size
    except OSError:
        return -1


def verbatim_copy(src, dst):
    """Copy src file -> dst file byte-for-byte in chunks (handles huge files)."""
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(CHUNK_BUF_SIZE)
            if not chunk:
                break
            fout.write(chunk)


def collect_files(src_root):
    """Return list of posix-relative file paths under src_root."""
    files = []
    for root, _dirs, fnames in os.walk(src_root):
        for f in fnames:
            abs_f = os.path.join(root, f)
            files.append(os.path.relpath(abs_f, src_root).replace(os.sep, "/"))
    return files


def load_state(state_path):
    if Path(state_path).exists():
        try:
            with open(state_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_state(state_path, data):
    tmp = state_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, state_path)


def _copy_layout(args, src_is_file, src):
    """Build and return (src_root, files, dst_target_or_base)."""
    if src_is_file:
        src_root = os.path.dirname(src)
        files = [os.path.basename(src)]
        dst_target = os.path.abspath(args.dst)
        os.makedirs(os.path.dirname(dst_target), exist_ok=True)
        return src_root, files, dst_target
    src_root = os.path.abspath(src)
    files = collect_files(src_root)
    if args.no_folder:
        dst_base = os.path.abspath(args.dst)
    else:
        dst_base = os.path.join(os.path.abspath(args.dst), os.path.basename(src.rstrip(os.sep)))
    os.makedirs(dst_base, exist_ok=True)
    return src_root, files, dst_base


def copy_command(args):
    src = os.path.abspath(args.src)

    if not os.path.exists(src):
        print(f"ERROR: source does not exist: {src}")
        return 1

    src_is_file = os.path.isfile(src)
    single = src_is_file
    src_root, files, dst_target = _copy_layout(args, src_is_file, src)

    uses_resume = bool(args.continue_)
    state_path = os.path.join(os.path.abspath(args.state or "."), STATE_FILE)
    state = load_state(state_path) if uses_resume else None

    if state:
        completed = set(state.get("completed_files", []))
        print(f"Resuming copy: {len(completed)} files already completed.")
    else:
        completed = set()
        if uses_resume:
            save_state(state_path, {
                "copy": {"src_root": src_root, "src_is_file": src_is_file,
                         "dst_target": dst_target},
                "completed_files": [],
                "updated_at": datetime.datetime.now().isoformat(),
            })

    total = len(files)
    done = 0
    copied = 0
    skipped = 0
    errors = []
    start_time = time.time()

    for rel in files:
        abs_src = os.path.join(src_root, rel)
        abs_dst = dst_target if single else os.path.join(dst_target, rel)

        # Skip files completed in a previous run, but only if the destination
        # actually exists and is complete (size matches source).
        if uses_resume and rel in completed:
            src_size = _size(abs_src)
            dst_size = _size(abs_dst) if os.path.exists(abs_dst) else -1
            if dst_size >= 0 and (src_size < 0 or dst_size == src_size):
                done += 1
                skipped += 1
                continue

        os.makedirs(os.path.dirname(abs_dst), exist_ok=True)

        try:
            verbatim_copy(abs_src, abs_dst)
            completed.add(rel)
            copied += 1
        except Exception as exc:
            errors.append((rel, str(exc)))
            print(f"  ERROR copying {rel}: {exc}")

        done += 1
        if done % 100 == 0 or done == total:
            print(f"  [{done}/{total}] copied={copied} skipped={skipped}")

        if uses_resume:
            save_state(state_path, {
                "copy": {"src_root": src_root, "src_is_file": src_is_file,
                         "dst_target": dst_target},
                "completed_files": sorted(completed),
                "updated_at": datetime.datetime.now().isoformat(),
            })

    elapsed = time.time() - start_time
    print()
    print(f"Done: {copied} copied, {skipped} already-present, {len(errors)} errors in "
          f"{elapsed:.1f}s (files in destination: {len(files)}).")
    if errors:
        for rel, err in errors:
            print(f"  {rel}: {err}")
        return 1
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pyosutil",
        description="Utility toolkit (copy files/folders across drives with resume).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    copy = sub.add_parser(
        "copy",
        help="Copy a file or folder from one drive/location to another.",
    )
    copy.add_argument("src", help="Source file or folder path.")
    copy.add_argument(
        "dst",
        help="Destination. For a single file, this is the full destination file path. "
             "For a folder, this is the parent folder that will receive the copied "
             "folder (or its contents with --no-folder).",
    )
    copy.add_argument(
        "-c", "--continue",
        dest="continue_",
        action="store_true",
        help="Continue a previously interrupted copy, skipping files already fully copied.",
    )
    copy.add_argument(
        "--state",
        default=".",
        help="Directory where the resume state file is stored (default: current dir).",
    )
    copy.add_argument(
        "--no-folder",
        action="store_true",
        help="For folder copies, copy the contents directly into the destination, "
             "instead of creating a subfolder named after the source.",
    )
    copy.set_defaults(func=copy_command)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
