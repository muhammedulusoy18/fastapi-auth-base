from pydantic import BaseModel, EmailStr

# Hem kayıt olurken hem de cevap dönerken ortak olan alan
class UserBase(BaseModel):
    email: EmailStr  #gerçekten bir e-posta formunda olup olmadığını denetliyoruz

# Kullanıcı kayıt olurken veya giriş yaparken bize göndereceği veri
class UserCreate(UserBase):
    password: str

# Bizim dışarıya döneceğimiz veri formatı
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # veritabanı modelini Pydantic şemasına  çeviriyoruz