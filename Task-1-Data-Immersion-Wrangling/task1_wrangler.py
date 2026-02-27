#!/usr/bin/env python3
"""
task1_wrangler.py - Data Immersion & Wrangling Module
=====================================================
A production-grade CLI tool that accepts a raw dataset, performs
comprehensive data cleaning, generates a data dictionary, and
outputs an analysis-ready dataset.

Usage:
    python task1_wrangler.py --input data/raw_data.csv --output ./Task_1_Output

Author : Hemang Dubey
Module : Task 1 - Data Immersion & Wrangling (ApexPlanet Internship)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ---- Suppress noisy pandas FutureWarnings so the CLI stays clean ----
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


# =====================================================================
#  Pretty Console Helpers
# =====================================================================
class _Style:
    """ANSI escape-code wrapper (no-ops on non-TTY terminals)."""

    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    RED       = "\033[91m"
    CYAN      = "\033[96m"
    MAGENTA   = "\033[95m"
    WHITE     = "\033[97m"
    BG_CYAN   = "\033[46m"
    RESET     = "\033[0m"

    @staticmethod
    def supports_color() -> bool:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


# If the terminal doesn't support colour, every attribute becomes ""
if _Style.supports_color():
    S = _Style
else:
    S = type("_NoColor", (), {k: "" for k in vars(_Style) if not k.startswith("_")})()


WIDTH = 62


def _banner() -> None:
    """Print the startup banner."""
    print()
    print(f"{S.CYAN}{'=' * WIDTH}{S.RESET}")
    print(f"{S.BOLD}{S.CYAN}  GRAVITY WRANGLER  -  Data Cleaning Pipeline{S.RESET}")
    print(f"{S.CYAN}{'=' * WIDTH}{S.RESET}")


def _header(title: str) -> None:
    """Print a styled section header."""
    print(f"\n{S.CYAN}{'─' * WIDTH}{S.RESET}")
    print(f"{S.BOLD}{S.CYAN}  STEP  |  {title}{S.RESET}")
    print(f"{S.CYAN}{'─' * WIDTH}{S.RESET}")


def _info(msg: str) -> None:
    print(f"  {S.GREEN}[OK]{S.RESET}  {msg}")


def _detail(msg: str) -> None:
    print(f"  {S.DIM}      {msg}{S.RESET}")


def _warn(msg: str) -> None:
    print(f"  {S.YELLOW}[!!]{S.RESET}  {msg}")


def _bullet(msg: str) -> None:
    print(f"  {S.DIM}      -{S.RESET} {msg}")


def _error(msg: str) -> None:
    print(f"  {S.RED}[ERR]{S.RESET} {msg}")


def _success_box(msg: str) -> None:
    """Print a highlighted success box."""
    pad = WIDTH - 6
    print()
    print(f"  {S.GREEN}{'=' * WIDTH}{S.RESET}")
    print(f"  {S.BOLD}{S.GREEN}  SUCCESS  {msg}{S.RESET}")
    print(f"  {S.GREEN}{'=' * WIDTH}{S.RESET}")
    print()


# =====================================================================
#  Main Class
# =====================================================================
class GravityWrangler:
    """End-to-end data wrangling pipeline.

    Parameters
    ----------
    file_path : str
        Path to a .csv or .xlsx raw dataset.
    """

    SUPPORTED_EXTENSIONS = (".csv", ".xlsx")

    _DATE_HINTS: Tuple[str, ...] = (
        "date", "time", "dt", "dob", "birth", "created", "updated",
        "timestamp", "registered", "joined", "expired", "due",
    )

    # ──────────────── Constructor ────────────────
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.data_dict: List[Dict[str, Any]] = []
        self._date_cols_converted: List[str] = []

        _header("LOADING DATASET")
        self.df: pd.DataFrame = self._load(file_path)

        rows, cols = self.df.shape
        _info(f"Loaded {rows:,} rows x {cols} columns")
        _detail(f"Source: {os.path.basename(file_path)}")
        _detail(f"Size  : {os.path.getsize(file_path) / (1024*1024):.1f} MB")

    # ──────────────── Private Helpers ────────────────
    @staticmethod
    def _load(path: str) -> pd.DataFrame:
        """Load .csv or .xlsx with graceful error handling."""
        if not os.path.isfile(path):
            _error(f"File not found: {path}")
            raise FileNotFoundError(
                f"The file '{path}' does not exist. "
                "Please verify the path and try again."
            )

        ext = os.path.splitext(path)[1].lower()
        if ext not in GravityWrangler.SUPPORTED_EXTENSIONS:
            _error(f"Unsupported file extension: {ext}")
            raise ValueError(
                f"Only .csv and .xlsx files are supported. Received: '{ext}'"
            )

        try:
            if ext == ".csv":
                return pd.read_csv(path, low_memory=False)
            return pd.read_excel(path, engine="openpyxl")
        except Exception as exc:
            _error(f"Failed to read file: {exc}")
            raise

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert an arbitrary column name to snake_case."""
        name = re.sub(r"[\s\-\.\/\\]+", "_", str(name).strip())
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        name = re.sub(r"_+", "_", name).strip("_").lower()
        return name

    @staticmethod
    def _classify_dtype(series: pd.Series) -> str:
        """Return a human-friendly type label for a pandas Series."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return "DateTime"
        if pd.api.types.is_numeric_dtype(series):
            return "Numerical"
        if pd.api.types.is_bool_dtype(series):
            return "Categorical"
        # Low-cardinality object columns -> Categorical
        if series.dtype == "object":
            if series.nunique() < max(20, int(len(series) * 0.05)):
                return "Categorical"
        return "Text"

    @staticmethod
    def _iqr_outlier_count(series: pd.Series) -> int:
        """Count outliers using the IQR method (1.5x IQR fence)."""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return int(((series < lower) | (series > upper)).sum())

    # ──────────────── 1. Assess Quality ────────────────
    def assess_quality(self) -> "GravityWrangler":
        """Profile the raw dataset and print a quality summary."""
        _header("DATA QUALITY ASSESSMENT")

        df = self.df
        total_rows, total_cols = df.shape
        _info(f"Shape: {total_rows:,} rows x {total_cols} columns")

        # Missing values
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            _info("No missing values detected")
        else:
            _warn(f"Missing values found in {len(missing)} column(s):")
            for col, cnt in missing.items():
                pct = cnt / total_rows * 100
                _bullet(f"{col:<25s}  {cnt:>8,} missing ({pct:.1f}%)")

        # Duplicates
        dup_count = df.duplicated().sum()
        if dup_count:
            _warn(f"Duplicate rows: {dup_count:,}")
        else:
            _info("No duplicate rows detected")

        # Outliers (IQR)
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols):
            _info("Outlier scan (IQR method) on numerical columns:")
            found_any = False
            for col in numeric_cols:
                oc = self._iqr_outlier_count(df[col].dropna())
                if oc:
                    _bullet(f"{col:<25s}  {oc:>8,} potential outliers")
                    found_any = True
            if not found_any:
                _detail("No outliers detected in any numerical column")
        else:
            _info("No numerical columns to scan for outliers")

        return self

    # ──────────────── 2. Generate Data Dictionary ────────────────
    def generate_data_dictionary(self) -> "GravityWrangler":
        """Build an in-memory data dictionary for every column."""
        _header("GENERATING DATA DICTIONARY")

        df = self.df
        total_rows = len(df)
        self.data_dict = []

        for col in df.columns:
            series = df[col]
            dtype_label = self._classify_dtype(series)
            missing_pct = series.isnull().sum() / total_rows * 100
            unique_count = series.nunique()

            if dtype_label == "Numerical":
                desc = (
                    f"Numeric feature; "
                    f"range [{series.min()}, {series.max()}]; "
                    f"mean={series.mean():.2f}"
                )
            elif dtype_label == "DateTime":
                desc = (
                    f"DateTime column; "
                    f"range [{series.min()} to {series.max()}]"
                )
            elif dtype_label == "Categorical":
                top = series.mode().iloc[0] if not series.mode().empty else "N/A"
                desc = f"Categorical ({unique_count} levels); mode='{top}'"
            else:
                avg_len = series.dropna().astype(str).str.len().mean()
                desc = f"Text field; avg length={avg_len:.0f} chars"

            self.data_dict.append(
                {
                    "Column Name": col,
                    "Type": dtype_label,
                    "Missing %": f"{missing_pct:.2f}%",
                    "Unique Values": unique_count,
                    "Description": desc,
                }
            )

        _info(f"Data dictionary created for {len(self.data_dict)} columns")

        # Print a quick table preview to the console
        print()
        hdr = f"  {'#':<4} {'Column':<25} {'Type':<14} {'Missing':<10} {'Unique':>10}"
        print(f"{S.DIM}{hdr}{S.RESET}")
        print(f"{S.DIM}  {'─'*4} {'─'*25} {'─'*14} {'─'*10} {'─'*10}{S.RESET}")
        for i, entry in enumerate(self.data_dict, 1):
            print(
                f"  {i:<4} {entry['Column Name']:<25} "
                f"{entry['Type']:<14} {entry['Missing %']:<10} "
                f"{entry['Unique Values']:>10,}"
            )
        print()

        return self

    # ──────────────── 3. Clean and Transform ────────────────
    def clean_and_transform(self) -> "GravityWrangler":
        """Impute missing values, drop duplicates, standardize names & text."""
        _header("CLEANING & TRANSFORMING")

        df = self.df

        # Standardize column names to snake_case
        original_names = list(df.columns)
        df.columns = [self._to_snake_case(c) for c in df.columns]
        renamed = {o: n for o, n in zip(original_names, df.columns) if o != n}
        if renamed:
            _info(f"Renamed {len(renamed)} column(s) to snake_case:")
            for old, new in renamed.items():
                _bullet(f"'{old}' -> '{new}'")

        # Impute missing values (using assignment, not inplace)
        num_imputed = 0
        cat_imputed = 0
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                num_imputed += 1
            else:
                mode_series = df[col].mode()
                if not mode_series.empty:
                    df[col] = df[col].fillna(mode_series.iloc[0])
                else:
                    df[col] = df[col].fillna("Unknown")
                cat_imputed += 1

        _info(
            f"Imputed {num_imputed} numerical (median) "
            f"+ {cat_imputed} categorical (mode) column(s)"
        )

        # Drop duplicate rows
        before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        dropped = before - len(df)
        if dropped:
            _info(f"Dropped {dropped:,} duplicate rows")
        else:
            _info("No duplicate rows to drop")

        # Strip whitespace from string columns
        str_cols = df.select_dtypes(include="object").columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
        _info(f"Stripped whitespace from {len(str_cols)} text column(s)")

        self.df = df
        return self

    # ──────────────── 4. Feature Engineering ────────────────
    def engineer_features(self) -> "GravityWrangler":
        """Auto-detect date columns, extract temporal features, compute age."""
        _header("FEATURE ENGINEERING")

        df = self.df
        date_cols_found: List[str] = []

        # Auto-detect & convert date columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols_found.append(col)
                continue

            col_lower = col.lower()
            if any(hint in col_lower for hint in self._DATE_HINTS):
                try:
                    converted = pd.to_datetime(df[col], errors="coerce")
                    success_rate = converted.notna().sum() / max(len(df), 1)
                    if success_rate >= 0.70:
                        df[col] = converted
                        date_cols_found.append(col)
                        _info(
                            f"Converted '{col}' to datetime "
                            f"({success_rate * 100:.1f}% parsed)"
                        )
                except Exception:
                    pass

        # Extract temporal features
        for col in date_cols_found:
            base = col.replace("_date", "").replace("_time", "").rstrip("_")
            yr_col = f"{base}_year"
            mo_col = f"{base}_month"
            dn_col = f"{base}_day_name"

            df[yr_col] = df[col].dt.year.astype("Int64")
            df[mo_col] = df[col].dt.month.astype("Int64")
            df[dn_col] = df[col].dt.day_name()
            _info(f"Extracted: {yr_col}, {mo_col}, {dn_col}")

        self._date_cols_converted = date_cols_found

        # Compute age from birth-related columns
        today = pd.Timestamp.now()
        for col in date_cols_found:
            if any(hint in col.lower() for hint in ("dob", "birth")):
                age_col = "age"
                df[age_col] = (
                    (today - df[col]).dt.days / 365.25
                ).round(0).astype("Int64")
                _info(f"Calculated '{age_col}' from '{col}'")

        if not date_cols_found:
            _info("No date-like columns detected for feature engineering")

        self.df = df
        return self

    # ──────────────── 5. Save Artifacts ────────────────
    def save_artifacts(self, output_folder: str) -> None:
        """Persist cleaned data and data dictionary to output_folder."""
        _header("SAVING ARTIFACTS")

        os.makedirs(output_folder, exist_ok=True)

        # Artifact 1: Cleaned CSV
        csv_path = os.path.join(output_folder, "cleaned_data.csv")
        self.df.to_csv(csv_path, index=False)
        size_mb = os.path.getsize(csv_path) / (1024 * 1024)
        _info(f"Cleaned data  ->  {csv_path}  ({size_mb:.1f} MB)")

        # Artifact 2: Data Dictionary
        md_path = os.path.join(output_folder, "data_dictionary.md")
        self._write_data_dictionary_md(md_path)
        _info(f"Data dictionary  ->  {md_path}")

        # Final stats
        _detail(f"Final shape: {self.df.shape[0]:,} rows x {self.df.shape[1]} columns")

        _success_box(f"Artifacts saved to {output_folder}")

    def _write_data_dictionary_md(self, path: str) -> None:
        """Render the data dictionary as a clean Markdown file."""
        lines: List[str] = [
            "# Data Dictionary",
            "",
            f"> Auto-generated by **GravityWrangler** on "
            f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            "",
            f"**Dataset:** `{os.path.basename(self.file_path)}`  ",
            f"**Rows (cleaned):** {len(self.df):,}  ",
            f"**Columns (after engineering):** {self.df.shape[1]}",
            "",
            "---",
            "",
            "| # | Column Name | Type | Missing % | Unique Values | Description |",
            "|---|-------------|------|-----------|---------------|-------------|",
        ]

        for idx, entry in enumerate(self.data_dict, start=1):
            lines.append(
                f"| {idx} "
                f"| `{entry['Column Name']}` "
                f"| {entry['Type']} "
                f"| {entry['Missing %']} "
                f"| {entry['Unique Values']:,} "
                f"| {entry['Description']} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("*End of Data Dictionary*")

        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))


# =====================================================================
#  CLI Entry Point
# =====================================================================
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gravity-wrangler",
        description=textwrap.dedent("""\
            Task 1: Data Immersion & Wrangling
            -----------------------------------
            Cleans a raw dataset, generates a data dictionary,
            and outputs an analysis-ready CSV.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the raw dataset (.csv or .xlsx).",
    )
    parser.add_argument(
        "--output", "-o",
        default="./Task_1_Output",
        help="Directory where artifacts will be saved (default: ./Task_1_Output).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Run the full wrangling pipeline."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    _banner()
    print(f"\n  {S.DIM}Input  :{S.RESET}  {args.input}")
    print(f"  {S.DIM}Output :{S.RESET}  {args.output}")

    wrangler = GravityWrangler(args.input)

    (
        wrangler
        .assess_quality()
        .clean_and_transform()
        .engineer_features()
        .generate_data_dictionary()
        .save_artifacts(args.output)
    )


if __name__ == "__main__":
    main()
