# MIT License
#
# Copyright (c) 2025 Jonas da Silva
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Minecraft NBT parser and writer library.

Note that this library uses little-endian byte order by default which differs
from most libraries that use big-endian byte order by default.
"""

from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import IO, Any, Literal, Self, override

type Endianness = Literal["little"] | Literal["big"]

PRETTY_INDENTATION = "  "
"""
Indentation used when pretty printing tags, more specifically ones that contain
nested tags.
"""

STRING_LENGTH_LIMIT = 32_767
"""
The maximum length for strings including string tag values and tag names.
"""


def _struct_code_for_endianness(endianness: Endianness) -> str:
    return "<" if endianness == "little" else ">"


def _unpack(
    endianness: Endianness,
    format: str,
    buffer: bytes,
) -> tuple[bytes, tuple[Any, ...]]:
    """
    A wrapper around `struct.unpack` that advances the provided buffer.
    """
    e = _struct_code_for_endianness(endianness)
    fmt = e + format
    size = struct.calcsize(fmt)
    (data_buffer, advanced_buffer) = (buffer[:size], buffer[size:])
    data = struct.unpack(fmt, data_buffer)
    return (advanced_buffer, data)


def _pack(
    endianness: Endianness,
    format: str,
    *data: Any,
) -> bytes:
    e = _struct_code_for_endianness(endianness)
    fmt = e + format
    return struct.pack(fmt, *data)


def _read_id(
    endianness: Endianness, buffer: bytes, *, compare: int | None = None
) -> tuple[bytes, int]:
    """
    Reads an NBT tag ID.

    If `compare` is provided, then this function compares the read ID with that
    value and raises a `ValueError` when there is a mismatch.
    """
    (buffer, (id,)) = _unpack(endianness, "b", buffer)
    assert isinstance(id, int)
    if compare is not None and id != compare:
        raise ValueError(f"read ID 0x{id:>02x}, but expected 0x{compare:>02x}")
    return (buffer, id)


def _write_id(endianness: Endianness, id: int, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "b", id))


def _read_byte(endianness: Endianness, buffer: bytes) -> tuple[bytes, int]:
    """
    Reads an NBT encoded byte without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "b", buffer)
    assert isinstance(value, int)
    return (buffer, value)


def _write_byte(endianness: Endianness, byte: int, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "b", byte))


def _read_short(endianness: Endianness, buffer: bytes) -> tuple[bytes, int]:
    """
    Reads an NBT encoded 16-bit signed integer without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "h", buffer)
    assert isinstance(value, int)
    return (buffer, value)


def _write_short(endianness: Endianness, integer: int, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "h", integer))


def _read_int(endianness: Endianness, buffer: bytes) -> tuple[bytes, int]:
    """
    Reads an NBT encoded 32-bit signed integer without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "i", buffer)
    assert isinstance(value, int)
    return (buffer, value)


def _write_int(endianness: Endianness, integer: int, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "i", integer))


def _read_long(endianness: Endianness, buffer: bytes) -> tuple[bytes, int]:
    """
    Reads an NBT encoded 64-bit signed integer without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "q", buffer)
    assert isinstance(value, int)
    return (buffer, value)


def _write_long(endianness: Endianness, integer: int, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "q", integer))


def _read_float(endianness: Endianness, buffer: bytes) -> tuple[bytes, float]:
    """
    Reads an NBT encoded 32-bit floating point without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "f", buffer)
    assert isinstance(value, float)
    return (buffer, value)


def _write_float(endianness: Endianness, floating: float, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "f", floating))


def _read_double(endianness: Endianness, buffer: bytes) -> tuple[bytes, float]:
    """
    Reads an NBT encoded 32-bit floating point without the tag ID.
    """
    (buffer, (value,)) = _unpack(endianness, "d", buffer)
    assert isinstance(value, float)
    return (buffer, value)


def _write_double(endianness: Endianness, floating: float, stream: IO[bytes]) -> None:
    stream.write(_pack(endianness, "d", floating))


