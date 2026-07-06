from pydantic import BaseModel
from typing import Any, Optional, List
from enum import Enum


class FileType(str, Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    PDF = "pdf"


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int


class DataPreview(BaseModel):
    file_name: str
    file_type: FileType
    row_count: int
    column_count: int
    columns: List[ColumnInfo]
    sample_data: List[dict]
    memory_usage: str


class CleaningResult(BaseModel):
    original_rows: int
    cleaned_rows: int
    duplicates_removed: int
    nulls_filled: int
    outliers_detected: int
    corrections_applied: List[str]


class Insight(BaseModel):
    type: str
    title: str
    description: str
    severity: str
    value: Optional[Any] = None
    recommendation: Optional[str] = None


class Prediction(BaseModel):
    target: str
    forecast: List[dict]
    confidence: float
    model_used: str
    features_importance: List[dict]


class Alert(BaseModel):
    type: str
    message: str
    severity: str
    column: str
    value: Any
    threshold: Any
    timestamp: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    reply: str
    insights: Optional[List[dict]] = []
    viz_suggestion: Optional[str] = None


class DashboardConfig(BaseModel):
    charts: List[str]
    layout: Optional[str] = "grid"


class RankingItem(BaseModel):
    rank: int
    label: str
    value: float
    change: Optional[float] = None


class ReportRequest(BaseModel):
    report_type: str = "summary"
    date_range: Optional[str] = None
    include_charts: bool = True


class SessionData(BaseModel):
    session_id: str
    file_name: str
    file_type: FileType
    upload_time: str
    status: str
    summary: Optional[dict] = None
