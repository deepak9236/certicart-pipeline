from typer.testing import CliRunner

from jobs.cli import app

runner = CliRunner()


def test_doctor_hides_database_url() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "configured" in result.stdout
    assert "postgresql" not in result.stdout
    assert "amazon" in result.stdout
    assert "smoke" in result.stdout


def test_pipeline_demo_runs() -> None:
    result = runner.invoke(app, ["pipeline-demo"])

    assert result.exit_code == 0
    assert '"decision": "match"' in result.stdout


def test_list_sources_reports_configured_retailers() -> None:
    result = runner.invoke(app, ["list-sources"])

    assert result.exit_code == 0
    assert '"amazon"' in result.stdout
    assert '"croma"' in result.stdout
    assert '"flipkart"' in result.stdout


def test_list_departments_reports_electronics() -> None:
    result = runner.invoke(app, ["list-departments"])

    assert result.exit_code == 0
    assert '"electronics"' in result.stdout


def test_list_categories_reports_electronics_laptop_taxonomy() -> None:
    result = runner.invoke(app, ["list-categories"])

    assert result.exit_code == 0
    assert '"department_code": "electronics"' in result.stdout
    assert '"gaming_laptop"' in result.stdout


def test_collection_plan_reports_bounded_product_and_review_volume() -> None:
    result = runner.invoke(
        app,
        [
            "collection-plan",
            "--source",
            "amazon",
            "--available-products",
            "1000",
            "--profile",
            "incremental",
        ],
    )

    assert result.exit_code == 0
    assert '"planned_products": 100' in result.stdout
    assert '"maximum_review_records": 2500' in result.stdout


def test_parse_demo_runs_for_all_sources() -> None:
    for source in ["flipkart", "croma", "amazon"]:
        result = runner.invoke(app, ["parse-demo", "--source", source])
        assert result.exit_code == 0
        assert f'"source": "{source}"' in result.stdout
        assert '"cpu_model"' in result.stdout
        assert '"price_paise": 5499000' in result.stdout


def test_reconcile_demo_runs() -> None:
    result = runner.invoke(app, ["reconcile-demo"])
    assert result.exit_code == 0
    assert '"total_collected": 4' in result.stdout
    assert '"total_clusters": 2' in result.stdout
    assert '"multi_source_clusters": 1' in result.stdout
    assert '"best_source": "croma"' in result.stdout


def test_live_collect_command_runs() -> None:
    result = runner.invoke(app, ["live-collect"])
    assert result.exit_code == 0
    assert "Initiating live collection" in result.stdout


def test_bulk_collect_laptops_command_runs() -> None:
    result = runner.invoke(app, ["bulk-collect-laptops", "--limit", "1"])
    assert result.exit_code == 0
    assert "Starting Multi-Source Bulk Collection" in result.stdout


def test_bulk_collect_all_command_runs() -> None:
    result = runner.invoke(
        app, ["bulk-collect", "--category", "all", "--sources", "all", "--limit", "1"]
    )
    assert result.exit_code == 0
    assert "Starting Multi-Source Bulk Collection" in result.stdout