def _read_string(endianness: Endianness, buffer: bytes) -> tuple[bytes, str]:
    """
    Reads a NBT encoded string without the tag ID.

    A string starts with a 16-bit signed integer declaring the length of the
    string followed by the bytes that form the UTF-8 string.
    """
    (buffer, (length,)) = _unpack(endianness, "h", buffer)
    if length < 0:
        raise ValueError(f"unexpected length {length} for string")
    data = bytes()
    for _ in range(length):
        (buffer, (byte,)) = _unpack(endianness, "c", buffer)
        data += byte
    return (buffer, data.decode("utf8"))


def _write_string(endianness: Endianness, string: str, stream: IO[bytes]) -> None:
    data = string.encode("utf8")
    stream.write(_pack(endianness, "h", len(data)))
    stream.write(data)


def _read_byte_list(
    endianness: Endianness, buffer: bytes
) -> tuple[bytes, Sequence[int]]:
    (buffer, length) = _read_int(endianness, buffer)
    children = []
    for _ in range(length):
        (buffer, byte) = _read_byte(endianness, buffer)
        children.append(byte)
    return (buffer, children)


def _write_byte_list(
    endianness: Endianness, children: Sequence[int], stream: IO[bytes]
) -> None:
    _write_int(endianness, len(children), stream)
    for byte in children:
        _write_byte(endianness, byte, stream)


def _read_long_list(
    endianness: Endianness, buffer: bytes
) -> tuple[bytes, Sequence[int]]:
    (buffer, length) = _read_int(endianness, buffer)
    children = []
    for _ in range(length):
        (buffer, long) = _read_long(endianness, buffer)
        children.append(long)
    return (buffer, children)


def _write_long_list(
    endianness: Endianness, children: Sequence[int], stream: IO[bytes]
) -> None:
    _write_int(endianness, len(children), stream)
    for long in children:
        _write_long(endianness, long, stream)


def _read_int_list(
    endianness: Endianness, buffer: bytes
) -> tuple[bytes, Sequence[int]]:
    (buffer, length) = _read_int(endianness, buffer)
    children = []
    for _ in range(length):
        (buffer, long) = _read_int(endianness, buffer)
        children.append(long)
    return (buffer, children)


def _write_int_list(
    endianness: Endianness, children: Sequence[int], stream: IO[bytes]
) -> None:
    _write_int(endianness, len(children), stream)
    for integer in children:
        _write_int(endianness, integer, stream)


def _read_list(
    endianness: Endianness, buffer: bytes
) -> tuple[bytes, Sequence[Any], int]:
    (buffer, child_id) = _read_byte(endianness, buffer)
    (buffer, length) = _read_int(endianness, buffer)
    children: list[Any] = []
    for _ in range(length):
        match child_id:
            case 0x01:
                (buffer, byte_data) = _read_byte(endianness, buffer)
                children.append(TagByte("", byte_data))
            case 0x02:
                (buffer, short_data) = _read_short(endianness, buffer)
                children.append(TagShort("", short_data))
            case 0x03:
                (buffer, int_data) = _read_int(endianness, buffer)
                children.append(TagInt("", int_data))
            case 0x04:
                (buffer, long_data) = _read_long(endianness, buffer)
                children.append(TagLong("", long_data))
            case 0x05:
                (buffer, float_data) = _read_float(endianness, buffer)
                children.append(TagFloat("", float_data))
            case 0x06:
                (buffer, double_data) = _read_double(endianness, buffer)
                children.append(TagDouble("", double_data))
            case 0x07:
                (buffer, byte_list_data) = _read_byte_list(endianness, buffer)
                children.append(TagByteList("", byte_list_data))
            case 0x08:
                (buffer, string_data) = _read_string(endianness, buffer)
                children.append(TagString("", string_data))
            case 0x09:
                (buffer, list_data, sublist_child_id) = _read_list(endianness, buffer)
                children.append(TagList("", list_data, child_id=sublist_child_id))
            case 0x0A:
                (buffer, compound_data) = _read_compound(endianness, buffer)
                children.append(TagCompound("", compound_data))
            case 0x0B:
                (buffer, int_list) = _read_int_list(endianness, buffer)
                children.append(TagIntList("", int_list))
            case 0x0C:
                (buffer, long_list) = _read_long_list(endianness, buffer)
                children.append(TagLongList("", long_list))
            case _:
                raise FormatError("expected valid ID")
    return (buffer, children, child_id)


