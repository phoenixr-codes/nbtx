from io import BytesIO

import nbtx
from nbtx import (
    TagByte,
    TagByteList,
    TagCompound,
    TagDouble,
    TagFloat,
    TagInt,
    TagIntList,
    TagList,
    TagLong,
    TagLongList,
    TagShort,
    TagString,
)


def test_nested_list() -> None:
    tree = TagCompound(
        "",
        [
            TagList(
                "foo",
                [
                    TagList(
                        "",
                        [TagList("", [], child_id=TagList.id())],
                        child_id=TagList.id(),
                    )
                ],
                child_id=TagList.id(),
            )
        ],
    )
    buffer = BytesIO()
    nbtx.dump(tree, buffer)
    buffer.seek(0)
    actual = nbtx.load(buffer)
    assert tree == actual


def test_round_trip() -> None:
    tree = TagCompound(
        "",
        [
            TagByte("hello", 127),
            TagShort("foo", 42),
            TagInt("bar", 69),
            TagLong("beep", 2_147_483_647),
            TagFloat("meow", -1.0),
            TagDouble("woof", 1.7),
            TagList(
                "baz",
                [
                    TagInt("", 42),
                    TagInt("", 100),
                    TagInt("", 420),
                ],
                child_id=TagInt.id(),
            ),
            TagByteList(
                "boo",
                [
                    42,
                    69,
                    99,
                ],
            ),
            TagIntList(
                "bee",
                [
                    42,
                    300,
                ],
            ),
            TagLongList(
                "moo",
                [
                    -3,
                    7,
                    10,
                ],
            ),
            TagString("boop", "Hello Wörld"),
        ],
    )
    buffer = BytesIO()
    nbtx.dump(tree, buffer)
    buffer.seek(0)
    actual = nbtx.load(buffer)
    assert tree == actual
