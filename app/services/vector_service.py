import chromadb
import google.generativeai as genai
from app.core.config import CHROMA_DIR, COLLECTION_PREFIX, MAX_SEARCH_RESULTS, GEMINI_API_KEY
import uuid

# إعداد Gemini للـ Embeddings
genai.configure(api_key=GEMINI_API_KEY)

# إعداد ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)

def _get_embedding(text: str) -> list:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]

def _get_query_embedding(text: str) -> list:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_query"
    )
    return result["embedding"]

def _get_user_collection(user_id: int):
    """كل مستخدم عنده collection منفصلة"""
    collection_name = f"{COLLECTION_PREFIX}_{user_id}_documents"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks_to_db(chunks: list[dict], user_id: int) -> int:
    """إضافة chunks إلى Vector DB"""
    collection = _get_user_collection(user_id)
    texts     = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids       = [str(uuid.uuid4()) for _ in chunks]

    embeddings = [_get_embedding(text) for text in texts]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)

def search_similar_chunks(query: str, user_id: int,
                          n_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """البحث في ملفات المستخدم"""
    collection = _get_user_collection(user_id)

    if collection.count() == 0:
        return []

    query_embedding = _get_query_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "source": results["metadatas"][0][i]["source"],
            "score": round(1 - results["distances"][0][i], 3)
        })
    return chunks

def get_user_documents(user_id: int) -> list[str]:
    """قائمة ملفات المستخدم"""
    collection = _get_user_collection(user_id)
    results = collection.get(include=["metadatas"])
    if not results["metadatas"]:
        return []
    return list(set(m["source"] for m in results["metadatas"]))

def delete_user_document(filename: str, user_id: int) -> int:
    """حذف ملف من Vector DB"""
    collection = _get_user_collection(user_id)
    results = collection.get(
        where={"source": filename},
        include=["metadatas"]
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
    return len(results["ids"])