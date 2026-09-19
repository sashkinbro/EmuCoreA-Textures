# Contributing PSP texture packs

Submit the following for every pack:

- game title and every tested PSP serial (`XXXX-#####`);
- pack name and upstream version/release tag;
- original author and complete credits;
- original repository or project URL;
- exact direct HTTPS ZIP URL;
- license or explicit redistribution permission;
- archive size, SHA-256, and number of replacement image files;
- optional preview URLs.

Only add a mirrored archive when the author has granted redistribution rights.
Otherwise use `distribution: "link-only"` and keep the exact upstream URL.
Do not re-upload packs that prohibit re-uploading, including packs whose
textures are owned by a game publisher. Never mix PS1 `vram-write-*` files
with PPSSPP packs.

Before submitting a new source:

```text
python scripts/inspect_pack.py SOURCE.zip
python scripts/validate_pack.py SOURCE.zip
python scripts/validate_catalog.py
```

The validator requires `textures.ini` at the ZIP root. Every non-empty
`[hashes]` value must resolve to an image in the same archive. Supported
replacement images are PNG, JPEG, BMP, TGA, and KTX2. ZIP paths must be
relative, non-empty, and free of `..`, drive letters, NUL bytes, and duplicate
case-insensitive names.
