# 📚 PDF RAG Chatbot — v2.0

Chatbot hỏi đáp tài liệu học tập, hỗ trợ nhiều workspace, trích dẫn nguồn, và phân tích chéo nhiều file PDF.

---

## 🏗️ Kiến trúc tổng quan

```
Streamlit UI  ──(HTTP)──►  FastAPI Backend  ──►  ChromaDB (Persistent)
                                │
                                ├──► parser.py      (Thùy)
                                ├──► retriever.py   (Phi)
                                └──► llm_generator.py (Tiến)
```

---

## 📁 Cấu trúc thư mục

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

## 🚀 Cài đặt & Chạy

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

## 🌿 Git Workflow

### Setup lần đầu (người tạo repo chạy)

```bash
bash git_setup.sh
git remote add origin https://github.com/<org>/<repo>.git
git push -u origin --all
```

### Mỗi thành viên làm việc

```bash
# 1. Checkout branch của mình
git checkout feature/thuy-data-parser      # Thùy
git checkout feature/phi-pipeline-retriever # Phi
git checkout feature/tien-model-generator   # Tiến
git checkout feature/manh-api-ui            # Mạnh

# 2. Đồng bộ code mới nhất từ develop trước khi làm
git fetch origin
git rebase origin/develop

# 3. Làm việc, commit thường xuyên
git add src/data/parser.py
git commit -m "feat(parser): implement _extract_text_chunks with PyMuPDF"

# 4. Push lên GitHub
git push origin feature/thuy-data-parser

# 5. Tạo Pull Request vào develop trên GitHub
```

### Quy ước đặt tên commit

| Prefix | Ý nghĩa |
|--------|---------|
| `feat` | Thêm tính năng mới |
| `fix`  | Sửa bug |
| `refactor` | Refactor code |
| `test` | Thêm/sửa test |
| `docs` | Cập nhật tài liệu |
| `chore` | Cấu hình, build |

Ví dụ: `feat(parser): add structured chunking by heading`

---

## 📋 API Contract

### Luồng dữ liệu giữa các module

```
parser.py (Thùy)
  └── process_pdf(file_path, workspace_name) → List[ChunkDict]
           │
           ▼
retriever.py (Phi)
  └── add_chunks_to_workspace(workspace_name, chunks) → None
  └── search_workspace(query, workspace_name, top_k) → List[RetrievedChunk]
           │
           ▼
llm_generator.py (Tiến)
  └── generate_cited_answer(question, retrieved_chunks) → AnswerDict
  └── summarize_doc(retrieved_chunks) → AnswerDict
  └── explain_term(term, retrieved_chunks) → AnswerDict
           │
           ▼
api_server.py (Mạnh) — tổng hợp tất cả qua REST endpoints
```

### ChunkDict (Thùy → Phi)

```python
{
    "content": str,
    "metadata": {
        "file_name"     : str,   # "giai_tich.pdf"
        "page"          : int,   # 5
        "workspace_name": str,   # "Giải Tích"
        "chunk_type"    : str,   # "text" | "table" | "heading"
        "heading"       : str,   # "1.1 Giới hạn"
    }
}
```

### RetrievedChunk (Phi → Tiến)

```python
{
    "content" : str,
    "metadata": { ... },   # Giống ChunkDict.metadata
    "score"   : float      # 0.0 - 1.0
}
```

### AnswerDict (Tiến → Mạnh)

```python
{
    "answer"    : str,
    "citations" : [
        { "file_name": str, "page": int, "heading": str, "snippet": str }
    ],
    "model"     : str
}
```

---

## 📌 Phân công & Tiến độ

| Thành viên | Branch | Module | Status |
|-----------|--------|--------|--------|
| Thùy | `feature/thuy-data-parser` | `src/data/parser.py` | 🔲 Chưa bắt đầu |
| Phi | `feature/phi-pipeline-retriever` | `src/pipeline/retriever.py` | 🔲 Chưa bắt đầu |
| Tiến | `feature/tien-model-generator` | `src/models/llm_generator.py` | 🔲 Chưa bắt đầu |
| Mạnh | `feature/manh-api-ui` | `src/api/api_server.py` + `src/app/main.py` | 🔲 Chưa bắt đầu |

**Thứ tự implement khuyến nghị:**
1. Thùy implement `process_pdf()` → test thủ công với 1 file PDF
2. Phi implement `add_chunks_to_workspace()` + `search_workspace()` → test với output của Thùy
3. Tiến implement `generate_cited_answer()` → test với output của Phi
4. Mạnh ghép tất cả vào API endpoints → test end-to-end
