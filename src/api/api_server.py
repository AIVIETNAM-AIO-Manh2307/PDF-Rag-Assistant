"""
=============================================================================
MODULE: api_server.py
TASKS : 4.1 Dựng Backend FastAPI (các REST endpoint)
        4.2 Tái cấu trúc Streamlit — chỉ gọi API, không có logic xử lý
        4.3 Nâng cấp giao diện (Workspace sidebar, Citations highlight)
=============================================================================

API CONTRACT
Chạy server:
    uvicorn src.api.api_server:app --reload --port 8000

Base URL: http://localhost:8000

=== ENDPOINT SUMMARY ===
POST /api/workspaces          Tạo workspace mới
GET  /api/workspaces          Lấy danh sách workspace
DELETE /api/workspaces/{name} Xóa workspace
POST /api/upload              Upload và xử lý PDF vào workspace
GET  /api/workspaces/{name}/files  Danh sách file trong workspace
POST /api/chat                Hỏi đáp trong workspace
POST /api/summarize           Tóm tắt tài liệu
POST /api/explain             Giải thích thuật ngữ
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile, os

# Import các module của các thành viên khác
# (sẽ hoạt động sau khi từng người implement xong)
from src.data.parser        import process_pdf
from src.pipeline.retriever import (
    search_workspace,
    add_chunks_to_workspace,
    delete_workspace,
    list_workspaces,
    list_files_in_workspace,
)
from src.models.llm_generator import (
    generate_cited_answer,
    summarize_doc,
    explain_term,
)

app = FastAPI(
    title="PDF RAG Chatbot API",
    description="Backend API cho chatbot hỏi đáp tài liệu học tập",
    version="2.0.0"
)

# Cho phép Streamlit frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# PYDANTIC SCHEMAS — Request & Response bodies
# =============================================================================

class WorkspaceCreate(BaseModel):
    name: str          # Tên workspace, vd: "Giải Tích"

class WorkspaceInfo(BaseModel):
    name: str
    file_count: int

class ChatRequest(BaseModel):
    question: str
    workspace_name: str
    top_k: int = 5

class Citation(BaseModel):
    file_name : str
    page      : int
    heading   : str
    snippet   : str

class ChatResponse(BaseModel):
    answer    : str
    citations : List[Citation]
    model     : str

class SummarizeRequest(BaseModel):
    workspace_name : str
    file_name      : Optional[str] = None   # None = tóm tắt toàn workspace

class SummarizeResponse(BaseModel):
    summary : str
    model   : str

class ExplainRequest(BaseModel):
    term           : str
    workspace_name : str

class ExplainResponse(BaseModel):
    explanation : str
    citations   : List[Citation]
    model       : str

class UploadResponse(BaseModel):
    file_name      : str
    workspace_name : str
    chunk_count    : int
    page_count     : int
    status         : str   # "success" | "error"


# =============================================================================
# TASK 4.1 — ENDPOINT: Quản lý Workspace
# =============================================================================

@app.post("/api/workspaces", response_model=WorkspaceInfo, status_code=201)
async def create_workspace(body: WorkspaceCreate):
    """
    Tạo một workspace mới (tạo collection trong ChromaDB).

    Request body:
        { "name": "Giải Tích" }

    Response:
        { "name": "Giải Tích", "file_count": 0 }
    """
    # TODO (Mạnh): Implement
    # Gợi ý:
    #   get_or_create_collection(body.name)  # từ retriever.py của Phi
    #   return WorkspaceInfo(name=body.name, file_count=0)
    raise NotImplementedError("POST /api/workspaces chưa được implement")


@app.get("/api/workspaces", response_model=List[WorkspaceInfo])
async def get_workspaces():
    """
    Lấy danh sách tất cả workspace hiện có.

    Response:
        [
            { "name": "Giải Tích", "file_count": 3 },
            { "name": "CTDL",      "file_count": 1 }
        ]
    """
    # TODO (Mạnh): Implement
    # names = list_workspaces()
    # return [WorkspaceInfo(name=n, file_count=len(list_files_in_workspace(n))) for n in names]
    raise NotImplementedError("GET /api/workspaces chưa được implement")


@app.delete("/api/workspaces/{workspace_name}", status_code=204)
async def remove_workspace(workspace_name: str):
    """
    Xóa toàn bộ dữ liệu của một workspace.
    """
    # TODO (Mạnh): Implement
    # delete_workspace(workspace_name)
    raise NotImplementedError("DELETE /api/workspaces/{name} chưa được implement")


@app.get("/api/workspaces/{workspace_name}/files", response_model=List[str])
async def get_workspace_files(workspace_name: str):
    """
    Lấy danh sách file PDF trong workspace.

    Response:
        ["giai_tich_c1.pdf", "giai_tich_c2.pdf"]
    """
    # TODO (Mạnh): Implement
    # return list_files_in_workspace(workspace_name)
    raise NotImplementedError("GET /api/workspaces/{name}/files chưa được implement")


# =============================================================================
# TASK 4.1 — ENDPOINT: Upload PDF
# =============================================================================

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(
    file           : UploadFile = File(...),
    workspace_name : str        = "default"
):
    """
    Upload file PDF, xử lý (parse + chunk + embed), lưu vào workspace.

    Form data:
        file           : file PDF
        workspace_name : tên workspace đích

    Response:
        {
            "file_name"      : "giai_tich.pdf",
            "workspace_name" : "Giải Tích",
            "chunk_count"    : 87,
            "page_count"     : 42,
            "status"         : "success"
        }
    """
    # TODO (Mạnh): Implement
    # Gợi ý:
    #   1. Lưu file tạm: tempfile.NamedTemporaryFile
    #   2. chunks = process_pdf(tmp_path, workspace_name)   # Thùy
    #   3. add_chunks_to_workspace(workspace_name, chunks)  # Phi
    #   4. Trả về UploadResponse
    raise NotImplementedError("POST /api/upload chưa được implement")


# =============================================================================
# TASK 4.1 — ENDPOINT: Chat
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Nhận câu hỏi, tìm kiếm trong workspace, sinh câu trả lời có trích dẫn.

    Request body:
        {
            "question"       : "Giới hạn là gì?",
            "workspace_name" : "Giải Tích",
            "top_k"          : 5
        }

    Response:
        {
            "answer"    : "Giới hạn của hàm số f(x) khi x tiến tới a ...",
            "citations" : [
                { "file_name": "giai_tich.pdf", "page": 5, "heading": "1.1", "snippet": "..." }
            ],
            "model"     : "vicuna:7b-v1.5-q5_1"
        }
    """
    # TODO (Mạnh): Implement
    # Gợi ý:
    #   chunks = search_workspace(body.question, body.workspace_name, body.top_k)  # Phi
    #   result = generate_cited_answer(body.question, chunks)                       # Tiến
    #   return ChatResponse(**result)
    raise NotImplementedError("POST /api/chat chưa được implement")


