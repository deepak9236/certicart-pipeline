from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from pricing import PriceObservation


def test_price_observation_keeps_conditional_price_separate() -> None:
    observation = PriceObservation(
        offer_id="offer-1",
        price_paise=6_000_000,
        mrp_paise=7_000_000,
        coupon_price_paise=5_900_000,
        in_stock=True,
        seller="Example Seller",
        observed_at=datetime.now(UTC),
    )

    assert observation.price_paise == 6_000_000
    assert observation.coupon_price_paise == 5_900_000


def test_price_observation_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        PriceObservation(
            offer_id="offer-1",
            price_paise=6_000_000,
            in_stock=True,
            observed_at=datetime.now(),
        )
