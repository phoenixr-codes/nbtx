from nbtx import TagCompound, TagInt

def test_access() -> None:
    compound =TagCompound("", [
        TagInt("foo", 1),
        TagInt("bar", 2)
    ])
    assert compound["foo"] == TagInt("foo", 1)
    assert compound["bar"] == TagInt("bar", 2)
