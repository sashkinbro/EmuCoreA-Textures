#!/usr/bin/env python3
"""Validate the EmuCoreA PSP catalog and immutable audit ledger."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SERIAL_RE = re.compile(r"^[A-Z]{4}-\d{5}$")
HASH_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
MAX_CATALOG_BYTES = 8 * 1024 * 1024


def https(value: object) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    errors: list[str] = []
    catalog_path = ROOT / "textures.json"
    if catalog_path.stat().st_size > MAX_CATALOG_BYTES:
        errors.append("textures.json exceeds 8 MiB")
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("platform") != "ppsspp":
        errors.append("schemaVersion must be 1 and platform must be ppsspp")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty array")
        entries = []
    ids: set[str] = set()
    urls: set[str] = set()
    digests: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        entry_id = str(entry.get("id", ""))
        if not entry_id or entry_id in ids:
            errors.append(f"{label}.id is missing or duplicated")
        ids.add(entry_id)
        serials = entry.get("serials")
        if not isinstance(serials, list) or not serials or any(not isinstance(s, str) or not SERIAL_RE.fullmatch(s) for s in serials):
            errors.append(f"{label}.serials contains invalid PSP serials")
        if not isinstance(entry.get("authors"), list) or not entry["authors"]:
            errors.append(f"{label}.authors must be non-empty")
        for field in ("downloadUrl", "sourceUrl"):
            if not https(entry.get(field)):
                errors.append(f"{label}.{field} must be HTTPS")
        url = str(entry.get("downloadUrl", "")).casefold()
        if url in urls:
            errors.append(f"duplicate downloadUrl: {entry_id}")
        urls.add(url)
        digest = str(entry.get("sha256", "")).upper()
        if not HASH_RE.fullmatch(digest):
            errors.append(f"{label}.sha256 must be SHA-256")
        elif digest in digests:
            errors.append(f"duplicate sha256: {entry_id}")
        digests.add(digest)
        for field in ("sizeBytes", "fileCount"):
            value = entry.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"{label}.{field} must be positive")
        if entry.get("distribution") not in {"link-only", "mirrored"}:
            errors.append(f"{label}.distribution must be link-only or mirrored")
        if not isinstance(entry.get("license"), str) or not entry["license"].strip():
            errors.append(f"{label}.license is required")
        for preview in entry.get("previewUrls", []):
            if not https(preview):
                errors.append(f"{label}.previewUrls contains a non-HTTPS URL")
    audit_path = ROOT / "catalog-audit.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        batches = audit.get("batches")
        audit_entries = audit.get("entries")
        if isinstance(batches, list):
            flattened = [item for batch in batches if isinstance(batch, dict) for item in batch.get("entries", [])]
        else:
            flattened = audit_entries
        if audit.get("schemaVersion") != 1 or not isinstance(flattened, list):
            errors.append("catalog-audit.json has invalid schema")
        else:
            known = {str(e.get("id")) for e in entries}
            audited = set()
            for item in flattened:
                item_id = str(item.get("catalogId", ""))
                if item_id not in known or item_id in audited:
                    errors.append(f"invalid or duplicate audit catalogId: {item_id}")
                audited.add(item_id)
                for field in ("sourceSha256", "normalizedSha256", "manifestSha256", "contentSetSha256"):
                    if not HASH_RE.fullmatch(str(item.get(field, ""))):
                        errors.append(f"audit {item_id}.{field} must be SHA-256")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"valid: {len(entries)} PPSSPP entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
