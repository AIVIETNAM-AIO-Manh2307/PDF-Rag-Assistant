import ollama

PROMPT_TEMPLATE = """Bạn là trợ lý hỏi đáp.
Dùng các đoạn ngữ cảnh dưới đây để trả lời câu hỏi.
Nếu ngữ cảnh không có thông tin, hãy nói là bạn không biết, đừng bịa.
Trả lời ngắn gọn, chính xác, bằng tiếng Việt.

Ngữ cảnh:
{context}

Câu hỏi: {question}
Trả lời:"""

def get_embedding(texts: list, model_name: str = "bge-m3") -> list:
    """
    Gọi API Ollama để chuyển đổi danh sách văn bản thành danh sách vector.
    """
    return ollama.embed(model=model_name, input=texts)["embeddings"]

def generate_answer(question: str, context: str, model_name: str = "vicuna:7b-v1.5-q5_1", temperature: float = 0.0) -> str:
    """
    Gửi prompt chứa ngữ cảnh và câu hỏi đến LLM để nhận câu trả lời.
    """
    formatted_prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    resp = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": formatted_prompt}],
        options={"temperature": temperature}
    )
    return resp["message"]["content"]