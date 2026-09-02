"""Tests for database lifecycle status persistence, updates, and distribution queries."""

from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from matching.fingerprint import ProductFingerprint
from matching.reconciliation import CanonicalVariantCluster, LinkedOffer, ReconciliationReport
from storage.engine import create_database_engine, get_session_factory, init_db
from storage.repository import PipelineRepository


def test_repository_lifecycle_persistence_and_distribution() -> None:
    engine = create_database_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)

    fp = ProductFingerprint(
        category="laptop",
        brand="Apple",
        model_name="MacBook Air M5",
        attributes={"ram_gb": 16, "storage_gb": 512},
    )

    offer1 = LinkedOffer(
        source="amazon",
        source_product_id="B0TEST001",
        source_url=AnyHttpUrl("https://amazon.in/dp/B0TEST001"),
        title="Apple MacBook Air M5 16GB 512GB",
        price_paise=13490000,
        mrp_paise=14990000,
        coupon_price_paise=None,
        in_stock=True,
        observed_at=datetime.now(UTC),
    )

    offer2 = LinkedOffer(
        source="croma",
        source_product_id="324343",
        source_url=AnyHttpUrl("https://croma.com/p/324343"),
        title="Apple MacBook Air M5 16GB 512GB",
        price_paise=13949000,
        mrp_paise=14990000,
        coupon_price_paise=None,
        in_stock=False,  # Out of stock -> UNAVAILABLE
        observed_at=datetime.now(UTC),
    )

    cluster = CanonicalVariantCluster.from_fingerprint(
        fingerprint=fp,
        offers=[offer1, offer2],
    )

    report = ReconciliationReport(
        total_collected=2,
        total_clusters=1,
        multi_source_clusters=1,
        review_required_count=0,
        source_breakdown={},
        clusters=(cluster,),
        generated_at=datetime.now(UTC),
    )

    with session_factory() as session, session.begin():
        metrics = PipelineRepository.persist_reconciliation_report(session, report)
        assert metrics["products_persisted"] == 1
        assert metrics["offers_persisted"] == 2

        dist = PipelineRepository.get_lifecycle_distribution(session)
        assert dist["ACTIVE"] == 1
        assert dist["UNAVAILABLE"] == 1

        # Test updating lifecycle manually to STALE / DISCONTINUED
        PipelineRepository.update_offer_lifecycle(
            session,
            retailer_product_id=1,
            lifecycle_status="STALE",
            missed_crawls=1,
        )

        dist2 = PipelineRepository.get_lifecycle_distribution(session)
        assert dist2["STALE"] == 1
