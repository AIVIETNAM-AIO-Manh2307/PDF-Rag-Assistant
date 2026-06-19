import streamlit as st

def clean_html(html_str: str) -> str:
    """ Loại bỏ khoảng trắng ở đầu mỗi dòng và nối thành 1 dòng để tránh lỗi Markdown/HTML của Streamlit """
    return " ".join(line.strip() for line in html_str.split("\n") if line.strip())

def render_header(document_name=None, app_state="empty"):
    """
    Hiển thị Header thanh lịch cố định phía trên khung chat chính.
    """
    status_html = ""
    status_text = ""
    status_class = ""
    
    if app_state == "empty":
        status_html = '<div class="w-2 h-2 rounded-full bg-outline" style="background-color: var(--outline);"></div>'
        status_text = "No document"
        subtitle = "Upload a PDF to start asking questions"
    elif app_state == "file_selected":
        status_html = '<div class="w-2 h-2 rounded-full bg-outline" style="background-color: var(--outline);"></div>'
        status_text = "Status: Waiting to process"
        subtitle = "Ready to analyze document"
    elif app_state == "processing":
        status_html = '<div class="w-2 h-2 rounded-full bg-primary pulse" style="background-color: var(--primary-container);"></div>'
        status_text = "Processing"
        subtitle = "Processing document..."
    elif app_state == "active_chat":
        status_html = '<div class="w-2 h-2 rounded-full bg-success" style="background-color: var(--success);"></div>'
        status_text = "Document ready"
        subtitle = f"Answering from: {document_name}" if document_name else "Document ready"
    
    header_html = f"""
    <div class="custom-header flex justify-between items-center w-full">
        <div>
            <h2>Chat with your document</h2>
            <p style="color: var(--on-surface-variant); font-size: 12px; margin: 2px 0 0 0; padding: 0;">{subtitle}</p>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full" style="background-color: var(--surface-container-low); border: 1px solid var(--outline-variant); display: flex; gap: 8px; align-items: center;">
            {status_html}
            <span style="font-size: 11px; font-weight: 500; color: var(--on-surface-variant);">{status_text}</span>
        </div>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

def render_empty_state():
    """
    Hiển thị giao diện chào mừng trống (chưa nạp tài liệu) kèm Grid hướng dẫn.
    """
    top_html = """
    <div style="text-align: center; max-width: 650px; margin: 2rem auto; display: flex; flex-direction: column; align-items: center;">
        <div class="empty-illustration">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAmjSY3ErO2-XlxSaHcCkm0VBkmEyactSrzxev8v-hZj0NadCiaad7w7NeKl9CRz-rcFq0rjQqyLj3vKrxpuZThK_VhfOD33NRiQpWBfMxKItgtG_YpPb9ptXi9Wm3Z-LT410hERd0WzYo5vE4SyUPYhNrC-QIS34VxixYdUl5G_dUoRjgvOo97HUzfzENF3VR7zX3j0-Rrk3XBMtlyMx0Uaa4p8I3yqJfjVtu1Qv8rhyxnfoJ6Aehx6qyGL-1qSGQAO85SinQpdpao" 
                 style="width: 100%; height: 100%; object-fit: contain; filter: drop-shadow(0px 8px 24px rgba(29, 41, 57, 0.08)); border-radius: 16px;" />
        </div>
        <h3 style="font-size: 24px; font-weight: 600; color: var(--on-surface); margin-bottom: 8px; letter-spacing: -0.02em;">Ask questions about any PDF</h3>
        <p style="font-size: 15px; color: var(--on-surface-variant); line-height: 1.6; margin-bottom: 2rem; max-width: 500px; margin-left: auto; margin-right: auto;">
            Upload a document and the AI assistant will answer based only on its content. Perfect for fast analysis, summarizing, and data extraction.
        </p>
    </div>
    """
    st.markdown(clean_html(top_html), unsafe_allow_html=True)
    
    # Render steps horizontally using native Streamlit columns
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(clean_html("""
        <div class="bento-card" style="text-align: left; height: 100%;">
            <div class="bento-badge">1</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-bottom: 4px;">Upload PDF</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">Use the sidebar to drag & drop or select your file.</p>
        </div>
        """), unsafe_allow_html=True)
    with c2:
        st.markdown(clean_html("""
        <div class="bento-card" style="text-align: left; height: 100%;">
            <div class="bento-badge">2</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-bottom: 4px;">Process document</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">Click process to let the AI analyze the content securely.</p>
        </div>
        """), unsafe_allow_html=True)
    with c3:
        st.markdown(clean_html("""
        <div class="bento-card" style="text-align: left; height: 100%;">
            <div class="bento-badge">3</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-bottom: 4px;">Start chatting</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">Ask questions and get answers cited directly from the text.</p>
        </div>
        """), unsafe_allow_html=True)


def render_processing_state(current_step=1):
    """
    Hiển thị giao diện 4 bước phân tích tài liệu động.
    Steps:
    1: Reading PDF
    2: Splitting into chunks
    3: Creating embeddings
    4: Building vector database
    """
    
    def get_step_class_and_icon(step_num):
        if current_step > step_num:
            # Done
            circle_class = "step-success"
            circle_content = "✓"
            desc_text = "Hoàn thành"
        elif current_step == step_num:
            # Active
            circle_class = "step-active"
            circle_content = '<span class="spin" style="display: inline-block;">↻</span>'
            desc_text = "Đang xử lý..."
        else:
            # Pending
            circle_class = "step-pending"
            circle_content = str(step_num)
            desc_text = "Đang chờ..."
        return circle_class, circle_content, desc_text

    c1, icon1, text1 = get_step_class_and_icon(1)
    c2, icon2, text2 = get_step_class_and_icon(2)
    c3, icon3, text3 = get_step_class_and_icon(3)
    c4, icon4, text4 = get_step_class_and_icon(4)
    
    processing_html = f"""
    <div class="step-container">
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="width: 48px; height: 48px; border-radius: 12px; background-color: var(--surface-container-low); display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 1px solid var(--outline-variant);">
                <span class="spin" style="font-size: 20px; color: var(--primary); display: inline-block;">⌛</span>
            </div>
            <h3 style="font-size: 18px; font-weight: 600; color: var(--on-surface); margin: 0 0 4px 0;">Analyzing Document</h3>
            <p style="font-size: 13px; color: var(--on-surface-variant); margin: 0;">Extracting knowledge and preparing vector database.</p>
        </div>
        
        <div>
            <!-- Step 1 -->
            <div class="step-item">
                <div class="step-circle {c1}">{icon1}</div>
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin: 0;">Reading PDF</h4>
                    <p style="font-size: 12px; color: var(--on-surface-variant); margin: 2px 0 0 0;">{text1 if current_step != 1 else "Đọc nội dung văn bản từ tệp PDF"}</p>
                </div>
            </div>
            
            <!-- Step 2 -->
            <div class="step-item">
                <div class="step-circle {c2}">{icon2}</div>
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin: 0;">Splitting into chunks</h4>
                    <p style="font-size: 12px; color: var(--on-surface-variant); margin: 2px 0 0 0;">{text2 if current_step != 2 else "Chia nhỏ văn bản thành các đoạn tối ưu"}</p>
                </div>
            </div>
            
            <!-- Step 3 -->
            <div class="step-item">
                <div class="step-circle {c3}">{icon3}</div>
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin: 0;">Creating embeddings</h4>
                    <p style="font-size: 12px; color: var(--on-surface-variant); margin: 2px 0 0 0;">{text3 if current_step != 3 else "Chuyển đổi văn bản thành vector bằng bge-m3"}</p>
                </div>
            </div>
            
            <!-- Step 4 -->
            <div class="step-item">
                <div class="step-circle {c4}">{icon4}</div>
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin: 0;">Building vector database</h4>
                    <p style="font-size: 12px; color: var(--on-surface-variant); margin: 2px 0 0 0;">{text4 if current_step != 4 else "Lưu trữ chỉ mục tìm kiếm vào database in-memory"}</p>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(processing_html), unsafe_allow_html=True)

