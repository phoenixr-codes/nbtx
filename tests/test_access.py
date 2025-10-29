from nbtx import TagByteList, TagCompound, TagInt, TagIntList, TagList, TagLongList


def test_compound() -> None:
    compound = TagCompound("", [TagInt("foo", 1), TagInt("bar", 2)])
    assert compound["foo"] == TagInt("foo", 1)
    assert compound["bar"] == TagInt("bar", 2)
    assert compound.get("foo") == TagInt("foo", 1)
    assert compound.get("bar", default=TagInt("boo", 42)) == TagInt("bar", 2)
    assert compound.get("baz", default=TagInt("boo", 42)) == TagInt("boo", 42)
    assert compound.get("baz") is None


def test_list() -> None:
    lst = TagList("", [TagInt("", 42), TagInt("", 69)], child_id=TagInt.id())
    assert lst[0] == TagInt("", 42)
    assert lst[1] == TagInt("", 69)


def test_byte_list() -> None:
    lst = TagByteList("", [42, 69])
    assert lst[0] == 42
    assert lst[1] == 69


def test_int_list() -> None:
    lst = TagIntList("", [42, 69])
    assert lst[0] == 42
    assert lst[1] == 69


def test_long_list() -> None:
    lst = TagLongList("", [42, 69])
    assert lst[0] == 42
    assert lst[1] == 69
