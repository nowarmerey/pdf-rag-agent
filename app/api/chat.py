from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, SessionResponse
from app.services.vector_service import search_similar_chunks
from app.services.llm_service import generate_legal_answer
from typing import List
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إرسال سؤال والحصول على إجابة"""

    # إنشاء session جديد إذا ما في
    if not request.session_id:
        session = ChatSession(
            title=request.question[:50],
            user_id=current_user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )

    # البحث في Vector DB
    language = request.language or current_user.language
    chunks   = search_similar_chunks(request.question, current_user.id)
    result   = generate_legal_answer(request.question, chunks, language)

    # حفظ السؤال
    user_msg = ChatMessage(
        role="user",
        content=request.question,
        session_id=session.id
    )
    db.add(user_msg)

    # حفظ الإجابة
    assistant_msg = ChatMessage(
        role="assistant",
        content=result["answer"],
        sources=json.dumps(result["sources"]),
        session_id=session.id
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session.id
    )

@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """قائمة جلسات الدردشة"""
    return db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تفاصيل جلسة محددة"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف جلسة"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    db.delete(session)
    db.commit()