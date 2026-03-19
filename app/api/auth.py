from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token,TokenData
from app.crud import user as user_crud
from app.core import security
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])


#KAYIT OLMA
@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Bu emaille daha önce kayıt olunmuş mu
    db_user = user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Bu e-posta adresi zaten kullanımda."
        )
    # Yoksa, yeni kullanıcıyı oluştur
    return user_crud.create_user(db=db, user=user_in)


# GİRİŞ YAPMA
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # NOT: OAuth2 standartlarında email alanı 'username' olarak gelir.
    user = user_crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Hatalı e-posta veya şifre.")

    # Şifreyi doğrula
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Hatalı e-posta veya şifre.")

    # Giriş başarılıysa Token'ları üret
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"

    }
#refresh token
@router.post("/refresh",response_model=Token)
def refresh_token(refresh_token:str,db:Session=Depends(get_db)):
    try:
        # gelen refresh tokeni açıyoruz
        payload=jwt.decode(refresh_token,security.settings.SECRET_KEY,algorithms=[security.settings.ALGORITHM])
        email:str=payload.get("sub")
        if email is None :
            raise HTTPException(status_code=401,detail="geçersiz refresh token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail="Refresh token süresi dolmuş veya geçersiz")
    user=user_crud.get_user_by_email(db,email=email)
    if user is None:
        raise HTTPException(status_code=404,detail="kullanıcı bulunamadı")
    new_access_token= security.create_access_token(data={"sub": user.email})
    new_refresh_token= security.create_refresh_token(data={"sub": user.email})
    return{
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
def get_current_user(db: Session = Depends(get_db),token: str =Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,security.settings.SECRET_KEY,algorithms=[security.settings.ALGORITHM])
        email: str=payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail= "geçersiz token:Email bulunamadı")
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="geçersiz veya süresi dolmuş token")
    user= user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(status_code=404, detail="kullanıcı bulunamadı")
    return user
@router.get("/me", response_model=UserResponse)
def get_me(current_user:UserResponse = Depends(get_current_user)):
    return current_user