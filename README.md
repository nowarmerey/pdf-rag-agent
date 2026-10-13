# ⚖️ LexAI — AI Legal-Document Assistant

> Upload contracts, laws or scans and ask questions about them in German or English.
> A multi-user SaaS built on a **RAG pipeline** (Retrieval-Augmented Generation).

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791)
![Gemini](https://img.shields.io/badge/Google-Gemini-8E75B2)

Part of my portfolio → **[nawarmeree.com](https://nawarmeree.com)**

## ✨ Features

- 📄 **Multi-format ingestion** — PDF (PyMuPDF), Word (`.docx`) and images (`.jpg`, `.png`, `.webp`) read with **Gemini Vision**
- ✂️ **Chunking** with LangChain's `RecursiveCharacterTextSplitter`
- 🧠 **Embeddings** with `gemini-embedding-001` (768 dimensions)
- 🔍 **Semantic search** in **PostgreSQL + pgvector** (Supabase); local ChromaDB fallback for development
- 🤖 **Answers** from Google Gemini, grounded in the retrieved passages
- 👤 **Multi-user**: JWT authentication, every user only sees their own documents and chat history
- 🌍 **Bilingual UI** (German / English) with dark & light mode
- ☁️ **Deployed** on Railway (`Procfile`), database on Supabase

## 🔄 How it works

```
upload ─▶ extract text (PDF / Word / Gemini Vision) ─▶ chunk ─▶ embed (Gemini)
       ─▶ store vectors (pgvector, per user)
question ─▶ embed ─▶ nearest chunks (pgvector) ─▶ Gemini answers with the retrieved context
```

## 🛠️ Tech stack

| Layer      | Technology                                        |
| ---------- | ------------------------------------------------- |
| Backend    | FastAPI · Python 3.11 · SQLAlchemy                |
| Database   | PostgreSQL (Supabase) + **pgvector**              |
| Embeddings | Google `gemini-embedding-001`                     |
| LLM        | Google Gemini (text + vision)                     |
| Parsing    | PyMuPDF · python-docx · LangChain text splitters  |
| Auth       | JWT (python-jose) · passlib/bcrypt                |
| Frontend   | HTML · CSS · vanilla JS (i18n DE/EN)              |
| Hosting    | Railway                                           |

## 🚀 Quick start

```bash
git clone https://github.com/nowarmerey/pdf-rag-agent.git
cd pdf-rag-agent

python -m venv .venv && source .venv/bin/activate   # or conda
pip install -r requirements.txt

cp .env.example .env    # then fill in the values below
python main.py          # → http://localhost:8000
```

## ⚙️ Environment variables

| Variable                      | Purpose                                            |
| ----------------------------- | -------------------------------------------------- |
| `GEMINI_API_KEY`              | Google AI Studio key (embeddings, answers, vision) |
| `DATABASE_URL`                | PostgreSQL with the `pgvector` extension           |
| `SECRET_KEY`                  | JWT signing key                                    |
| `ALGORITHM`                   | JWT algorithm (default `HS256`)                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default `1440`)                    |

## 📁 Project structure

```
pdf-rag-agent/
├── app/
│   ├── api/        # REST endpoints: auth, documents, chat
│   ├── core/       # config, database, security (JWT)
│   ├── models/     # SQLAlchemy models
│   ├── schemas/    # Pydantic schemas
│   └── services/   # pdf_service (extraction), vector_service (pgvector), llm_service (Gemini)
├── static/         # CSS, JS (incl. i18n)
├── templates/      # HTML pages
└── main.py
```

## 👨‍💻 Author

**Nawar Meree** — System Administrator & SaaS Developer · Leverkusen, Germany

- 🌐 [nawarmeree.com](https://nawarmeree.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/nawar-meree-036491164)
- 🐙 [GitHub](https://github.com/nowarmerey)
