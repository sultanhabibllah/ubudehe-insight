
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

poverty_file = DATA_DIR / "EICV7_Tables_Rwanda_Poverty_Profile.xlsx"
mpi_file = DATA_DIR / "Tables_and_Figures_EICV7_Multidimensional_Poverty_MPI.xlsx"

# Read the provincial monetary poverty table (Table 0.1)
poverty = pd.read_excel(
    poverty_file,
    sheet_name="Table 0.1. ",
    header=None,
    skiprows=5,
    nrows=5,
    usecols="A,B,F,G",
)

poverty.columns = [
    "province",
    "monetary_poverty",
    "monetary_ci_lower",
    "monetary_ci_upper",
]

# Standardize provincial names
names = {
    "Kigali City": "City of Kigali",
    "South": "Southern",
    "West": "Western",
    "North": "Northern",
    "East": "Eastern",
}

poverty["province"] = (
    poverty["province"].str.strip().replace(names)
)

# Read multidimensional poverty (Table B.5)
mpi = pd.read_excel(
    mpi_file,
    sheet_name="Table B.5",
    header=None,
    skiprows=8,
    nrows=5,
    usecols="B,D,E,F",
)

mpi.columns = [
    "province",
    "mpi_incidence",
    "mpi_intensity",
    "mpi_index",
]

mpi["province"] = mpi["province"].str.strip()

# Combine both official datasets by province
combined = poverty.merge(
    mpi,
    on="province",
    how="inner",
    validate="one_to_one",
)

# Verify all five provinces were included
assert len(combined) == 5, (
    "Expected five provinces. Check the source tables."
)

# Save cleaned dataset
output = DATA_DIR / "poverty_cleaned.csv"
combined.to_csv(output, index=False)

print("\nSUCCESS! NISR datasets combined.\n")
print(combined.to_string(index=False))
print(f"\nSaved to: {output}")
