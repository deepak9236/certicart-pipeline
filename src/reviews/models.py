"""Review target and aspect-sentiment contracts."""

from datetime import datetime
from enum import StrEnum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from categories import get_category


class ReviewTarget(StrEnum):
    PRODUCT = "product"
    SELLER = "seller"
    DELIVERY = "delivery"
    SERVICE = "service"


class Sentiment(StrEnum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class CollectedReview(BaseModel):
    """Auditable review captured from one source without author PII."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str = Field(min_length=1)
    source_product_id: str = Field(min_length=1)
    review_id: str = Field(min_length=1)
    category: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    target: ReviewTarget
    rating: float | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=500)
    body: str = Field(min_length=1, max_length=10_000)
    verified_purchase: bool | None = None
    helpful_votes: int | None = Field(default=None, ge=0)
    source_url: AnyHttpUrl
    published_at: datetime | None = None
    observed_at: datetime
    content_hash: str = Field(min_length=16)

    @field_validator("published_at", "observed_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("review timestamps must be timezone-aware")
        return value

    @field_validator("category")
    @classmethod
    def require_supported_category(cls, value: str) -> str:
        return get_category(value).code


class ReviewCollectionPage(BaseModel):
    """One bounded page returned by an authorized retailer review adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str = Field(min_length=1)
    source_product_id: str = Field(min_length=1)
    category: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    reviews: tuple[CollectedReview, ...] = Field(max_length=100)
    next_cursor: str | None = None
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value

    @field_validator("category")
    @classmethod
    def require_supported_category(cls, value: str) -> str:
        return get_category(value).code

    @model_validator(mode="after")
    def require_consistent_reviews(self) -> "ReviewCollectionPage":
        for review in self.reviews:
            identity = (review.source, review.source_product_id, review.category)
            if identity != (self.source, self.source_product_id, self.category):
                raise ValueError("review page contains a review for a different product")
        return self


class ReviewAspectEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    review_id: str = Field(min_length=1)
    variant_id: str | None = None
    category: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    target: ReviewTarget
    aspect: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    evidence_text: str = Field(min_length=1, max_length=500)
    model_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_category_aspect(self) -> "ReviewAspectEvidence":
        definition = get_category(self.category)
        if self.aspect not in definition.review_aspects:
            raise ValueError(f"unsupported {self.category} review aspect: {self.aspect!r}")
        return self
