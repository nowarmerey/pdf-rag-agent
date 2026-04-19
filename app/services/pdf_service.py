import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(file_path: str) -> str:
    """استخراج النص من PDF"""
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def split_text_into_chunks(text: str, filename: str) -> list[dict]:
    """تقسيم النص إلى chunks مع metadata"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    
    return [
        {
            "text": chunk,
            "metadata": {
                "source": filename,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(chunks)
    ]