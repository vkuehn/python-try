"""Tests for the python_try.nmea2000 module.

Note:
    Physical conversions are checked against well-known reference values.
    The data-class helpers are checked to confirm they delegate correctly
    to the underlying conversion functions.
"""

from __future__ import annotations

import math

import pytest

from python_try.nmea2000 import (
    DepthData,
    DepthUnit,
    GpsData,
    SpeedUnit,
    TemperatureUnit,
    WindData,
    celsius_to_fahrenheit,
    convert_depth,
    convert_speed,
    convert_temperature,
    ft_to_m,
    kelvin_to_celsius,
    kmh_to_ms,
    knots_to_ms,
    m_to_ft,
    ms_to_kmh,
    ms_to_knots,
    rad_to_deg,
)

# ---------------------------------------------------------------------------
# Speed conversions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("speed_ms", "expected_knots"),
    [
        pytest.param(0.0, 0.0, id="zero"),
        pytest.param(1.0, 1.94384449, id="one-ms"),
        pytest.param(10.0, 19.4384449, id="ten-ms"),
    ],
)
def test_ms_to_knots(speed_ms: float, expected_knots: float) -> None:
    """Test ms_to_knots against reference values."""
    assert ms_to_knots(speed_ms) == pytest.approx(expected_knots, rel=1e-5)


@pytest.mark.parametrize(
    ("speed_knots", "expected_ms"),
    [
        pytest.param(0.0, 0.0, id="zero"),
        pytest.param(1.0, 0.514444, id="one-knot"),
    ],
)
def test_knots_to_ms(speed_knots: float, expected_ms: float) -> None:
    """Test knots_to_ms against reference values."""
    assert knots_to_ms(speed_knots) == pytest.approx(expected_ms, rel=1e-4)


def test_ms_to_kmh() -> None:
    """Test ms_to_kmh with known values."""
    assert ms_to_kmh(1.0) == pytest.approx(3.6)
    assert ms_to_kmh(0.0) == 0.0


def test_kmh_to_ms() -> None:
    """Test kmh_to_ms with known values."""
    assert kmh_to_ms(3.6) == pytest.approx(1.0)


def test_knots_ms_roundtrip() -> None:
    """Converting knots→m/s→knots must be lossless."""
    assert knots_to_ms(ms_to_knots(5.0)) == pytest.approx(5.0, rel=1e-9)


def test_kmh_ms_roundtrip() -> None:
    """Converting km/h→m/s→km/h must be lossless."""
    assert kmh_to_ms(ms_to_kmh(7.5)) == pytest.approx(7.5, rel=1e-9)


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        pytest.param(SpeedUnit.KNOTS, 1.94384449, id="knots"),
        pytest.param(SpeedUnit.KMH, 3.6, id="kmh"),
        pytest.param(SpeedUnit.MS, 1.0, id="ms"),
    ],
)
def test_convert_speed(unit: SpeedUnit, expected: float) -> None:
    """Test convert_speed for each supported unit."""
    assert convert_speed(1.0, unit) == pytest.approx(expected, rel=1e-5)


# ---------------------------------------------------------------------------
# Depth / distance conversions
# ---------------------------------------------------------------------------


def test_m_to_ft() -> None:
    """Test m_to_ft with known values."""
    assert m_to_ft(1.0) == pytest.approx(3.28084, rel=1e-5)
    assert m_to_ft(0.0) == 0.0


def test_ft_to_m() -> None:
    """Test ft_to_m with known values."""
    assert ft_to_m(3.28084) == pytest.approx(1.0, rel=1e-5)


def test_ft_m_roundtrip() -> None:
    """Converting ft→m→ft must be lossless."""
    assert ft_to_m(m_to_ft(10.0)) == pytest.approx(10.0, rel=1e-9)


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        pytest.param(DepthUnit.METERS, 5.0, id="meters"),
        pytest.param(DepthUnit.FEET, 5.0 * 3.28084, id="feet"),
    ],
)
def test_convert_depth(unit: DepthUnit, expected: float) -> None:
    """Test convert_depth for each supported unit."""
    assert convert_depth(5.0, unit) == pytest.approx(expected, rel=1e-5)


# ---------------------------------------------------------------------------
# Temperature conversions
# ---------------------------------------------------------------------------


def test_kelvin_to_celsius() -> None:
    """Test kelvin_to_celsius at water freeze and boil points."""
    assert kelvin_to_celsius(273.15) == pytest.approx(0.0)
    assert kelvin_to_celsius(373.15) == pytest.approx(100.0)


