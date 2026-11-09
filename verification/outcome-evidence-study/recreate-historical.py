#!/usr/bin/env python3
"""Recreate the frozen selective historical input from a local Git checkout."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

REVISION = "c578659143f400b7a56f444d4d9773b5a813394b"
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_repo", type=Path, help="Git checkout containing the historical commit")
    parser.add_argument("destination", type=Path, help="new directory for the selective copy")
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        parser.error("destination must not already exist")
    entries = []
    for line in (HERE / "freeze/historical-sha256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        name = name.removeprefix("./")
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe manifest path: {name}")
        entries.append((digest, name))
    tracked = [name for _, name in entries if name != "EXERCISE.md"]
    with tempfile.TemporaryDirectory(prefix="outcome-study-") as temp:
        archive = Path(temp) / "snapshot.tar"
        subprocess.run(["git", "-C", str(args.source_repo), "archive", "--format=tar",
                        "--output", str(archive), REVISION, "--", *tracked], check=True)
        destination.mkdir(parents=True)
        with tarfile.open(archive) as tar:
            tar.extractall(destination, filter="data")
    shutil.copyfile(HERE / "historical/EXERCISE.md", destination / "EXERCISE.md")
    failures = []
    for expected, name in entries:
        path = destination / name
        if not path.is_file():
            failures.append(f"missing {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(f"changed {name}")
    if failures:
        raise SystemExit("Manifest verification failed:\n" + "\n".join(failures))
    print(f"Verified {len(entries)} files at {destination} (including the exercise task; source commit {REVISION})")


if __name__ == "__main__":
    main()
