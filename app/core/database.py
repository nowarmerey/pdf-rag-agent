from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # تحقق من الاتصال قبل كل query
    pool_size=10,             # عدد connections في الـ pool
    max_overflow=20           # connections إضافية عند الحاجة
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """Dependency للحصول على database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()