"""Tests for database engine and session factory."""

from storage.engine import create_database_engine, get_session_factory, init_db
from storage.models import Base


def test_create_database_engine_sqlite() -> None:
    engine = create_database_engine("sqlite:///:memory:")
    assert engine is not None
    init_db(engine)
    assert len(Base.metadata.tables) >= 5

    factory = get_session_factory(engine)
    session = factory()
    assert session is not None
    session.close()
    engine.dispose()
