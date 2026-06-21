"""
=============================================================================
MODULE: parser.py
TASKS : 1.1 Tích hợp Parser mới (PyMuPDF + pdfplumber)
        1.2 Xây dựng Structured Chunking (Heading/Paragraph)
        1.3 Đóng gói Metadata cho mỗi chunk
=============================================================================

API CONTRACT - Các hàm được định nghĩa ở đây là "giao kèo" với các module khác.
Tên hàm, tham số, và kiểu trả về KHÔNG ĐƯỢC THAY ĐỔI.
Chỉ viết code bên trong phần thân hàm (thay thế `pass` hoặc `return []`).

Kiểu dữ liệu của 1 chunk (ChunkDict):
{
    "content"        : str,   # Nội dung văn bản của chunk
    "metadata": {
        "file_name"      : str,   # Tên file PDF (vd: "giai_tich.pdf")
        "page"           : int,   # Số trang bắt đầu của chunk (1-indexed)
        "workspace_name" : str,   # Tên workspace/notebook (vd: "Giải Tích")
        "chunk_type"     : str,   # "text" | "table" | "heading"
        "heading"        : str,   # Heading cha gần nhất (hoặc "" nếu không có)
    }
}
"""

from typing import List, Dict, Any

ChunkDict = Dict[str, Any]


# =============================================================================
# TASK 1.1 + 1.2 + 1.3 — HÀM CHÍNH (Pipeline hoàn chỉnh)
# =============================================================================

def process_pdf(file_path: str, workspace_name: str) -> List[ChunkDict]:
    """
    Hàm chính — đọc 1 file PDF và trả về list các chunk đã có metadata.

    Quy trình bên trong:
        1. Dùng PyMuPDF (fitz) quét từng trang, nhận diện Heading/Paragraph
        2. Dùng pdfplumber extract bảng biểu (table)
        3. Cắt text thành chunk có nghĩa theo cấu trúc (structured chunking)
        4. Gắn metadata vào từng chunk

    Args:
        file_path      (str): Đường dẫn tuyệt đối đến file PDF trên server
        workspace_name (str): Tên workspace mà file này thuộc về

    Returns:
        List[ChunkDict]: Danh sách các chunk, mỗi chunk là dict theo format
                         ChunkDict ở trên.

    Raises:
        FileNotFoundError: Nếu file_path không tồn tại
        ValueError       : Nếu workspace_name rỗng

    Example:
        >>> chunks = process_pdf("/data/giai_tich.pdf", "Giải Tích")
        >>> print(chunks[0])
        {
            "content": "1.1 Giới hạn của hàm số\\nĐịnh nghĩa: ...",
            "metadata": {
                "file_name": "giai_tich.pdf",
                "page": 5,
                "workspace_name": "Giải Tích",
                "chunk_type": "text",
                "heading": "1.1 Giới hạn của hàm số"
            }
        }
    """
    # TODO : Implement
    # Gợi ý:
    #   text_chunks  = _extract_text_chunks(file_path, workspace_name)
    #   table_chunks = _extract_table_chunks(file_path, workspace_name)
    #   return text_chunks + table_chunks
    raise NotImplementedError("process_pdf chưa được implement — Task của Thùy")


# =============================================================================
# TASK 1.1 — HELPER: Extract text với PyMuPDF
# =============================================================================

def _extract_text_chunks(file_path: str, workspace_name: str) -> List[ChunkDict]:
    """
    (Private) Dùng PyMuPDF (fitz) đọc text, nhận diện block Heading/Paragraph,
    rồi cắt thành chunk có nghĩa và gắn metadata.

    Args:
        file_path      (str): Đường dẫn file PDF
        workspace_name (str): Tên workspace

    Returns:
        List[ChunkDict]: Các chunk loại "text" và "heading"
    """
    # TODO : Implement bằng fitz
    # import fitz
    # doc = fitz.open(file_path)
    # ...
    raise NotImplementedError("_extract_text_chunks chưa được implement")


# =============================================================================
# TASK 1.1 — HELPER: Extract bảng biểu với pdfplumber
# =============================================================================

def _extract_table_chunks(file_path: str, workspace_name: str) -> List[ChunkDict]:
    """
    (Private) Dùng pdfplumber extract các bảng biểu trong PDF,
    chuyển mỗi bảng thành chuỗi markdown, rồi đóng gói thành chunk.

    Args:
        file_path      (str): Đường dẫn file PDF
        workspace_name (str): Tên workspace

    Returns:
        List[ChunkDict]: Các chunk loại "table"
    """
    # TODO (Thùy): Implement bằng pdfplumber
    # import pdfplumber
    # with pdfplumber.open(file_path) as pdf:
    #     for page_num, page in enumerate(pdf.pages, start=1):
    #         tables = page.extract_tables()
    #         ...
    raise NotImplementedError("_extract_table_chunks chưa được implement")


# =============================================================================
# TASK 1.2 — HELPER: Nhận diện Heading
# =============================================================================

def _is_heading(text: str, font_size: float, avg_font_size: float) -> bool:
    """
    (Private) Kiểm tra xem một block text có phải là Heading không,
    dựa trên font size, font flags (bold/italic), hoặc pattern regex.

    Args:
        text          (str)  : Nội dung text của block
        font_size     (float): Font size của block (lấy từ PyMuPDF)
        avg_font_size (float): Font size trung bình của toàn trang

    Returns:
        bool: True nếu là Heading, False nếu là Paragraph thường
    """
    # TODO (Thùy): Implement logic nhận diện heading
    # Gợi ý: heading thường có font_size > avg_font_size * 1.2
    # hoặc match pattern như "1.", "1.1", "Chương", "CHƯƠNG", v.v.
    raise NotImplementedError("_is_heading chưa được implement")


# =============================================================================
# BACKWARD COMPATIBILITY — Giữ lại hàm cũ để không break code hiện tại
# =============================================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    [DEPRECATED] Hàm cũ từ pdf_processor.py — giữ lại để không break code.
    Nên dùng process_pdf() thay thế.
    """
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, size: int = 1000, overlap: int = 200) -> list:
    """
    [DEPRECATED] Hàm cắt chunk cũ theo ký tự — giữ lại để không break code.
    Nên dùng process_pdf() thay thế.
    """
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= size:
            cur += p + "\n"
        else:
            if cur:
                chunks.append(cur.strip())
            cur = (cur[-overlap:] + p + "\n") if overlap else (p + "\n")
    if cur.strip():
        chunks.append(cur.strip())
    return chunks
