import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import tempfile
import time
import pypdf
from src.data.pdf_processor import extract_text_from_pdf, chunk_text
from src.pipeline.rag_pipeline import RAGPipeline
from src.models.llm_manager import generate_answer
from src.app.state import init_state, reset_state
from src.app.ui_components import (
    clean_html,
    render_header,
    render_empty_state,
    render_processing_state,
    render_doc_info_card,
    render_file_selected_state
)

# ============================================================
# CẤU HÌNH TRANG & NẠP CSS
# ============================================================
st.set_page_config(
    page_title="PDF RAG Chatbot Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nạp file CSS tùy chỉnh
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Khởi tạo Session State
init_state()

# ============================================================
# THANH SIDEBAR
# ============================================================
with st.sidebar:
    # Header Logo
    st.markdown(clean_html("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding: 0 4px;">
        <div style="width: 38px; height: 38px; border-radius: 8px; background-color: var(--primary-container); display: flex; align-items: center; justify-content: center; color: var(--on-primary); font-size: 18px;">
            <span class="material-symbols-outlined" style="font-size: 20px; color: white;">description</span>
        </div>
        <div>
            <h1 style="font-size: 16px; font-weight: 600; color: var(--primary); margin: 0; line-height: 1.2;">PDF RAG Assistant</h1>
            <p style="font-size: 10px; color: var(--on-surface-variant); margin: 0;">Ask questions about your documents</p>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    # Navigation Links (Decorative tabs from design)
    st.markdown(clean_html("""
    <nav style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 20px;">
        <a class="nav-item nav-active" href="#">
            <span class="material-symbols-outlined" style="font-size: 18px;">description</span>
            <span>Documents</span>
        </a>
        <a class="nav-item" href="#">
            <span class="material-symbols-outlined" style="font-size: 18px;">history</span>
            <span>History</span>
        </a>
        <a class="nav-item" href="#">
            <span class="material-symbols-outlined" style="font-size: 18px;">settings</span>
            <span>Settings</span>
        </a>
    </nav>
    """), unsafe_allow_html=True)
    
    st.markdown("<h2 style='font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--on-surface-variant); margin: 0 0 10px 4px;'>Upload Document</h2>", unsafe_allow_html=True)
    
    # Upload File PDF
    if st.session_state.app_state in ["empty", "file_selected"]:
        uploaded_file = st.file_uploader("Chọn file PDF", type="pdf", label_visibility="collapsed")
        if uploaded_file:
            st.session_state.document_name = uploaded_file.name
            size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.session_state.document_size = f"{size_mb:.1f} MB"
            st.session_state.file_bytes = uploaded_file.getvalue()
            st.session_state.app_state = "file_selected"
        else:
            st.session_state.app_state = "empty"
            st.session_state.document_name = None
            st.session_state.document_size = None
            st.session_state.file_bytes = None
            
    # Hiển thị card thông tin tài liệu hiện hành
    if st.session_state.document_name:
        render_doc_info_card(
            st.session_state.document_name, 
            st.session_state.document_size,
            st.session_state.document_pages,
            st.session_state.document_chunks
        )
        
        # Nút xóa tài liệu
        st.markdown('<div class="clear-btn" style="margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("Remove document", key="remove_doc"):
            reset_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Nút bấm "Process Document"
    if st.session_state.app_state == "file_selected":
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        if st.button("Process Document", key="process_doc_btn"):
            st.session_state.app_state = "processing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    elif st.session_state.app_state == "processing":
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        st.button("Processing document...", key="process_doc_disabled", disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Chân trang sidebar
    st.markdown("<div style='margin-top: auto; padding-top: 16px; border-top: 1px solid var(--outline-variant);'>", unsafe_allow_html=True)
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# KHU VỰC CHAT CHÍNH
# ============================================================

# TRẠNG THÁI 1: CHƯA UPLOAD TÀI LIỆU (EMPTY STATE)
if st.session_state.app_state == "empty":
    render_header(app_state="empty")
    render_empty_state()
    st.chat_input("Upload a document to enable chat", disabled=True)

# TRẠNG THÁI 2: ĐÃ CHỌN TÀI LIỆU, CHỜ PROCESS (FILE SELECTED)
elif st.session_state.app_state == "file_selected":
    render_header(st.session_state.document_name, app_state="file_selected")
    render_file_selected_state(st.session_state.document_name)
    st.chat_input("Process the document to start asking questions...", disabled=True)

# TRẠNG THÁI 3: ĐANG XỬ LÝ TÀI LIỆU (PROCESSING STATE)
elif st.session_state.app_state == "processing":
    render_header(st.session_state.document_name, app_state="processing")
    
    step_placeholder = st.empty()
    
    # Bước 1: Reading PDF
    with step_placeholder.container():
        render_processing_state(current_step=1)
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(st.session_state.file_bytes)
        tmp_path = tmp.name
        
    try:
        reader = pypdf.PdfReader(tmp_path)
        st.session_state.document_pages = len(reader.pages)
    except Exception:
        st.session_state.document_pages = 1
        
    raw_text = extract_text_from_pdf(tmp_path)
    os.unlink(tmp_path)
    time.sleep(0.5)
    
    # Bước 2: Splitting chunks
    with step_placeholder.container():
        render_processing_state(current_step=2)
    chunks = chunk_text(raw_text)
    st.session_state.document_chunks = len(chunks)
    time.sleep(0.5)
    
    # Bước 3: Creating embeddings
    with step_placeholder.container():
        render_processing_state(current_step=3)
    
    st.session_state.pipeline = RAGPipeline()
    time.sleep(0.5)
    
    # Bước 4: Building DB
    with step_placeholder.container():
        render_processing_state(current_step=4)
    st.session_state.pipeline.add_documents(chunks)
    time.sleep(0.5)
    
    # Chuyển trạng thái sang Chat hoạt động
    st.session_state.app_state = "active_chat"
    st.rerun()

# TRẠNG THÁI 4: HỘI THOẠI ĐANG HOẠT ĐỘNG (ACTIVE CHAT STATE)
elif st.session_state.app_state == "active_chat":
    render_header(st.session_state.document_name, app_state="active_chat")
    
    # Hiển thị lịch sử chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(clean_html(f'<div class="user-message">{message["content"]}</div>'), unsafe_allow_html=True)
            else:
                st.markdown(clean_html(f"""
                <div class="assistant-message">
                    <div>{message["content"]}</div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(199, 196, 214, 0.3); font-size: 11px; color: var(--on-surface-variant);">
                        <span class="material-symbols-outlined" style="font-size: 14px;">library_books</span> Answer generated from the uploaded document
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
    # Ô nhập câu hỏi
    user_query = st.chat_input("Ask a question about the uploaded document...")
    
    if user_query:
        # Lưu và hiển thị câu hỏi của user ngay lập tức
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(clean_html(f'<div class="user-message">{user_query}</div>'), unsafe_allow_html=True)
            
        # Gọi LLM sinh câu trả lời
        with st.chat_message("assistant"):
            with st.spinner("Generating answer..."):
                # 1. Tìm kiếm context liên quan từ ChromaDB
                relevant_context = st.session_state.pipeline.retrieve(user_query)
                context_str = "\n\n".join(relevant_context)
                
                # 2. Sinh câu trả lời từ LLM với context nhận được
                answer = generate_answer(user_query, context_str)
                
            # Hiển thị câu trả lời của trợ lý
            st.markdown(clean_html(f"""
            <div class="assistant-message">
                <div>{answer}</div>
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(199, 196, 214, 0.3); font-size: 11px; color: var(--on-surface-variant);">
                    <span class="material-symbols-outlined" style="font-size: 14px;">library_books</span> Answer generated from the uploaded document
                </div>
            </div>
            """), unsafe_allow_html=True)
            
        # Lưu câu trả lời vào lịch sử và tải lại trang
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
