#!/usr/bin/env python3
"""flac2alac - Convert all .flac files in a directory (recursively) to .m4a (ALAC)"""

import argparse
import signal
import sys
import subprocess
from pathlib import Path

def call_on_shell(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out + err).strip().decode('UTF-8')
    # return out.strip().decode('UTF-8'), err.strip().decode('UTF-8')

def convert_file(flac_file):
    out_file = flac_file.with_suffix('.m4a')
    tmp_file = flac_file.with_suffix('.tmp.m4a')

    if out_file.exists():
        print(f"Skipping (already exists): {out_file.name}")
        return True

    print(f"Converting: {flac_file.name}")

    try:
        output = call_on_shell(f'ffmpeg -loglevel error -y -i "{flac_file}" -c:v copy -c:a alac "{tmp_file}" 2>&1')
        if output:
            print(output)
            if tmp_file.exists():
                tmp_file.unlink()
            return False

        # Move temp file to final destination
        tmp_file.rename(out_file)
        print(f"    Successfully converted: {out_file}")
        return True
    except Exception as e:
        print(f"!!  Failed to convert: {flac_file}")
        print(f"    Error: {e}")
        if tmp_file.exists():
            tmp_file.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert all .flac files in a directory (recursively) to .m4a (ALAC)'
    )
    parser.add_argument('directory', help='Directory to search for .flac files')
    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: '{directory}' does not exist.")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    # Convert to absolute path
    directory = directory.resolve()

    print(f"Searching for .flac files in: {directory}")
    print()

    # Find all .flac files recursively
    flac_files = list(directory.rglob('*.flac')) + list(directory.rglob('*.FLAC'))

    if not flac_files:
        print("No .flac files found.")
        return

    print(f"Found {len(flac_files)} .flac file(s)")
    print()

    # Convert each file
    any_conversion_failed = False
    for flac_file in flac_files:
        if not convert_file(flac_file):
            any_conversion_failed = True
            break

    # Ask for deletion if no failures occurred
    if not any_conversion_failed:
        print()
        response = input("Delete original .flac files? (y/N): ").strip().lower()
        if response == 'y' or response == 'yes':
            print("Deleting .flac files...")
            deleted_count = 0
            for flac_file in flac_files:
                if flac_file.exists():
                    flac_file.unlink()
                    deleted_count += 1
            print(f"Deleted {deleted_count} .flac file(s).")
        else:
            print("Keeping original .flac files.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
