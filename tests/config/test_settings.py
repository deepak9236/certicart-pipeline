from config import Settings


def test_settings_use_safe_pipeline_defaults() -> None:
    settings = Settings()

    assert settings.environment == "development"
    assert settings.obey_robots_txt is True
    assert settings.max_source_concurrency == 2
    assert settings.collection_profile == "smoke"
    assert settings.database_url.get_secret_value().startswith("postgresql+psycopg://")
