from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import APP_NAME, APP_VERSION, UPLOAD_DIR, CHROMA_DIR
from app.core.database import engine, Base
from app.api import auth, documents, chat
import os

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# إنشاء المجلدات
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# ═══════════════════════════════
# إنشاء التطبيق
# ═══════════════════════════════
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ═══════════════════════════════
# No Cache Middleware
# ═══════════════════════════════
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "/static/" in str(request.url.path):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response

app.add_middleware(NoCacheMiddleware)

# ═══════════════════════════════
# Static & Templates
# ═══════════════════════════════
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ═══════════════════════════════
# API Routes
# ═══════════════════════════════
app.include_router(auth.router,      prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router,      prefix="/api")

# ═══════════════════════════════
# Pages
# ═══════════════════════════════
@app.get('/favicon.ico')
async def favicon():
    return FileResponse('static/favicon.ico')

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)