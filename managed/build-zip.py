#!/usr/bin/env python3
"""Create a stable, uncompressed ZIP containing the managed fixture DLL."""

from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo


def main() -> None:
    directory = Path(__file__).resolve().parent
    source = directory / "Fixture.dll"
    archive = directory / "Fixture.zip"
    entry = ZipInfo("Fixture.dll", date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = ZIP_STORED
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    entry.extra = b""
    entry.comment = b""
    with ZipFile(archive, "w") as output:
        output.comment = b""
        output.writestr(entry, source.read_bytes())


if __name__ == "__main__":
    main()
