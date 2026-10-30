
import pandas as pd
import pytest

from analysis import (
    load_data,
    compare_provinces,
    calculate_priorities,
    generate_insight,
)


@pytest.fixture
def data():
    return load_data()


def test_dataset_has_five_provinces(data):
    assert len(data) == 5


def test_provinces_are_unique(data):
    assert data["province"].is_unique


def test_no_missing_values(data):
    assert data.isna().sum().sum() == 0


def test_monetary_poverty_valid(data):
    assert data["monetary_poverty"].between(
        0, 100
    ).all()


def test_mpi_incidence_valid(data):
    assert data["mpi_incidence"].between(
        0, 100
    ).all()


def test_western_poverty(data):
    western = data.loc[
        data["province"] == "Western"
    ].iloc[0]

    assert western["monetary_poverty"] == pytest.approx(
        37.4
    )


def test_southern_mpi(data):
    southern = data.loc[
        data["province"] == "Southern"
    ].iloc[0]

    assert southern["mpi_incidence"] == pytest.approx(
        35.2
    )


def test_comparison(data):
    result = compare_provinces(
        data, "Western", "Southern"
    )

    assert len(result) == 2
    assert result.iloc[0]["province"] == "Western"
    assert result.iloc[1]["province"] == "Southern"


def test_scenario_scores(data):
    result = calculate_priorities(
        data,
        {
            "monetary_poverty": 50,
            "mpi_incidence": 50,
        },
    )

    assert len(result) == 5

    assert result["priority_score"].between(
        0, 100
    ).all()


def test_priority_order(data):
    result = calculate_priorities(
        data,
        {"monetary_poverty": 100}
    )

    assert result.iloc[0]["province"] == "Western"


def test_zero_weights(data):
    with pytest.raises(ValueError):
        calculate_priorities(
            data,
            {
                "monetary_poverty": 0,
                "mpi_incidence": 0,
            },
        )


def test_insight_generation(data):
    insight = generate_insight(
        data, "Western"
    )

    assert "Western" in insight
    assert "37.4%" in insight


def test_confidence_intervals(data):
    assert (
        data["monetary_ci_lower"]
        <= data["monetary_poverty"]
    ).all()

    assert (
        data["monetary_poverty"]
        <= data["monetary_ci_upper"]
    ).all()


def test_mpi_consistency(data):
    calculated = (
        data["mpi_incidence"]
        * data["mpi_intensity"]
        / 10000
    )

    assert all(
        abs(calculated - data["mpi_index"]) < 0.002
    )
