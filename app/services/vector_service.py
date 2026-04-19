import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import CHROMA_DIR, COLLECTION_PREFIX, MAX_SEARCH_RESULTS
import uuid

# تحميل النموذج مرة واحدة عند بدء التشغيل
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# إعداد ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)

def _get_user_collection(user_id: int):
    """كل مستخدم عنده collection منفصلة - Multi-tenant"""
    collection_name = f"{COLLECTION_PREFIX}_{user_id}_documents"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks_to_db(chunks: list[dict], user_id: int) -> int:
    """إضافة chunks إلى Vector DB الخاص بالمستخدم"""
    collection = _get_user_collection(user_id)
    texts     = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids       = [str(uuid.uuid4()) for _ in chunks]

    embeddings = embedding_model.encode(texts).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)

def search_similar_chunks(query: str, user_id: int,
                          n_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """البحث في ملفات المستخدم فقط"""
    collection = _get_user_collection(user_id)

    # تحقق إن في documents أصلاً
    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
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
    """قائمة ملفات المستخدم فقط"""
    collection = _get_user_collection(user_id)
    results = collection.get(include=["metadatas"])
    if not results["metadatas"]:
        return []
    return list(set(m["source"] for m in results["metadatas"]))

def delete_user_document(filename: str, user_id: int) -> int:
    """حذف ملف من Vector DB الخاص بالمستخدم"""
    collection = _get_user_collection(user_id)
    results = collection.get(
        where={"source": filename},
        include=["metadatas"]
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
    return len(results["ids"])