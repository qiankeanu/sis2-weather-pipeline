"""Копирует только файлы выбранного участника из подготовленного пакета."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("package", help="Path to 01_Balnur, 02_Kundyz, 03_Nurdaulet or 04_Kian")
args = parser.parse_args()
package = Path(args.package).expanduser().resolve()
manifest = json.loads((package / "package_manifest.json").read_text(encoding="utf-8"))
allowed = json.loads((root / "docs/upload_manifest.json").read_text(encoding="utf-8"))
key = manifest["part"]
if key not in allowed["parts"]:
    raise SystemExit("Unknown project part")
expected = set(allowed["parts"][key]["files"])
if set(manifest["files"]) != expected:
    raise SystemExit("Package file list differs from the agreed ownership manifest")
for name, checksum in manifest["files"].items():
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("Unsafe path in package")
    source = package / "upload_to_repo" / relative
    if source.is_symlink() or not source.is_file():
        raise SystemExit(f"Missing or unsafe package file: {name}")
    if hashlib.sha256(source.read_bytes()).hexdigest() != checksum:
        raise SystemExit(f"Package file changed: {name}")
# Сначала проверили все файлы; только теперь копируем в существующие папки.
for name in manifest["files"]:
    destination = root / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(package / "upload_to_repo" / name, destination)
print(f"Copied {len(manifest['files'])} files for {manifest['name']}")
print("Review the files, then use the exact git add command from HOW_TO_UPLOAD.md")
