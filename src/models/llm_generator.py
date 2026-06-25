import os
import time
import re
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Kiểu alias
RetrievedChunk = Dict[str, Any]
AnswerDict     = Dict[str, Any]
CitationDict   = Dict[str, Any]

# 1. BẢO MẬT API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("⚠️ CHƯA CÓ API KEY: Vui lòng kiểm tra lại file .env")

genai.configure(api_key=GEMINI_API_KEY)

# =============================================================================
# 2. CẤU HÌNH MÔ HÌNH CHUẨN XÁC (Tránh lỗi 404 Not Found)
# Sử dụng Gemini 2.0 Flash mới nhất và mô hình Embedding chuẩn của Google
# =============================================================================
DEFAULT_LLM_MODEL   = "gemini-2.5-flash-lite"
DEFAULT_EMBED_MODEL = "gemini-embedding-001"
MAX_CONTEXT_CHARS   = 20000


# =============================================================================
# TASK 3.1 — HÀM CHÍNH: Sinh câu trả lời có trích dẫn
# =============================================================================

def generate_cited_answer(
    question: str,
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.0
) -> AnswerDict:
    context = _build_context(retrieved_chunks)
    prompt = _build_cited_prompt(question, context)
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=temperature)
        )
        raw_answer = response.text
    except Exception as e:
        raw_answer = f"⚠️ Lỗi từ máy chủ AI: {str(e)}"
    
    citations = _extract_citations(retrieved_chunks, raw_answer)
    
    clean_answer = re.sub(r'\s*\[Nguồn \d+\]|\s*\[\d+\]', '', raw_answer)
    
    # CƠ CHẾ FALLBACK 
    if not citations and retrieved_chunks and "⚠️ Lỗi" not in raw_answer:
        best_chunk = retrieved_chunks[0]
        meta = best_chunk.get('metadata', {})
        content = best_chunk.get('content', '')
        
        snippet = content[:120] + "..." if len(content) > 120 else content
        citations.append({
            "file_name": meta.get('file_name', 'Tài liệu không tên'),
            "page": meta.get('page', 1),
            "heading": meta.get('heading', ""),
            "snippet": snippet
        })
    
    return {
        "answer": clean_answer,  
        "citations": citations,
        "model": model_name
    }

# =============================================================================
# TASK 3.3 — Tóm tắt tài liệu
# =============================================================================

def summarize_doc(
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL
) -> AnswerDict:
    context =  _build_context(retrieved_chunks)
    prompt =  f"""Bạn là chuyên gia phân tích. Hãy tóm tắt ngắn gọn nội dung cốt lõi dựa trên phần Context dưới đây.

---
CONTEXT:
{context}
---
YÊU CẦU:
- Bố cục rõ ràng (dùng gạch đầu dòng).
- Độ dài khoảng 3-5 câu chất lượng.

TÓM TẮT:"""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.2)
        )
        ans = response.text
    except Exception as e:
        ans = f"⚠️ Lỗi tóm tắt: {str(e)}"
        
    return {
        "answer": ans,
        "citations": [],
        "model": model_name
    }


# =============================================================================
# TASK 3.3 — Giải thích thuật ngữ
# =============================================================================

def explain_term(
    term: str,
    retrieved_chunks: List[RetrievedChunk],
    model_name: str = DEFAULT_LLM_MODEL
) -> AnswerDict:
    context = _build_context(retrieved_chunks)
    prompt = f"""Hãy giải thích thuật ngữ: "{term}" dựa trên ngữ cảnh dưới đây.

---
CONTEXT:
{context}
---
YÊU CẦU:
- Định nghĩa dễ hiểu. Nêu ví dụ nếu có trong tài liệu.
- Trích dẫn nguồn [Nguồn N].

GIẢI THÍCH:"""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.0)
        )
        raw_answer = response.text
    except Exception as e:
        raw_answer = f"⚠️ Lỗi tra cứu: {str(e)}"
        
    # 1. Trích xuất trích dẫn để làm nút bấm phía dưới
    citations = _extract_citations(retrieved_chunks, raw_answer)
    
    # 2. Xóa các thẻ [Nguồn X] hoặc [X] ra khỏi văn bản hiển thị cho người dùng
    clean_answer = re.sub(r'\s*\[Nguồn \d+\]|\s*\[\d+\]', '', raw_answer)
    
    return {
        "answer": clean_answer,  # <--- Trả về đoạn văn đã được dọn sạch thẻ
        "citations": citations,
        "model": model_name
    }


