import pandas as pd
import numpy as np

def validate_file(file_path):
    """
    Validate the dataset and return:
    - stats about valid/invalid rows
    - error summary
    """
    errors = []
    df = pd.read_csv(file_path)

    n_rows = len(df)
    n_invalid = 0

    # Check required columns
    required_columns = ["Airline", "Source", "Destination", "Price", "Date_of_Journey"]
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
            n_invalid = n_rows
            return df, {"rows": n_rows, "invalid": n_invalid, "errors": errors}

    # Missing values
    for col in required_columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            errors.append(f"Missing values in {col}: {missing_count}")
            n_invalid += missing_count

    # Unknown categorical values (simple rule: "Unknown_" prefix)
    for col in ["Airline", "Source", "Destination"]:
        if col in df.columns:
            mask = df[col].astype(str).str.startswith("Unknown_")
            unknown_count = mask.sum()
            if unknown_count > 0:
                errors.append(f"Unknown values in {col}: {unknown_count}")
                n_invalid += unknown_count

    # Negative numeric values
    for col in ["Price", "Total_Stops"]:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                errors.append(f"Negative values in {col}: {neg_count}")
                n_invalid += neg_count

    # String in numeric column
    for col in ["Price", "Total_Stops"]:
        if col in df.columns:
            non_numeric = df[col].apply(lambda x: isinstance(x, str)).sum()
            if non_numeric > 0:
                errors.append(f"Non-numeric values in {col}: {non_numeric}")
                n_invalid += non_numeric

    # Invalid date format
    if "Date_of_Journey" in df.columns:
        invalid_dates = 0
        for v in df["Date_of_Journey"]:
            try:
                pd.to_datetime(v, format="%Y/%m/%d", errors="raise")
            except Exception:
                invalid_dates += 1
        if invalid_dates > 0:
            errors.append(f"Invalid date format in Date_of_Journey: {invalid_dates}")
            n_invalid += invalid_dates

    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        errors.append(f"Duplicate rows: {dup_count}")
        n_invalid += dup_count

    return df, {
        "rows": n_rows,
        "invalid": n_invalid,
        "valid": n_rows - n_invalid,
        "errors": errors
    }
