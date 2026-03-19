from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


# Kullanıcıyı E-posta Adresinden Bulma
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Yeni Kullanıcı Oluşturma (Kayıt)
def create_user(db: Session, user: UserCreate):
    # Şifreyi açık haliyle değil, hashleyerek (kıyma yaparak) alıyoruz
    hashed_password = get_password_hash(user.password)

    # Veritabanı modelini oluşturuyoruz
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )

    # Veritabanına ekle ve kaydet
    db.add(db_user)
    db.commit()

    # Veritabanındaki son halini (ID vb. atanmış halini) nesneye geri yükle
    db.refresh(db_user)

    return db_user