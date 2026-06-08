import pypdf

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Đọc và trích xuất toàn bộ văn bản từ file PDF.
    Xử lý trường hợp trang rỗng bằng cách trả về chuỗi rỗng.
    """




    reader = pypdf.PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, size: int = 1000, overlap: int = 200) -> list:
    """
    Cắt text thành các đoạn nhỏ (chunks) dựa trên số ký tự và độ trùng lặp.
    """



    
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= size:
            cur += p + "\n"
        else:
            if cur:
                chunks.append(cur.strip())
            cur = (cur[-overlap:] + p + "\n") if overlap else (p + "\n")
    if cur.strip():
        chunks.append(cur.strip())
    return chunks