"""
=============================================================================
MODULE: llm_generator.py
TASKS : 3.1 Prompt Engineering cho Citations (trích dẫn trang)
        3.2 Quản lý Context Window (đếm/cắt token)
        3.3 Tính năng phụ: Tóm tắt tài liệu & Giải thích thuật ngữ
=============================================================================

API CONTRACT - Các hàm được định nghĩa ở đây là "giao kèo" với module khác.
Tên hàm, tham số, và kiểu trả về KHÔNG ĐƯỢC THAY ĐỔI.

Đầu vào từ retriever.py của Phi (RetrievedChunk):
{
    "content" : str,
    "metadata": {
        "file_name"      : str,
        "page"           : int,
        "workspace_name" : str,
        "chunk_type"     : str,
        "heading"        : str,
    },
    "score"   : float
}

Đầu ra trả cho FastAPI của Mạnh (AnswerDict):
{
    "answer"    : str,          # Câu trả lời chính
    "citations" : List[Dict],   # Danh sách trích dẫn
    "model"     : str           # Tên model đã dùng
}

Cấu trúc 1 citation:
{
    "file_name" : str,   # "giai_tich.pdf"
    "page"      : int,   # 12
    "heading"   : str,   # "1.2 Giới hạn hàm số" (hoặc "")
    "snippet"   : str    # Đoạn text ngắn (~100 ký tự) trích từ chunk
}
"""

from typing import List, Dict, Any, Optional

# Kiểu alias
RetrievedChunk = Dict[str, Any]
AnswerDict     = Dict[str, Any]
CitationDict   = Dict[str, Any]

# Config mặc định
DEFAULT_LLM_MODEL   = "vicuna:7b-v1.5-q5_1"
DEFAULT_EMBED_MODEL = "bge-m3"
MAX_CONTEXT_CHARS   = 6000     # ~1500 tokens, giới hạn an toàn cho Vicuna 7B


# =============================================================================
# TASK 3.1 — HÀM CHÍNH: Sinh câu trả lời có trích dẫn
# =============================================================================

def generate_cited_answer(
    question: str,
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.0
) -> AnswerDict:
    """
    Sinh câu trả lời từ LLM kèm theo danh sách trích dẫn nguồn.

    Quy trình bên trong:
        1. Gọi _build_context() để ghép chunks thành context string
        2. Gọi _build_cited_prompt() để tạo prompt yêu cầu LLM trích dẫn
        3. Gọi Ollama LLM để sinh answer
        4. Parse citations từ answer và trả về AnswerDict

    Args:
        question        (str)              : Câu hỏi của người dùng
        retrieved_chunks (List[RetrievedChunk]): Chunks từ retriever.search_workspace()
        model_name      (str)              : Tên model Ollama
        temperature     (float)            : Độ ngẫu nhiên (0.0 = tất định)

    Returns:
        AnswerDict: {
            "answer"   : str,        # Câu trả lời thuần text
            "citations": List[Dict], # Danh sách trích dẫn
            "model"    : str         # Tên model đã dùng
        }

    Example:
        >>> chunks = search_workspace("Giới hạn là gì?", "Giải Tích")
        >>> result = generate_cited_answer("Giới hạn là gì?", chunks)
        >>> print(result["answer"])
        "Giới hạn của hàm số f(x) khi x tiến tới a là..."
        >>> print(result["citations"])
        [{"file_name": "giai_tich.pdf", "page": 5, "heading": "1.1 Giới hạn", "snippet": "..."}]
    """
    # TODO : Implement
    # Gợi ý:
    #   context    = _build_context(retrieved_chunks)
    #   prompt     = _build_cited_prompt(question, context)
    #   raw_answer = _call_ollama(prompt, model_name, temperature)
    #   citations  = _extract_citations(retrieved_chunks)
    #   return {"answer": raw_answer, "citations": citations, "model": model_name}
    raise NotImplementedError("generate_cited_answer chưa được implement — Task của Tiến")


# =============================================================================
# TASK 3.3 — Tóm tắt tài liệu
# =============================================================================

def summarize_doc(
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL
) -> AnswerDict:
    """
    Tóm tắt nội dung tài liệu dựa trên các chunks đã retrieve.
    Được gọi bởi FastAPI endpoint POST /api/summarize.

    Args:
        retrieved_chunks (List[RetrievedChunk]): Chunks đại diện cho tài liệu
        model_name       (str)                 : Tên model Ollama

    Returns:
        AnswerDict: {
            "answer"   : str,   # Bản tóm tắt
            "citations": [],    # Rỗng (tóm tắt không cần citation)
            "model"    : str
        }
    """
    # TODO : Implement bằng prompt chuyên biệt cho tóm tắt
    raise NotImplementedError("summarize_doc chưa được implement — Task của Tiến")


# =============================================================================
# TASK 3.3 — Giải thích thuật ngữ khó
# =============================================================================

