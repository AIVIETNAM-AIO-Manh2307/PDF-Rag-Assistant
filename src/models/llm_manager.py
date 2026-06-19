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

def get_embedding(texts: list, model_name: str = "bge-m3") -> list:
    """
    Gọi API Ollama để chuyển đổi danh sách văn bản thành danh sách vector.
    
    Args: 
        text (List): List văn bản cần vector hóa
        model_name (str): Tên mô hình embedding chạy trên Ollama (mặc định: "bge-m3")
        
    Return:
        List: list vector
    """
    embeddings = [] 
    for text in texts:
        respone =  ollama.embeddings(
            model = model_name,
            prompt = text
        )
        embeddings.append(respone["embedding"])
    
    return embeddings

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