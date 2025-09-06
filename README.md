# nbtx - NBT parser in Python

Zero-dependency, strictly-typed NBT parser and writer.

## Installation

Because the entire implementation finds place in a single file and does not
depend on third-party libraries, you can simply copy `src/nbtx/__init__.py`
to your project. Alternatively, you can install nbtx by using a package
manager.

### Pip

```console
pip install nbtx
```

### Poetry

```console
poetry add nbtx
```

### uv

```console
uv add nbtx
```

## Usage (Library)

```python
import nbtx

with open("file.nbt", "rb") as f:
    content = nbtx.load(f)

print(content.pretty())
```

## References

- <https://wiki.bedrock.dev/nbt/nbt-in-depth>
