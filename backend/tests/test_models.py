import pytest
from pydantic import ValidationError

from app.domain.models import LocationItem, TargetLocation, UnitsSpec


def test_location_item_validation():
    item = LocationItem(
        provider_id="123",
        name="Tingo María",
        country="Perú",
        country_code="PE",
        latitude=-9.29,
        longitude=-76.00,
        timezone="America/Lima",
        admin1="Huánuco",
        admin2="Leoncio Prado",
        display_name="Tingo María, Leoncio Prado, Huánuco, Perú",
    )
    assert item.name == "Tingo María"
    assert item.country_code == "PE"


def test_invalid_coordinates():
    with pytest.raises(ValidationError):
        LocationItem(
            provider_id="123",
            name="Invalid",
            country="Test",
            country_code="TS",
            latitude=100.0,  # Invalid latitude (>90)
            longitude=0.0,
            timezone="UTC",
            display_name="Invalid",
        )


def test_target_location():
    loc = TargetLocation(latitude=-9.29, longitude=-76.00, timezone="America/Lima")
    assert loc.latitude == -9.29
    assert loc.longitude == -76.00


def test_units_spec():
    u = UnitsSpec(temperature="°C", wind_speed="km/h", precipitation="mm")
    assert u.temperature == "°C"