def _write_list(
    endianness: Endianness, children: Sequence[Any], child_id: int, stream: IO[bytes]
) -> None:
    _write_byte(endianness, child_id, stream)
    _write_int(endianness, len(children), stream)
    for child in children:
        match child.id():
            case 0x01:
                _write_byte(endianness, child.value, stream)
            case 0x02:
                _write_short(endianness, child.value, stream)
            case 0x03:
                _write_int(endianness, child.value, stream)
            case 0x04:
                _write_long(endianness, child.value, stream)
            case 0x05:
                _write_float(endianness, child.value, stream)
            case 0x06:
                _write_double(endianness, child.value, stream)
            case 0x07:
                _write_byte_list(endianness, child.value, stream)
            case 0x08:
                _write_string(endianness, child.value, stream)
            case 0x09:
                _write_list(endianness, child.value, child.child_id, stream)
            case 0x0A:
                _write_compound(endianness, child.value, stream)
            case 0x0B:
                _write_int_list(endianness, child.value, stream)
            case 0x0C:
                _write_long_list(endianness, child.value, stream)
            case _:
                raise FormatError("expected valid ID")


def _read_compound(
    endianness: Endianness, buffer: bytes
) -> tuple[bytes, Sequence[Tag[Any]]]:
    compound: list[Tag[Any]] = []
    while True:
        (new_buffer_if_end, child_id) = _read_id(endianness, buffer)
        if child_id == 0x00:
            buffer = new_buffer_if_end
            break
        tag = _tag_class_by_id(child_id)
        (child, buffer) = tag._read(buffer, endianness=endianness)
        for index, old_child in enumerate(compound):
            if child.name == old_child.name:
                raise ValueError(
                    f"duplicate key in compound at index {index}: {old_child.name}"
                )
        compound.append(child)
    return (buffer, compound)


def _write_compound(
    endianness: Endianness, children: Sequence[Tag[Any]], stream: IO[bytes]
) -> None:
    for child in children:
        child._write(stream, endianness=endianness)
    stream.write(b"\0")


def _tag_class_by_id(id: int) -> type[Tag[Any]]:
    if id == TagByte.id():
        return TagByte
    if id == TagShort.id():
        return TagShort
    if id == TagInt.id():
        return TagInt
    if id == TagLong.id():
        return TagLong
    if id == TagFloat.id():
        return TagFloat
    if id == TagDouble.id():
        return TagDouble
    if id == TagList.id():
        return TagList
    if id == TagByteList.id():
        return TagByteList
    if id == TagIntList.id():
        return TagIntList
    if id == TagLongList.id():
        return TagLongList
    if id == TagCompound.id():
        return TagCompound
    if id == TagString.id():
        return TagString
    raise ValueError(f"read ID 0x{id:>02x}, but expected 0x00/.../0x12")


@dataclass
class NBTException(Exception):
    """
    Base exceptions for NBT related exceptions.
    """

    pass


@dataclass
class UnexpectedNameException(NBTException):
    """
    Exception raised when a named tag is used when an unnamed one was expected.
    """

    def __str__(self) -> str:
        return "unexpected name"


@dataclass
class ExpectedNameException(NBTException):
    """
    Exception raised when an named tag is expected when an unnamed one was
    provided.
    """

    def __str__(self) -> str:
        return "expected name"


@dataclass
class TypeConflictException(NBTException):
    """
    Exception raised when there is a conflict of tags within a container.
    """

    id_actual: int
    id_expected: int

    def __str__(self) -> str:
        return f"conflicting type: {self.id_actual:>02x} vs {self.id_expected:>02x}"


