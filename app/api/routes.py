from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, shutil
from app.core.config import UPLOAD_DIR
from app.services.pdf_service import extract_text_from_pdf, split_text_into_chunks
from app.services.vector_service import (
    add_chunks_to_db, search_similar_chunks,
    get_all_documents, delete_document
)
from app.services.llm_service import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """رفع ومعالجة PDF"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="الملف يجب أن يكون PDF")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # حفظ الملف
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # معالجة PDF
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="الملف لا يحتوي على نص قابل للقراءة")
    
    chunks = split_text_into_chunks(text, file.filename)
    count = add_chunks_to_db(chunks)
    
    return {
        "message": f"تم رفع الملف ومعالجته بنجاح",
        "filename": file.filename,
        "chunks_count": count
    }

@router.post("/query")
async def query_documents(request: QueryRequest):
    """الاستعلام عن المستندات"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="السؤال لا يمكن أن يكون فارغاً")
    
    chunks = search_similar_chunks(request.question, n_results=5)
    result = generate_answer(request.question, chunks)
    
    return result

@router.get("/documents")
async def list_documents():
    """قائمة بالمستندات المرفوعة"""
    docs = get_all_documents()
    return {"documents": docs}

@router.delete("/documents/{filename}")
async def remove_document(filename: str):
    """حذف مستند"""
    count = delete_document(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": f"تم حذف {filename}", "chunks_removed": count}