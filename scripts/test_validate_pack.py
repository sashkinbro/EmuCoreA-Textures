import tempfile
import unittest
import zipfile
from pathlib import Path

from validate_pack import PackError, validate


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + b"\x00" * 32


class ValidatePackTests(unittest.TestCase):
    def make_zip(self, files: dict[str, bytes]) -> Path:
        handle = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        handle.close()
        path = Path(handle.name)
        with zipfile.ZipFile(path, "w") as archive:
            for name, value in files.items():
                archive.writestr(name, value)
        self.addCleanup(path.unlink)
        return path

    def test_valid_ppsspp_pack(self):
        path = self.make_zip({
            "textures.ini": b"[options]\nversion = 1\nhash = xxh64\n[hashes]\n0123456789abcdef = ui/title.png\n",
            "ui/title.png": PNG,
        })
        summary = validate(str(path))
        self.assertEqual(summary["fileCount"], 1)
        self.assertEqual(summary["references"], 1)

    def test_rejects_missing_mapping_target(self):
        path = self.make_zip({
            "textures.ini": b"[options]\nversion = 1\n[hashes]\n0123456789abcdef = missing.png\n",
        })
        with self.assertRaises(PackError):
            validate(str(path))

    def test_rejects_ps1_filename(self):
        path = self.make_zip({
            "textures.ini": b"[options]\nversion = 1\n[hashes]\n0123456789abcdef = vram-write-0123456789abcdef0123456789abcdef.png\n",
            "vram-write-0123456789abcdef0123456789abcdef.png": PNG,
        })
        with self.assertRaises(PackError):
            validate(str(path))


if __name__ == "__main__":
    unittest.main()
