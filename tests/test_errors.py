import pytest

from nbtx import (
    STRING_LENGTH_LIMIT,
    ExpectedNameException,
    StringTooLongException,
    TagByte,
    TagCompound,
    TagInt,
    TagList,
    TagString,
    TypeConflictException,
    UnexpectedNameException,
)


def test_unexpected_name() -> None:
    with pytest.raises(UnexpectedNameException):
        TagList(
            "perhaps valid key",
            [TagList("invalid key", [], child_id=TagByte.id())],
            child_id=TagList.id(),
        )


def test_expected_name() -> None:
    with pytest.raises(ExpectedNameException):
        TagCompound("perhaps valid key", [TagByte("", 0)])


def test_string_too_long() -> None:
    TagString("a" * STRING_LENGTH_LIMIT, "b" * STRING_LENGTH_LIMIT)  # this is fine
    with pytest.raises(StringTooLongException):
        TagString("a" * (STRING_LENGTH_LIMIT + 1), "b" * (STRING_LENGTH_LIMIT + 1))


def test_conflicting_type_and_id() -> None:
    with pytest.raises(TypeConflictException):
        TagList("", [TagByte("", 0)], child_id=TagInt.id())
