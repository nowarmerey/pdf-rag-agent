import os
import uuid
import google.generativeai as genai
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import GEMINI_API_KEY, DATABASE_URL, MAX_SEARCH_RESULTS, COLLECTION_PREFIX
import chromadb

# إعداد Gemini للـ Embeddings (768 dimension)
genai.configure(api_key=GEMINI_API_KEY)

# إعداد ChromaDB كـ fallback محلي
chroma_client = chromadb.PersistentClient(path="chroma_db")

# إعداد PostgreSQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# ═══════════════════════════════════════════
# Embeddings
# ═══════════════════════════════════════════

def _get_embedding(text: str) -> list:
    """توليد embedding بـ 768 dimension"""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=768
    )
    return result["embedding"]

def _get_query_embedding(text: str) -> list:
    """توليد embedding للسؤال"""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_query",
        output_dimensionality=768
    )
    return result["embedding"]

# ═══════════════════════════════════════════
# Vector Operations
# ═══════════════════════════════════════════

def add_chunks_to_db(chunks: list[dict], user_id: int) -> int:
    """إضافة chunks إلى Supabase pgvector"""
    db = SessionLocal()
    try:
        for chunk in chunks:
            embedding = _get_embedding(chunk["text"])
            db.execute(
                text("""
                    INSERT INTO document_chunks 
                    (user_id, filename, content, embedding, chunk_index)
                    VALUES (:user_id, :filename, :content, :embedding, :chunk_index)
                """),
                {
                    "user_id":     user_id,
                    "filename":    chunk["metadata"]["source"],
                    "content":     chunk["text"],
                    "embedding":   str(embedding),
                    "chunk_index": chunk["metadata"]["chunk_index"]
                }
            )
        db.commit()
        return len(chunks)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def search_similar_chunks(query: str, user_id: int,
                          n_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """البحث في ملفات المستخدم"""
    db = SessionLocal()
    try:
        query_embedding = _get_query_embedding(query)
        embedding_str   = str(query_embedding)

        results = db.execute(
            text("""
                SELECT content, filename,
                       1 - (embedding <=> :embedding::vector) as score
                FROM document_chunks
                WHERE user_id = :user_id
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": embedding_str,
                "user_id":   user_id,
                "limit":     n_results
            }
        ).fetchall()

        return [
            {
                "text":   row[0],
                "source": row[1],
                "score":  round(float(row[2]), 3)
            }
            for row in results
        ]
    finally:
        db.close()

def get_user_documents(user_id: int) -> list[str]:
    """قائمة ملفات المستخدم"""
    db = SessionLocal()
    try:
        results = db.execute(
            text("""
                SELECT DISTINCT filename
                FROM document_chunks
                WHERE user_id = :user_id
                ORDER BY filename
            """),
            {"user_id": user_id}
        ).fetchall()
        return [row[0] for row in results]
    finally:
        db.close()

def delete_user_document(filename: str, user_id: int) -> int:
    """حذف ملف من pgvector"""
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                DELETE FROM document_chunks
                WHERE user_id = :user_id
                AND filename = :filename
            """),
            {"user_id": user_id, "filename": filename}
        )
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()