def test_celsius_to_fahrenheit() -> None:
    """Test celsius_to_fahrenheit at known reference points."""
    assert celsius_to_fahrenheit(0.0) == pytest.approx(32.0)
    assert celsius_to_fahrenheit(100.0) == pytest.approx(212.0)
    assert celsius_to_fahrenheit(-40.0) == pytest.approx(-40.0)


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        pytest.param(TemperatureUnit.CELSIUS, 0.0, id="celsius"),
        pytest.param(TemperatureUnit.FAHRENHEIT, 32.0, id="fahrenheit"),
    ],
)
def test_convert_temperature(unit: TemperatureUnit, expected: float) -> None:
    """Test convert_temperature for each supported unit."""
    assert convert_temperature(273.15, unit) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Angle helper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rad", "expected_deg"),
    [
        pytest.param(0.0, 0.0, id="zero"),
        pytest.param(math.pi, 180.0, id="pi"),
        pytest.param(2 * math.pi, 0.0, id="full-circle"),
        pytest.param(-math.pi / 2, 270.0, id="negative"),
    ],
)
def test_rad_to_deg(rad: float, expected_deg: float) -> None:
    """Test rad_to_deg normalises output to [0, 360)."""
    assert rad_to_deg(rad) == pytest.approx(expected_deg, abs=1e-9)


# ---------------------------------------------------------------------------
# WindData dataclass
# ---------------------------------------------------------------------------


def test_wind_data_speed_default_unit() -> None:
    """WindData.speed() defaults to knots."""
    wind = WindData(speed_ms=5.0, angle_rad=math.pi / 4)
    assert wind.speed() == pytest.approx(ms_to_knots(5.0), rel=1e-9)


def test_wind_data_speed_kmh() -> None:
    """WindData.speed() returns km/h when requested."""
    wind = WindData(speed_ms=5.0, angle_rad=0.0)
    assert wind.speed(SpeedUnit.KMH) == pytest.approx(ms_to_kmh(5.0), rel=1e-9)


def test_wind_data_angle_degrees() -> None:
    """WindData.angle_degrees() converts radians to degrees."""
    wind = WindData(speed_ms=1.0, angle_rad=math.pi / 2)
    assert wind.angle_degrees() == pytest.approx(90.0, abs=1e-9)


def test_wind_data_apparent_default() -> None:
    """WindData.apparent defaults to True (apparent wind)."""
    wind = WindData(speed_ms=1.0, angle_rad=0.0)
    assert wind.apparent is True


# ---------------------------------------------------------------------------
# GpsData dataclass
# ---------------------------------------------------------------------------


def test_gps_data_sog_default_unit() -> None:
    """GpsData.sog() defaults to knots."""
    gps = GpsData(latitude=51.5, longitude=0.1, sog_ms=3.0, cog_rad=0.0)
    assert gps.sog() == pytest.approx(ms_to_knots(3.0), rel=1e-9)


def test_gps_data_sog_ms() -> None:
    """GpsData.sog() returns m/s when requested."""
    gps = GpsData(latitude=51.5, longitude=0.1, sog_ms=3.0, cog_rad=0.0)
    assert gps.sog(SpeedUnit.MS) == pytest.approx(3.0)


def test_gps_data_cog_degrees() -> None:
    """GpsData.cog_degrees() converts radians to degrees."""
    gps = GpsData(latitude=51.5, longitude=0.1, sog_ms=0.0, cog_rad=math.pi)
    assert gps.cog_degrees() == pytest.approx(180.0, abs=1e-9)


# ---------------------------------------------------------------------------
# DepthData dataclass
# ---------------------------------------------------------------------------


def test_depth_data_no_offset() -> None:
    """DepthData.depth() returns raw depth when offset is zero."""
    depth = DepthData(depth_m=10.0)
    assert depth.depth() == pytest.approx(10.0)


def test_depth_data_with_offset() -> None:
    """DepthData.depth() adds the transducer offset."""
    depth = DepthData(depth_m=10.0, offset_m=1.5)
    assert depth.depth() == pytest.approx(11.5)


def test_depth_data_feet() -> None:
    """DepthData.depth() converts to feet when requested."""
    depth = DepthData(depth_m=10.0)
    assert depth.depth(DepthUnit.FEET) == pytest.approx(m_to_ft(10.0), rel=1e-5)


def test_depth_data_default_offset_is_zero() -> None:
    """DepthData.offset_m defaults to 0.0."""
    depth = DepthData(depth_m=5.0)
    assert depth.offset_m == 0.0
