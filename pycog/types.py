import enum
from io import IOBase
import typing
from dataclasses import dataclass


class Endian(enum.Enum):
    """Endiannes of the TIFF file."""

    big = ">"
    little = "<"


class TiffVersion(enum.IntEnum):
    """An arbitrary but carefully chosen number which identifies the file as a TIFF."""

    tiff = 42
    bigtiff = 43


@dataclass
class Header:
    """A TIFF header.

    Consists of the first 8 bytes of the TIFF containing byte order (endianness),
    TIFF version, and offset to the first IFD.

    Args:
        endian: Endianness of the file.
        version: The TIFF version of the file.
        first_ifd_offset: Byte offset to first IFD.
    """

    endian: Endian
    version: TiffVersion
    first_ifd_offset: int


@dataclass
class IFD:
    """An Image File Directory (IFD).

    An IFD contains a set of TIFF tags that reference and describe the underlying image data.  Each IFD typically
    represents a single overview of a COG (or one level in an image pyramid).

    Args:
        tag_count: The number of tags in the IFD.
        next_ifd_offset: Byte offset to the next IFD; the last IFD should always have an offset of 0.
        tags: TIFF tags contained by the IFD.
    """

    tag_count: int
    next_ifd_offset: int
    tags: typing.Dict[str, typing.Any]


@dataclass
class TagType:
    """Tag data type.

    Args:
        format: The format character of the data type.
            (https://docs.python.org/3/library/struct.html#format-characters)
        length: The length of the data type.
        value: TIFF encoding of this data type.
    """

    format: str
    length: int
    value: int


TAG_TYPES = {
    1: TagType(format="B", length=1, value=1),  # TIFFByte
    2: TagType(format="c", length=1, value=2),  # TIFFascii
    3: TagType(format="H", length=2, value=3),  # TIFFshort
    4: TagType(format="L", length=4, value=4),  # TIFFlong
    5: TagType(format="f", length=4, value=5),  # TIFFrational
    7: TagType(format="B", length=1, value=7),  # undefined
    12: TagType(format="d", length=8, value=12),  # TIFFdouble
    16: TagType(format="Q", length=8, value=16),  # TIFFlong8
}


@dataclass
class Tag:
    """A TIFF Tag.

    Tags are named key/value pairs which contain metadata about the underlying image data.  They are grouped into:
        Baseline Tags: Tags included as part of the core TIFF spec.
        Extension Tags: Tags incldued as part of TIFf extensions (ex. GEOTIFF tags).
        Private Tags: Tags reserved for private use, allowing users to extend the TIFF spec as needed.

    Tags are often referred to as IFD entries.  Each entry contains a unique identifier, a data type, the number of
    expected values, and the tag value.  If the tag value is larger than 4 bytes, the value is isntead an offset
    to where the tag value is stored.  COGs typically store large tag values immediately after the respective IFD
    so they may be fetched in a single GET request upon opening the file.

    See `pycog/tags.py` for implementations of specific tags.

    Args:
        id: A unique identifier for the TIFF tag (ex. 256).
        name: A human readable name for the TIFF tag (ex. ImageWidth).
        count: The number of values included in the tag (ex. 1).
        size: The number of bytes in the tag value (ex. 6).
        type: The data type of the tag value (ex. TIFFShort).
        value: The serialized value of the TIFF tag (ex. \x08\x00).
    """

    id: typing.ClassVar[int]
    name: typing.ClassVar[str]
    type: TagType
    count: int
    size: int
    value: typing.Tuple[typing.Any]


@dataclass
class Cog:
    """A Cloud Optimized GeoTiff (COG).

    Just a wrapper over the other types defined in this file.

    Args:
        header: COG header.
        ifds: COG ifds.
    """

    header: Header
    ifds: typing.List[IFD]
    file_handle: IOBase
