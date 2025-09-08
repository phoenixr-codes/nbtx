# nbtx - NBT parser in Python

Zero-dependency, strictly-typed NBT parser and writer.

- Documentation: <https://phoenixr-codes.github.io/nbtx/>
- PyPI: <https://pypi.org/project/nbtx/>

## Installation (Library)

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

## Installation (CLI)

### pipx

```
pipx install nbtx
```

## Usage (Library)

```python
import nbtx

with open("file.nbt", "rb") as f:
    content = nbtx.load(f)

print(content.pretty())
```

## Usage (CLI)

You can display the contents of an NBT file by using the CLI of nbtx:

### Read Big Endian NBT File

```sh
cat samples/bigtest.nbt | nbtx -e big
# or
nbtx -e big samples/bigtest.nbt
```

### Read Little Endian NBT File

```sh
cat samples/caged_villager.mcstructure | nbtx -e little
# or
nbtx -e little samples/caged_villager.mcstructure
```

## References

- <https://wiki.bedrock.dev/nbt/nbt-in-depth>
