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
from pycog.tags import ChromaSubSampling, Tag, Compression, PhotometricInterpretation
from pycog.constants import SAMPLE_DTYPES


@dataclass
class Codec(abc.ABC):
    id: typing.ClassVar[int]
    # numcodec: numcodecs.abc.Codec = None

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


@dataclass
class Jpeg(Codec):
    id: typing.ClassVar[int] = 7
    numcodec: imagecodecs.numcodecs.Jpeg = field(default_factory=imagecodecs.numcodecs.Jpeg)


    class Photometric(enum.IntEnum):
        """https://github.com/cgohlke/imagecodecs/blob/master/imagecodecs/_jpeg8.pyx#L403"""
        MINISWHITE = 0
        MINISBLACK = 1
        RGB = 2
        CMYK = 5
        YCBCR = 6


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
        if self.numcodec.colorspace_data:
            tags[PhotometricInterpretation.name] = PhotometricInterpretation(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(getattr(self.Photometric, self.numcodec.colorspace_data).value,)
            )
        if self.numcodec.subsampling:
            tags[ChromaSubSampling.name] = ChromaSubSampling(
                type=TAG_TYPES[3],
                count=2,
                size=4,
                value=self.numcodecs.subsampling
            )
        return tags


    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        """Decode bytes into a numpy array."""
        jpeg_tables = ifd.tags['JPEGTables']
        jpeg_table_bytes = struct.pack(
            f"{endian.value}{jpeg_tables.count}{jpeg_tables.type.format}",
            *jpeg_tables.value,
        )

        try:
            subsampling = ifd.tags['ChromaSubSampling'].value
        except KeyError:
            subsampling = None

        codec = self.numcodec.__class__(
            tables=jpeg_table_bytes,
            # TOOD: I think imagecodecs might infer `colorspace_jpeg`
            colorspace_jpeg=self.Photometric(ifd.tags['PhotometricInterpretation'].value[0]).name,
            colorspace_data=self.Photometric.RGB.name,
            subsampling=subsampling
        )
        print("DECOMPRESSING WITH: ", codec)
        return codec.decode(b)
    
    def encode(self, arr: np.ndarray) -> bytes:
        """Encode numpy array to bytes."""
        print("COMPRESSING WITH: ", self.numcodec)

        return self.numcodec.encode(arr)


@dataclass
class Deflate(Codec):
    id: typing.ClassVar[int] = 8
    numcodec: imagecodecs.numcodecs.Deflate = field(default_factory=imagecodecs.numcodecs.Deflate)

    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        """Decode bytes into a numpy array."""
        dtype = np.dtype(
            SAMPLE_DTYPES[(ifd.tags['SampleFormat'].value[0], ifd.tags['BitsPerSample'].value[0])]
        )
        codec = self.numcodec.__class__()
        decoded = codec.decode(b)
        arr = np.frombuffer(decoded, dtype).reshape(
            ifd.tags['TileHeight'].value[0], ifd.tags['TileWidth'].value[0], ifd.tags['SamplesPerPixel'].value[0]
        )
        
        # Unpredict
        if ifd.tags['Predictor'].value[0] == 2:
            imagecodecs.delta_decode(arr, out=arr, axis=1)
        
        return arr
    
    def encode(self, arr: np.ndarray) -> bytes:
        """Encode numpy array to bytes."""
        ...

    def create_tags(self) -> typing.Dict[int, Tag]:
        """Create compression-specific tiff tags."""
        ...


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
    *[inst() for inst in Codec.__subclasses__()]
)