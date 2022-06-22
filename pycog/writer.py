import struct

from pycog.types import Cog, Endian, Header
from pycog.reader import read_tile

_ENDIAN_BYTES_REVERSE = {Endian.big: b"MM", Endian.little: b"II"}


def write_endian(endian: Endian) -> bytes:
    return _ENDIAN_BYTES_REVERSE[endian]


def write_header(header: Header) -> bytes:
    return (
        write_endian(header.endian)
        + header.version.to_bytes(2, header.endian.name)
        + header.first_ifd_offset.to_bytes(4, header.endian.name)
    )


def write_cog(cog: Cog) -> bytes:
    # TODO: Store image data
    endian = cog.header.endian

    # Hard code header size to 8; skip GDAL ghost area.
    # https://gdal.org/drivers/raster/cog.html#header-ghost-area
    cog.header.first_ifd_offset = 8


    # Read image data from the COG.
    image_segments = []
    for ifd in cog.ifds[::-1]:
        for (tile_offset, tile_byte_count) in zip(ifd.tags['TileOffsets'].value, ifd.tags['TileByteCounts'].value):
            cog.file_handle.seek(tile_offset)
            content = cog.file_handle.read(tile_byte_count)
            image_segments.append(content)
            # SANITY CHECK
            assert len(content) == tile_byte_count

    # Adjust tile offsets
    image_data_offset = cog.header_size
    for ifd in cog.ifds[::-1]:
        tile_byte_counts = ifd.tags['TileByteCounts'].value

        new_offsets = []
        for byte_count in tile_byte_counts:
            new_offsets.append(image_data_offset)
            image_data_offset += byte_count

        ifd.tags['TileOffsets'].value = tuple(new_offsets)

    # Write the header (first 8 bytes).
    cog_segments = [
        write_header(cog.header)
    ]

    next_ifd_offset = cog.header.first_ifd_offset
    for idx, ifd in enumerate(cog.ifds):
        # Keep track of where we are writing large tag values.
        large_tag_offset = 0
        large_tag_values = []

        # Calculate the expected size of the IFD body.
        ifd_size = 2 + (12 * len(ifd.tags)) + 4

        # First 2 bytes of the IFD contains number of tags.
        ifd_segments = []
        ifd_segments.append(len(ifd.tags).to_bytes(2, endian.name))

        # Write the tags next, 12 bytes each.
        for tag in ifd.tags.values():
            tag_code = tag.id.to_bytes(2, endian.name)
            tag_type = tag.type.value.to_bytes(2, endian.name)
            tag_count = tag.count.to_bytes(4, endian.name)

            if tag.size <= 4:
                # Short tag values (less than 4 bytes) are stored directly in the tag body.
                tag_value = struct.pack(
                    f"{endian.value}{tag.count}{tag.type.format}", *tag.value
                )
                if tag.size != 4:
                    # Zero pad the tag value until it's 4 bytes.
                    tag_value = tag_value.ljust(4, b"\0")
            else:
                # Write long tag values to the end of the IFD.
                # The last 4 bytes of the tag become offset to the tag's value.
                tag_value_offset = next_ifd_offset + ifd_size + large_tag_offset
                tag_value = tag_value_offset.to_bytes(4, endian.name)
                large_tag_values.append(
                    struct.pack(
                        f"{endian.value}{tag.count}{tag.type.format}", *tag.value
                    )
                )
                large_tag_offset += tag.size

            # Write tag to the IFD.
            tag_segments = [tag_code, tag_type, tag_count, tag_value]
            ifd_segments += tag_segments

            # SANITY CHECK
            assert sum(map(len, tag_segments)) == 12

        # Last 4 bytes of the IFD are the offset to the next IFD.
        # The next IFD begins after the long tag values from the previous IFD.
        # If this is the last IFD in the file the offset should be 0.
        # Note that image data is stored after all IFDs.
        if idx == len(cog.ifds) - 1:
            next_ifd_offset = 0
        else:
            next_ifd_offset += ifd_size + large_tag_offset

        ifd_segments.append(
            next_ifd_offset.to_bytes(4, endian.name)
        )

        # Append large tag values to the end of the IFD
        ifd_segments += large_tag_values

        # Write the IFD to the COG
        cog_segments += ifd_segments

    # SANITY CHECK
    assert sum(map(len, cog_segments)) == cog.header_size

    # Write image data
    cog_segments += image_segments

    # SANITY CHECK
    assert sum(map(len, cog_segments)) == image_data_offset

    return b"".join(cog_segments)