def render_doc_info_card(name, size="--", pages=0, chunks=0):
    """
    Vẽ Card hiển thị thông tin tài liệu hiện hành trong Sidebar.
    """
    card_html = f"""
    <div class="doc-card" style="margin-top: 10px;">
        <div class="doc-card-highlight"></div>
        <div style="display: flex; align-items: start; gap: 10px;">
            <div style="width: 32px; height: 32px; border-radius: 6px; background-color: var(--surface-container-low); display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 16px; border: 1px solid var(--outline-variant); flex-shrink: 0;">
                📄
            </div>
            <div style="min-w-0; flex-grow: 1;">
                <h4 style="font-size: 13px; font-weight: 600; color: var(--on-surface); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{name}">{name}</h4>
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 4px;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background-color: var(--success); display: inline-block;"></span>
                    <span style="font-size: 11px; color: var(--on-surface-variant);">{size}</span>
                </div>
            </div>
        </div>
        
        <div class="doc-grid">
            <div style="text-align: left;">
                <span style="display: block; font-size: 10px; color: var(--on-surface-variant); text-transform: uppercase; letter-spacing: 0.02em;">Pages</span>
                <span style="font-size: 13px; font-weight: 600; color: var(--on-surface);">{pages if pages > 0 else "--"}</span>
            </div>
            <div style="text-align: left;">
                <span style="display: block; font-size: 10px; color: var(--on-surface-variant); text-transform: uppercase; letter-spacing: 0.02em;">Chunks</span>
                <span style="font-size: 13px; font-weight: 600; color: var(--on-surface);">{chunks if chunks > 0 else "--"}</span>
            </div>
        </div>
        
        <div style="margin-top: 10px; display: flex; align-items: center; gap: 6px; padding: 6px 8px; border-radius: 4px; background-color: rgba(34, 160, 107, 0.05); border: 1px solid rgba(34, 160, 107, 0.1); font-size: 11px; color: var(--success);">
            ✓ Document indexed successfully
        </div>
    </div>
    """
    st.markdown(clean_html(card_html), unsafe_allow_html=True)

