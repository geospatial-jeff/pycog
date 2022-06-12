from pycog.reader import open_cog
from pycog.writer import write_cog
from pycog.tags import tag_registry, ImageWidth, ImageHeight, TileByteCounts, TileOffsets

# Register ImageWidth and ImageHeight tags
tag_registry.add(ImageWidth)
tag_registry.add(ImageHeight)
tag_registry.add(TileByteCounts)
tag_registry.add(TileOffsets)

# Open the COG.
with open("cog.tif", "rb") as f:
    data = f.read()

# Read the COG into pycog types.
cog = open_cog(data)

# Write COG back to bytes.
cog_bytes = write_cog(cog)

# Read it back into pycog types.
another_cog = open_cog(cog_bytes)

# Make sure both COGs have the same header
assert cog.header == another_cog.header

# Make sure both COGs have the same number of IFDs.
assert len(cog.ifds) == len(another_cog.ifds)

for (cog_ifd, another_cog_ifd) in zip(cog.ifds, another_cog.ifds):
    # Make sure both tags are present
    assert (
        list(cog_ifd.tags)
        == list(another_cog_ifd.tags)
        == ["ImageWidth", "ImageHeight"]
    )

    # Make sure tags are the same
    assert cog_ifd.tags["ImageWidth"] == another_cog_ifd.tags["ImageWidth"]
    assert cog_ifd.tags["ImageHeight"] == another_cog_ifd.tags["ImageHeight"]
