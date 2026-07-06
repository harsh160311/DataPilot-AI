import json
import logging
from typing import Optional
from pandas import DataFrame

from app.config import settings

logger = logging.getLogger(__name__)


class ChatAssistant:
    def __init__(self):
        self._gemini_model = None
        self._openrouter_client = None
        self._try_init_gemini()
        self._try_init_openrouter()

    def _try_init_gemini(self):
        if not settings.GEMINI_API_KEY:
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("Gemini initialized")
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")
            self._gemini_model = None

    def _try_init_openrouter(self):
        if not settings.OPENROUTER_API_KEY:
            logger.warning("No OPENROUTER_API_KEY found")
            return
        if settings.OPENROUTER_API_KEY == "sk-or-v1-your_openrouter_api_key":
            logger.warning("OpenRouter key is placeholder, skipping")
            return
        try:
            import httpx
            self._openrouter_client = httpx.Client(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
            logger.info("OpenRouter initialized via httpx")
        except Exception as e:
            logger.warning(f"OpenRouter init failed: {e}")
            self._openrouter_client = None

    def _build_context(self, df: Optional[DataFrame], summary: dict) -> str:
        if df is None:
            return "No dataset loaded."

        context_parts = [
            f"Dataset Summary:",
            f"- {summary.get('total_rows', 0)} rows, {summary.get('total_columns', 0)} columns",
            f"- Numeric columns: {summary.get('numeric_columns', 0)}",
            f"- Categorical columns: {summary.get('categorical_columns', 0)}",
            f"- Missing cells: {summary.get('missing_cells', 0)}",
            f"\nColumns:",
        ]

        for col in summary.get("column_details", []):
            context_parts.append(
                f"- {col['name']} ({col['dtype']}): "
                f"{col['non_null_count']} non-null, "
                f"{col['null_count']} null, "
                f"{col['unique_count']} unique"
            )

        text_cols = [c for c in df.columns if df[c].dtype == "object"]
        if text_cols:
            sample_texts = []
            for col in text_cols[:3]:
                vals = df[col].dropna().head(20).tolist()
                if vals:
                    sample_texts.append(f"\nSample values from '{col}' column:")
                    for v in vals[:20]:
                        text = str(v)[:300]
                        sample_texts.append(f"  - {text}")
            context_parts.extend(sample_texts)

        numeric_summary = summary.get("numeric_summary", {})
        if numeric_summary:
            try:
                import pandas as pd
                context_parts.append(f"\nNumeric Summary:\n{pd.DataFrame(numeric_summary).to_string()}")
            except Exception:
                context_parts.append(f"\nNumeric Summary available.")

        return "\n".join(context_parts)

    def ask(self, message: str, df: Optional[DataFrame], summary: dict, history: list[dict] = None) -> dict:
        context = self._build_context(df, summary)
        history = history or []

        if self._openrouter_client:
            result = self._ask_openrouter(message, context, history, df, summary)
            if result:
                return result
        if self._gemini_model:
            result = self._ask_gemini(message, context, history, df, summary)
            if result:
                return result
        return self._ask_local(message, df, summary)

    def _call_llm(self, system_prompt: str, message: str, history: list[dict]) -> Optional[str]:
        try:
            messages = [{"role": "system", "content": system_prompt}]

            for msg in history:
                role = "assistant" if msg.get("role") == "model" else "user"
                parts = msg.get("parts", [])
                if isinstance(parts, list) and len(parts) > 0:
                    text = parts[0].get("text", "") if isinstance(parts[0], dict) else str(parts[0])
                else:
                    text = str(parts)
                messages.append({"role": role, "content": text})

            messages.append({"role": "user", "content": message})

            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.3,
            }

            resp = self._openrouter_client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            return None

    def _ask_openrouter(self, message: str, context: str, history: list[dict], df: Optional[DataFrame], summary: dict) -> Optional[dict]:
        system_prompt = f"""You are DataPilot AI, an expert data analyst assistant. You help users understand their data.

Context about the loaded dataset:
{context}

Rules:
- Answer questions about the dataset using the provided context.
- If asked for predictions or trends, explain what the data suggests.
- Suggest visualization types when relevant.
- Keep responses concise and data-driven (2-4 paragraphs max).
- If you cannot answer from the data, say so clearly.
- Format numbers with commas for readability.
- The user may ask in Hindi, Hinglish, or English — respond in the same language."""

        reply = self._call_llm(system_prompt, message, history)
        if reply is None:
            return None

        return {
            "reply": reply,
            "insights": [],
            "viz_suggestion": None,
        }

    def _ask_gemini(self, message: str, context: str, history: list[dict], df: Optional[DataFrame], summary: dict) -> Optional[dict]:
        system_prompt = f"""You are DataPilot AI, an expert data analyst assistant. You help users understand their data.

Context about the loaded dataset:
{context}

Rules:
- Answer questions about the dataset using the provided context.
- If asked for predictions or trends, explain what the data suggests.
- Suggest visualization types when relevant.
- Keep responses concise and data-driven.
- If you cannot answer from the data, say so clearly.
- The user may ask in Hindi, Hinglish, or English — respond in the same language."""

        try:
            converted_history = []
            for msg in history:
                role = "assistant" if msg.get("role") == "model" else "user"
                parts = msg.get("parts", [])
                text = parts[0].get("text", "") if isinstance(parts, list) and len(parts) > 0 and isinstance(parts[0], dict) else str(parts)
                converted_history.append({"role": role, "parts": [{"text": text}]})

            chat = self._gemini_model.start_chat(history=converted_history)
            response = chat.send_message(f"{system_prompt}\n\nUser Question: {message}")
            return {
                "reply": response.text,
                "insights": [],
                "viz_suggestion": None,
            }
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    def _detect_intent(self, msg_lower: str) -> str:
        what_words = ["kya", "kaunsa", "konsa", "kis", "cheez", "chij",
                       "what", "which", "tell", "about", "describe", "explain"]
        project_words = ["project", "report", "document", "file", "topic",
                          "subject", "title", "name", "overview"]
        row_words = ["kitni", "kitne", "kitte", "pankti", "row", "kitna",
                     "record", "how many", "total", "kulle"]
        col_words = ["column", "kalam", "kaun si"]
        missing_words = ["missing", "null", "khali"]
        avg_words = ["average", "mean", "median", "ausat"]
        top_words = ["sabse", "top", "highest", "most", "jyda", "zyada",
                     "maximum", "max", "bhadi", "badi"]
        chart_words = ["chart", "graph", "plot", "graf"]

        is_what = any(w in msg_lower for w in what_words)
        is_project = any(w in msg_lower for w in project_words)
        is_row = any(w in msg_lower for w in row_words)
        is_col = any(w in msg_lower for w in col_words)
        is_missing = any(w in msg_lower for w in missing_words)
        is_avg = any(w in msg_lower for w in avg_words)
        is_top = any(w in msg_lower for w in top_words)
        is_chart = any(w in msg_lower for w in chart_words)

        if is_what and is_project:
            return "summary"
        if is_what:
            return "summary"
        if is_project and not is_row:
            return "summary"
        if is_row and not is_top:
            return "rows"
        if is_col:
            return "columns"
        if is_missing:
            return "missing"
        if is_avg:
            return "average"
        if is_top:
            return "top"
        if is_chart:
            return "chart"
        return "smart"

    def _get_dataset_summary(self, df: DataFrame, summary: dict) -> str:
        cols = summary.get("column_details", [])
        name_cols = [c["name"] for c in cols
                     if any(kw in c["name"].lower() for kw in
                            ["title", "name", "project", "topic", "subject", "desc", "file"])]

        if name_cols:
            for col_name in name_cols:
                vals = df[col_name].dropna().astype(str).str.strip()
                vals = vals[vals.str.len() > 5]
                if len(vals) > 0:
                    top_val = vals.iloc[0]
                    if len(top_val) > 500:
                        top_val = top_val[:500]
                    return f"**{top_val}**"

        text_cols = [c["name"] for c in cols if c["dtype"] == "object"]
        for col_name in text_cols:
            vals = df[col_name].dropna().astype(str).str.strip()
            long_vals = vals[vals.str.len() > 30]
            if len(long_vals) > 0:
                text = long_vals.iloc[0]
                lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 15]
                if lines:
                    title = lines[0]
                    if len(title) > 500:
                        title = title[:500]
                    return f"**{title}**"

        cat_cols = [c for c in cols if "object" in c["dtype"] or "category" in c["dtype"]]
        if cat_cols:
            parts = ["**Dataset Overview:**"]
            for col_info in cat_cols[:4]:
                col_name = col_info["name"]
                top_key = f"top_values_{col_name}"
                if top_key in summary:
                    top_vals = summary[top_key]
                    vals_str = ", ".join(f"{k} ({v})" for k, v in list(top_vals.items())[:3])
                    if vals_str:
                        parts.append(f"\n**{col_name}**: {vals_str}")
            return "\n".join(parts)

        return None

    def _ask_top(self, df: DataFrame, summary: dict) -> str:
        cols = summary.get("column_details", [])
        cat_cols = [c for c in cols if "object" in c["dtype"] or "category" in c["dtype"]]
        if cat_cols:
            parts = ["**Top values:**"]
            for col_info in cat_cols[:3]:
                col_name = col_info["name"]
                top_key = f"top_values_{col_name}"
                if top_key in summary:
                    top_vals = summary[top_key]
                    vals_str = ", ".join(f"{k}: {v}" for k, v in list(top_vals.items())[:5])
                    parts.append(f"\n**{col_name}**:\n{vals_str}")
            return "\n".join(parts)
        numeric_cols = [c for c in cols if "int" in c["dtype"] or "float" in c["dtype"]]
        if numeric_cols:
            top_col = numeric_cols[0]["name"]
            top_vals = df[top_col].nlargest(5)
            parts = [f"**Top 5 highest {top_col}:**"]
            for i, (idx, val) in enumerate(top_vals.items(), 1):
                parts.append(f"  {i}. {val:,}")
            return "\n".join(parts)
        return "No suitable columns found."

    def _smart_answer(self, df: DataFrame, summary: dict, message: str) -> str:
        desc = self._get_dataset_summary(df, summary)
        if desc:
            return desc

        total_rows = summary.get("total_rows", 0)
        total_cols = summary.get("total_columns", 0)
        cols = summary.get("column_details", [])
        col_names = [c["name"] for c in cols]

        msg_lower = message.lower()
        msg_words = set(w.lower() for w in message.split() if len(w) > 2)

        matched_cols = []
        for col_name in col_names:
            col_lower = col_name.lower()
            for w in msg_words:
                if w in col_lower or col_lower in w:
                    matched_cols.append(col_name)
                    break

        if matched_cols:
            parts = [f"**Column '{matched_cols[0]}' data:**"]
            vals = df[matched_cols[0]].dropna().head(10).astype(str).tolist()
            for v in vals[:10]:
                parts.append(f"  - {v[:200]}")
            return "\n".join(parts)

        return (
            f"Your dataset has **{total_rows:,} rows** and **{total_cols} columns**.\n\n"
            f"**Columns:** " + ", ".join(f"`{c}`" for c in col_names[:8]) +
            ("..." if len(col_names) > 8 else "") +
            "\n\nAsk me: \"How many rows?\", \"Show columns\", \"Kya file hai?\", \"Top values\""
        )

    def _ask_local(self, message: str, df: Optional[DataFrame], summary: dict) -> dict:
        msg_lower = message.lower()
        reply = ""
        viz_suggestion = None

        if df is None or summary.get("total_rows", 0) == 0:
            reply = "No dataset is currently loaded. Please upload a dataset first."
            return {"reply": reply, "insights": [], "viz_suggestion": None}

        intent = self._detect_intent(msg_lower)

        if intent == "summary":
            reply = self._get_dataset_summary(df, summary)
            if not reply:
                reply = self._smart_answer(df, summary, message)
        elif intent == "rows":
            reply = f"**Total: {summary.get('total_rows', 0):,} records**\n\nThe dataset has **{summary.get('total_rows', 0):,} rows** and **{summary.get('total_columns', 0)} columns**."
        elif intent == "columns":
            cols = summary.get("column_details", [])
            reply = f"The dataset has these columns (**{len(cols)} total**):\n\n" + "\n".join(f"- **{c['name']}** ({c['dtype']})" for c in cols)
        elif intent == "missing":
            missing = summary.get("missing_cells", 0)
            reply = f"There are **{missing:,}** missing cells in the dataset."
            if missing > 0:
                cols = summary.get("column_details", [])
                null_cols = [c for c in cols if c["null_count"] > 0]
                if null_cols:
                    reply += f"\n\nColumns with missing values:\n" + "\n".join(f"- {c['name']}: {c['null_count']} missing" for c in null_cols[:5])
        elif intent == "average":
            numeric_summary = summary.get("numeric_summary", {})
            if numeric_summary:
                reply = "**Numeric summary statistics:**\n\n"
                import pandas as pd
                reply += pd.DataFrame(numeric_summary).to_string()
            else:
                reply = "No numeric columns found in the dataset."
        elif intent == "top":
            reply = self._ask_top(df, summary)
        elif intent == "chart":
            cols = summary.get("column_details", [])
            numeric_cols = [c for c in cols if "int" in c["dtype"] or "float" in c["dtype"]]
            cat_cols = [c for c in cols if "object" in c["dtype"]]
            if numeric_cols and cat_cols:
                reply = f"I recommend a **bar chart** showing **{numeric_cols[0]['name']}** by **{cat_cols[0]['name']}**."
                viz_suggestion = f"bar:{cat_cols[0]['name']}:{numeric_cols[0]['name']}"
            elif numeric_cols:
                reply = f"I recommend a **line chart** showing trends for **{numeric_cols[0]['name']}**."
                viz_suggestion = f"line:{numeric_cols[0]['name']}"
            else:
                reply = "I recommend a **pie chart** showing the distribution of categorical data."
                viz_suggestion = f"pie:{cat_cols[0]['name']}" if cat_cols else "pie"
        else:
            reply = self._smart_answer(df, summary, message)

        return {
            "reply": reply,
            "insights": [],
            "viz_suggestion": viz_suggestion,
        }


chat_assistant = ChatAssistant()