def explain_term(
    term: str,
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL
) -> AnswerDict:
    """
    Giải thích một thuật ngữ kỹ thuật dựa trên ngữ cảnh trong tài liệu.

    Args:
        term             (str)              : Thuật ngữ cần giải thích
        retrieved_chunks (List[RetrievedChunk]): Chunks liên quan đến thuật ngữ
        model_name       (str)              : Tên model Ollama

    Returns:
        AnswerDict: {
            "answer"   : str,   # Giải thích thuật ngữ
            "citations": List[Dict],
            "model"    : str
        }
    """
    # TODO : Implement bằng prompt chuyên biệt cho giải thích thuật ngữ
    raise NotImplementedError("explain_term chưa được implement — Task của Tiến")


# =============================================================================
# TASK 3.2 — HELPER: Quản lý Context Window
# =============================================================================

def _build_context(
    retrieved_chunks: List[RetrievedChunk],
    max_chars: int = MAX_CONTEXT_CHARS
) -> str:
    """
    (Private) Ghép các chunks thành một context string, cắt bớt nếu vượt giới hạn.
    Đảm bảo không vượt quá context window của LLM.

    Args:
        retrieved_chunks (List[RetrievedChunk]): Chunks đã retrieve và sort theo score
        max_chars        (int)                 : Giới hạn ký tự tối đa

    Returns:
        str: Context string đã được ghép và cắt gọt
    """
    # TODO : Implement
    # Gợi ý: Ghép từ chunk có score cao nhất, dừng lại khi vượt max_chars
    raise NotImplementedError("_build_context chưa được implement")


def _build_cited_prompt(question: str, context: str) -> str:
    """
    (Private) Xây dựng prompt yêu cầu LLM trả lời và ghi rõ nguồn trích dẫn.

    Args:
        question (str): Câu hỏi
        context  (str): Context đã được format với số trang

    Returns:
        str: Prompt hoàn chỉnh
    """
    # TODO : Implement
    # Gợi ý: Định dạng context kèm [File: xxx, Trang: N] vào prompt
    raise NotImplementedError("_build_cited_prompt chưa được implement")


def _extract_citations(retrieved_chunks: List[RetrievedChunk]) -> List[CitationDict]:
    """
    (Private) Tạo danh sách citations từ metadata của các chunks đã dùng.

    Args:
        retrieved_chunks (List[RetrievedChunk]): Các chunks đã được đưa vào context

    Returns:
        List[CitationDict]: Danh sách trích dẫn không trùng lặp
    """
    # TODO : Implement
    # Gợi ý: De-duplicate theo (file_name, page), lấy snippet ~100 ký tự đầu
    raise NotImplementedError("_extract_citations chưa được implement")


def _count_tokens(text: str) -> int:
    """
    (Private) Ước lượng số token của một chuỗi text.
    Quy tắc đơn giản: 1 token ≈ 4 ký tự (cho tiếng Anh/Việt).

    Args:
        text (str): Chuỗi cần đếm token

    Returns:
        int: Số token ước lượng
    """
    # TODO : Implement (có thể dùng len(text) // 4 trước, cải thiện sau)
    raise NotImplementedError("_count_tokens chưa được implement")


# =============================================================================
# BACKWARD COMPATIBILITY — Giữ lại hàm cũ để không break code hiện tại
# =============================================================================

def get_embedding(texts: list, model_name: str = DEFAULT_EMBED_MODEL) -> list:
    """[DEPRECATED] Dùng trực tiếp từ llm_manager.py cũ."""
    import ollama
    embeddings = []
    for text in texts:
        response = ollama.embeddings(model=model_name, prompt=text)
        embeddings.append(response["embedding"])
    return embeddings


def generate_answer(
    question: str,
    context: str,
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.0
) -> str:
    """
    [DEPRECATED] Hàm cũ từ llm_manager.py — giữ lại để không break code.
    Nên dùng generate_cited_answer() thay thế.
    """
    import ollama
    PROMPT_TEMPLATE = """Bạn là một trợ lý hỏi đáp tài liệu học tập thông minh và trung thực.
Hãy sử dụng các đoạn ngữ cảnh (Context) được cung cấp dưới đây để trả lời câu hỏi (Question).

---
NGỮ CẢNH (CONTEXT):
{context}
---

CÂU HỎI (QUESTION):
{question}

---
YÊU CẦU:
- Trả lời ngắn gọn, rõ ràng, đi thẳng vào vấn đề.
- Chỉ dựa vào thông tin có trong phần NGỮ CẢNH phía trên.
- Nếu thông tin trong NGỮ CẢNH không có hoặc không đủ để trả lời, hãy nói thẳng là "Tôi không biết câu trả lời dựa trên tài liệu đã cung cấp", TUYỆT ĐỐI KHÔNG ĐƯỢC BỊA ĐẶT thông tin.

TRẢ LỜI:"""
    formatted_prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    resp = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": formatted_prompt}],
        options={"temperature": temperature}
    )
    return resp["message"]["content"]
