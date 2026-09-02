"""Unit tests for strongly-typed LaptopAttributes and MobileAttributes Pydantic schemas."""

import pytest
from pydantic import ValidationError

from categories.electronics.laptop.schemas import LaptopAttributes
from categories.electronics.mobile.schemas import MobileAttributes


def test_laptop_attributes_validation() -> None:
    attrs = LaptopAttributes(
        ram_gb=16,
        storage_gb=512,
        cpu_model="Apple M3 Pro",
        gpu_model="M3 Pro GPU",
        screen_size_inches=14.2,
        operating_system="macOS",
        color="Space Black",
        ram_type="Unified Memory",
        display_resolution="Liquid Retina",
        weight_kg=1.6,
        battery_wh=70.0,
        keyboard_backlight=True,
    )
    dumped = attrs.to_attribute_dict()
    assert dumped["ram_gb"] == 16
    assert dumped["storage_gb"] == 512
    assert dumped["cpu_model"] == "Apple M3 Pro"
    assert dumped["screen_size_inches"] == 14.2
    assert dumped["operating_system"] == "macOS"
    assert dumped["ram_type"] == "Unified Memory"
    assert dumped["display_resolution"] == "Liquid Retina"
    assert dumped["weight_kg"] == 1.6
    assert dumped["battery_wh"] == 70.0
    assert dumped["keyboard_backlight"] is True


def test_laptop_attributes_invalid_bounds() -> None:
    with pytest.raises(ValidationError):
        LaptopAttributes(ram_gb=0)  # ge=1

    with pytest.raises(ValidationError):
        LaptopAttributes(screen_size_inches=50.0)  # le=24.0

    with pytest.raises(ValidationError):
        LaptopAttributes(weight_kg=50.0)  # le=10.0


def test_mobile_attributes_validation() -> None:
    attrs = MobileAttributes(
        ram_gb=12,
        storage_gb=256,
        chipset="Snapdragon 8 Gen 3",
        color="Titanium Gray",
        screen_size_inches=6.8,
        display_type="Dynamic AMOLED 2X",
        refresh_rate_hz=120,
        primary_camera_mp=200,
        battery_mah=5000,
        fast_charging_w=45,
        operating_system="Android 14",
        resolution_standard="QHD+",
        camera_setup="Quad Camera",
        water_resistance_rating="IP68",
        screen_protection="Gorilla Glass Victus 2",
        ois_supported=True,
        weight_grams=221.0,
    )
    dumped = attrs.to_attribute_dict()
    assert dumped["ram_gb"] == 12
    assert dumped["storage_gb"] == 256
    assert dumped["chipset"] == "Snapdragon 8 Gen 3"
    assert dumped["screen_size_inches"] == 6.8
    assert dumped["display_type"] == "Dynamic AMOLED 2X"
    assert dumped["refresh_rate_hz"] == 120
    assert dumped["primary_camera_mp"] == 200
    assert dumped["battery_mah"] == 5000
    assert dumped["fast_charging_w"] == 45
    assert dumped["operating_system"] == "Android 14"
    assert dumped["resolution_standard"] == "QHD+"
    assert dumped["camera_setup"] == "Quad Camera"
    assert dumped["water_resistance_rating"] == "IP68"
    assert dumped["screen_protection"] == "Gorilla Glass Victus 2"
    assert dumped["ois_supported"] is True
    assert dumped["weight_grams"] == 221.0


def test_mobile_attributes_invalid_bounds() -> None:
    with pytest.raises(ValidationError):
        MobileAttributes(ram_gb=64)  # le=32 for phones

    with pytest.raises(ValidationError):
        MobileAttributes(primary_camera_mp=1000)  # le=300

    with pytest.raises(ValidationError):
        MobileAttributes(peak_brightness_nits=50000)  # le=10000
