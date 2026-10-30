
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "poverty_cleaned.csv"

METRICS = {
    "Monetary poverty": "monetary_poverty",
    "Multidimensional poverty": "mpi_incidence",
}

NATIONAL = {
    "monetary_poverty": 27.4,
    "mpi_incidence": 30.5,
}


# --------------------------------------------------
# Load and validate NISR data
# --------------------------------------------------

def load_data(path=DATA_FILE):
    df = pd.read_csv(path)

    required = [
        "province",
        "monetary_poverty",
        "mpi_incidence",
        "mpi_intensity",
        "mpi_index",
        "monetary_ci_lower",
        "monetary_ci_upper",
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df["province"].duplicated().any():
        raise ValueError("Duplicate provinces found.")

    numeric_columns = [
        column for column in required
        if column != "province"
    ]

    df[numeric_columns] = df[numeric_columns].apply(
        pd.to_numeric,
        errors="raise",
    )

    if df[numeric_columns].isna().any().any():
        raise ValueError("Dataset contains missing values.")

    percentage_columns = [
        "monetary_poverty",
        "mpi_incidence",
        "mpi_intensity",
        "monetary_ci_lower",
        "monetary_ci_upper",
    ]

    for column in percentage_columns:
        if not df[column].between(0, 100).all():
            raise ValueError(
                f"Invalid percentage in {column}"
            )

    if not df["mpi_index"].between(0, 1).all():
        raise ValueError(
            "MPI index must be between 0 and 1."
        )

    invalid_intervals = (
        (df["monetary_ci_lower"] > df["monetary_poverty"])
        |
        (df["monetary_poverty"] > df["monetary_ci_upper"])
    )

    if invalid_intervals.any():
        raise ValueError(
            "Invalid monetary poverty confidence intervals."
        )

    if len(df) != 5:
        raise ValueError(
            f"Expected 5 provinces, found {len(df)}."
        )

    return df


# --------------------------------------------------
# Compare provinces
# --------------------------------------------------

def compare_provinces(df, first, second):
    if first not in df["province"].values:
        raise ValueError(f"Unknown province: {first}")

    if second not in df["province"].values:
        raise ValueError(f"Unknown province: {second}")

    result = df[
        df["province"].isin([first, second])
    ].copy()

    return (
        result.set_index("province")
        .loc[list(dict.fromkeys([first, second]))]
        .reset_index()
    )


# --------------------------------------------------
# Calculate intervention priority scores
# --------------------------------------------------

def calculate_priorities(df, weights):
    """
    Calculate illustrative regional priority scores.

    Each indicator is min-max normalized across the
    five provinces, then combined using user weights.

    This is not a prediction of policy effectiveness,
    the number of people living in poverty, or funding
    requirements.
    """

    total_weight = sum(weights.values())

    if total_weight <= 0:
        raise ValueError(
            "At least one weight must be greater than zero."
        )

    result = df[["province"]].copy()
    result["priority_score"] = 0.0

    for metric, weight in weights.items():

        if metric not in METRICS.values():
            raise ValueError(
                f"Unsupported metric: {metric}"
            )

        values = df[metric].astype(float)

        minimum = values.min()
        maximum = values.max()

        if maximum == minimum:
            normalized = pd.Series(
                0.0,
                index=df.index,
            )
        else:
            normalized = (
                (values - minimum)
                / (maximum - minimum)
            )

        result["priority_score"] += (
            normalized
            * (weight / total_weight)
            * 100
        )

    return (
        result.sort_values(
            "priority_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# --------------------------------------------------
# Generate evidence-based insights
# --------------------------------------------------

def generate_insight(df, province):

    selected = df.loc[
        df["province"] == province
    ]

    if selected.empty:
        raise ValueError(
            f"Unknown province: {province}"
        )

    row = selected.iloc[0]

    monetary = row["monetary_poverty"]
    mpi = row["mpi_incidence"]

    monetary_difference = (
        monetary - NATIONAL["monetary_poverty"]
    )

    mpi_difference = (
        mpi - NATIONAL["mpi_incidence"]
    )

    def describe_difference(value):
        if value > 0:
            return (
                f"{abs(value):.1f} percentage points "
                "above"
            )

        if value < 0:
            return (
                f"{abs(value):.1f} percentage points "
                "below"
            )

        return "equal to"

    return (
        f"{province} has an estimated monetary "
        f"poverty rate of {monetary:.1f}%, which is "
        f"{describe_difference(monetary_difference)} "
        "the national estimate. "

        f"Its multidimensional poverty incidence "
        f"is {mpi:.1f}%, which is "
        f"{describe_difference(mpi_difference)} "
        "the national estimate. "

        "These figures describe provincial "
        "conditions and should not be interpreted "
        "as predictions of individual poverty "
        "or the effectiveness of specific policies."
    )


# --------------------------------------------------
# Test directly
# --------------------------------------------------

if __name__ == "__main__":

    data = load_data()

    print("\nNISR EICV7 DATA LOADED SUCCESSFULLY\n")
    print(data.to_string(index=False))

    print("\nSAMPLE REGIONAL INSIGHT\n")

    print(
        generate_insight(
            data,
            "Western",
        )
    )

    print("\nSAMPLE PRIORITY RANKING\n")

    rankings = calculate_priorities(
        data,
        {
            "monetary_poverty": 60,
            "mpi_incidence": 40,
        },
    )

    print(rankings.to_string(index=False))
