import streamlit as st
import tempfile
import os
from src.data.pdf_processor import extract_text_from_pdf, chunk_text
from src.pipeline.rag_pipeline import RAGPipeline
from src.models.llm_manager import generate_answer

# Khởi tạo trạng thái ứng dụng
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("PDF RAG Chatbot Assistant")

# Giao diện Sidebar hỗ trợ nạp tài liệu
with st.sidebar:
    uploaded_file = st.file_uploader("Chọn file PDF", type="pdf")
    if uploaded_file and st.button("Xử lý tài liệu"):
        with st.spinner("Hệ thống đang phân tích..."):
            # Tạo file tạm thời để trích xuất text
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            raw_text = extract_text_from_pdf(tmp_path)
            os.unlink(tmp_path)  # Giải phóng file tạm
            
            chunks = chunk_text(raw_text)
            
            # Khởi tạo pipeline mới và nạp dữ liệu vào database
            st.session_state.pipeline = RAGPipeline()
            st.session_state.pipeline.add_documents(chunks)
            st.success("Tài liệu đã được xử lý và nạp vào database thành công!")

# Luồng hiển thị và nhập nội dung hội thoại
if st.session_state.pipeline:
    # Hiển thị lịch sử chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    # Ô nhập câu hỏi của người dùng
    if user_query := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        # Tìm kiếm tài liệu và sinh câu trả lời
        relevant_context = st.session_state.pipeline.retrieve(user_query)
        context_str = "\n\n".join(relevant_context)
        answer = generate_answer(user_query, context_str)
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)
else:
    st.info("Vui lòng tải lên và xử lý file PDF ở thanh bên trước khi bắt đầu hỏi đáp.")