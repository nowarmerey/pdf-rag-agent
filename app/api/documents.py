from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from app.api.auth import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.pdf_service import extract_text, split_text_into_chunks
from app.services.vector_service import add_chunks_to_db, delete_user_document
from typing import List
import os, shutil

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """رفع ومعالجة الملفات (PDF, Word, Images)"""

    # التحقق من نوع الملف
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported: {', '.join(SUPPORTED_EXTENSIONS.keys())}"
        )

    # التحقق من الحجم
    content      = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"
        )

    # مجلد خاص لكل مستخدم
    user_upload_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    file_path = os.path.join(user_upload_dir, file.filename)

    # حفظ الملف
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # استخراج النص حسب نوع الملف
        text = extract_text(file_path, file.filename)

        if not text.strip():
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from file"
            )

        # تقسيم وحفظ في Vector DB
        chunks       = split_text_into_chunks(text, file.filename)
        chunks_count = add_chunks_to_db(chunks, current_user.id)

        # حفظ في PostgreSQL
        document = Document(
            filename     = file.filename,
            file_size    = round(file_size_mb, 2),
            chunks_count = chunks_count,
            user_id      = current_user.id
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """قائمة ملفات المستخدم"""
    return db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).all()

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف ملف"""
    document = db.query(Document).filter(
        Document.id      == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # حذف من Vector DB
    delete_user_document(document.filename, current_user.id)

    # حذف الملف الفيزيائي
    file_path = os.path.join(UPLOAD_DIR, str(current_user.id), document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # حذف من PostgreSQL
    db.delete(document)
    db.commit()