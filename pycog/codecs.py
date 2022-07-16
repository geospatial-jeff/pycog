import abc
from dataclasses import dataclass, field
import enum
import struct
import typing

import numpy as np
import numcodecs.abc
import imagecodecs
import imagecodecs.numcodecs
from tifffile.tifffile import jpeg_decode_colorspace

from pycog.constants import JPEG_TABLES_RGB
from pycog.types import IFD, Endian, TagType, TAG_TYPES
from pycog.tags import ChromaSubSampling, Tag, Predictor, Compression, PhotometricInterpretation, ReferenceBlackWhite
from pycog.constants import SAMPLE_DTYPES


@dataclass
class Codec(numcodecs.abc.Codec):
    id: typing.ClassVar[int]
    ifd: IFD

    @classmethod
    @abc.abstractmethod
    def create_from_ifd(cls, ifd: IFD, endian: Endian) -> "Codec":
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


class Jpeg(imagecodecs.numcodecs.Jpeg, Codec):
    id: typing.ClassVar[int] = 7

    def __init__(
        self,
        bitspersample=None,
        tables=None,
        header=None,
        colorspace_data=None,
        colorspace_jpeg=None,
        level=None,
        subsampling=None,
        optimize=None,
        smoothing=None,
    ):
        super().__init__(
            bitspersample,
            tables,
            header,
            colorspace_data,
            colorspace_jpeg,
            level,
            subsampling,
            optimize,
            smoothing
        )

    @classmethod
    def create_from_ifd(cls, ifd: IFD, endian: Endian) -> "Codec":
        extra_samples = ifd.tags.get("ExtraSamples")
        photometric = ifd.tags.get("PhotometricInterpretation")
        planar_config = ifd.tags.get("PlanarConfiguration")

        colorspace, outcolorspace = jpeg_decode_colorspace(
            photometric.value[0],
            planar_config.value[0],
            extra_samples.value[0] if extra_samples else None
        )

        try:
            jpeg_tables = ifd.tags['JPEGTables']
            jpeg_tables = struct.pack(
                f"{endian.value}{jpeg_tables.count}{jpeg_tables.type.format}",
                *jpeg_tables.value,
            )
        except KeyError:
            jpeg_tables = None
        
        try:
            subsampling = ifd.tags['ChromaSubSampling'].value
        except KeyError:
            subsampling = None

        return cls(
            bitspersample=ifd.tags['BitsPerSample'].value[0],
            tables=jpeg_tables,
            # colorspace_data=outcolorspace,
            # colorspace_jpeg=colorspace,
            subsampling=subsampling,
            optimize=True,
            level=75
        )
    
    def create_tags(self) -> typing.Dict[int, Tag]:
        tags = {
            Compression.name: Compression(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(7,)
            ),
        }
        # Update photometric interpretation
        if self.colorspace_data is not None:
            tags[PhotometricInterpretation.name] = PhotometricInterpretation(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(self.colorspace_data,)
            )
        # Update subsampling
        if self.colorspace_data in {2, 6} and self.subsampling:
            tags[ChromaSubSampling.name] = ChromaSubSampling(
                type=TAG_TYPES[3],
                count=2,
                size=4,
                value=self.subsampling
            )
        # ReferenceBlackWhite is required for YCbCr images
        # https://www.verypdf.com/document/tiff6/pg_0087.htm
        if self.colorspace_data == 6:
            tags[ReferenceBlackWhite.name] = ReferenceBlackWhite(
                type=TAG_TYPES[5],
                count=6,
                size=24,
                value=(0.0, 255.0, 128.0, 255.0, 128.0, 255.0)
            )
        return tags


    def delete_tags(self) -> typing.List[str]:
        return [
            Predictor.name
        ]


@dataclass
class Deflate(imagecodecs.numcodecs.Deflate, Codec):
    id: typing.ClassVar[int] = 8

    def __init__(self, dtype=None, width=None, height=None, samples=None, level=None, raw=False):
        self.dtype = dtype
        self.width = width
        self.height = height
        self.samples = samples
        super().__init__(level, raw)

    @classmethod
    def create_from_ifd(cls, ifd: IFD, endian: Endian) -> "Deflate":
        dtype = np.dtype(
            SAMPLE_DTYPES[(ifd.tags['SampleFormat'].value[0], ifd.tags['BitsPerSample'].value[0])]
        )
        width = ifd.tags['TileWidth'].value[0]
        height = ifd.tags['TileHeight'].value[0]
        samples = ifd.tags['SamplesPerPixel'].value[0]
        return cls(dtype, width, height, samples)


    def create_tags(self) -> typing.Dict[int, Tag]:
        tags = {
                Compression.name: Compression(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(8,)
            ),
        }

        # Guess photometric interpretation
        if self.samples in (3, 4):
            tags[PhotometricInterpretation.name] = PhotometricInterpretation(
                type=TAG_TYPES[3],
                count=1,
                size=2,
                value=(Photometric.RGB.value,)
            )
        return tags


    def delete_tags(self):
        return []


    def decode(self, buf, out=None) -> np.ndarray:
        decoded = super().decode(buf, out)
        arr = np.frombuffer(decoded, self.dtype).reshape(
            self.height, self.width, self.samples
        )
        return arr


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