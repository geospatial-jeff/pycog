import typing

from pycog.tags import tag_registry
from pycog.types import IFD, TAG_TYPES, Cog, Endian, Header, Tag, TiffVersion


# Byte order constants at the beginning of a TIFF file.
_ENDIAN_BYTES = {b"MM": Endian.big, b"II": Endian.little}


def read_endian(b: bytes) -> Endian:
    return _ENDIAN_BYTES[b]


def read_header(b: bytes) -> Header:
    endian = read_endian(b[:2])
    return Header(
        endian=endian,
        version=TiffVersion.from_bytes(b[2:4], endian.name),
        first_ifd_offset=int.from_bytes(b[4:8], endian.name),
    )


def read_tag(b: bytes, endian: Endian) -> typing.Optional[Tag]:
    # Bytes 0-2 contain the tag code.
    tag_code = int.from_bytes(b[:2], endian.name)
    tag_cls = tag_registry.get(tag_code)
    if not tag_cls:
        return None

    # Bytes 2-4 contain the tag's data type.
    data_type = int.from_bytes(b[2:4], endian.name)
    tag_type = TAG_TYPES[data_type]

    # Bytes 4-8 contain the number of values in the tag.
    # We use this to determine the size of the tag value.
    count = int.from_bytes(b[4:8], endian.name)
    size = count * tag_type.length

    # Bytes 8-12 contain the tag value if it fits, otherwise
    # it contains an offset to where the tag value is stored.
    if size <= 4:
        tag_value = b[8 : 8 + size]
    else:
        raise Exception("Not yet implemented")

    return tag_cls(count=count, type=tag_type, value=tag_value)


def read_ifd(b: bytes, endian: Endian) -> IFD:
    # Bytes 0-2 contain number of tags in the IFD.
    tag_count = int.from_bytes(b[:2], endian.name)

    tags = {}
    for idx in range(tag_count):
        tag_start = 2 + (12 * idx)
        tag = read_tag(b[tag_start:], endian)
        if tag:
            tags[tag.name] = tag

    # Last 4 bytes of the IFD point to the next IFD offset
    start = 2 + (12 * tag_count)
    next_ifd_offset = int.from_bytes(b[start : start + 4], endian.name)
    return IFD(tag_count=tag_count, next_ifd_offset=next_ifd_offset, tags=tags)


def open_cog(b: bytes) -> Cog:
    header = read_header(b)

    ifds = []
    ifd_offset = header.first_ifd_offset
    while ifd_offset != 0:
        ifd = read_ifd(b[ifd_offset:], header.endian)
        ifds.append(ifd)
        ifd_offset = ifd.next_ifd_offset

    return Cog(header=header, ifds=ifds)
