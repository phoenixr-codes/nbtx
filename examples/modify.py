from copy import replace
from pathlib import Path

import nbtx

root = Path(__file__).parent.parent
samples = root / "samples"

with (samples / "caged_villager.mcstructure").open("rb") as f:
    data = nbtx.load(f, endianness="little")
    data = replace(data, name="root")
    print(data.pretty())
