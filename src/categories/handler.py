"""Protocol defining the CategoryHandler interface for domain-specific intelligence."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from matching.fingerprint import ProductFingerprint
    from sources.contracts import ParsedProduct


@runtime_checkable
class CategoryHandler(Protocol):
    """Protocol for domain-specific category normalization and conflict resolution."""

    @property
    def category_code(self) -> str:
        """Category code identifier (e.g. 'laptop', 'mobile')."""
        ...

    def normalize(self, product: ParsedProduct) -> ProductFingerprint:
        """Extract structured attributes and build canonical fingerprint from parsed product."""
        ...

    def check_hard_conflicts(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> tuple[bool, str | None]:
        """Verify if two product fingerprints in this category have hard identity conflicts."""
        ...

    def compute_similarity(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> float:
        """Compute category-specific weighted attribute similarity score between 0.0 and 1.0."""
        ...
