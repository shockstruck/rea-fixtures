#!/usr/bin/env python3
"""Build a deterministic PCAP containing a fabricated local HTTP exchange."""

import ipaddress
import struct
from pathlib import Path


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    words = struct.unpack(f"!{len(data) // 2}H", data)
    total = sum(words)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def frame(src_mac: bytes, dst_mac: bytes, src_ip: str, dst_ip: str,
          src_port: int, dst_port: int, seq: int, ack: int, payload: bytes) -> bytes:
    tcp_without_checksum = struct.pack(
        "!HHIIHHHH", src_port, dst_port, seq, ack,
        (5 << 12) | 0x18, 4096, 0, 0,  # 20-byte header, PSH+ACK
    ) + payload
    source = ipaddress.ip_address(src_ip).packed
    destination = ipaddress.ip_address(dst_ip).packed
    pseudo_header = source + destination + struct.pack("!BBH", 0, 6, len(tcp_without_checksum))
    tcp_checksum = checksum(pseudo_header + tcp_without_checksum)
    tcp = tcp_without_checksum[:16] + struct.pack("!H", tcp_checksum) + tcp_without_checksum[18:]

    ip_without_checksum = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), 1, 0x4000, 64, 6, 0,
        source, destination,
    )
    ip_checksum = checksum(ip_without_checksum)
    ip_header = ip_without_checksum[:10] + struct.pack("!H", ip_checksum) + ip_without_checksum[12:]
    ethernet = dst_mac + src_mac + struct.pack("!H", 0x0800)
    return ethernet + ip_header + tcp


def record(timestamp: int, packet: bytes) -> bytes:
    return struct.pack("<IIII", timestamp, 0, len(packet), len(packet)) + packet


def main() -> None:
    # Documentation-only IP range and locally administered MAC addresses.
    client_mac = bytes.fromhex("020000000001")
    server_mac = bytes.fromhex("020000000002")
    client_ip, server_ip = "192.0.2.10", "192.0.2.20"
    request = b"GET /fixture HTTP/1.1\r\nHost: fixture.invalid\r\nConnection: close\r\n\r\n"
    response_body = b"synthetic fixture\n"
    response = (
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        + f"Content-Length: {len(response_body)}\r\nConnection: close\r\n\r\n".encode()
        + response_body
    )
    packets = (
        frame(client_mac, server_mac, client_ip, server_ip, 49152, 8080, 1000, 2000, request),
        frame(server_mac, client_mac, server_ip, client_ip, 8080, 49152, 2000, 1000 + len(request), response),
    )
    global_header = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    output = Path(__file__).with_name("local-exchange.pcap")
    output.write_bytes(global_header + b"".join(record(index + 1, packet) for index, packet in enumerate(packets)))


if __name__ == "__main__":
    main()
