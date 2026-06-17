import streamlit as st

def init_state():
    """ Khởi tạo tất cả các giá trị trạng thái cần thiết nếu chưa tồn tại """
    st.session_state.setdefault("pipeline", None)          # Instance RAGPipeline
    st.session_state.setdefault("chat_history", [])         # Lịch sử hội thoại
    st.session_state.setdefault("document_name", None)      # Tên file PDF
    st.session_state.setdefault("document_size", None)      # Dung lượng file PDF (MB)
    st.session_state.setdefault("document_pages", 0)        # Số trang tài liệu
    st.session_state.setdefault("document_chunks", 0)       # Số lượng chunk văn bản
    st.session_state.setdefault("app_state", "empty")       # Trạng thái UI: "empty", "file_selected", "processing", "active_chat"

def reset_state():
    """ Xóa toàn bộ trạng thái và quay về màn hình ban đầu """
    st.session_state.pipeline = None
    st.session_state.chat_history = []
    st.session_state.document_name = None
    st.session_state.document_size = None
    st.session_state.document_pages = 0
    st.session_state.document_chunks = 0
    st.session_state.app_state = "empty"
