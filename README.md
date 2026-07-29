<div align="center">

# 🕵️ Company Research Agent

**A multi-agent AI system that researches any company using live web search and produces a downloadable PDF/DOCX report with actionable suggestions**

[![AutoGen](https://img.shields.io/badge/AutoGen-00A67E?style=for-the-badge&logo=microsoft&logoColor=white)](https://microsoft.github.io/autogen/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=lightning&logoColor=white)](https://console.groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![DuckDuckGo](https://img.shields.io/badge/DuckDuckGo%20Search-DE5833?style=for-the-badge&logo=duckduckgo&logoColor=white)](https://pypi.org/project/duckduckgo-search/)
[![Llama 3.3 70B](https://img.shields.io/badge/Llama%203.3%2070B-0467DF?style=for-the-badge&logo=meta&logoColor=white)](https://console.groq.com)

[![PDF Export](https://img.shields.io/badge/export-PDF-EC1C24?style=flat-square&logo=adobeacrobatreader&logoColor=white)](#)
[![DOCX Export](https://img.shields.io/badge/export-DOCX-2B579A?style=flat-square&logo=microsoftword&logoColor=white)](#)
[![License](https://img.shields.io/badge/license-MIT-9B59B6?style=flat-square)](./LICENSE)

</div>

Exposed via a **FastAPI** backend — no paid API keys required.

---

## 🧭 How it works

Four **AutoGen** agents run in sequence:

| # | Agent | Role |
|---|---|---|
| 1️⃣ | 🔎 **Researcher** | Calls a `web_search` tool (DuckDuckGo, no API key needed) to gather live info: overview, products, recent news, market position, competitors, leadership |
| 2️⃣ | 🗂️ **Analyst** | Structures the raw findings into clean markdown sections |
| 3️⃣ | 💡 **Strategist** | Generates 5-8 concrete, company-specific suggestions (growth ideas, risks, positioning, partnerships) |
| 4️⃣ | ✍️ **Writer** | Compiles everything into a polished final report |

The report is then rendered to both **PDF** and **DOCX** and served as downloads.

---

## 🧱 Stack

| | |
|---|---|
| 🤖 **Agents / orchestration** | AutoGen (`pyautogen`) |
| ⚡ **LLM** | Groq's free tier (OpenAI-compatible API, Llama 3.3 70B by default) |
| 🔎 **Web search** | `duckduckgo-search` (free, no API key) |
| 🚀 **Backend** | FastAPI |
| 📄 **Report export** | `python-docx`, `fpdf2` |

---

## ⚙️ Setup

```bash
git clone <your-repo-url>
cd company-research-agent
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your free Groq API key (https://console.groq.com/keys)
```

---

## ▶️ Run

```bash
uvicorn app.main:app --reload
```

API docs (Swagger UI) will be live at: `http://127.0.0.1:8000/docs`

---

## 📡 Usage

**Run research on a company:**

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Stripe"}'
```

Response includes a `job_id`, the full markdown report, and download URLs:

```json
{
  "job_id": "b3f1...",
  "company_name": "Stripe",
  "final_report": "# Stripe Research Report\n\n...",
  "pdf_url": "/download/b3f1.../pdf",
  "docx_url": "/download/b3f1.../docx"
}
```

**Download the report:**

```bash
curl -OJ http://127.0.0.1:8000/download/<job_id>/pdf
curl -OJ http://127.0.0.1:8000/download/<job_id>/docx
```

---

## 📁 Project structure

```
company-research-agent/
├── app/
│   ├── main.py                 # FastAPI app + routes
│   ├── config.py               # env/config + LLM config for AutoGen
│   ├── agents/
│   │   ├── agents.py           # Researcher, Analyst, Strategist, Writer
│   │   └── orchestrator.py     # runs the 4-agent pipeline sequentially
│   ├── tools/
│   │   └── web_search.py       # DuckDuckGo search tool for the Researcher
│   └── utils/
│       └── report_export.py    # markdown -> PDF / DOCX
├── outputs/                    # generated reports land here
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📝 Notes / next steps

- 💾 Swap the in-memory `JOBS` dict in `main.py` for Redis/Postgres if you need persistence across restarts.
- 🔎 Swap DuckDuckGo for Tavily/Serper if you want higher-quality search (both have free tiers, just add an API key and edit `web_search.py`).
- ⏱️ Add a `/research/async` + background task (Celery/RQ) if reports start taking too long for a synchronous request.
