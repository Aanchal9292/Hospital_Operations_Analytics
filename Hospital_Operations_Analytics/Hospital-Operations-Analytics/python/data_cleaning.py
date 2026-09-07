"""
Hospital Operations Analytics - Data Cleaning
Demonstrates the cleaning steps referenced in the project write-up:
standardizing department names, handling duplicates, fixing missing
values, and validating dates/ages before loading into MySQL.
"""

import pandas as pd
import numpy as np

DATA_DIR = "../data"

# ---------------------------------------------------------------------
# Example 1: Standardizing inconsistent department name entries
# ---------------------------------------------------------------------
def standardize_department_names(df: pd.DataFrame, col: str = "Department_Name") -> pd.DataFrame:
    mapping = {
        "cardiology": "Cardiology", "CARDIOLOGY": "Cardiology", "Cardio": "Cardiology",
        "emergency": "Emergency", "ER": "Emergency",
    }
    df[col] = df[col].replace(mapping)
    df[col] = df[col].str.strip().str.title()
    return df


# ---------------------------------------------------------------------
# Example 2: Cleaning the raw appointments export (duplicates + missing waits)
# ---------------------------------------------------------------------
def clean_appointments(path_in: str, path_out: str) -> pd.DataFrame:
    df = pd.read_csv(path_in)

    n_before = len(df)
    df = df.drop_duplicates(subset=["Appointment_ID"])
    n_after_dedup = len(df)

    # Impute missing waiting times with the department-level median
    df["Waiting_Time"] = df.groupby("Department_ID")["Waiting_Time"].transform(
        lambda s: s.fillna(s.median())
    )

    df.to_csv(path_out, index=False)

    print(f"Appointments cleaning report:")
    print(f"  Rows before dedup   : {n_before}")
    print(f"  Rows after dedup    : {n_after_dedup} ({n_before - n_after_dedup} duplicates removed)")
    print(f"  Missing waits filled: {df['Waiting_Time'].isna().sum()} remaining nulls")
    return df


# ---------------------------------------------------------------------
# Example 3: Validating patient ages and admission/discharge date logic
# ---------------------------------------------------------------------
def validate_patients(df: pd.DataFrame) -> pd.DataFrame:
    invalid_age = ~df["Age"].between(0, 110)
    if invalid_age.any():
        print(f"Found {invalid_age.sum()} invalid ages -> clipping to [0, 110]")
        df["Age"] = df["Age"].clip(0, 110)
    return df


def validate_admissions(df: pd.DataFrame) -> pd.DataFrame:
    df["Admission_Date"] = pd.to_datetime(df["Admission_Date"])
    df["Discharge_Date"] = pd.to_datetime(df["Discharge_Date"], errors="coerce")

    bad_dates = df["Discharge_Date"] < df["Admission_Date"]
    if bad_dates.any():
        print(f"Found {bad_dates.sum()} rows where discharge precedes admission -> dropping")
        df = df[~bad_dates]
    return df


if __name__ == "__main__":
    print("=== 1. Standardizing department name variants (demo) ===")
    demo = pd.DataFrame({"Department_Name": ["Cardiology", "cardiology", "CARDIOLOGY", "Cardio", "  emergency "]})
    print(standardize_department_names(demo))

    print("\n=== 2. Cleaning raw appointments export ===")
    clean_appointments(
        f"{DATA_DIR}/appointments_RAW_uncleaned.csv",
        f"{DATA_DIR}/appointments_cleaned.csv",
    )

    print("\n=== 3. Validating patients & admissions ===")
    patients = pd.read_csv(f"{DATA_DIR}/patients.csv")
    patients = validate_patients(patients)

    admissions = pd.read_csv(f"{DATA_DIR}/admissions.csv")
    admissions = validate_admissions(admissions)
    print(f"Admissions rows after validation: {len(admissions)}")

    print("\nData cleaning complete. Cleaned files are in the data/ folder.")