def render_file_selected_state(name):
    """
    Hiển thị giao diện khi tài liệu đã được chọn nhưng chưa bấm Process.
    """
    top_html = f"""
    <div style="text-align: center; max-width: 650px; margin: 2rem auto; display: flex; flex-direction: column; align-items: center;">
        <div style="margin-bottom: 24px; width: 140px; height: 140px; background-color: var(--surface-container-low); display: flex; align-items: center; justify-content: center; border: 2px dashed var(--outline-variant); border-radius: 50%; position: relative;">
            <span style="font-size: 60px; color: var(--outline-variant);">✨</span>
        </div>
        
        <h3 style="font-size: 24px; font-weight: 600; color: var(--on-surface); margin-bottom: 8px;">Awaiting Processing</h3>
        <p style="font-size: 15px; color: var(--on-surface-variant); line-height: 1.6; margin-bottom: 2rem; max-width: 500px; margin-left: auto; margin-right: auto;">
            You have selected <b>{name}</b>. Click 'Process Document' in the sidebar to analyze it and begin your conversation.
        </p>
    </div>
    """
    st.markdown(clean_html(top_html), unsafe_allow_html=True)
    
    # Render steps horizontally using native Streamlit columns
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(clean_html(f"""
        <div style="background-color: var(--surface-container-lowest); padding: 16px; border-radius: 12px; border: 1px solid var(--outline-variant); text-align: left; position: relative; height: 100%;">
            <div style="position: absolute; top: -10px; left: -10px; width: 24px; height: 24px; border-radius: 50%; background-color: var(--success); color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; box-shadow: 0px 2px 4px rgba(0,0,0,0.1);">1</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-top: 8px; margin-bottom: 4px;">Selected</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">{name} is ready in the queue.</p>
        </div>
        """), unsafe_allow_html=True)
    with c2:
        st.markdown(clean_html("""
        <div style="background-color: var(--surface-container-lowest); padding: 16px; border-radius: 12px; border: 2px dashed var(--primary-container); text-align: left; position: relative; height: 100%;">
            <div style="position: absolute; top: -10px; left: -10px; width: 24px; height: 24px; border-radius: 50%; background-color: var(--primary-container); color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; box-shadow: 0px 2px 4px rgba(0,0,0,0.1);">2</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--primary-container); margin-top: 8px; margin-bottom: 4px;">Process</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">Click process to extract text and generate embeddings.</p>
        </div>
        """), unsafe_allow_html=True)
    with c3:
        st.markdown(clean_html("""
        <div style="background-color: var(--surface-container-lowest); padding: 16px; border-radius: 12px; border: 1px solid var(--outline-variant); text-align: left; position: relative; opacity: 0.5; height: 100%;">
            <div style="position: absolute; top: -10px; left: -10px; width: 24px; height: 24px; border-radius: 50%; background-color: var(--outline-variant); color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600;">3</div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-top: 8px; margin-bottom: 4px;">Chat</h4>
            <p style="font-size: 12px; color: var(--on-surface-variant); margin: 0; line-height: 1.4;">Ask questions and get answers cited from your PDF.</p>
        </div>
        """), unsafe_allow_html=True)
