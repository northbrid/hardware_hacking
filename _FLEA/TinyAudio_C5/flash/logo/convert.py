#!/usr/bin/env python3
"""Render raw bytes as RGB565 big-endian in 4-byte slots -> PNG."""

import argparse
import struct
from pathlib import Path

from PIL import Image


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("-w", "--width", type=int, default=480)
    p.add_argument("--lines", type=int, default=240)
    p.add_argument("--offset", type=lambda x: int(x, 0), default=0xCEF40)
    args = p.parse_args()

    need = args.lines * args.width * 4
    data = args.input.read_bytes()[args.offset : args.offset + need]
    if len(data) < need:
        raise SystemExit(f"need {need} bytes from offset {args.offset:#x}, got {len(data)}")

    pixels: list[tuple[int, int, int]] = []
    for i in range(0, need, 4):
        hi, lo = data[i], data[i + 1]
        v = (hi << 8) | lo
        r = ((v >> 11) & 0x1F) * 255 // 31
        g = ((v >> 5) & 0x3F) * 255 // 63
        b = (v & 0x1F) * 255 // 31
        pixels.append((r, g, b))

    img = Image.new("RGB", (args.width, args.lines))
    img.putdata(pixels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.output)
    print(f"{args.output}  {args.width}x{args.lines}  offset {args.offset:#x}  {need} bytes")


if __name__ == "__main__":
    main()
