#!/usr/bin/env python3
"""Validate a PPSSPP texture replacement ZIP without extracting it."""

from __future__ import annotations

import argparse
import posixpath
import re
import struct
import sys
import zipfile
from pathlib import PurePosixPath

MAX_ENTRIES = 50_000
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 12 * 1024 * 1024 * 1024
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".ktx2", ".zim"}
HASH_LINE = re.compile(r"^\s*([0-9A-Fa-f]{8,32})\s*=\s*(.*?)\s*$")
PS1_NAME = re.compile(r"^vram-write-[0-9a-f]{32}\.", re.IGNORECASE)


class PackError(ValueError):
    pass


def safe_path(name: str) -> str:
    if not name or "\\" in name or "\x00" in name:
        raise PackError(f"unsafe ZIP path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PackError(f"unsafe ZIP path: {name!r}")
    if any(":" in part for part in path.parts):
        raise PackError(f"drive-qualified ZIP path: {name!r}")
    return "/".join(path.parts)


def signature_ok(name: str, data: bytes) -> bool:
    ext = PurePosixPath(name).suffix.casefold()
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR"
    if ext in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if ext == ".bmp":
        return data.startswith(b"BM")
    if ext == ".ktx2":
        return data.startswith(b"\xabKTX 20\xbb\r\n\x1a\n")
    if ext == ".zim":
        # PPSSPP's ZIMG texture container is used by some font/UI packs.
        return data.startswith(b"ZIMG")
    if ext == ".tga":
        return len(data) >= 3 and data[2] in {1, 2, 3, 9, 10, 11}
    return False


def validate(path: str) -> dict[str, int | str]:
    with zipfile.ZipFile(path) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        if len(infos) > MAX_ENTRIES:
            raise PackError("archive contains too many entries")
        paths: dict[str, str] = {}
        total = 0
        textures: set[str] = set()
        ini_info = None
        for info in infos:
            normalized = safe_path(info.filename)
            key = normalized.casefold()
            if key in paths:
                raise PackError(f"duplicate ZIP path: {info.filename!r} / {paths[key]!r}")
            paths[key] = normalized
            if info.flag_bits & 1:
                raise PackError(f"encrypted entry: {info.filename}")
            if info.file_size > MAX_FILE_BYTES:
                raise PackError(f"entry exceeds 512 MiB: {info.filename}")
            total += info.file_size
            if total > MAX_UNCOMPRESSED_BYTES:
                raise PackError("archive exceeds 12 GiB uncompressed")
            if normalized.casefold() == "textures.ini":
                ini_info = info
            ext = PurePosixPath(normalized).suffix.casefold()
            if ext in IMAGE_EXTENSIONS:
                if PS1_NAME.match(PurePosixPath(normalized).name):
                    raise PackError("PS1 vram-write texture found in PSP catalog")
                with archive.open(info) as stream:
                    if not signature_ok(normalized, stream.read(64)):
                        raise PackError(f"invalid image signature: {normalized}")
                textures.add(key)
        if ini_info is None:
            raise PackError("textures.ini must be present at the archive root")
        if len(textures) == 0:
            raise PackError("archive contains no supported texture images")
        ini = archive.read(ini_info).decode("utf-8-sig")
        if "[options]" not in ini.casefold() or "[hashes]" not in ini.casefold():
            raise PackError("textures.ini must contain [options] and [hashes]")
        references = 0
        missing: list[str] = []
        in_hashes = False
        for line in ini.splitlines():
            section = line.strip().casefold()
            if section.startswith("["):
                in_hashes = section == "[hashes]"
                continue
            if not in_hashes or not line.strip() or line.lstrip().startswith("#"):
                continue
            match = HASH_LINE.match(line)
            if not match or not match.group(2):
                continue
            target = match.group(2).split("#", 1)[0].strip().replace("\\", "/")
            if target.startswith("/") or ".." in PurePosixPath(target).parts:
                raise PackError(f"unsafe textures.ini target: {target!r}")
            target_key = target.casefold()
            if target_key not in paths:
                missing.append(target)
            else:
                ext = PurePosixPath(target).suffix.casefold()
                if ext not in IMAGE_EXTENSIONS:
                    raise PackError(f"unsupported replacement image: {target}")
            references += 1
        if missing:
            raise PackError("textures.ini references missing files: " + ", ".join(missing[:5]))
        if references == 0:
            raise PackError("[hashes] contains no replacement mappings")
        return {"sizeBytes": int(__import__("os").path.getsize(path)), "fileCount": len(textures), "uncompressedBytes": total, "references": references}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    try:
        summary = validate(args.archive)
    except (OSError, zipfile.BadZipFile, UnicodeError, PackError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
