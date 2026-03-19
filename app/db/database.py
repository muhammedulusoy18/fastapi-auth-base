from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Veritabanı motorunu oluşturuluyor
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# Veritabanı ile işlem yaptığımızda açılacak oturum
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Veritabanı tablolarımızın ana sınıfı
Base = declarative_base()

# Her api isteğinde veritabanı bağlantısı açıp işlem bitince kapatacak fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()