"""
=============================================================================
MODULE: retriever.py
TASKS : 2.1 Nâng cấp Vector DB sang PersistentClient
        2.2 Xây dựng Workspaces (lọc theo metadata)
        2.3 Thuật toán Cross Analysis (nhiều file cùng workspace)
        2.4 [Optional] Hybrid Search (BM25 + Vector)
=============================================================================

API CONTRACT - Các hàm được định nghĩa ở đây là "giao kèo" với các module khác.
Tên hàm, tham số, và kiểu trả về KHÔNG ĐƯỢC THAY ĐỔI.
Chỉ viết code bên trong phần thân hàm.

Kiểu dữ liệu đầu vào (ChunkDict) — nhận từ parser.py của Thùy:
{
    "content" : str,
    "metadata": {
        "file_name"      : str,
        "page"           : int,
        "workspace_name" : str,
        "chunk_type"     : str,   # "text" | "table" | "heading"
        "heading"        : str,
    }
}

Kiểu dữ liệu đầu ra (RetrievedChunk) — trả cho llm_generator.py của Tiến:
{
    "content" : str,
    "metadata": {
        "file_name"      : str,
        "page"           : int,
        "workspace_name" : str,
        "chunk_type"     : str,
        "heading"        : str,
    },
    "score"   : float    # Điểm similarity (0.0 - 1.0), cao hơn = liên quan hơn
}
"""

from typing import List, Dict, Any, Optional

# Kiểu alias
ChunkDict     = Dict[str, Any]
RetrievedChunk = Dict[str, Any]

# Đường dẫn lưu ChromaDB xuống ổ cứng (thay đổi nếu cần)
CHROMA_PERSIST_DIR = "./chroma_db"


# =============================================================================
# TASK 2.2 + 2.3 — HÀM CHÍNH (được gọi bởi FastAPI endpoint /api/chat)
# =============================================================================

def search_workspace(
    query: str,
    workspace_name: str,
    top_k: int = 5
) -> List[RetrievedChunk]:
    """
    Tìm kiếm top-k chunks liên quan nhất trong một workspace cụ thể.
    Tự động quét nhiều file khác nhau trong cùng workspace (Cross Analysis).

    Args:
        query          (str): Câu hỏi của người dùng
        workspace_name (str): Tên workspace cần tìm kiếm trong đó
        top_k          (int): Số lượng chunk trả về (default: 5)

    Returns:
        List[RetrievedChunk]: Danh sách chunks sắp xếp theo độ liên quan giảm dần.
                              Mỗi phần tử chứa "content", "metadata", "score".

    Raises:
        ValueError: Nếu workspace_name không tồn tại trong DB

    Example:
        >>> results = search_workspace("Định nghĩa giới hạn là gì?", "Giải Tích", top_k=4)
        >>> for r in results:
        ...     print(r["metadata"]["file_name"], r["metadata"]["page"], r["score"])
        giai_tich_chuong1.pdf  5  0.92
        giai_tich_chuong2.pdf  12 0.87
    """
    # TODO : Implement
    # Gợi ý:
    #   1. Lấy query embedding từ llm_manager.get_embedding([query])
    #   2. Gọi ChromaDB với where={"workspace_name": workspace_name}
    #   3. Map kết quả sang List[RetrievedChunk]
    raise NotImplementedError("search_workspace chưa được implement — Task của Phi")


# =============================================================================
# TASK 2.1 — Quản lý kết nối ChromaDB Persistent
# =============================================================================

def get_or_create_collection(workspace_name: str):
    """
    Lấy (hoặc tạo mới) một ChromaDB collection tương ứng với workspace.
    Sử dụng PersistentClient để dữ liệu được lưu xuống ổ cứng.

    Args:
        workspace_name (str): Tên workspace (dùng làm tên collection)

    Returns:
        chromadb.Collection: Collection object của ChromaDB
    """
    # TODO : Implement
    # import chromadb
    # client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    # return client.get_or_create_collection(name=workspace_name)
    raise NotImplementedError("get_or_create_collection chưa được implement")


