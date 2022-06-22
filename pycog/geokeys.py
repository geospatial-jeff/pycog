from dataclasses import dataclass
from typing import ClassVar

from pycog.types import MetaTag


@dataclass
class GeoKey(metaclass=MetaTag):
    tag_location: int
    count: int
    value: int
    code: ClassVar[int]


@dataclass
class GTModelType(GeoKey):
    code: ClassVar[int] = 1024


@dataclass
class GTRasterType(GeoKey):
    code: ClassVar[int] = 1025


@dataclass
class GTCitation(GeoKey):
    code: ClassVar[int] = 1026


@dataclass
class GeographicType(GeoKey):
    code: ClassVar[int] = 2048


@dataclass
class GeographicCitation(GeoKey):
    code: ClassVar[int] = 2049


@dataclass
class GeographicGeodeticDatum(GeoKey):
    code: ClassVar[int] = 2050


@dataclass
class GeographicPrimeMeridian(GeoKey):
    code: ClassVar[int] = 2051


@dataclass
class GeographicLinearUnits(GeoKey):
    code: ClassVar[int] = 2052


@dataclass
class GeographicLinearUnitSize(GeoKey):
    code: ClassVar[int] = 2053


@dataclass
class GeographicAngularUnits(GeoKey):
    code: ClassVar[int] = 2054


@dataclass
class GeographicAngularUnitSize(GeoKey):
    code: ClassVar[int] = 2055


@dataclass
class GeographicEllipsoid(GeoKey):
    code: ClassVar[int] = 2056


@dataclass
class GeographicSemiMajorAxis(GeoKey):
    code: ClassVar[int] = 2057


@dataclass
class GeographicSemiMinorAxis(GeoKey):
    code: ClassVar[int] = 2058


@dataclass
class GeographicInvFlattening(GeoKey):
    code: ClassVar[int] = 2059


@dataclass
class GeographicAzimuthUnits(GeoKey):
    code: ClassVar[int] = 2060


@dataclass
class ProjectedType(GeoKey):
    code: ClassVar[int] = 3072


@dataclass
class ProjectedLinearUnits(GeoKey):
    code: ClassVar[int] = 3076