import os
import json
import math
import uuid
import tempfile
from typing import Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np
from pandas import DataFrame

from app.config import settings


def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, np.floating):
        val = float(obj)
        return None if math.isnan(val) else val
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_nan(v) for v in obj]
    return obj


class DataProcessor:
    def __init__(self):
        self._session_store: dict[str, dict] = {}

    def _detect_file_type(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            return "csv"
        elif ext in (".xls", ".xlsx"):
            return "excel"
        elif ext == ".json":
            return "json"
        elif ext == ".pdf":
            return "pdf"
        return "unknown"

    def _parse_csv(self, file_path: str, **kwargs) -> DataFrame:
        return pd.read_csv(file_path, **kwargs)

    def _parse_excel(self, file_path: str, **kwargs) -> DataFrame:
        return pd.read_excel(file_path, **kwargs)

    def _parse_json(self, file_path: str, **kwargs) -> DataFrame:
        return pd.read_json(file_path, **kwargs)

    def _parse_pdf(self, file_path: str, **kwargs) -> DataFrame:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                rows = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        rows.append({
                            "page": page.page_number,
                            "type": "text",
                            "content": text.strip(),
                        })

                    tables = page.extract_tables()
                    if tables:
                        for ti, table in enumerate(tables):
                            if len(table) < 2:
                                continue
                            header = [h.strip() if h else f"col_{ci}" for ci, h in enumerate(table[0])]
                            for row_data in table[1:]:
                                row_obj = {"page": page.page_number, "type": f"table_{ti+1}"}
                                for ci, cell in enumerate(row_data):
                                    col_name = header[ci] if ci < len(header) else f"col_{ci+1}"
                                    row_obj[col_name] = cell.strip() if cell else ""
                                rows.append(row_obj)

                if rows:
                    df = DataFrame(rows)
                    text_rows = df[df["type"] == "text"]["content"].tolist()
                    if text_rows:
                        full_text = "\n".join(text_rows)
                        title_line = ""
                        for line in full_text.split("\n"):
                            line = line.strip()
                            if line and len(line) > 10 and not line.startswith("http"):
                                title_line = line
                                break
                        if title_line:
                            meta_row = {"page": 1, "type": "title", "content": title_line}
                            df = DataFrame([meta_row] + rows)
                    return df

                return DataFrame({"info": ["No extractable content found in PDF"]})

        except ImportError:
            pass

        try:
            import PyPDF2
        except ImportError:
            raise ImportError("pdfplumber or PyPDF2 required for PDF parsing")

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text_data = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    text_data.append({"page": i + 1, "type": "text", "content": text.strip()})
            return DataFrame(text_data) if text_data else DataFrame({"info": ["No extractable text found"]})

    def parse_file(self, file_path: str, filename: str) -> DataFrame:
        file_type = self._detect_file_type(filename)
        parsers = {
            "csv": self._parse_csv,
            "excel": self._parse_excel,
            "json": self._parse_json,
            "pdf": self._parse_pdf,
        }
        parser = parsers.get(file_type)
        if not parser:
            raise ValueError(f"Unsupported file type: {file_type}")
        return parser(file_path)

    def _get_columns_info(self, df: DataFrame) -> list[dict]:
        columns = []
        for col in df.columns:
            columns.append({
                "name": str(col),
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique()),
            })
        return columns

    def clean_data(self, df: DataFrame) -> tuple[DataFrame, dict]:
        original_len = len(df)
        corrections = []

        duplicate_count = df.duplicated().sum()
        df = df.drop_duplicates()
        if duplicate_count > 0:
            corrections.append(f"Removed {duplicate_count} duplicate rows")

        null_before = df.isna().sum().sum()
        for col in df.columns:
            if df[col].dtype in ("object", "string"):
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown")
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median() if not df[col].isna().all() else 0)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].ffill()
        null_filled = null_before - df.isna().sum().sum()
        if null_filled > 0:
            corrections.append(f"Filled {int(null_filled)} null values")

        outlier_count = 0
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            outlier_count += len(outliers)
        if outlier_count > 0:
            corrections.append(f"Detected {outlier_count} outliers in numeric columns")

        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass

        result = {
            "original_rows": original_len,
            "cleaned_rows": len(df),
            "duplicates_removed": int(duplicate_count),
            "nulls_filled": int(null_filled),
            "outliers_detected": int(outlier_count),
            "corrections_applied": corrections,
        }
        return df, result

    def save_session_data(self, session_id: str, df: DataFrame, filename: str) -> None:
        self._session_store[session_id] = {
            "dataframe": df,
            "filename": filename,
            "file_type": self._detect_file_type(filename),
            "upload_time": datetime.utcnow().isoformat(),
            "columns": self._get_columns_info(df),
            "row_count": len(df),
            "column_count": len(df.columns),
        }

    def get_session_data(self, session_id: str) -> Optional[dict]:
        return self._session_store.get(session_id)

    def get_dataframe(self, session_id: str) -> Optional[DataFrame]:
        session = self._session_store.get(session_id)
        return session["dataframe"] if session else None

    def delete_session(self, session_id: str) -> None:
        self._session_store.pop(session_id, None)

    def get_summary(self, df: DataFrame) -> dict:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "datetime_columns": len(datetime_cols),
            "missing_cells": int(df.isna().sum().sum()),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            "column_details": self._get_columns_info(df),
        }

        if numeric_cols:
            desc = df[numeric_cols].describe()
            summary["numeric_summary"] = clean_nan(desc.to_dict())

        if categorical_cols:
            for col in categorical_cols[:5]:
                summary[f"top_values_{col}"] = clean_nan(df[col].value_counts().head(5).to_dict())

        return clean_nan(summary)


data_processor = DataProcessor()
