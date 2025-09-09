from typing import Any

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
)


def test_byte() -> None:
    assert TagByte("foo", 42).as_python() == 42


def test_short() -> None:
    assert TagShort("foo", -12).as_python() == -12


def test_int() -> None:
    assert TagInt("foo", 69).as_python() == 69


def test_int_list() -> None:
    assert TagIntList("foo", [1, 2, 3, 4]).as_python() == [1, 2, 3, 4]


def test_long_list() -> None:
    assert TagLongList("foo", [1, 2, 3, 4]).as_python() == [1, 2, 3, 4]


def test_byte_list() -> None:
    assert TagByteList("foo", [1, 2, 3, 4]).as_python() == [1, 2, 3, 4]


def test_long() -> None:
    assert TagLong("foo", 30_000).as_python() == 30_000


def test_float() -> None:
    assert TagFloat("foo", 3.14).as_python() == 3.14


def test_double() -> None:
    assert TagDouble("foo", -1.01).as_python() == -1.01


def test_list() -> None:
    assert TagList(
        "foo",
        child_id=TagByte.id(),
        value=[TagByte("", 0), TagByte("", 1), TagByte("", 2)],
    ).as_python() == [0, 1, 2]


def test_compound() -> None:
    assert TagCompound[Any, Any](
        "foo",
        [
            TagByte("key1", 42),
            TagList(
                "key2",
                child_id=TagFloat.id(),
                value=[TagFloat("", 1.0), TagFloat("", 2.0), TagFloat("", 3.0)],
            ),
        ],
    ).as_python() == {"key1": 42, "key2": [1.0, 2.0, 3.0]}
