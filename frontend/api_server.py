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
from fastapi.responses import HTMLResponse, FileResponse
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
    try:
        # Giả định retriever có hàm get_or_create_collection
        from src.pipeline.retriever import get_or_create_collection
        get_or_create_collection(body.name)
        return WorkspaceInfo(name=body.name, file_count=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo workspace: {str(e)}")

@app.get("/api/workspaces", response_model=List[WorkspaceInfo])
async def get_workspaces():
    try:
        names = list_workspaces()
        result = []
        for n in names:
            files = list_files_in_workspace(n)
            result.append(WorkspaceInfo(name=n, file_count=len(files)))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/workspaces/{workspace_name}", status_code=204)
async def remove_workspace(workspace_name: str):
    try:
        delete_workspace(workspace_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workspaces/{workspace_name}/files", response_model=List[str])
async def get_workspace_files(workspace_name: str):
    try:
        return list_files_in_workspace(workspace_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Không tìm thấy workspace")

# =============================================================================
# TASK 4.1 — ENDPOINT: Upload PDF
# =============================================================================

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(
    file           : UploadFile = File(...),
    workspace_name : str        = "default"
):
    tmp_path = ""
    try:
        # 1. Lưu file tạm an toàn
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 2. Extract & Chunking (Module Thùy)
        chunks = process_pdf(tmp_path, workspace_name)
        if not chunks:
            raise ValueError("Không thể trích xuất nội dung từ PDF.")

        # 3. Vector Database (Module Phi)
        add_chunks_to_workspace(workspace_name, chunks)

        # 4. Tính toán metadata trả về
        page_count = max([c["metadata"].get("page", 1) for c in chunks])
        
        return UploadResponse(
            file_name=file.filename,
            workspace_name=workspace_name,
            chunk_count=len(chunks),
            page_count=page_count,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload lỗi: {str(e)}")
    finally:
        # Luôn dọn dẹp file rác
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# =============================================================================
# TASK 4.1 — ENDPOINT: Chat
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    try:
        chunks = search_workspace(body.question, body.workspace_name, body.top_k)
        result = generate_cited_answer(body.question, chunks)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# TASK 4.1 — ENDPOINT: Tóm tắt
# =============================================================================

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(body: SummarizeRequest):
    try:
        # Lấy các chunk đại diện nhất (có thể tinh chỉnh query theo thuật toán của Phi)
        query = f"Nội dung chính của file {body.file_name}" if body.file_name else "Tóm tắt toàn bộ tài liệu"
        chunks = search_workspace(query, body.workspace_name, top_k=10)
        result = summarize_doc(chunks)
        return SummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# TASK 4.1 — ENDPOINT: Giải thích thuật ngữ
# =============================================================================

@app.post("/api/explain", response_model=ExplainResponse)
async def explain(body: ExplainRequest):
    try:
        chunks = search_workspace(body.term, body.workspace_name, top_k=3)
        result = explain_term(body.term, chunks)
        return ExplainResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Kiểm tra server có đang chạy không."""
    return {"status": "ok", "version": "2.0.0"}

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")