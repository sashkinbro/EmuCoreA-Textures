#!/usr/bin/env python3
"""Print immutable metadata for a PPSSPP ZIP and optionally check its format."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from validate_pack import validate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    result = validate(str(args.archive))
    result["path"] = str(args.archive)
    result["sha256"] = sha256(args.archive)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