@dataclass
class StringTooLongException(NBTException):
    """
    Exception raised for string that exceed the limit of 32.767.
    """

    length: int

    def __str__(self) -> str:
        return f"string exceeds limit: {self.length > STRING_LENGTH_LIMIT}"


@dataclass
class UnemptyBufferException(NBTException):
    """
    Exception raised when a buffer was not empty after full parse.
    """

    def __str__(self) -> str:
        return "buffer was not empty after full parse"


@dataclass
class FormatError(NBTException):
    """
    Exception raised when the input is not valid NBT format.
    """

    message: str

    def __str__(self) -> str:
        return f"malformed data: {self.message}"


@dataclass(frozen=True)
class Tag[T](ABC):
    """
    Base class for NBT tags.
    """

    name: str
    """
    The name of the tag.

    Commonly the name is irrelevant such as in a list. In that case an empty
    string must be used.
    """

    value: T
    """
    The value of the tag.
    """

    @staticmethod
    @abstractmethod
    def id() -> int:
        """
        The ID that represents the tag in binary format.
        """

    @classmethod
    @abstractmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Tag[T], bytes]:
        """
        Reads bytes from a buffer and interprets them as this tag.

        This is a low-level function. If you intend to read an NBT input
        use `load` instead.

        This process includes parsing the ID, the name and the value of the tag.
        This function returns a tuple containing the tag instance and the
        remaining bytes.
        """

    @abstractmethod
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        """
        Writes bytes to a buffer.

        This is a low-level function. If you intend to write NBT tags use
        `dump` instead.
        """

    @abstractmethod
    def pretty(self) -> str:
        """
        Returns a human readable pretty representation of the tag structure.
        """


