# ⚖️ LexAI - Legal Document Assistant

> AI-powered legal document analysis platform for law firms and legal professionals.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Overview

LexAI allows legal professionals to upload PDF documents and ask questions
about them in German or English. The AI analyzes contracts, laws, and legal
documents with precision.

## ✨ Features

- 📄 PDF upload and intelligent text extraction
- 🔍 Semantic search using Vector Database (ChromaDB)
- 🤖 AI-powered legal analysis (Google Gemini)
- 👤 Multi-user system with JWT authentication
- 💬 Chat history per user
- 🌍 Bilingual interface (German / English)
- 🔒 Secure - each user sees only their documents

## 🛠️ Tech Stack

| Layer      | Technology              |
| ---------- | ----------------------- |
| Backend    | FastAPI + Python 3.11   |
| Database   | PostgreSQL (Supabase)   |
| Vector DB  | ChromaDB                |
| Embeddings | Sentence Transformers   |
| LLM        | Google Gemini           |
| Auth       | JWT (python-jose)       |
| Frontend   | HTML + CSS + Vanilla JS |

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/pdf-rag-agent.git
cd pdf-rag-agent
```

### 2. Create environment

```bash
conda create -n rag-agent python=3.11
conda activate rag-agent
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your keys
```

### 4. Run the application

```bash
python main.py
```

Open http://localhost:8000

## ⚙️ Environment Variables

Create a `.env` file with the following:
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

## 📁 Project Structure

pdf-rag-agent/
├── app/
│ ├── api/ # API endpoints
│ ├── core/ # Config, Database, Security
│ ├── models/ # SQLAlchemy models
│ ├── schemas/ # Pydantic schemas
│ └── services/ # Business logic
├── static/ # CSS, JS
├── templates/ # HTML templates
└── main.py

## 👨‍💻 Author

**Nawar Meree** - Full Stack Developer

- GitHub: [@nowarmerey](https://github.com/nowarmerey)
- LinkedIn: [nawar-meree-036491164](https://linkedin.com/in/nawar-meree-036491164)
