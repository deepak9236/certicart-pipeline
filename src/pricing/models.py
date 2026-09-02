"""Price contracts separating unconditional and conditional prices."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    offer_id: str = Field(min_length=1)
    price_paise: int = Field(ge=0)
    mrp_paise: int | None = Field(default=None, ge=0)
    coupon_price_paise: int | None = Field(default=None, ge=0)
    in_stock: bool
    seller: str | None = None
    delivery_pincode: str | None = None
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value
