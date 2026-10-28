#!/usr/bin/env python3
"""Compile the intentionally tiny answer.wat fixture without external tools."""

import re
from pathlib import Path


def uleb(value: int) -> bytes:
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        encoded.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(encoded)


def section(section_id: int, payload: bytes) -> bytes:
    return bytes([section_id]) + uleb(len(payload)) + payload


def sleb32(value: int) -> bytes:
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        done = (value == 0 and byte & 0x40 == 0) or (value == -1 and byte & 0x40 != 0)
        encoded.append(byte if done else byte | 0x80)
        if done:
            return bytes(encoded)


def main() -> None:
    source = Path(__file__).with_name("answer.wat").read_text(encoding="utf-8")
    match = re.fullmatch(
        r'\s*\(module\s+\(func\s+\(export\s+"([A-Za-z_][A-Za-z0-9_]*)"\)'
        r'\s+\(result\s+i32\)\s+i32\.const\s+([0-9]+)\)\)\s*',
        source,
    )
    if not match:
        raise SystemExit("answer.wat is outside the supported one-function fixture grammar")

    export_name, result = match.group(1).encode("utf-8"), int(match.group(2))
    if result > 0x7FFFFFFF:
        raise SystemExit("answer.wat result must fit a signed i32")

    module = bytearray(b"\0asm\x01\0\0\0")
    module += section(1, b"\x01\x60\x00\x01\x7f")  # () -> i32
    module += section(3, b"\x01\x00")  # one function, type 0
    module += section(7, b"\x01" + uleb(len(export_name)) + export_name + b"\x00\x00")
    body = b"\x00\x41" + sleb32(result) + b"\x0b"  # no locals; i32.const; end
    module += section(10, b"\x01" + uleb(len(body)) + body)
    Path(__file__).with_name("answer.wasm").write_bytes(module)


if __name__ == "__main__":
    main()
