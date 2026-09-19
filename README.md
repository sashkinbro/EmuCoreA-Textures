# EmuCoreA PSP Texture Catalog

Curated PlayStation Portable texture-pack catalog for PPSSPP and the EmuCoreA
texture manager. The catalog contains PSP replacement packs only; PS1
DuckStation/SwanStation packs belong in EmuCoreR-Textures.

The Git history contains catalog metadata and validation tooling. Pack bytes
remain at the original author's release URL unless the author explicitly
allows redistribution. This avoids turning an attribution catalog into an
unauthorized mirror.

## Files

- `textures.json` - production catalog consumed by EmuCoreA.
- `catalog-audit.json` - source and content fingerprints for verified entries.
- `schemas/texture-catalog.schema.json` - public JSON format contract.
- `scripts/validate_catalog.py` - dependency-free catalog validation.
- `scripts/validate_pack.py` - PPSSPP ZIP safety and manifest validation.
- `scripts/inspect_pack.py` - deterministic archive summary and SHA-256 output.

## PPSSPP pack format

PPSSPP replacement archives contain `textures.ini` at the archive root and
image files referenced by its `[hashes]` section. The pack is installed under
`PSP/TEXTURES/<GAME_ID>/`, where `<GAME_ID>` is the serial without the dash
(for example `ULUS10041`). The hash mode is declared in `[options]`; both
`quick` and `xxh32`/`xxh64` are accepted. Filenames and directories use
lowercase ASCII-safe paths in new packs, but existing upstream packs are
validated without rewriting their case.

The validator rejects traversal paths, encrypted ZIPs, duplicate paths,
missing `textures.ini` references, unsupported image extensions, invalid PNG,
JPEG, BMP and KTX2 signatures, oversized entries, and archives over the
catalog limits. It also rejects PS1 `vram-write-*` packs accidentally added to
this repository.

PPSSPP's official documentation describes the format and installation flow:

- <https://dev.ppsspp.org/docs/reference/use-texture-replacement/>
- <https://github.com/hrydgard/ppsspp-site/blob/main/docs/reference/texture-replacement.md>

## Catalog URL contract

Each entry has `downloadUrl` (the exact ZIP), `sourceUrl` (the project page),
`sizeBytes`, `sha256`, and `fileCount`. `distribution` is `link-only` unless
EmuCoreA has written permission to mirror the archive. `serials` use the
hyphenated PSP form (`ULUS-10041`) while installers remove the hyphen.

The current mirrored ZIP assets are published in the
[`texture-catalog-psp-packs-20260919`](https://github.com/sashkinbro/EmuCoreA-Textures/releases/tag/texture-catalog-psp-packs-20260919)
release. Its assets include the IMASSP Idolmaster SP pack, the normalized La
Pucelle Ragnarok UI pack, and the Persona 3 Portable Chinese overlay. Entries
marked `link-only` keep the author's direct URL and are not copied into this
release. The large Monster Hunter Freedom Unite pack is published separately
in the [`texture-catalog-psp-mhfu-20260919`](https://github.com/sashkinbro/EmuCoreA-Textures/releases/tag/texture-catalog-psp-mhfu-20260919)
release. Entries marked `link-only` keep the author's direct URL and are not
copied into these releases.

Run the checks before publishing a catalog change:

```text
python scripts/validate_catalog.py
python scripts/inspect_pack.py path/to/pack.zip
python scripts/validate_pack.py path/to/pack.zip
python -m unittest discover -s scripts -p "test_*.py"
```

Do not add a source archive to a release without preserving the original
author, credits, license/permission status, source URL, and SHA-256.
