from pathlib import Path

import nbtx
from nbtx import TagCompound, TagString

root = Path(__file__).parent.parent
samples = root / "samples"


def test_simple() -> None:
    with (samples / "hello_world.nbt").open("rb") as f:
        tree = nbtx.load(f, endianness="big")
        assert tree == TagCompound("hello world", [TagString("name", "Bananrama")])


def test_bigtest() -> None:
    with (samples / "bigtest.nbt").open("rb") as f:
        nbtx.load(f, endianness="big")


def test_mcstructure() -> None:
    with (samples / "caged_villager.mcstructure").open("rb") as f:
        nbtx.load(f, endianness="little")
