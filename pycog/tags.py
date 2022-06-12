import typing
from dataclasses import dataclass, field

from pycog.types import Tag


@dataclass
class ImageWidth(Tag):
    """The number of columns (width) in the image.
    https://www.awaresystems.be/imaging/tiff/tifftags/imagewidth.html
    """

    id: typing.ClassVar[int] = 256
    name: typing.ClassVar[str] = "ImageWidth"
    value: bytes


@dataclass
class ImageHeight(Tag):
    """The number of rows (height) in the image.
    https://www.awaresystems.be/imaging/tiff/tifftags/imagelength.html
    """

    id: typing.ClassVar[int] = 257
    name: typing.ClassVar[str] = "ImageHeight"
    value: bytes


@dataclass
class TileOffsets(Tag):
    """The byte offset to each compressed image tile.
    https://www.awaresystems.be/imaging/tiff/tifftags/tileoffsets.html
    """

    id: typing.ClassVar[int] = 324
    name: typing.ClassVar[str] = "TileOffsets"
    value: bytes


@dataclass
class TileByteCounts(Tag):
    """The number of bytes in each compressed image tile.
    https://www.awaresystems.be/imaging/tiff/tifftags/tilebytecounts.html
    """

    id: typing.ClassVar[int] = 325
    name: typing.ClassVar[str] = "TileByteCounts"
    value: bytes


@dataclass
class TagRegistry:
    """Defines which tags are read when opening an image.
    Allows for the inclusion of additional TIFF tags (ex. private tags).
    Args:
        tags: a dictionary mapping tag codes to the appropriate class.
    """

    tags: typing.Dict[int, typing.Type[Tag]] = field(default_factory=dict)

    def add(self, *tag: typing.Type[Tag]):
        """Add a tag to the registry.
        Args:
            tag: The tag added to the registry.
        """
        self.tags.update({t.id: t for t in tag})

    def get(self, tag_code: int) -> typing.Optional[typing.Type[Tag]]:
        """Get a tag from the registry.
        Args:
            tag_code: The numerical code of the desired tag.
        Returns:
        """
        return self.tags.get(tag_code)


tag_registry = TagRegistry()
