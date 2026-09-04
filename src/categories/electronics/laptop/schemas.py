"""Strongly-typed Pydantic schema for Laptop category attributes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from categories.contracts import AttributeValue


class LaptopAttributes(BaseModel):
    """Pydantic validated attributes schema for laptops and notebooks."""

    model_config = ConfigDict(extra="allow", frozen=True)

    ram_gb: int | None = Field(default=None, ge=1, le=256, description="RAM in GB")
    storage_gb: int | None = Field(
        default=None, ge=16, le=16384, description="Internal storage in GB"
    )
    storage_type: str = Field(default="ssd", description="Storage drive technology")
    cpu_model: str | None = Field(default=None, description="Processor / Chipset model")
    gpu_model: str | None = Field(default=None, description="Graphics processing unit")
    screen_size_inches: float | None = Field(
        default=None, ge=9.0, le=24.0, description="Display diagonal in inches"
    )
    generation: str | None = Field(default=None, description="Processor generation")
    touch_screen: bool | None = Field(default=None, description="Touch screen support")
    refresh_rate_hz: int | None = Field(
        default=None, ge=30, le=360, description="Display refresh rate in Hz"
    )
    operating_system: str | None = Field(default=None, description="Pre-installed OS")
    color: str | None = Field(default=None, description="Product color finish")
    ram_type: str | None = Field(
        default=None, description="Memory technology (LPDDR5X, DDR5, DDR4, Unified Memory)"
    )
    gpu_vram_gb: int | None = Field(
        default=None, ge=1, le=48, description="Dedicated GPU VRAM in GB"
    )
    display_resolution: str | None = Field(
        default=None, description="Display resolution (4K UHD, 2.8K, 2.5K, FHD)"
    )
    display_type: str | None = Field(
        default=None, description="Panel type (OLED, IPS, Liquid Retina XDR, TN)"
    )
    aspect_ratio: str | None = Field(
        default=None, description="Screen aspect ratio (16:10, 16:9, 3:2)"
    )
    keyboard_backlight: bool | None = Field(default=None, description="Backlit keyboard present")
    webcam_resolution: str | None = Field(
        default=None, description="Integrated webcam resolution (1080p FHD, 720p HD)"
    )
    weight_kg: float | None = Field(
        default=None, ge=0.5, le=10.0, description="Device weight in kilograms"
    )
    battery_wh: float | None = Field(
        default=None, ge=10.0, le=150.0, description="Battery capacity in Watt-hours"
    )
    wifi_standard: str | None = Field(
        default=None, description="Wi-Fi connectivity standard (Wi-Fi 7, Wi-Fi 6E, Wi-Fi 6)"
    )
    model_number: str | None = Field(default=None, description="Manufacturer model number")
    mpn: str | None = Field(default=None, description="Manufacturer Part Number")
    gtin: str | None = Field(default=None, description="Global Trade Item Number")
    ean: str | None = Field(default=None, description="European Article Number")
    asin: str | None = Field(default=None, description="Amazon Standard Identification Number")

    def to_attribute_dict(self) -> dict[str, AttributeValue]:
        """Convert validated model to standard flat attribute dictionary."""
        data: dict[str, Any] = self.model_dump(exclude_none=True)
        return {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool, dict, list))}
