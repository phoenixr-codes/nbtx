"""
Command-line interface for NBTX.
"""

import sys
from argparse import ArgumentParser, FileType

import nbtx

parser = ArgumentParser(
    description="Print content of a NBT file in a human-readable format"
)

parser.add_argument(
    "-e",
    "--endianness",
    help="whether to use little or big endian",
    choices={"little", "big"},
    default="little",
)
parser.add_argument(
    "file",
    help="file to read from or standard input if omitted",
    nargs="?",
    type=FileType("rb"),
    default=sys.stdin.buffer,
)

args = parser.parse_args()

nbt = nbtx.load(args.file, endianness=args.endianness)
print(nbt.pretty())
