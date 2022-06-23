from dataclasses import dataclass, field
from enum import IntEnum
import typing

from pycog.types import MetaTag


@dataclass
class GeoKey(metaclass=MetaTag):
    tag_location: int
    count: int
    value_offset: int
    id: typing.ClassVar[int]
    parsed_value: typing.Optional[typing.Any] = None


@dataclass
class GTModelType(GeoKey):
    id: typing.ClassVar[int] = 1024


@dataclass
class GTRasterType(GeoKey):
    id: typing.ClassVar[int] = 1025

    class GTRasterTypeEnum(IntEnum):
        RasterPixelIsArea = 1
        RasterPixelIsPoint = 2

    def __post_init__(self):
        # TODO: This pattern will break when a geokey references another TIFF tag
        self.parsed_value = self.GTRasterTypeEnum(self.value_offset)



@dataclass
class GTCitation(GeoKey):
    id: typing.ClassVar[int] = 1026


@dataclass
class GeographicType(GeoKey):
    id: typing.ClassVar[int] = 2048


@dataclass
class GeographicCitation(GeoKey):
    id: typing.ClassVar[int] = 2049


@dataclass
class GeographicGeodeticDatum(GeoKey):
    id: typing.ClassVar[int] = 2050


@dataclass
class GeographicPrimeMeridian(GeoKey):
    id: typing.ClassVar[int] = 2051


@dataclass
class GeographicLinearUnits(GeoKey):
    id: typing.ClassVar[int] = 2052


@dataclass
class GeographicLinearUnitSize(GeoKey):
    id: typing.ClassVar[int] = 2053


@dataclass
class GeographicAngularUnits(GeoKey):
    id: typing.ClassVar[int] = 2054


@dataclass
class GeographicAngularUnitSize(GeoKey):
    id: typing.ClassVar[int] = 2055


@dataclass
class GeographicEllipsoid(GeoKey):
    id: typing.ClassVar[int] = 2056


@dataclass
class GeographicSemiMajorAxis(GeoKey):
    id: typing.ClassVar[int] = 2057


@dataclass
class GeographicSemiMinorAxis(GeoKey):
    id: typing.ClassVar[int] = 2058


@dataclass
class GeographicInvFlattening(GeoKey):
    id: typing.ClassVar[int] = 2059


@dataclass
class GeographicAzimuthUnits(GeoKey):
    id: typing.ClassVar[int] = 2060


@dataclass
class ProjectedType(GeoKey):
    id: typing.ClassVar[int] = 3072


@dataclass
class ProjectedLinearUnits(GeoKey):
    id: typing.ClassVar[int] = 3076


@dataclass
class GeoKeyRegistry:
    """Defines which geokeys are read when opening the GeoKeyDirectory tag.
    """

    tags: typing.Dict[int, typing.Type[GeoKey]] = field(default_factory=dict)

    def __post_init__(self):
        # Messing with GeoKeys is probably something most users won't do.
        # So it seems reasonable to register them all on import.
        self.add(
            GTModelType,
            GTRasterType,
            GTCitation,
            GeographicType,
            GeographicCitation,
            GeographicGeodeticDatum,
            GeographicPrimeMeridian,
            GeographicLinearUnits,
            GeographicLinearUnitSize,
            GeographicAngularUnits,
            GeographicAngularUnitSize,
            GeographicEllipsoid,
            GeographicSemiMajorAxis,
            GeographicSemiMinorAxis,
            GeographicInvFlattening,
            GeographicAzimuthUnits,
            ProjectedType,
            ProjectedLinearUnits,
        )

    def add(self, *keys: typing.Type[GeoKey]):
        self.tags.update({t.id:t for t in keys})

    def get(self, tag_code: int) -> typing.Optional[typing.Type[GeoKey]]:
        return self.tags.get(tag_code)


geokey_registry = GeoKeyRegistry()