# PDF RAG Chatbot 

Chatbot hỏi đáp tài liệu học tập, hỗ trợ nhiều workspace, trích dẫn nguồn, và phân tích chéo nhiều file PDF.

---

## Kiến trúc tổng quan

```
Streamlit UI  ──(HTTP)──►  FastAPI Backend  ──►  ChromaDB (Persistent)
                                │
                                ├──► parser.py      (Thùy)
                                ├──► retriever.py   (Phi)
                                └──► llm_generator.py (Tiến)
```

---

## Cấu trúc thư mục

```
pdf-rag-chatbot/
├── src/
│   ├── data/
│   │   ├── parser.py          ← THÙY: PDF parsing + chunking + metadata
│   │   └── __init__.py
│   ├── pipeline/
│   │   ├── retriever.py       ← PHI: ChromaDB persistent + workspace search
│   │   └── __init__.py
│   ├── models/
│   │   ├── llm_generator.py   ← TIẾN: LLM prompting + citations + summarize
│   │   └── __init__.py
│   ├── api/
│   │   ├── api_server.py      ← MẠNH: FastAPI endpoints
│   │   └── __init__.py
│   └── app/
│       ├── main.py            ← MẠNH: Streamlit UI (gọi API thuần túy)
│       ├── state.py
│       ├── ui_components.py
│       ├── styles.css
│       └── __init__.py
├── configs/
│   └── config.yaml
├── notebooks/
├── requirements.txt
├── git_setup.sh
└── README.md
```

---

## Cài đặt & Chạy

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Đảm bảo Ollama đang chạy với model cần thiết
ollama pull bge-m3
ollama pull vicuna:7b-v1.5-q5_1

# 3. Terminal 1 — Chạy FastAPI backend
uvicorn src.api.api_server:app --reload --port 8000

# 4. Terminal 2 — Chạy Streamlit frontend
streamlit run src/app/main.py
```

---
