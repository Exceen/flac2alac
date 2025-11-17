#!/usr/bin/env python3
"""alac2flac - Convert all .m4a files (ALAC) in a directory (recursively) to .flac"""

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

def convert_file(alac_file):
    out_file = alac_file.with_suffix('.flac')
    tmp_file = alac_file.with_suffix('.tmp.flac')

    if out_file.exists():
        print(f"Skipping (already exists): {out_file.name}")
        return True

    print(f"Converting: {alac_file.name}")

    try:
        output = call_on_shell(f'ffmpeg -loglevel error -y -i "{alac_file}" -c:a flac "{tmp_file}" 2>&1')
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
        print(f"!!  Failed to convert: {alac_file}")
        print(f"    Error: {e}")
        if tmp_file.exists():
            tmp_file.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert all .m4a files (ALAC) in a directory (recursively) to .flac'
    )
    parser.add_argument('directory', help='Directory to search for .m4a files')
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

    print(f"Searching for .m4a files in: {directory}")
    print()

    # Find all .m4a files recursively
    alac_files = list(directory.rglob('*.m4a')) + list(directory.rglob('*.M4A'))

    if not alac_files:
        print("No .m4a files found.")
        return

    print(f"Found {len(alac_files)} .m4a file(s)")
    print()

    # Convert each file
    any_conversion_failed = False
    for alac_file in alac_files:
        if not convert_file(alac_file):
            any_conversion_failed = True
            break

    # Ask for deletion if no failures occurred
    if not any_conversion_failed:
        print()
        response = input("Delete original .m4a files? (y/N): ").strip().lower()
        if response == 'y' or response == 'yes':
            print("Deleting .m4a files...")
            deleted_count = 0
            for alac_file in alac_files:
                if alac_file.exists():
                    alac_file.unlink()
                    deleted_count += 1
            print(f"Deleted {deleted_count} .m4a file(s).")
        else:
            print("Keeping original .m4a files.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
