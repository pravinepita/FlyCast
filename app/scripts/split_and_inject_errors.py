#!/usr/bin/env python3
"""
Split main dataset into multiple files and inject synthetic errors.
Save generated CSVs into the project-level `raw-data/` folder.
"""

import os
import argparse
import random
import numpy as np
import pandas as pd

# ---------- Path helpers ----------
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))  # SkyFareCast/
DEFAULT_DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset", "dataset.xlsx")
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "raw-data")  # folder to save split files

# ---------- Error injection utilities ----------
def safe_sample(df, size):
    """Return indices sampled without replacement, handle small dfs."""
    size = min(size, len(df))
    if size <= 0:
        return np.array([], dtype=int)
    return np.random.choice(df.index, size=size, replace=False)

def inject_errors(df_chunk, file_idx, seed=None):
    """Inject different types of synthetic errors into a dataframe chunk."""
    if seed is not None:
        np.random.seed(seed + file_idx)
        random.seed(seed + file_idx)

    df_err = df_chunk.copy(deep=True)
    n = len(df_err)
    cols = df_err.columns.tolist()

    # Candidate columns (adjust if your dataset uses different names)
    cat_candidates = [c for c in ["Airline", "Source", "Destination"] if c in cols]
    num_candidates = [c for c in ["Price", "Total_Stops", "dep_hour", "dep_minute", "arrival_hour", "arrival_minute"] if c in cols]
    date_candidates = [c for c in ["Date_of_Journey"] if c in cols]

    applied = []

    # 1) Drop a required column (20% chance)
    if cat_candidates and random.random() < 0.2:
        col_to_drop = random.choice(cat_candidates)
        df_err = df_err.drop(columns=[col_to_drop])
        applied.append(f"dropped_column:{col_to_drop}")

    # 2) Missing values in a required categorical column
    if cat_candidates and random.random() < 0.6:
        col = random.choice(cat_candidates)
        idx = safe_sample(df_err, max(1, n // 10))
        df_err.loc[idx, col] = np.nan
        applied.append(f"missing_cat_values:{col}:{len(idx)}")

    # 3) Unknown categorical values
    if cat_candidates and random.random() < 0.6:
        col = random.choice(cat_candidates)
        idx = safe_sample(df_err, max(1, n // 15))
        df_err.loc[idx, col] = f"Unknown_{file_idx}"
        applied.append(f"unknown_cat_values:{col}:{len(idx)}")

    # 4) Negative numeric values
    if num_candidates and random.random() < 0.5:
        col = random.choice(num_candidates)
        idx = safe_sample(df_err, max(1, n // 20))
        df_err.loc[idx, col] = -abs(np.random.randint(1, 100, size=len(idx)))
        applied.append(f"negative_numeric:{col}:{len(idx)}")

    # 5) String in numeric column
    if num_candidates and random.random() < 0.4:
        col = random.choice(num_candidates)
        idx = safe_sample(df_err, max(1, n // 20))
        df_err.loc[idx, col] = "NotANumber"
        applied.append(f"string_in_numeric:{col}:{len(idx)}")

    # 6) Invalid date format
    if date_candidates and random.random() < 0.4:
        col = date_candidates[0]
        idx = safe_sample(df_err, max(1, n // 20))
        df_err.loc[idx, col] = "31-31-2025"
        applied.append(f"invalid_date_format:{col}:{len(idx)}")

    # 7) Missing numeric values
    if num_candidates and random.random() < 0.5:
        col = random.choice(num_candidates)
        idx = safe_sample(df_err, max(1, n // 15))
        df_err.loc[idx, col] = np.nan
        applied.append(f"missing_numeric:{col}:{len(idx)}")

    # 8) Duplicate some rows
    if random.random() < 0.3:
        dup_idx = safe_sample(df_err, max(1, n // 20))
        if len(dup_idx) > 0:
            df_dup = df_err.loc[dup_idx].copy()
            df_err = pd.concat([df_err, df_dup], ignore_index=True)
            applied.append(f"duplicated_rows:{len(dup_idx)}")

    # 9) Leading/trailing whitespace in categorical values
    if cat_candidates and random.random() < 0.4:
        col = random.choice(cat_candidates)
        idx = safe_sample(df_err, max(1, n // 25))
        for i in idx:
            if pd.notna(df_err.at[i, col]):
                df_err.at[i, col] = f" {df_err.at[i, col]} "
        applied.append(f"whitespace_cat:{col}:{len(idx)}")

    return df_err, applied

# ---------- Main splitting logic ----------
def split_and_inject(dataset_path, raw_data_dir, num_files=10, seed=None, error_prob=0.5):
    os.makedirs(raw_data_dir, exist_ok=True)

    # Load dataset (try excel then csv)
    if dataset_path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    if seed is not None:
        df = df.sample(frac=1, random_state=seed).reset_index(drop=True)  # shuffle globally
    else:
        df = df.sample(frac=1).reset_index(drop=True)

    splits = np.array_split(df, num_files)
    summary = []

    for i, split in enumerate(splits, start=1):
        # randomly decide to inject errors into this file (controlled by error_prob)
        if random.random() < error_prob:
            split_err, applied = inject_errors(split, file_idx=i, seed=seed)
        else:
            split_err = split.copy()
            applied = ["no_errors"]

        fname = os.path.join(raw_data_dir, f"raw_data_part_{i}.csv")
        split_err.to_csv(fname, index=False)
        summary.append((fname, len(split_err), applied))
        print(f"Saved: {fname} (rows: {len(split_err)})  errors: {applied}")

    return summary

# ---------- CLI ----------
def parse_args():
    p = argparse.ArgumentParser(description="Split dataset and inject synthetic errors.")
    p.add_argument("--dataset", default=DEFAULT_DATASET_PATH, help="Path to dataset (xlsx or csv)")
    p.add_argument("--outdir", default=RAW_DATA_DIR, help="Output raw-data directory")
    p.add_argument("--num-files", "-n", type=int, default=10, help="Number of files to generate")
    p.add_argument("--seed", type=int, default=42, help="Random seed (optional)")
    p.add_argument("--error-prob", type=float, default=0.6, help="Probability to inject errors per file (0-1)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print("Project root:", PROJECT_ROOT)
    print("Dataset path:", args.dataset)
    print("Raw-data dir:", args.outdir)
    print("Number of files:", args.num_files)
    print("Seed:", args.seed)
    print("Error injection probability per file:", args.error_prob)
    summary = split_and_inject(
        dataset_path=args.dataset,
        raw_data_dir=args.outdir,
        num_files=args.num_files,
        seed=args.seed,
        error_prob=args.error_prob
    )
    print("Done. Files generated:", len(summary))
