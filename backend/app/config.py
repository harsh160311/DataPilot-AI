import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "DataPilot AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "datapilot")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/datapilot/uploads")
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".json", ".pdf"}

    ENABLE_GPU: bool = os.getenv("ENABLE_GPU", "false").lower() == "true"
    ENABLE_CLOUD: bool = os.getenv("ENABLE_CLOUD", "false").lower() == "true"

    SESSION_EXPIRE_MINUTES: int = 60


settings = Settings()
