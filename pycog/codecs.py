import abc
from dataclasses import dataclass, field
import struct
import typing

import numpy as np
import numcodecs.abc
import imagecodecs
import imagecodecs.numcodecs

from pycog.types import IFD, Endian
from pycog.constants import SAMPLE_DTYPES


@dataclass
class Codec(abc.ABC):
    id: typing.ClassVar[int]
    numcodec: typing.ClassVar[typing.Type[numcodecs.abc.Codec]]

    @abc.abstractmethod
    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        ...


@dataclass
class Jpeg(Codec):
    id: typing.ClassVar[int] = 7
    numcodec: typing.ClassVar[typing.Type[imagecodecs.numcodecs.Jpeg]] = imagecodecs.numcodecs.Jpeg

    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        jpeg_tables = ifd.tags['JPEGTables']
        # TODO: Support photometric/colorspace
        jpeg_table_bytes = struct.pack(
            f"{endian.value}{jpeg_tables.count}{jpeg_tables.type.format}",
            *jpeg_tables.value,
        )
        
        codec = self.numcodec(tables=jpeg_table_bytes)
        return codec.decode(b)
    
    def encode(self, arr: np.ndarray) -> bytes:
        return self.numcodec().encode(arr)


class Deflate(Codec):
    id: typing.ClassVar[int] = 8
    numcodec: typing.ClassVar[typing.Type[imagecodecs.numcodecs.Deflate]] = imagecodecs.numcodecs.Deflate

    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        dtype = np.dtype(
            SAMPLE_DTYPES[(ifd.tags['SampleFormat'].value[0], ifd.tags['BitsPerSample'].value[0])]
        )
        decoded = self.numcodec().decode(b)
        arr = np.frombuffer(decoded, dtype).reshape(
            ifd.tags['TileHeight'].value[0], ifd.tags['TileWidth'].value[0], ifd.tags['SamplesPerPixel'].value[0]
        )
        
        # Unpredict
        if ifd.tags['Predictor'].value[0] == 2:
            imagecodecs.delta_decode(arr, out=arr, axis=1)
        
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
    *[inst() for inst in Codec.__subclasses__()]
)