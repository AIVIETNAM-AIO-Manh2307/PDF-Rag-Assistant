"""
=============================================================================
FILE  : main.py  (Streamlit Frontend — Version 2)
TASK  : 4.2 Tái cấu trúc Streamlit — chỉ gọi API, không có logic xử lý
        4.3 Nâng cấp giao diện (Workspace sidebar, Citations highlight)
=============================================================================

Nguyên tắc:
  - File này KHÔNG import trực tiếp bất kỳ module data/model/pipeline nào.
  - Mọi tác vụ đều thông qua requests đến http://localhost:8000
  - Streamlit chỉ làm: Nhận input → Gọi API → Hiển thị kết quả

Chạy:
  # Terminal 1: Start FastAPI backend
  uvicorn src.api.api_server:app --reload --port 8000

  # Terminal 2: Start Streamlit frontend
  streamlit run src/app/main.py
"""

import streamlit as st
import requests
import os

# ============================================================
# CONFIG
# ============================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PDF RAG Chatbot Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nạp CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS — Gọi API 
# ============================================================

def api_get_workspaces():
    """GET /api/workspaces → List[{name, file_count}]"""
    # TODO (Mạnh): Implement
    # try:
    #     r = requests.get(f"{API_BASE_URL}/api/workspaces")
    #     r.raise_for_status()
    #     return r.json()
    # except Exception as e:
    #     st.error(f"Không thể kết nối API: {e}")
    #     return []
    return []   # placeholder


def api_create_workspace(name: str) -> bool:
    """POST /api/workspaces → bool (success)"""
    # TODO (Mạnh): Implement
    return False  # placeholder


def api_upload_pdf(file_bytes: bytes, file_name: str, workspace_name: str) -> dict:
    """POST /api/upload → {file_name, workspace_name, chunk_count, page_count, status}"""
    # TODO (Mạnh): Implement
    return {}  # placeholder


def api_chat(question: str, workspace_name: str, top_k: int = 5) -> dict:
    """POST /api/chat → {answer, citations, model}"""
    # TODO (Mạnh): Implement
    return {"answer": "API chưa được implement", "citations": [], "model": ""}


def api_summarize(workspace_name: str, file_name: str = None) -> dict:
    """POST /api/summarize → {summary, model}"""
    # TODO (Mạnh): Implement
    return {}  # placeholder


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    st.session_state.setdefault("selected_workspace", None)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("app_state", "empty")   # empty | ready | uploading

init_state()


# ============================================================
# SIDEBAR — Quản lý Workspaces (Task 4.3)
# ============================================================

with st.sidebar:
    st.markdown("### 📚 PDF RAG Assistant")
    st.markdown("---")

    # --- Tạo workspace mới ---
    st.markdown("**Workspaces**")
    new_ws_name = st.text_input("Tạo workspace mới", placeholder="vd: Giải Tích")
    if st.button("➕ Tạo", key="create_ws"):
        if new_ws_name.strip():
            # TODO (Mạnh): Gọi api_create_workspace(new_ws_name)
            st.success(f"Đã tạo workspace: {new_ws_name}")
        else:
            st.warning("Vui lòng nhập tên workspace")

    st.markdown("---")

    # --- Chọn workspace ---
    workspaces = api_get_workspaces()   # [{name, file_count}, ...]
    ws_names   = [w["name"] for w in workspaces]

    if ws_names:
        selected = st.selectbox("Chọn Workspace", ws_names, key="ws_select")
        st.session_state.selected_workspace = selected
        st.caption(f"{next(w['file_count'] for w in workspaces if w['name']==selected)} file(s)")
    else:
        st.info("Chưa có workspace. Tạo một cái mới bên trên.")
        st.session_state.selected_workspace = None

    st.markdown("---")

    # --- Upload PDF vào workspace đã chọn ---
    if st.session_state.selected_workspace:
        st.markdown(f"**Upload PDF vào `{st.session_state.selected_workspace}`**")
        uploaded_file = st.file_uploader("Chọn file PDF", type="pdf", label_visibility="collapsed")

        if uploaded_file and st.button("⚡ Xử lý tài liệu", key="process_btn"):
            with st.spinner("Đang xử lý..."):
                result = api_upload_pdf(
                    file_bytes     = uploaded_file.getvalue(),
                    file_name      = uploaded_file.name,
                    workspace_name = st.session_state.selected_workspace
                )
                if result.get("status") == "success":
                    st.success(f"✅ {result['chunk_count']} chunks từ {result['page_count']} trang")
                    st.rerun()
                else:
                    st.error("Upload thất bại, kiểm tra lại API server.")

    st.markdown("---")

    # --- Nút tiện ích ---
    if st.button("🗑️ Xóa lịch sử chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


# ============================================================
# MAIN CHAT AREA (Task 4.3)
# ============================================================

if not st.session_state.selected_workspace:
    # Empty state
    st.markdown("## Chào mừng đến PDF RAG Chatbot 👋")
    st.info("Tạo hoặc chọn một **Workspace** ở thanh bên trái để bắt đầu.")

else:
    workspace = st.session_state.selected_workspace
    st.markdown(f"## 💬 Chat — Workspace: `{workspace}`")

    # Hiển thị lịch sử chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # TODO (Mạnh - Task 4.3): Render Citations nổi bật nếu role == "assistant"
            if msg["role"] == "assistant" and msg.get("citations"):
                with st.expander(f"📎 {len(msg['citations'])} trích dẫn nguồn"):
                    for cite in msg["citations"]:
                        st.markdown(
                            f"- **{cite['file_name']}**, trang {cite['page']}"
                            + (f" — *{cite['heading']}*" if cite.get("heading") else "")
                        )

    # Input câu hỏi
    user_query = st.chat_input(f"Hỏi về tài liệu trong {workspace}...")

    if user_query:
        # Hiển thị câu hỏi
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Gọi API và hiển thị trả lời
        with st.chat_message("assistant"):
            with st.spinner("Đang tìm kiếm và sinh câu trả lời..."):
                result = api_chat(user_query, workspace)

            answer    = result.get("answer", "Lỗi: không nhận được câu trả lời từ API.")
            citations = result.get("citations", [])

            st.markdown(answer)

            # TODO (Mạnh - Task 4.3): Style citations đẹp hơn
            if citations:
                with st.expander(f"📎 {len(citations)} trích dẫn nguồn"):
                    for cite in citations:
                        st.markdown(
                            f"- **{cite['file_name']}**, trang {cite['page']}"
                            + (f" — *{cite['heading']}*" if cite.get("heading") else "")
                        )

        # Lưu vào history
        st.session_state.chat_history.append({
            "role"     : "assistant",
            "content"  : answer,
            "citations": citations
        })
        st.rerun()
