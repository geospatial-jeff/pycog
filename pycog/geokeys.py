from dataclasses import dataclass
from typing import ClassVar


@dataclass
class GeoKey:
    tag_location: int
    count: int
    value: int
    name: ClassVar[str]
    code: ClassVar[int]


@dataclass
class GTModelType(GeoKey):
    name: ClassVar[str] = "GTModelType"
    code: ClassVar[int] = 1024


@dataclass
class GTRasterType(GeoKey):
    name: ClassVar[str] = "GTRasterType"
    code: ClassVar[int] = 1025


@dataclass
class GTCitation(GeoKey):
    name: ClassVar[str] = "GTCitation"
    code: ClassVar[int] = 1026


@dataclass
class GeographicType(GeoKey):
    name: ClassVar[str] = "GeographicType"
    code: ClassVar[int] = 2048


@dataclass
class GeographicCitation(GeoKey):
    name: ClassVar[str] = "GeographicCitation"
    code: ClassVar[int] = 2049


@dataclass
class GeographicGeodeticDatum(GeoKey):
    name: ClassVar[str] = "GeographicGeodeticDatum"
    code: ClassVar[int] = 2050


@dataclass
class GeographicPrimeMeridian(GeoKey):
    name: ClassVar[str] = "GeographicPrimeMeridian"
    code: ClassVar[int] = 2051


@dataclass
class GeographicLinearUnits(GeoKey):
    name: ClassVar[str] = "GeographicLinearUnits"
    code: ClassVar[int] = 2052


@dataclass
class GeographicLinearUnitSize(GeoKey):
    name: ClassVar[str] = "GeographicLinearUnitSize"
    code: ClassVar[int] = 2053


@dataclass
class GeographicAngularUnits(GeoKey):
    name: ClassVar[str] = "GeographicAngularUnits"
    code: ClassVar[int] = 2054


@dataclass
class GeographicAngularUnitSize(GeoKey):
    name: ClassVar[str] = "GeographicLinearUnits"
    code: ClassVar[int] = 2055


@dataclass
class GeographicEllipsoid(GeoKey):
    name: ClassVar[str] = "GeographicEllipsoid"
    code: ClassVar[int] = 2056


@dataclass
class GeographicSemiMajorAxis(GeoKey):
    name: ClassVar[str] = "GeographicSemiMajorAxis"
    code: ClassVar[int] = 2057


@dataclass
class GeographicSemiMinorAxis(GeoKey):
    name: ClassVar[str] = "GeographicSemiMinorAxis"
    code: ClassVar[int] = 2058


@dataclass
class GeographicInvFlattening(GeoKey):
    name: ClassVar[str] = "GeographicInvFlattening"
    code: ClassVar[int] = 2059


@dataclass
class GeographicAzimuthUnits(GeoKey):
    name: ClassVar[str] = "GeographicAzimuthUnits"
    code: ClassVar[int] = 2060


@dataclass
class ProjectedType(GeoKey):
    name: ClassVar[str] = "ProjectedType"
    code: ClassVar[int] = 3072


@dataclass
class ProjectedLinearUnits(GeoKey):
    name: ClassVar[str] = "ProjectedLinearUnits"
    code: ClassVar[int] = 3076