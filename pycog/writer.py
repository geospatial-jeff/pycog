import typing
from collections import deque

from pycog.types import IFD, Cog, Endian, Header, Tag

_ENDIAN_BYTES_REVERSE = {Endian.big: b"MM", Endian.little: b"II"}


def write_endian(endian: Endian) -> bytes:
    return _ENDIAN_BYTES_REVERSE[endian]


def write_header(header: Header) -> bytes:
    return (
        write_endian(header.endian)
        + header.version.to_bytes(2, header.endian.name)
        + header.first_ifd_offset.to_bytes(4, header.endian.name)
    )


def write_tag(tag: Tag, endian: Endian) -> typing.Tuple[bytes, bytes]:
    tag_code = tag.id.to_bytes(2, endian.name)
    tag_type = tag.type.value.to_bytes(2, endian.name)
    tag_count = tag.count.to_bytes(4, endian.name)

    # We return the tag header (first 8 bytes) and tag value separately.
    # This allows the caller to determine where values are inserted into the file.
    # Which is especially useful when writing values larger than 4 bytes.
    return (tag_code + tag_type + tag_count, tag.value)


def write_ifd(ifd: IFD, endian: Endian) -> bytes:
    # Write tags first.
    ifd_segments = deque()
    for tag in ifd.tags.values():
        tag_header, tag_value = write_tag(tag, endian)
        if len(tag_value) > 4:
            # TODO: Implement writing of large tags
            # Write the tag value to the end of the IFD.
            # Update last 4 bytes of the tag to contain offset to this value.
            continue
        else:
            tag_value = tag_value.ljust(4, b"\0")
        ifd_segments.append(tag_header + tag_value)

    # Prepend tag count based on how many tags we wrote.
    tag_count = len(ifd_segments).to_bytes(2, endian.name)
    ifd_segments.appendleft(tag_count)

    # Defer writing of last 4 bytes of IFD (next IFD offset) to caller.
    return b"".join(ifd_segments)


def write_cog(cog: Cog) -> bytes:
    # Strip ghost header area
    # https://gdal.org/drivers/raster/cog.html#header-ghost-area
    cog.header.first_ifd_offset = 8
    cog_segments = [write_header(cog.header)]

    ifd_offset = cog.header.first_ifd_offset
    for idx, ifd in enumerate(cog.ifds):
        # Write the body of each IFD.
        ifd_bytes = write_ifd(ifd, cog.header.endian)

        # Write the offset to the next IFD.
        # The last IFD in the file should have an offset of 0.
        if idx == len(cog.ifds) - 1:
            ifd_offset = 0
        else:
            ifd_offset = ifd_offset + len(ifd_bytes) + 4
        ifd_bytes += ifd_offset.to_bytes(4, cog.header.endian.name)
        cog_segments.append(ifd_bytes)

    return b"".join(cog_segments)
