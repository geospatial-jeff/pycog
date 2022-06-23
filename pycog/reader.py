import math
from io import IOBase
import struct

from pycog.tags import tag_registry
from pycog.types import IFD, TAG_TYPES, Cog, Endian, Header, TiffVersion


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


def open_cog(file_handle: IOBase, header_size: int = 65536) -> Cog:
    # TODO: Simplifying assumption; header is read in one request.
    b = file_handle.read(header_size)
    header = read_header(b)

    # Find the offset of the first IFD.
    next_ifd_offset = header.first_ifd_offset

    # Read each IFD, the last IFD in the image will have a next IFD offset of 0.
    ifds = []
    while next_ifd_offset != 0:
        # First 2 bytes contain number of tags in the IFD.
        tag_count = int.from_bytes(
            b[next_ifd_offset : next_ifd_offset + 2], header.endian.name
        )

        # Read each tag.
        tags = {}
        for idx in range(tag_count):
            # Tags are always 12 bytes each.
            tag_start = next_ifd_offset + 2 + (12 * idx)

            # First 2 bytes contain tag code.
            tag_code = int.from_bytes(b[tag_start : tag_start + 2], header.endian.name)
            tag_cls = tag_registry.get(tag_code)

            if not tag_cls:
                print("Skipping tag: ", tag_code)
                continue

            # Bytes 2-4 contain the tag's field type.
            data_type = int.from_bytes(
                b[tag_start + 2 : tag_start + 4], header.endian.name
            )
            tag_type = TAG_TYPES[data_type]

            # Bytes 4-8 contain the number of values in the tag.
            # We use this to determine the overall size of the tag's value.
            count = int.from_bytes(b[tag_start + 4 : tag_start + 8], header.endian.name)
            size = count * tag_type.length

            # Bytes 8-12 contain the tag value if it fits, otherwise it contains
            # an offset to where the tag value is stored.
            if size <= 4:
                tag_value = b[tag_start + 8 : tag_start + 8 + size]
            else:
                value_offset = int.from_bytes(
                    b[tag_start + 8 : tag_start + 12], header.endian.name
                )
                tag_value = b[value_offset : value_offset + size]

            # Decode the tag's value based on field type.
            decoded_tag_value = struct.unpack(
                f"{header.endian.value}{count}{tag_type.format}", tag_value
            )
            tag = tag_cls(count=count, type=tag_type, size=size, value=decoded_tag_value)
            tags[tag.name] = tag

        # Last 4 bytes of IFD contains offset to the next IFD.
        next_ifd_offset = int.from_bytes(
            b[tag_start + 12 : tag_start + 12 + 4], header.endian.name
        )
        print(next_ifd_offset)
        ifds.append(
            IFD(tag_count=tag_count, next_ifd_offset=next_ifd_offset, tags=tags)
        )

    return Cog(header=header, ifds=ifds, file_handle=file_handle)


def read_tile(x: int, y: int, z: int, cog: Cog) -> bytes:
    # Calculate number of columns in the IFD.
    ifd = cog.ifds[z]
    image_width = ifd.tags["ImageWidth"].value[0]
    tile_width = ifd.tags["TileWidth"].value[0]
    columns = math.ceil(image_width / tile_width)

    # Tiles are stored row-major.
    idx = (y * columns) + x
    tile_offset = ifd.tags["TileOffsets"].value[idx]
    tile_byte_count = ifd.tags["TileByteCounts"].value[idx]

    # Read the tile.
    cog.file_handle.seek(tile_offset)
    tile_content = cog.file_handle.read(tile_byte_count)
    return tile_content
