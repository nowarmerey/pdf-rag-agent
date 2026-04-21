from dotenv import load_dotenv
import os
import secrets

load_dotenv()

# ═══════════════════════════════
# Application Settings
# ═══════════════════════════════
APP_NAME    = "LexAI"
APP_VERSION = "1.0.0"
DEBUG       = os.getenv("DEBUG", "False").lower() == "true"

# ═══════════════════════════════
# AI Settings
# ═══════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

# ═══════════════════════════════
# Database Settings
# ═══════════════════════════════
DATABASE_URL = os.getenv("DATABASE_URL")

# ═══════════════════════════════
# Security Settings
# ═══════════════════════════════
SECRET_KEY                  = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM                   = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# ═══════════════════════════════
# Files Settings
# ═══════════════════════════════
UPLOAD_DIR      = "uploads"
CHROMA_DIR      = "chroma_db"
COLLECTION_PREFIX = "user"
CHUNK_SIZE      = 1000
CHUNK_OVERLAP   = 200
MAX_SEARCH_RESULTS = 5
MAX_FILE_SIZE_MB   = 50

# ═══════════════════════════════
# Supported File Types
# ═══════════════════════════════
SUPPORTED_EXTENSIONS = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc":  "application/msword",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".webp": "image/webp"
}

# ═══════════════════════════════
# Legal AI Settings
# ═══════════════════════════════
SUPPORTED_LANGUAGES = ["de", "en"]
DEFAULT_LANGUAGE    = "de"