#!/usr/bin/env python3
"""Repack a PPSSPP source directory/ZIP with only referenced assets.

The source pack is never modified. The output keeps textures.ini, every image
referenced by its [hashes] section, and common attribution files when present.
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

HASH_LINE = re.compile(r"^\s*([0-9A-Fa-f]{8,32})\s*=\s*(.*?)\s*$")
KEEP_DOCS = {"license", "license.txt", "copying", "copying.md", "readme.md", "credits.txt"}


def clean(name: str) -> str:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in path.parts):
        raise ValueError(f"unsafe path: {name}")
    return "/".join(path.parts)


def read_sources(source: Path) -> dict[str, bytes]:
    if source.is_dir():
        return {
            clean(str(item.relative_to(source).as_posix())): item.read_bytes()
            for item in source.rglob("*")
            if item.is_file()
        }
    with zipfile.ZipFile(source) as archive:
        result: dict[str, bytes] = {}
        for info in archive.infolist():
            if not info.is_dir():
                result[clean(info.filename)] = archive.read(info)
        # Remove a GitHub codeload wrapper when present.
        ini = next((key for key in result if key.casefold().endswith("/textures.ini") or key.casefold() == "textures.ini"), None)
        if ini and ini.casefold() != "textures.ini":
            prefix = ini[: -len("textures.ini")]
            result = {key[len(prefix):]: value for key, value in result.items() if key.startswith(prefix)}
        return result


def referenced_paths(ini: str) -> set[str]:
    paths: set[str] = {"textures.ini"}
    in_hashes = False
    for line in ini.splitlines():
        section = line.strip().casefold()
        if section.startswith("["):
            in_hashes = section == "[hashes]"
            continue
        if not in_hashes or not line.strip() or line.lstrip().startswith("#"):
            continue
        match = HASH_LINE.match(line)
        if match and match.group(2).strip():
            target = match.group(2).split("#", 1)[0].strip().replace("\\", "/")
            paths.add(clean(target))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    files = read_sources(args.source)
    ini_key = next((key for key in files if key.casefold() == "textures.ini"), None)
    if ini_key is None:
        raise SystemExit("source has no root textures.ini")
    ini = files[ini_key].decode("utf-8-sig")
    keep = referenced_paths(ini)
    missing = sorted(path for path in keep if path.casefold() not in {key.casefold() for key in files})
    if missing:
        raise SystemExit("textures.ini references missing files: " + ", ".join(missing[:8]))
    for key in files:
        if PurePosixPath(key).name.casefold() in KEEP_DOCS:
            keep.add(key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for key in sorted(keep, key=str.casefold):
            source_key = next((candidate for candidate in files if candidate.casefold() == key.casefold()), None)
            if source_key is None:
                continue
            info = zipfile.ZipInfo(key, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[source_key])
    shutil.move(temp, args.output)
    print(f"prepared {args.output} ({len(keep)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
