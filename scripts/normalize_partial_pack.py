#!/usr/bin/env python3
"""Normalize an incomplete PPSSPP ZIP without changing image bytes.

Some upstream packs publish a textures.ini containing mappings for files that
are not present in the published archive.  This tool removes only those
dangling [hashes] lines, keeps every upstream file, and writes a deterministic
ZIP that can be checked by validate_pack.py.  It must not be used to remove
files that are present.
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path, PurePosixPath
import re

HASH_LINE = re.compile(r"^(\s*[0-9A-Fa-f]{8,32}\s*=\s*)(.*?)\s*$")


def clean(name: str) -> str:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in path.parts):
        raise ValueError(f"unsafe ZIP path: {name}")
    return "/".join(path.parts)


def read_zip(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        files: dict[str, bytes] = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = clean(info.filename)
            if name.casefold() in {key.casefold() for key in files}:
                raise ValueError(f"duplicate ZIP path: {name}")
            files[name] = archive.read(info)
    return files


def normalize_ini(data: bytes, files: dict[str, bytes]) -> tuple[bytes, int]:
    text = data.decode("utf-8-sig")
    available = {name.casefold() for name in files}
    lines: list[str] = []
    in_hashes = False
    removed = 0
    for line in text.splitlines():
        section = line.strip().casefold()
        if section.startswith("["):
            in_hashes = section == "[hashes]"
        if in_hashes and not line.lstrip().startswith("#"):
            match = HASH_LINE.match(line)
            if match and match.group(2).strip():
                target = match.group(2).split("#", 1)[0].strip().replace("\\", "/")
                if target.casefold() not in available:
                    removed += 1
                    continue
        lines.append(line)
    return ("\n".join(lines) + "\n").encode("utf-8"), removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--readme", type=Path, help="optional upstream README to retain")
    parser.add_argument("--note", type=str, default="", help="normalization note to write inside the ZIP")
    args = parser.parse_args()

    files = read_zip(args.source)
    ini_key = next((key for key in files if key.casefold() == "textures.ini"), None)
    if ini_key is None:
        raise SystemExit("source has no root textures.ini")
    ini, removed = normalize_ini(files[ini_key], files)
    files.pop(ini_key)
    files["textures.ini"] = ini
    if args.readme:
        files["README.md"] = args.readme.read_bytes()
    if args.note:
        files["EMuCoreA-NORMALIZATION.md"] = (args.note.rstrip() + "\n").encode("utf-8")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for name in sorted(files, key=str.casefold):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    shutil.move(temp, args.output)
    print(f"normalized {args.output} (removed {removed} dangling mappings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
