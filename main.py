from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user
from app.api import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service API")


app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Kimlik Doğrulama Servisi Çalışıyor!"}