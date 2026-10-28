#!/usr/bin/env python3
"""Normalize a dotnet-pack NuGet archive for reproducible output bytes."""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def main() -> None:
    directory = Path(__file__).resolve().parent
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else directory / "out/raw-packages/Fixture.1.0.0.nupkg"
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else directory / "Fixture.nupkg"
    with ZipFile(source, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit("NuGet input contains duplicate entry names")
        contents = {name: archive.read(name) for name in names}

    metadata_paths = [
        name for name in contents
        if name.startswith("package/services/metadata/core-properties/") and name.endswith(".psmdcp")
    ]
    if len(metadata_paths) != 1:
        raise SystemExit("NuGet input must contain exactly one core-properties metadata file")
    metadata_path = metadata_paths[0]
    stable_metadata_path = "package/services/metadata/core-properties/Fixture.psmdcp"
    metadata = contents.pop(metadata_path)
    old_path, new_path = metadata_path.encode(), stable_metadata_path.encode()
    contents = {name: data.replace(old_path, new_path) for name, data in contents.items()}
    contents[stable_metadata_path] = metadata
    for name in sorted(contents):
        if name.endswith(".rels"):
            relationship_index = 0

            def stable_id(_match: re.Match[bytes]) -> bytes:
                nonlocal relationship_index
                relationship_index += 1
                return f'Id="R{relationship_index:016X}"'.encode()

            contents[name] = re.sub(rb'Id="[^"]+"', stable_id, contents[name])

    nuspec_names = [name for name in contents if name.endswith(".nuspec")]
    if len(nuspec_names) != 1:
        raise SystemExit("NuGet input must contain exactly one nuspec")
    if contents.get("lib/net8.0/Fixture.dll") != (directory / "Fixture.dll").read_bytes():
        raise SystemExit("NuGet package DLL differs from managed/Fixture.dll")
    nuspec = ET.fromstring(contents[nuspec_names[0]])
    if any("commit" in element.attrib for element in nuspec.iter()):
        raise SystemExit("NuGet nuspec contains source commit metadata")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_STORED) as archive:
        archive.comment = b""
        for name in sorted(contents):
            entry = ZipInfo(name, date_time=FIXED_TIMESTAMP)
            entry.compress_type = ZIP_STORED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.extra = b""
            entry.comment = b""
            archive.writestr(entry, contents[name])


if __name__ == "__main__":
    main()