# =============================================================================
# TASK 4.1 — ENDPOINT: Tóm tắt
# =============================================================================

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(body: SummarizeRequest):
    """
    Tóm tắt nội dung một file hoặc toàn bộ workspace.

    Request body:
        {
            "workspace_name" : "Giải Tích",
            "file_name"      : "giai_tich_c1.pdf"   // null = tóm tắt cả workspace
        }

    Response:
        { "summary": "Tài liệu trình bày về...", "model": "vicuna:7b..." }
    """
    # TODO (Mạnh): Implement
    raise NotImplementedError("POST /api/summarize chưa được implement")


# =============================================================================
# TASK 4.1 — ENDPOINT: Giải thích thuật ngữ
# =============================================================================

@app.post("/api/explain", response_model=ExplainResponse)
async def explain(body: ExplainRequest):
    """
    Giải thích một thuật ngữ kỹ thuật trong ngữ cảnh tài liệu.

    Request body:
        { "term": "Big-O notation", "workspace_name": "CTDL" }

    Response:
        {
            "explanation" : "Big-O notation là ký hiệu dùng để...",
            "citations"   : [...],
            "model"       : "vicuna:7b..."
        }
    """
    # TODO (Mạnh): Implement
    raise NotImplementedError("POST /api/explain chưa được implement")


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Kiểm tra server có đang chạy không."""
    return {"status": "ok", "version": "2.0.0"}