def add_chunks_to_workspace(workspace_name: str, chunks: List[ChunkDict]) -> None:
    """
    Vector hóa và lưu danh sách chunks vào workspace (ChromaDB collection).
    Được gọi bởi FastAPI endpoint POST /api/upload.

    Args:
        workspace_name (str)         : Tên workspace đích
        chunks         (List[ChunkDict]): Danh sách chunks từ parser.process_pdf()

    Returns:
        None

    Raises:
        ValueError: Nếu chunks rỗng
    """
    # TODO : Implement
    # Gợi ý:
    #   1. collection = get_or_create_collection(workspace_name)
    #   2. texts     = [c["content"] for c in chunks]
    #   3. metadatas = [c["metadata"] for c in chunks]
    #   4. embeddings = get_embedding(texts)   # từ llm_manager
    #   5. collection.add(ids=..., documents=texts, embeddings=embeddings, metadatas=metadatas)
    raise NotImplementedError("add_chunks_to_workspace chưa được implement")


def delete_workspace(workspace_name: str) -> None:
    """
    Xóa toàn bộ dữ liệu của một workspace khỏi ChromaDB.

    Args:
        workspace_name (str): Tên workspace cần xóa

    Returns:
        None
    """
    # TODO (Phi): Implement
    raise NotImplementedError("delete_workspace chưa được implement")


def list_workspaces() -> List[str]:
    """
    Trả về danh sách tên tất cả workspace hiện có trong ChromaDB.

    Returns:
        List[str]: Ví dụ ["Giải Tích", "CTDL", "Toán Rời Rạc"]
    """
    # TODO (Phi): Implement
    raise NotImplementedError("list_workspaces chưa được implement")


def list_files_in_workspace(workspace_name: str) -> List[str]:
    """
    Trả về danh sách tên file PDF trong một workspace.

    Args:
        workspace_name (str): Tên workspace

    Returns:
        List[str]: Ví dụ ["giai_tich_c1.pdf", "giai_tich_c2.pdf"]
    """
    # TODO (Phi): Implement
    raise NotImplementedError("list_files_in_workspace chưa được implement")


# =============================================================================
# TASK 2.4 [OPTIONAL] — Hybrid Search
# =============================================================================

def hybrid_search(
    query: str,
    workspace_name: str,
    top_k: int = 5,
    alpha: float = 0.7
) -> List[RetrievedChunk]:
    """
    [Tùy chọn nâng cao] Kết hợp Vector Search và BM25 keyword search,
    dùng Reciprocal Rank Fusion (RRF) để rerank kết quả.

    Args:
        query          (str)  : Câu hỏi của người dùng
        workspace_name (str)  : Tên workspace
        top_k          (int)  : Số chunk trả về
        alpha          (float): Trọng số của vector search (0.0-1.0).
                                1-alpha là trọng số của BM25.

    Returns:
        List[RetrievedChunk]: Chunks đã được rerank
    """
    # TODO (Phi): Implement — chỉ làm sau khi search_workspace hoạt động ổn
    raise NotImplementedError("hybrid_search chưa được implement (tùy chọn)")


# =============================================================================
# BACKWARD COMPATIBILITY — Giữ lại class cũ để không break code hiện tại
# =============================================================================

class RAGPipeline:
    """
    [DEPRECATED] Class cũ từ rag_pipeline.py — giữ lại để không break code.
    Nên dùng search_workspace() và add_chunks_to_workspace() thay thế.
    """
    def __init__(self, collection_name: str = "rag_collection"):
        import chromadb
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(self, chunks: list):
        from src.models.llm_manager import get_embedding
        embeddings = get_embedding(chunks)
        self.collection.add(
            ids=[str(i) for i in range(len(chunks))],
            documents=chunks,
            embeddings=embeddings
        )

    def retrieve(self, query: str, k: int = 4) -> list:
        from src.models.llm_manager import get_embedding
        query_vector = get_embedding([query])
        res = self.collection.query(query_embeddings=query_vector, n_results=k)
        return res["documents"][0]
