import abc
from dataclasses import dataclass, field
import struct
import typing

from pycog.types import IFD, Endian

import numpy as np
import numcodecs.abc
import imagecodecs.numcodecs as imagecodecs


# @singledispatch
# def decompress(codec: Codec, ifd: IFD, b: bytes):
#     ...


# @decompress.register
# def _(codec: Jpeg, ifd: IFD, b: bytes):
#     jpeg_tables = 

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
    numcodec: typing.ClassVar[typing.Type[imagecodecs.Jpeg]] = imagecodecs.Jpeg

    def decode(self, b: bytes, ifd: IFD, endian: Endian) -> np.ndarray:
        jpeg_tables = ifd.tags['JPEGTables']
        # TODO: Support photometric/colorspace
        jpeg_table_bytes = struct.pack(
            f"{endian.value}{jpeg_tables.count}{jpeg_tables.type.format}",
            *jpeg_tables.value,
        )
        
        codec = self.numcodec(tables=jpeg_table_bytes)
        return codec.decode(b)    


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