# =============================================================================
# GENERATE EMBEDDINGS (Có cơ chế chia lô chống cạn Quota 429)
# =============================================================================

def get_embedding(texts: list, model_name: str = DEFAULT_EMBED_MODEL) -> list:
    all_embeddings = []
    batch_size = 90 
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        try:
            result = genai.embed_content(
                model=model_name,
                content=batch,
                task_type="retrieval_document"
            )
            # Thư viện cũ dùng 'embedding' thay vì 'embeddings'
            all_embeddings.extend(result['embedding'])
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"⏳ Quá tải API Google, đang đợi 60s để reset Quota (Lô {i//batch_size + 1})...")
                time.sleep(60)
                result = genai.embed_content(
                    model=model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                all_embeddings.extend(result['embedding'])
            else:
                raise e
                
    return all_embeddings


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _build_context(
    retrieved_chunks: List[RetrievedChunk],
    max_chars: int = MAX_CONTEXT_CHARS
) -> str:
    context_parts = []
    current_length = 0
    
    for idx, chunk in enumerate(retrieved_chunks):
        source_label = f"[Nguồn {idx + 1}]"
        meta = chunk.get('metadata', {})
        file_name = meta.get('file_name', 'Unknown')
        page_num = meta.get('page', 1)
        content = chunk.get('content', '')
        
        chunk_text = f"--- Khối Ngữ Cảnh {source_label} ---\n"
        chunk_text += f"Nội dung: {content}\n"
        chunk_text += f"Nguồn file: {file_name}, Trang: {page_num}\n\n"
        
        if current_length + len(chunk_text) > max_chars:
            break
            
        context_parts.append(chunk_text)
        current_length += len(chunk_text)
        
    return "".join(context_parts)


def _build_cited_prompt(question: str, context: str) -> str:
    return f"""Bạn là một trợ lý hỏi đáp tài liệu học tập trung thực.
Nhiệm vụ: Hãy trả lời câu hỏi dựa TRÊN ĐÚNG THÔNG TIN TRONG PHẦN NGỮ CẢNH.

---
HƯỚNG DẪN QUAN TRỌNG:
1. TUYỆT ĐỐI KHÔNG dùng kiến thức bên ngoài. Nếu không có thông tin, hãy nói: "Tôi không biết câu trả lời dựa trên tài liệu đã cung cấp."
2. Chèn nhãn trích dẫn [Nguồn X] ở cuối mỗi ý.

NGỮ CẢNH:
{context}

CÂU HỎI:
{question}

TRẢ LỜI:"""


def _extract_citations(retrieved_chunks: List[RetrievedChunk], raw_answer: str) -> List[CitationDict]:
    citations = []
    seen_indices = []
    
    for idx in range(len(retrieved_chunks)):
        source_number = idx + 1
        pattern_1 = f"[Nguồn {source_number}]"
        pattern_2 = f"[{source_number}]"
        
        if (pattern_1 in raw_answer) or (pattern_2 in raw_answer):
            if idx not in seen_indices:
                seen_indices.append(idx)
                
    for i in seen_indices:
        chunk = retrieved_chunks[i]
        content = chunk.get('content', '')
        snippet = content[:100] + "..." if len(content) > 100 else content
        meta = chunk.get('metadata', {})

        citation = {
            "file_name": meta.get('file_name', 'Unknown'),
            "page": meta.get('page', 1),
            "heading": meta.get('heading', ""),
            "snippet": snippet
        }
        citations.append(citation)
        
    return citations