@dataclass(frozen=True)
class TagByte(Tag[int]):
    """
    NBT tag for a single byte.
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x01

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_byte(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_byte(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Byte({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagShort(Tag[int]):
    """
    NBT tag for a short integer (signed 16-bit integer).
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x02

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_short(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_short(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Short({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagInt(Tag[int]):
    """
    NBT tag for an integer (signed 32-bit integer).
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x03

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_int(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_int(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Int({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagLong(Tag[int]):
    """
    NBT tag for a long integer (signed 64-bit integer).
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x04

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_long(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_long(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Long({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagFloat(Tag[float]):
    """
    NBT tag for an integer (32-bit floating point).
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x05

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_float(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_float(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Float({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagDouble(Tag[float]):
    """
    NBT tag for an integer (64-bit floating point).
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x06

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, value) = _read_double(endianness, buffer)
        return (cls(name, value), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_double(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"Double({self.name!r}): {self.value}"


@dataclass(frozen=True)
class TagString(Tag[str]):
    """
    NBT tag for a UTF-8 encoded string.
    """

    def __post_init__(self) -> None:
        if len(self.value) > STRING_LENGTH_LIMIT:
            raise StringTooLongException(len(self.value))

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x08

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, string) = _read_string(endianness, buffer)
        return (cls(name, string), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_string(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        return f"String({self.name!r}): {self.value!r}"


@dataclass(frozen=True)
class TagList[T](Tag[Sequence[Tag[T]]]):
    """
    NBT tag for a list containing nameless tags of one kind.
    """

    child_id: int = field(kw_only=True)

    def __post_init__(self) -> None:
        for child in self.value:
            if child.id() != self.child_id:
                raise TypeConflictException(
                    id_actual=child.id(), id_expected=self.child_id
                )
            if child.name != "":
                raise UnexpectedNameException()

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x09

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, children, child_id) = _read_list(endianness, buffer)
        return (cls(name, children, child_id=child_id), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_list(endianness, self.value, self.child_id, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        string = ""
        string += f"Compound({self.name!r}): {len(self.value)} entries\n"
        string += "{\n"
        for child in self.value:
            for line in child.pretty().splitlines():
                string += f"{PRETTY_INDENTATION}{line}\n"
        string += "}"
        return string


@dataclass(frozen=True)
class TagByteList[T](Tag[Sequence[int]]):
    """
    NBT tag for a list of bytes.
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x07

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, children) = _read_byte_list(endianness, buffer)
        return (cls(name, children), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_byte_list(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        string = ""
        string += f"ByteList({self.name!r}) : {len(self.value)} entries\n"
        string += "{\n"
        for long in self.value:
            string += f"{PRETTY_INDENTATION}{long}\n"
        string += "}"
        return string


@dataclass(frozen=True)
class TagIntList(Tag[Sequence[int]]):
    """
    NBT tag for a list of integers.
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x0B

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, children) = _read_int_list(endianness, buffer)
        return (cls(name, children), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_int_list(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        string = ""
        string += f"IntList({self.name!r}) : {len(self.value)} entries\n"
        string += "{\n"
        for integer in self.value:
            string += f"{PRETTY_INDENTATION}{integer}\n"
        string += "}"
        return string


@dataclass(frozen=True)
class TagLongList(Tag[Sequence[int]]):
    """
    NBT tag for a list of long integers.
    """

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x0C

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, children) = _read_long_list(endianness, buffer)
        return (cls(name, children), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_long_list(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        string = ""
        string += f"LongList({self.name!r}) : {len(self.value)} entries\n"
        string += "{\n"
        for byte in self.value:
            string += f"{PRETTY_INDENTATION}{byte}\n"
        string += "}"
        return string


@dataclass(frozen=True)
class TagCompound(Tag[Sequence[Tag[Any]]]):
    """
    NBT tag for a compound (list of uniquely named tags).
    """

    def __post_init__(self) -> None:
        for child in self.value:
            if child.name == "":
                raise ExpectedNameException()

    # docstr-coverage:inherited
    @override
    @staticmethod
    def id() -> int:
        return 0x0A

    @override
    @classmethod
    def _read(cls, buffer: bytes, *, endianness: Endianness) -> tuple[Self, bytes]:
        (buffer, _) = _read_id(endianness, buffer, compare=cls.id())
        (buffer, name) = _read_string(endianness, buffer)
        (buffer, compound) = _read_compound(endianness, buffer)
        return (cls(name, compound), buffer)

    @override
    def _write(self, stream: IO[bytes], *, endianness: Endianness) -> None:
        _write_id(endianness, self.id(), stream)
        _write_string(endianness, self.name, stream)
        _write_compound(endianness, self.value, stream)

    # docstr-coverage:inherited
    @override
    def pretty(self) -> str:
        string = ""
        string += f"Compound({self.name!r}): {len(self.value)} entries\n"
        string += "{\n"
        for child in self.value:
            for line in child.pretty().splitlines():
                string += f"{PRETTY_INDENTATION}{line}\n"
        string += "}"
        return string


def load(
    file: IO[bytes],
    *,
    endianness: Endianness = "little",
    ignore_rest: bool = False,
) -> Tag[Any]:
    """
    Loads an NBT file and returns the contained NBT tag.

    # Parameters

    - `file` -- The file-like object to read the data from.
    - `endianness` -- The byte order to use during parsing. Java Edition usually
      uses big endian byte order and Bedrock Edition usually uses little endian
      byte order.
    - `ignore_rest` -- Whether to ignore remaining bytes after a full parse. By
      default, this function expects the buffer to be empty after an NBT tree
      has been serialized and raises an exception otherwise.
    """
    buffer = file.read()
    (_, id) = _read_id(endianness, buffer)
    tag_cls = _tag_class_by_id(id)
    (tag, rest) = tag_cls._read(buffer, endianness=endianness)
    print(rest)
    if rest and not ignore_rest:
        raise UnemptyBufferException()
    return tag


def dump(
    tag: Tag[Any], stream: IO[bytes], *, endianness: Endianness = "little"
) -> None:
    """
    Dumps an NBT tag to a file.

    # Parameters

    - `tag` -- The root tag to write to the stream.
    - `stream` -- The stream to write to.
    - `endianness` -- The byte order to use. Java Edition usually uses big
      endian byte order and Bedrock Edition usually uses little endian byte
      order.
    """
    tag._write(stream, endianness=endianness)
