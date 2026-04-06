"""NMEA2000 marine navigation utilities.

This module provides unit conversions and data structures for working with
NMEA2000 marine navigation data, as used in displays such as the
NMEA2000 Display on ESP32S3.

Note:
    NMEA2000 messages carry physical values in SI units (m/s, radians,
    kelvin, etc.).  The helpers below convert those values to the units
    commonly shown on marine instruments.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Conversion constants
# ---------------------------------------------------------------------------

_MS_TO_KNOTS: float = 1.94384449
_MS_TO_KMH: float = 3.6
_M_TO_FT: float = 3.28084
_K_TO_C_OFFSET: float = 273.15


# ---------------------------------------------------------------------------
# Unit enumerations
# ---------------------------------------------------------------------------


class SpeedUnit(Enum):
    """Speed unit options shown on marine displays.

    Attributes:
        KNOTS: Nautical miles per hour.
        KMH: Kilometres per hour.
        MS: Metres per second (SI).
    """

    KNOTS = "kn"
    KMH = "km/h"
    MS = "m/s"


class DepthUnit(Enum):
    """Depth / distance unit options.

    Attributes:
        METERS: Metres (SI).
        FEET: Feet.
    """

    METERS = "m"
    FEET = "ft"


class TemperatureUnit(Enum):
    """Temperature unit options.

    Attributes:
        CELSIUS: Degrees Celsius.
        FAHRENHEIT: Degrees Fahrenheit.
    """

    CELSIUS = "°C"
    FAHRENHEIT = "°F"


# ---------------------------------------------------------------------------
# Speed conversions
# ---------------------------------------------------------------------------


def ms_to_knots(speed_ms: float) -> float:
    """Convert speed from metres per second to knots.

    Args:
        speed_ms (float): Speed in m/s.

    Returns:
        float: Speed in knots.

    Examples:
        >>> round(ms_to_knots(1.0), 5)
        1.94384
    """
    return speed_ms * _MS_TO_KNOTS


def knots_to_ms(speed_knots: float) -> float:
    """Convert speed from knots to metres per second.

    Args:
        speed_knots (float): Speed in knots.

    Returns:
        float: Speed in m/s.

    Examples:
        >>> round(knots_to_ms(1.0), 5)
        0.51444
    """
    return speed_knots / _MS_TO_KNOTS


def ms_to_kmh(speed_ms: float) -> float:
    """Convert speed from metres per second to kilometres per hour.

    Args:
        speed_ms (float): Speed in m/s.

    Returns:
        float: Speed in km/h.

    Examples:
        >>> ms_to_kmh(1.0)
        3.6
    """
    return speed_ms * _MS_TO_KMH


def kmh_to_ms(speed_kmh: float) -> float:
    """Convert speed from kilometres per hour to metres per second.

    Args:
        speed_kmh (float): Speed in km/h.

    Returns:
        float: Speed in m/s.

    Examples:
        >>> kmh_to_ms(3.6)
        1.0
    """
    return speed_kmh / _MS_TO_KMH


def convert_speed(speed_ms: float, unit: SpeedUnit) -> float:
    """Convert speed from m/s to the requested unit.

    Args:
        speed_ms (float): Speed in m/s.
        unit (SpeedUnit): Target unit.

    Returns:
        float: Speed in the requested unit.

    Examples:
        >>> round(convert_speed(1.0, SpeedUnit.KNOTS), 5)
        1.94384
        >>> convert_speed(1.0, SpeedUnit.KMH)
        3.6
        >>> convert_speed(1.0, SpeedUnit.MS)
        1.0
    """
    if unit == SpeedUnit.KNOTS:
        return ms_to_knots(speed_ms)
    if unit == SpeedUnit.KMH:
        return ms_to_kmh(speed_ms)
    return speed_ms


# ---------------------------------------------------------------------------
# Depth / distance conversions
# ---------------------------------------------------------------------------


def m_to_ft(distance_m: float) -> float:
    """Convert a distance from metres to feet.

    Args:
        distance_m (float): Distance in metres.

    Returns:
        float: Distance in feet.

    Examples:
        >>> round(m_to_ft(1.0), 5)
        3.28084
    """
    return distance_m * _M_TO_FT


def ft_to_m(distance_ft: float) -> float:
    """Convert a distance from feet to metres.

    Args:
        distance_ft (float): Distance in feet.

    Returns:
        float: Distance in metres.

    Examples:
        >>> round(ft_to_m(3.28084), 5)
        1.0
    """
    return distance_ft / _M_TO_FT


def convert_depth(depth_m: float, unit: DepthUnit) -> float:
    """Convert depth from metres to the requested unit.

    Args:
        depth_m (float): Depth in metres.
        unit (DepthUnit): Target unit.

    Returns:
        float: Depth in the requested unit.

    Examples:
        >>> round(convert_depth(1.0, DepthUnit.FEET), 5)
        3.28084
        >>> convert_depth(1.0, DepthUnit.METERS)
        1.0
    """
    if unit == DepthUnit.FEET:
        return m_to_ft(depth_m)
    return depth_m


# ---------------------------------------------------------------------------
# Temperature conversions
# ---------------------------------------------------------------------------


def kelvin_to_celsius(temp_k: float) -> float:
    """Convert temperature from kelvin to Celsius.

    Args:
        temp_k (float): Temperature in kelvin.

    Returns:
        float: Temperature in degrees Celsius.

    Examples:
        >>> kelvin_to_celsius(273.15)
        0.0
    """
    return temp_k - _K_TO_C_OFFSET


def celsius_to_fahrenheit(temp_c: float) -> float:
    """Convert temperature from Celsius to Fahrenheit.

    Args:
        temp_c (float): Temperature in degrees Celsius.

    Returns:
        float: Temperature in degrees Fahrenheit.

    Examples:
        >>> celsius_to_fahrenheit(0.0)
        32.0
        >>> celsius_to_fahrenheit(100.0)
        212.0
    """
    return temp_c * 9.0 / 5.0 + 32.0


def convert_temperature(temp_k: float, unit: TemperatureUnit) -> float:
    """Convert temperature from kelvin (NMEA2000 SI unit) to the requested unit.

    Args:
        temp_k (float): Temperature in kelvin.
        unit (TemperatureUnit): Target unit.

    Returns:
        float: Temperature in the requested unit.

    Examples:
        >>> convert_temperature(273.15, TemperatureUnit.CELSIUS)
        0.0
        >>> convert_temperature(373.15, TemperatureUnit.FAHRENHEIT)
        212.0
    """
    temp_c = kelvin_to_celsius(temp_k)
    if unit == TemperatureUnit.FAHRENHEIT:
        return celsius_to_fahrenheit(temp_c)
    return temp_c


# ---------------------------------------------------------------------------
# Angle helpers
# ---------------------------------------------------------------------------


def rad_to_deg(angle_rad: float) -> float:
    """Convert an angle from radians to degrees, normalised to [0, 360).

    Args:
        angle_rad (float): Angle in radians.

    Returns:
        float: Angle in degrees in the range [0, 360).

    Examples:
        >>> rad_to_deg(0.0)
        0.0
        >>> round(rad_to_deg(math.pi), 1)
        180.0
        >>> round(rad_to_deg(2 * math.pi), 1)
        0.0
    """
    return math.degrees(angle_rad) % 360.0


# ---------------------------------------------------------------------------
# NMEA2000 data structures
# ---------------------------------------------------------------------------


@dataclass
class WindData:
    """Wind data decoded from NMEA2000 PGN 130306.

    NMEA2000 transmits wind speed in m/s and the wind angle in radians.

    Attributes:
        speed_ms (float): Wind speed in m/s.
        angle_rad (float): Wind angle in radians.
        apparent (bool): True for apparent wind, False for true wind.
    """

    speed_ms: float
    angle_rad: float
    apparent: bool = True

    def speed(self, unit: SpeedUnit = SpeedUnit.KNOTS) -> float:
        """Return wind speed in the requested unit.

        Args:
            unit (SpeedUnit): Target speed unit. Defaults to knots.

        Returns:
            float: Wind speed in the requested unit.
        """
        return convert_speed(self.speed_ms, unit)

    def angle_degrees(self) -> float:
        """Return wind angle in degrees, normalised to [0, 360).

        Returns:
            float: Wind angle in degrees.
        """
        return rad_to_deg(self.angle_rad)


@dataclass
class GpsData:
    """GPS position and velocity decoded from NMEA2000 PGN 129025 / 129026.

    NMEA2000 transmits SOG in m/s and COG in radians.

    Attributes:
        latitude (float): Latitude in decimal degrees (positive = North).
        longitude (float): Longitude in decimal degrees (positive = East).
        sog_ms (float): Speed over ground in m/s.
        cog_rad (float): Course over ground in radians.
    """

    latitude: float
    longitude: float
    sog_ms: float
    cog_rad: float

    def sog(self, unit: SpeedUnit = SpeedUnit.KNOTS) -> float:
        """Return speed over ground in the requested unit.

        Args:
            unit (SpeedUnit): Target speed unit. Defaults to knots.

        Returns:
            float: Speed over ground in the requested unit.
        """
        return convert_speed(self.sog_ms, unit)

    def cog_degrees(self) -> float:
        """Return course over ground in degrees, normalised to [0, 360).

        Returns:
            float: Course over ground in degrees.
        """
        return rad_to_deg(self.cog_rad)


@dataclass
class DepthData:
    """Water depth decoded from NMEA2000 PGN 128267.

    NMEA2000 transmits depth in metres.  An optional transducer offset can
    be applied to obtain depth below keel or below surface.

    Attributes:
        depth_m (float): Depth below transducer in metres.
        offset_m (float): Transducer offset in metres (positive = below keel).
    """

    depth_m: float
    offset_m: float = field(default=0.0)

    def depth(self, unit: DepthUnit = DepthUnit.METERS) -> float:
        """Return corrected water depth in the requested unit.

        Args:
            unit (DepthUnit): Target depth unit. Defaults to metres.

        Returns:
            float: Water depth with offset applied, in the requested unit.
        """
        return convert_depth(self.depth_m + self.offset_m, unit)
