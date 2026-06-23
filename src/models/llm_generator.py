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
    
    """Sinh câu trả lời kèm trích dẫn cụ thể"""
    context = _build_context(retrieved_chunks)
    prompt = _build_cited_prompt(question, context)
    
    # Gọi Ollama
    resp  = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature}
    )
    raw_answer = resp["message"]["content"]
    
    # Lấy danh sách trích dẫn dựa trên những gì LLM thực tế đã dùng
    citations = _extract_citations(retrieved_chunks, raw_answer)
    
    return {
        "answer": raw_answer,
        "citations": citations,
        "model": model_name
    }
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
        
    """Tóm tắt nội dung chính của bộ dữ liệu văn bản được truyền vào"""
    context =  _build_context(retrieved_chunks)
    
    prompt =  f"""Bạn là một chuyên gia phân tích dữ liệu. Hãy viết một bản tóm tắt ngắn gọn, 
súc tích về nội dung cốt lõi của tài liệu dựa trên phần văn bản (Context) được cung cấp dưới đây.

---
VĂN BẢN (CONTEXT):
{context}
---

YÊU CẦU:
- Bản tóm tắt phải có bố cục rõ ràng (sử dụng dấu gạch đầu dòng nếu cần).
- Tập trung vào các ý chính, định nghĩa quan trọng hoặc mục tiêu chính của tài liệu.
- Độ dài khoảng 3-5 câu chất lượng.

BẢN TÓM TẮT:"""

    resp = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2} # Tăng độ mượt mà cho việc tóm tắt văn bản
    )
    
    return {
        "answer": resp["message"]["content"],
        "citations": [],
        "model": model_name
    }
    
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
    """Giải thích chi tiết một thuật ngữ kỹ thuật/học thuật dựa trên ngữ cảnh tài liệu"""
    context = _build_context(retrieved_chunks)
    
    prompt = f"""Bạn là một giảng viên đại học chuyên ngành. Hãy giải thích ý nghĩa của thuật ngữ dưới đây 
dựa trên thông tin tìm thấy trong phần ngữ cảnh (Context).

Thuật ngữ cần giải thích: "{term}"

---
NGỮ CẢNH (CONTEXT):
{context}
---

YÊU CẦU:
- Định nghĩa rõ ràng, dễ hiểu.
- Nêu rõ ngữ cảnh hoặc ví dụ áp dụng thuật ngữ này nếu có nhắc tới trong tài liệu.
- Trích dẫn nguồn dạng [Nguồn N] nếu có sử dụng thông tin cụ thể lấy ra từ ngữ cảnh.

GIẢI THÍCH:"""

    resp = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.0}
    )
    raw_answer = resp["message"]["content"]
    citations = _extract_citations(retrieved_chunks, raw_answer)
    
    return {
        "answer": raw_answer,
        "citations": citations,
        "model": model_name
    }
    
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
    
    """Ghép các chunks thành chuỗi ngữ cảnh được đánh số ID để LLM trích dẫn"""
    context_parts = []
    current_length = 0
    
    for idx, chunk in enumerate(retrieved_chunks):
        # Định dạng nguồn 
        chunk_text = f"[Nguồn {idx+1}]: File: {chunk['metadata']['file_name']}, Trang: {chunk['metadata']['page']}\n"
        if chunk['metadata'].get('heading'):
            chunk_text += f"Tiêu đề: {chunk['metadata']['heading']}\n"
        chunk_text += f"Nội dung: {chunk['content']}\n\n"
        
        if current_length + len(chunk_text) > max_chars:
            break
        
        context_parts.append(chunk_text)
        current_length += len(chunk_text)
        
    return "".join(context_parts)
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
    
    """Tạo prompt yêu cầu trả lời và trích dẫn"""
    return f"""Bạn là một trợ lý hỏi đáp tài liệu học tập thông minh và trung thực.
Hãy sử dụng các đoạn ngữ cảnh (Context) được cung cấp dưới đây để trả lời câu hỏi (Question).

---
NGỮ CẢNH (CONTEXT):
{context}
---

CÂU HỎI (QUESTION):
{question}

---
YÊU CẦU NGHIÊM NGẶT:
1. Trả lời ngắn gọn, rõ ràng, đi thẳng vào vấn đề.
2. Chỉ dựa vào thông tin có trong phần NGỮ CẢNH phía trên. Nếu ngữ cảnh không có thông tin, hãy nói thẳng là "Tôi không biết câu trả lời dựa trên tài liệu đã cung cấp", TUYỆT ĐỐI KHÔNG ĐƯỢC BỊA ĐẶT.
3. KỸ THUẬT TRÍCH DẪN (CITATION): Với mỗi thông tin bạn lấy ra từ ngữ cảnh để viết câu trả lời, bạn BẮT BUỘC phải chèn ký hiệu tương ứng ở cuối câu đó, ví dụ: [Nguồn 1] hoặc [Nguồn 2]. Không tự chế ra số nguồn không tồn tại.

TRẢ LỜI:"""
    raise NotImplementedError("_build_cited_prompt chưa được implement")


def _extract_citations(retrieved_chunks: List[RetrievedChunk], raw_answer: str) -> List[CitationDict]:
    """
    (Private) Tạo danh sách citations từ metadata của các chunks đã dùng.

    Args:
        retrieved_chunks (List[RetrievedChunk]): Các chunks đã được đưa vào context

    Returns:
        List[CitationDict]: Danh sách trích dẫn không trùng lặp
    """
    # TODO : Implement
    # Gợi ý: De-duplicate theo (file_name, page), lấy snippet ~100 ký tự đầu
    
    """Tìm các ký hiệu [Nguồn N] hoặc [N] trong câu trả lời mà không dùng thư viện re"""
    citations = []
    seen_indices = []
    
    # Cách 1: Duyệt qua danh sách tất cả các nguồn khả thi có trong retrieved_chunks
    # Giả sử tối đa bạn truyền vào 4 chunks, idx sẽ chạy từ 0 đến 3 (Nguồn 1 đến Nguồn 4)
    for idx in range(len(retrieved_chunks)):
        source_number = idx + 1
        
        # Tạo ra các mẫu chuỗi mà LLM có thể viết
        pattern_1 = f"[Nguồn {source_number}]"
        pattern_2 = f"[{source_number}]"
        
        # Kiểm tra xem chuỗi mẫu này có xuất hiện trong câu trả lời của LLM hay không
        if (pattern_1 in raw_answer) or (pattern_2 in raw_answer):
            if idx not in seen_indices:
                seen_indices.append(idx)
                
    # Sắp xếp lại seen_indices theo thứ tự xuất hiện thực tế trong văn bản (tùy chọn)
    # Ở đây ta duyệt và đóng gói kết quả
    for i in seen_indices:
        chunk = retrieved_chunks[i]
        snippet = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
        
        citation = {
            "file_name": chunk['metadata']['file_name'],
            "page": chunk['metadata']['page'],
            "heading": chunk['metadata'].get('heading', ""),
            "snippet": snippet
        }
        citations.append(citation)
        
    return citations

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
    return len(text) // 4
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
