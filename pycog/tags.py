import typing
from dataclasses import dataclass, field

from pycog.types import Tag


@dataclass
class NewSubfileType(Tag):
    """A general indication of the kind of data contained in this IFD.
    https://www.awaresystems.be/imaging/tiff/tifftags/newsubfiletype.html
    """

    id: typing.ClassVar[int] = 254
    name: typing.ClassVar[str] = "NewSubfileType"
    value: bytes


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
class BitsPerSample(Tag):
    """The number of bits per component.
    https://www.awaresystems.be/imaging/tiff/tifftags/bitspersample.html
    """

    id: typing.ClassVar[int] = 258
    name: typing.ClassVar[str] = "BitsPerSample"
    value: bytes


@dataclass
class Compression(Tag):
    """Compression scheme used on the image data.
    https://www.awaresystems.be/imaging/tiff/tifftags/compression.html
    """

    id: typing.ClassVar[int] = 259
    name: typing.ClassVar[str] = "Compression"
    value: bytes


@dataclass
class PhotometricInterpretation(Tag):
    """The color space of the image data.
    https://www.awaresystems.be/imaging/tiff/tifftags/photometricinterpretation.html
    """

    id: typing.ClassVar[int] = 262
    name: typing.ClassVar[str] = "PhotometricInterpretation"
    value: bytes


@dataclass
class SamplesPerPixel(Tag):
    """The number of components per pixel.
    https://www.awaresystems.be/imaging/tiff/tifftags/samplesperpixel.html
    """

    id: typing.ClassVar[int] = 277
    name: typing.ClassVar[str] = "SamplesPerPixel"
    value: bytes


@dataclass
class XResolution(Tag):
    """The number of pixels per ResolutionUnit in the ImageWidth direction.
    https://www.awaresystems.be/imaging/tiff/tifftags/xresolution.html
    """

    id: typing.ClassVar[int] = 282
    name: typing.ClassVar[str] = "XResolution"
    value: bytes


@dataclass
class YResolution(Tag):
    """The number of pixels per ResolutionUnit in the ImageHeight direction.
    https://www.awaresystems.be/imaging/tiff/tifftags/yresolution.html
    """

    id: typing.ClassVar[int] = 283
    name: typing.ClassVar[str] = "YResolution"
    value: bytes


@dataclass
class PlanarConfiguration(Tag):
    """How the components of each pixel are stored (chunky or planar).
    https://www.awaresystems.be/imaging/tiff/tifftags/planarconfiguration.html
    """

    id: typing.ClassVar[int] = 284
    name: typing.ClassVar[str] = "PlanarConfiguration"
    value: bytes


@dataclass
class ResolutionUnit(Tag):
    """The unit of measurement for XResolution and YResolution.
    https://www.awaresystems.be/imaging/tiff/tifftags/resolutionunit.html
    """

    id: typing.ClassVar[int] = 296
    name: typing.ClassVar[str] = "ResolutionUnit"
    value: bytes


@dataclass
class TileWidth(Tag):
    """TThe tile width in pixels, or the number of columns in each tile.
    https://www.awaresystems.be/imaging/tiff/tifftags/tilewidth.html
    """

    id: typing.ClassVar[int] = 322
    name: typing.ClassVar[str] = "TileWidth"
    value: bytes


@dataclass
class TileHeight(Tag):
    """TThe tile height in pixels, or the number of rows in each tile.
    https://www.awaresystems.be/imaging/tiff/tifftags/tileheight.html
    """

    id: typing.ClassVar[int] = 323
    name: typing.ClassVar[str] = "TileHeight"
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
class ExtraSamples(Tag):
    """Description of extra components, usually used to determine how to handle a potential alpha channel.
    https://www.awaresystems.be/imaging/tiff/tifftags/extrasamples.html
    """

    id: typing.ClassVar[int] = 338
    name: typing.ClassVar[str] = "ExtraSamples"
    value: bytes


@dataclass
class SampleFormat(Tag):
    """Specifies how to interpret each data sample in a pixel.
    https://www.awaresystems.be/imaging/tiff/tifftags/sampleformat.html
    """

    id: typing.ClassVar[int] = 339
    name: typing.ClassVar[str] = "SampleFormat"
    value: bytes


@dataclass
class JPEGTables(Tag):
    """JPEG quanitization and/or Huffman tables when image data is JPEG compressed.
    https://www.awaresystems.be/imaging/tiff/tifftags/jpegtables.html
    """

    id: typing.ClassVar[int] = 347
    name: typing.ClassVar[str] = "JPEGTables"
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

    def register_baseline(self):
        self.add(
            NewSubfileType,
            ImageWidth,
            ImageHeight,
            BitsPerSample,
            Compression,
            PhotometricInterpretation,
            SamplesPerPixel,
            XResolution,
            YResolution,
            PlanarConfiguration,
            ResolutionUnit,
            TileWidth,
            TileHeight,
            TileOffsets,
            TileByteCounts,
            ExtraSamples,
            SampleFormat,
            JPEGTables,
        )


tag_registry = TagRegistry()
