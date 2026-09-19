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

All current mirrored ZIP assets are published in the single stable
[`texture-catalog`](https://github.com/sashkinbro/EmuCoreA-Textures/releases/tag/texture-catalog)
release: IMASSP Idolmaster SP, La Pucelle Ragnarok UI, Persona 3 Portable
Chinese overlay, Monster Hunter Freedom Unite (US/EU), and SonofUgly's
Liberty City Stories, Vice City Stories, and Chinatown Wars packs. Entries
marked `link-only` keep the author's direct URL and are not copied into the
release.

The release asset names preserve the upstream project or pack identity; they
do not claim authorship for EmuCoreA and do not use an `-emucorea` suffix.
The mirrored pack provenance is:

- **IMASSP Idolmaster SP** — IMASSP-TL contributors,
  [Imas-SP-Texture-Patch-CN](https://github.com/IMASSP-TL/Imas-SP-Texture-Patch-CN),
  GPL-3.0.
- **La Pucelle: Ragnarok UI** — althonos,
  [lapucelle-textures](https://github.com/althonos/lapucelle-textures),
  CC-NC 1.0; non-commercial redistribution only.
- **Persona 3 Portable Chinese overlay** — PandaQuQ and TridentOfTheAbyss,
  [P3P_HD_CHINESE](https://github.com/PandaQuQ/P3P_HD_CHINESE), MIT;
  the separately credited base pack remains a prerequisite.
- **Monster Hunter Freedom Unite US** — three5media,
  [mfhu-hd-retexture](https://github.com/three5media/mfhu-hd-retexture);
  the upstream README grants permission to use the project materials.
- **Monster Hunter Freedom Unite EU** — replydev,
  [mhfu-hd-retexture-eu](https://github.com/replydev/mhfu-hd-retexture-eu);
  the upstream README grants permission to use the project materials.
- **Grand Theft Auto: Liberty City Stories** — SonofUgly,
  [LCS-Texture-Pack](https://github.com/SonofUgly/LCS-Texture-Pack);
  the author grants use of any or all of the project in the
  [PPSSPP forum thread](https://forums.ppsspp.org/showthread.php?pid=142853&tid=22930).
- **Grand Theft Auto: Vice City Stories** — SonofUgly,
  [VCS-Texture-Pack](https://github.com/SonofUgly/VCS-Texture-Pack);
  the same author permission applies.
- **Grand Theft Auto: Chinatown Wars** — SonofUgly,
  [CW-Texture-Pack](https://github.com/SonofUgly/CW-Texture-Pack);
  the same author permission applies.

The three SonofUgly source releases contain dangling mappings for image files
that are absent from the published snapshots. Their normalized assets retain
all available upstream images and remove only those missing mapping lines;
`EMuCoreA-NORMALIZATION.md` inside each ZIP records the counts. Image bytes and
the original README are preserved.

Each mirrored ZIP retains the upstream README and license or permission notice
where available. Third-party game and texture rights remain with their
respective owners. The authoritative author, source, license, serial,
mapping, size, and SHA-256 fields are in `textures.json`.

The reasons the remaining eleven entries stay external are recorded in
[`LINK-ONLY-AUDIT.md`](LINK-ONLY-AUDIT.md), including the explicit no-reupload
restriction on the Manhunt 2 pack and the non-standalone Persona 2 overlay.

Run the checks before publishing a catalog change:

```text
python scripts/validate_catalog.py
python scripts/inspect_pack.py path/to/pack.zip
python scripts/validate_pack.py path/to/pack.zip
python -m unittest discover -s scripts -p "test_*.py"
```

Do not add a source archive to a release without preserving the original
author, credits, license/permission status, source URL, and SHA-256.
