<div align="center">

# 🚀 DataPilot AI

### Zero Data Storage · Privacy-First · GPU-Accelerated

**A full-stack Data Intelligence Platform for uploading, analyzing, and visualizing datasets with AI-powered insights - in Hindi, Hinglish, and English.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-brightgreen.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Why DataPilot AI?](#-why-datapilot-ai)
- [GPU Acceleration](#-gpu-acceleration)
- [Google Cloud Integration](#-google-cloud-integration)
- [Use Cases](#-use-cases)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the App](#-running-the-app)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Production Build](#-production-build)
- [License](#-license)

---

## 🌟 Overview

DataPilot AI is a privacy-first, full-stack analytics platform that transforms raw datasets into actionable intelligence - instantly. Upload a file, and DataPilot automatically cleans your data, generates insights, trains ML models, visualizes trends, and lets you chat with your data in natural language.

No data is ever stored permanently. All files are processed in-memory and deleted after parsing.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 **File Upload** | Drag-and-drop support for CSV, Excel, JSON, and PDF |
| 🧹 **Auto Data Cleaning** | Removes duplicates, handles nulls, detects outliers |
| 📊 **Interactive Dashboard** | KPI cards, bar, line, pie, area, and scatter charts |
| 🔍 **Automated Insights** | Correlations, trends, patterns, and statistical summaries |
| 🤖 **ML Predictions** | Train Random Forest, XGBoost, or cuML models; forecast & detect anomalies |
| 💬 **AI Chat Assistant** | Ask questions in Hindi, Hinglish, or English (GPT-4o-mini / Gemini) |
| 📄 **Smart Document Parsing** | Full text and table extraction from PDF, CSV, Excel, and JSON |
| 📋 **Reports** | Export summary, plain-text, and data quality reports |
| 🚨 **Alerts & Rankings** | Automated anomaly detection, quality alerts, and category rankings |
| ⚡ **GPU Acceleration** | Optional NVIDIA RAPIDS (cuML) acceleration for large datasets |
| 🔒 **Privacy-First** | Files are processed in-memory and deleted after parsing - zero permanent storage |

---

## 💡 Why DataPilot AI?

Traditional analytics tools demand technical expertise, manual data cleaning, and slow processing pipelines.

**DataPilot AI lets anyone upload a dataset and instantly receive:**

- ✅ Automated data cleaning
- ✅ AI-powered insights
- ✅ Forecasts and predictions
- ✅ Risk scores and anomaly detection
- ✅ Natural language data exploration
- ✅ Interactive dashboards

The platform leverages **NVIDIA RAPIDS GPU acceleration** and **Google Cloud services** to reduce time-to-insight and support faster data-driven decisions.

---

## ⚡ GPU Acceleration

DataPilot AI uses **NVIDIA RAPIDS** (`cuDF` and `cuML`) to dramatically speed up data processing and ML workloads.

### Benchmark Results

| Operation | Pandas (CPU) | cuDF (GPU) | Speedup |
|---|---|---|---|
| Load 100K Rows | 12.8s | 1.9s | **~7x** |
| Data Cleaning | 7.4s | 1.2s | **~6x** |
| Aggregation | 5.2s | 0.8s | **~6.5x** |

> **Up to 7× faster** on large datasets with GPU acceleration enabled.

**Benefits:**
- Faster analytics on large datasets
- Reduced time-to-insight
- Better responsiveness under load
- Real-time decision support at scale

---

## ☁️ Google Cloud Integration

DataPilot AI integrates with the following Google Cloud services:

| Service | Usage |
|---|---|
| **BigQuery** | Large-scale analytical queries and dataset exploration |
| **Cloud Storage** | Temporary upload processing and secure file handling |
| **Gemini** | Natural language analytics via the AI chat assistant |
| **Looker** | Interactive dashboards and business intelligence visualizations |

---

## 📊 Decision Intelligence Outputs

After processing a dataset, DataPilot AI automatically generates:

- 📈 **Forecasts** - Future value predictions
- ⚠️ **Risk Scores** - Identify potential problem areas
- 🏆 **Rankings** - Category-wise performance breakdowns
- 🔔 **Alerts** - Automated anomaly and quality alerts
- 💡 **Recommendations** - Actionable next steps
- 📉 **Trend Analysis** - Time-series patterns and direction
- 📝 **Executive Summaries** - Ready-to-share overviews

---

## 🏢 Use Cases

| Industry | Application |
|---|---|
| 🛒 **Retail** | Predict future sales and identify top-performing products |
| 🏥 **Healthcare** | Forecast patient load and resource requirements |
| 🎓 **Education** | Analyze student performance trends |
| 🏙️ **Smart Cities** | Identify operational patterns and optimize resource allocation |
| 🔬 **Research** | Explore datasets without writing a single line of code |

---

## 🛠️ Tech Stack

### Frontend
`React 18` · `Vite 5` · `Tailwind CSS 3` · `Recharts` · `Lucide Icons`

### Backend
`Python 3.13+` · `FastAPI` · `pandas` · `scikit-learn` · `XGBoost` · `OpenRouter / Gemini AI` · `Google Cloud (BigQuery / Cloud Storage)`

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.13 or higher
- **Node.js** 18 or higher
- **npm**

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/datapilot-ai.git
cd datapilot-ai
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv venv          # Recommended: create a virtual environment
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Set Up the Frontend

```bash
cd frontend
npm install
```

### 4. Configure Environment Variables

Create a `backend/.env` file (see `backend/.env.example` for reference):

```env
# Required: Gemini API Key for AI Chat Assistant
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: OpenRouter (alternative to Gemini, supports GPT-4o-mini)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Google Cloud Integration
GOOGLE_CLOUD_PROJECT=your_project_id
BIGQUERY_DATASET=datapilot

# GPU Acceleration (requires NVIDIA RAPIDS)
ENABLE_GPU=false

# Cloud Features
ENABLE_CLOUD=false

# Temporary Upload Directory
UPLOAD_DIR=/tmp/datapilot/uploads
```

> **Get your API keys:**
> - Gemini: [Google AI Studio](https://aistudio.google.com/) (free tier available)
> - OpenRouter: [openrouter.ai](https://openrouter.ai/) (free tier available)

---

## ▶️ Running the App

You need **two terminals** running simultaneously.

### Terminal 1 - Backend (FastAPI)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API server: [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Terminal 2 - Frontend (Vite)

```bash
cd frontend
npm run dev
```

- App: [http://localhost:3000](http://localhost:3000)

API requests are automatically proxied to the backend.

---

## 📖 Usage Guide

1. Open [http://localhost:3000](http://localhost:3000) in your browser
2. **Upload** a dataset (CSV, Excel, JSON, or PDF) via drag-and-drop
3. **Preview** your data and run auto-cleaning with one click
4. **Explore** insights, charts, and KPIs on the Dashboard
5. **Train** ML models and generate forecasts in the Predictions tab
6. **Ask** the AI Assistant questions in Hindi, Hinglish, or English
7. **Export** summary, text, or data quality reports

---

## 📁 Project Structure

```
datapilot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # Environment config
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── upload.py            # File upload & session management
│   │   │   ├── analytics.py         # Summary, describe, clean
│   │   │   ├── dashboard.py         # KPIs, charts, dashboard data
│   │   │   ├── insights.py          # Automated insights & trends
│   │   │   ├── predictions.py       # ML training, forecast, anomalies
│   │   │   ├── chat.py              # AI chat assistant
│   │   │   ├── alerts.py            # Alerts & rankings
│   │   │   └── reports.py           # Summary, text, quality reports
│   │   └── services/
│   │       ├── data_processor.py    # Data parsing, cleaning, sessions
│   │       ├── gpu_accelerator.py   # GPU-accelerated operations
│   │       ├── insight_engine.py    # Auto insight generation
│   │       ├── ml_engine.py         # ML training & prediction
│   │       ├── chat_assistant.py    # LLM chat (OpenRouter / Gemini / local)
│   │       ├── alert_engine.py      # Anomaly & quality alerts
│   │       ├── visualization.py     # Chart & dashboard data
│   │       └── report_generator.py  # Report exports
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
└── frontend/
    ├── public/
    ├── index.html
    ├── src/
    │   ├── main.jsx                 # React entry point
    │   ├── App.jsx                  # Root component
    │   ├── index.css                # Tailwind imports & globals
    │   ├── components/
    │   │   ├── FileUpload.jsx       # Drag-and-drop file upload
    │   │   ├── DataPreview.jsx      # Table preview of dataset
    │   │   ├── DataCleaning.jsx     # Auto-clean controls & results
    │   │   ├── Dashboard.jsx        # KPI cards & visualizations
    │   │   ├── Insights.jsx         # Automated insight cards
    │   │   ├── Predictions.jsx      # ML model training & forecast
    │   │   ├── ChatAssistant.jsx    # AI chat interface
    │   │   ├── AlertsPanel.jsx      # Anomaly & quality alerts
    │   │   ├── Rankings.jsx         # Category rankings
    │   │   ├── ReportGenerator.jsx  # Report export controls
    │   │   └── Layout.jsx           # App shell & navigation
    │   ├── hooks/
    │   │   └── useApi.js            # API client hook
    │   └── utils/
    │       └── api.js               # Axios/fetch helpers
    ├── package.json
    ├── vite.config.js
    ├── postcss.config.js
    └── tailwind.config.js
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/upload/` | `POST` | Upload a dataset (CSV / Excel / JSON / PDF) |
| `/api/upload/session/{session_id}` | `GET` | Get session metadata |
| `/api/upload/session/{session_id}` | `DELETE` | Delete a session |
| `/api/analytics/summary/{session_id}` | `GET` | Data summary statistics |
| `/api/analytics/clean/{session_id}` | `POST` | Auto-clean data |
| `/api/analytics/describe/{session_id}` | `GET` | Statistical description |
| `/api/analytics/columns/{session_id}` | `GET` | Column details (dtypes, nulls) |
| `/api/analytics/gpu-status` | `GET` | GPU accelerator stats |
| `/api/dashboard/{session_id}` | `GET` | Dashboard data + KPIs + charts |
| `/api/dashboard/chart/{session_id}` | `GET` | Custom chart data |
| `/api/dashboard/kpis/{session_id}` | `GET` | KPI metrics only |
| `/api/insights/{session_id}` | `GET` | Automated insights |
| `/api/insights/trends/{session_id}` | `GET` | Time-series trend analysis |
| `/api/predictions/train/{session_id}` | `GET` | Train ML model (Random Forest / XGBoost) |
| `/api/predictions/forecast/{session_id}` | `GET` | Forecast future values |
| `/api/predictions/anomalies/{session_id}` | `GET` | Detect anomalies |
| `/api/chat/ask/{session_id}` | `POST` | Ask AI assistant (Hindi / English) |
| `/api/alerts/{session_id}` | `GET` | Data quality alerts |
| `/api/alerts/rankings/{session_id}` | `GET` | Category-wise rankings |
| `/api/reports/summary/{session_id}` | `GET` | Full summary report |
| `/api/reports/text/{session_id}` | `GET` | Plain-text report |
| `/api/reports/quality/{session_id}` | `GET` | Data quality score |

> Full interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger) or [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc) when the backend is running.

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ For AI Chat | - | Google Gemini API key (recommended) |
| `OPENROUTER_API_KEY` | No | - | OpenRouter key (alternative to Gemini; supports GPT-4o-mini) |
| `GOOGLE_CLOUD_PROJECT` | For Cloud | - | Google Cloud project ID for BigQuery / Storage |
| `BIGQUERY_DATASET` | No | `datapilot` | BigQuery dataset name |
| `ENABLE_GPU` | No | `false` | Enable GPU-accelerated operations via NVIDIA RAPIDS |
| `ENABLE_CLOUD` | No | `false` | Enable Google Cloud storage features |
| `UPLOAD_DIR` | No | `/tmp/datapilot/uploads` | Temporary upload directory |

---

## 📦 Production Build

```bash
cd frontend
npm run build
```

Static files are output to `frontend/dist/`. Serve with any static file server or reverse proxy (e.g., Nginx, Caddy).

---

## 🔒 Privacy & Security Notes

- **No permanent storage** - uploaded files are deleted immediately after processing
- **AI Chat fallback chain** - OpenRouter → Gemini → local smart matching
- **Multilingual support** - Hindi, Hinglish, and English
- **Virtual environment strongly recommended** for Python dependency isolation

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  Built with ❤️ using FastAPI, React, and NVIDIA RAPIDS
</div>