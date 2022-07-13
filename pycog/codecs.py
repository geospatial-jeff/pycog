import abc
from dataclasses import dataclass, field
import enum
import struct
import typing

import numpy as np
import numcodecs.abc
import imagecodecs
import imagecodecs.numcodecs

from pycog.constants import JPEG_TABLES_RGB
from pycog.types import IFD, Endian, TagType, TAG_TYPES
from pycog.tags import ChromaSubSampling, Tag, Compression, PhotometricInterpretation, ExtraSamples
from pycog.constants import SAMPLE_DTYPES


@dataclass
class Codec(abc.ABC):
    id: typing.ClassVar[int]
    # numcodec: numcodecs.abc.Codec = None

    @classmethod
    @abc.abstractmethod
    def create_from_ifd(cls, ifd: IFD) -> "Codec":
        ...

    @abc.abstractmethod
    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        """Decode bytes into a numpy array."""
        ...
    
    @abc.abstractmethod
    def encode(self, arr: np.ndarray) -> bytes:
        """Encode numpy array to bytes."""
        ...
    
    @abc.abstractmethod
    def create_tags(self) -> typing.Dict[int, Tag]:
        """Create compression-specific tiff tags."""
        ...


class Photometric(enum.IntEnum):
    """https://github.com/cgohlke/imagecodecs/blob/master/imagecodecs/_jpeg8.pyx#L403"""
    MINISWHITE = 0
    MINISBLACK = 1
    RGB = 2
    CMYK = 5
    YCBCR = 6


@dataclass
class Jpeg(Codec):
    id: typing.ClassVar[int] = 7
    jpeg_tables: typing.Optional[bytes] = None
    colorspace: typing.Optional[Photometric] = None
    subsampling: typing.Optional[typing.Tuple[int, int]] = None

    def __post_init__(self):
        self._encode = imagecodecs.numcodecs.Jpeg(
            tables=self.jpeg_tables,
            colorspace_jpeg=self.colorspace.name if self.colorspace else self.colorspace, # source
            colorspace_data=Photometric.YCBCR.value,
            subsampling=self.subsampling,
            optimize=True,
        ).encode
        self._decode = imagecodecs.numcodecs.Jpeg(
            tables=self.jpeg_tables,
            colorspace_jpeg=None,
            colorspace_data=None,
            subsampling=self.subsampling
        ).decode


    @classmethod
    def create_from_ifd(cls, ifd: IFD, endian: Endian) -> "Codec":
        try:
            jpeg_tables = ifd.tags['JPEGTables']
            jpeg_table_bytes = struct.pack(
                f"{endian.value}{jpeg_tables.count}{jpeg_tables.type.format}",
                *jpeg_tables.value,
            )
        except KeyError:
            jpeg_table_bytes = None

        try:
            subsampling = ifd.tags['ChromaSubSampling'].value
        except KeyError:
            subsampling = None
        
        colorspace = Photometric(ifd.tags['PhotometricInterpretation'].value[0])

        return cls(
            jpeg_tables=jpeg_table_bytes,
            colorspace=colorspace,
            subsampling=subsampling
        )


    def create_tags(self) -> typing.Dict[int, Tag]:
        """Create compression-specific tiff tags."""
        tags = {
            JPEG_TABLES_RGB.name: JPEG_TABLES_RGB,
            Compression.name: Compression(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(7,)
            )
        }
        if self.colorspace is not None:
            tags[PhotometricInterpretation.name] = PhotometricInterpretation(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(self.colorspace.value,)
            )
        if self.subsampling is not None:
            tags[ChromaSubSampling.name] = ChromaSubSampling(
                type=TAG_TYPES[3],
                count=2,
                size=4,
                value=self.subsampling
            )
        return tags


    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        """Decode bytes into a numpy array."""
        return self._decode(b)
    
    def encode(self, arr: np.ndarray) -> bytes:
        """Encode numpy array to bytes."""
        return self._encode(arr)


# @dataclass
# class Deflate(Codec):
#     id: typing.ClassVar[int] = 8
#     numcodec: imagecodecs.numcodecs.Deflate = field(default_factory=imagecodecs.numcodecs.Deflate)

#     def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
#         """Decode bytes into a numpy array."""
#         dtype = np.dtype(
#             SAMPLE_DTYPES[(ifd.tags['SampleFormat'].value[0], ifd.tags['BitsPerSample'].value[0])]
#         )
#         codec = self.numcodec.__class__()
#         decoded = codec.decode(b)
#         arr = np.frombuffer(decoded, dtype).reshape(
#             ifd.tags['TileHeight'].value[0], ifd.tags['TileWidth'].value[0], ifd.tags['SamplesPerPixel'].value[0]
#         )
        
#         # Unpredict
#         if ifd.tags['Predictor'].value[0] == 2:
#             imagecodecs.delta_decode(arr, out=arr, axis=1)
        
#         return arr
    
#     def encode(self, arr: np.ndarray) -> bytes:
#         """Encode numpy array to bytes."""
#         ...

#     def create_tags(self) -> typing.Dict[int, Tag]:
#         """Create compression-specific tiff tags."""
#         ...


@dataclass
class CodecRegistry:
    """Defines compressions supported by the library."""

    codecs: typing.Dict[int, Codec] = field(default_factory=dict)

    def add(self, *codec: Codec):
        self.codecs.update({c.id: c for c in codec})

    def get(self, code: int) -> typing.Optional[Codec]:
        return self.codecs.get(code)


codec_registry = CodecRegistry()
codec_registry.add(
    *[inst for inst in Codec.__subclasses__()]
)