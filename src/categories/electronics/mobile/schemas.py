"""Strongly-typed Pydantic schema for Smartphone & Mobile category attributes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from categories.contracts import AttributeValue


class MobileAttributes(BaseModel):
    """Pydantic validated attributes schema for smartphones and mobile devices."""

    model_config = ConfigDict(extra="allow", frozen=True)

    ram_gb: int | None = Field(default=None, ge=1, le=32, description="RAM in GB")
    storage_gb: int | None = Field(
        default=None, ge=1, le=2048, description="Internal storage in GB"
    )
    chipset: str | None = Field(default=None, description="SoC / Processor chipset")
    color: str | None = Field(default=None, description="Color finish")
    network_type: str = Field(default="5G", description="Network generation: 5G, 4G, 3G")
    screen_size_inches: float | None = Field(
        default=None, ge=1.5, le=8.5, description="Display size diagonal in inches"
    )
    display_type: str | None = Field(
        default=None, description="Display panel type (AMOLED, OLED, Super Retina, LCD)"
    )
    refresh_rate_hz: int | None = Field(
        default=None, ge=30, le=240, description="Display refresh rate in Hz"
    )
    primary_camera_mp: int | None = Field(
        default=None, ge=2, le=300, description="Main rear camera resolution in MP"
    )
    front_camera_mp: int | None = Field(
        default=None, ge=2, le=100, description="Front selfie camera resolution in MP"
    )
    battery_mah: int | None = Field(
        default=None, ge=500, le=15000, description="Battery capacity in mAh"
    )
    fast_charging_w: int | None = Field(
        default=None, ge=5, le=300, description="Fast charging speed in Watts"
    )
    operating_system: str | None = Field(
        default=None, description="Operating system (iOS, Android, etc.)"
    )
    camera_setup: str | None = Field(
        default=None, description="Camera configuration (Triple, Dual, Quad, Single)"
    )
    ois_supported: bool | None = Field(
        default=None, description="Optical Image Stabilization support"
    )
    resolution_standard: str | None = Field(
        default=None, description="Display resolution (FHD+, QHD+, 1.5K, HD+)"
    )
    peak_brightness_nits: int | None = Field(
        default=None, ge=100, le=10000, description="Peak display brightness in nits"
    )
    screen_protection: str | None = Field(
        default=None, description="Display glass protection (Ceramic Shield, Gorilla Glass)"
    )
    water_resistance_rating: str | None = Field(
        default=None, description="Ingress protection rating (IP68, IP67, IP65, IP54)"
    )
    biometrics: str | None = Field(
        default=None, description="Biometric security (Face ID, In-Display Fingerprint)"
    )
    audio_jack_3_5mm: bool | None = Field(
        default=None, description="Presence of 3.5mm headphone jack"
    )
    nfc_supported: bool | None = Field(default=None, description="Near-Field Communication support")
    weight_grams: float | None = Field(
        default=None, ge=50.0, le=600.0, description="Weight in grams"
    )
    sim_type: str | None = Field(
        default=None, description="SIM configuration (Dual SIM, eSIM, etc.)"
    )
    model_number: str | None = Field(default=None, description="Manufacturer model number")
    mpn: str | None = Field(default=None, description="Manufacturer Part Number")
    gtin: str | None = Field(default=None, description="Global Trade Item Number")
    ean: str | None = Field(default=None, description="European Article Number")
    asin: str | None = Field(default=None, description="Amazon Standard Identification Number")
    warranty: str | None = Field(default=None, description="Product warranty terms")
    spec_sections: dict[str, Any] | str | None = Field(
        default=None, description="Hierarchical specification categories"
    )

    def to_attribute_dict(self) -> dict[str, AttributeValue]:
        """Convert validated model to standard flat attribute dictionary."""
        data: dict[str, Any] = self.model_dump(exclude_none=True)
        return {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool, dict, list))}
