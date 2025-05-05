from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel # type: ignore
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("POSTGRESQL_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Doktor(Base):
    __tablename__ = "doktorlar"
    id = Column(String, primary_key=True, index=True)
    ad = Column(String)
    soyad = Column(String)
    email = Column(String)
    brans = Column(String)
    universite = Column(String)
    sehir = Column(String)
    profil_foto = Column(Text)
    created_at = Column(DateTime)

class Hasta(Base):
    __tablename__ = "hastalar"
    id = Column(String, primary_key=True, index=True)
    ad = Column(String)
    soyad = Column(String)
    email = Column(String)
    cinsiyet = Column(String)
    dogum_tarihi = Column(String)
    sehir = Column(String)
    profil_foto = Column(Text)
    created_at = Column(DateTime)

class Randevu(Base):
    __tablename__ = "randevular"
    id = Column(Integer, primary_key=True, index=True)
    hasta_id = Column(String, ForeignKey("hastalar.id"))
    doktor_id = Column(String, ForeignKey("doktorlar.id"))
    tarih = Column(String)
    not_ = Column(Text)
    onayli = Column(Boolean, default=False)
    olusturulma = Column(DateTime)

class HastaDosya(Base):
    __tablename__ = "hasta_dosyalari"
    id = Column(Integer, primary_key=True, index=True)
    hasta_id = Column(String, ForeignKey("hastalar.id"))
    dosya_url = Column(Text)
    dosya_adi = Column(String)
    tur = Column(String)
    eklenme_tarihi = Column(DateTime)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sahte veri tabanı
hastalar = []
randevular = []

class Hasta(BaseModel):
    id: int
    ad: str
    soyad: str
    yas: int
    cinsiyet: str
    tani: str

class Randevu(BaseModel):
    hasta_id: str
    doktor_id: str
    tarih: str
    not_: str

@app.get("/")
def root():
    return {"message": "API aktif 🚀"}

@app.get("/doktorlar")
def doktor_listesi():
    return [
        {"id": 1, "ad": "Dr. Ayşe Özmen"},
        {"id": 2, "ad": "Dr. Mehmet Kulaklı"}
    ]

@app.post("/hastalar")
def hasta_ekle(hasta: Hasta):
    yeni_hasta = {
        "id": hasta.id,
        "ad": hasta.ad,
        "soyad": hasta.soyad,
        "yas": hasta.yas,
        "cinsiyet": hasta.cinsiyet,
        "tani": hasta.tani,
        "eklenme_tarihi": datetime.now().isoformat()
    }
    hastalar.append(yeni_hasta)
    return {"message": "Hasta başarıyla eklendi", "hasta": yeni_hasta}

@app.get("/hastalar")
def hasta_listesi():
    return {"toplam": len(hastalar), "veriler": hastalar}

@app.post("/randevular")
def randevu_olustur(randevu: Randevu):
    randevu_kaydi = {
        "hasta_id": randevu.hasta_id,
        "doktor_id": randevu.doktor_id,
        "tarih": randevu.tarih,
        "not": randevu.not_,
        "olusturulma": datetime.now().isoformat(),
        "onayli": False
    }
    randevular.append(randevu_kaydi)
    return {"message": "Randevu oluşturuldu", "randevu": randevu_kaydi}

@app.get("/randevular/{hasta_id}")
def hasta_randevulari(hasta_id: str):
    hasta_randevu_listesi = [r for r in randevular if r["hasta_id"] == hasta_id]
    return {"hasta_id": hasta_id, "randevu_sayisi": len(hasta_randevu_listesi), "randevular": hasta_randevu_listesi}

@app.get("/randevular")
def tum_randevular():
    return {"toplam_randevu": len(randevular), "randevular": randevular}

@app.patch("/randevular")
def randevu_guncelle(payload: dict):
    doktor_id = payload.get("doktor_id")
    hasta_id = payload.get("hasta_id")
    tarih = payload.get("tarih")
    onayli = payload.get("onayli")

    for r in randevular:
        if (
            r["doktor_id"] == doktor_id and
            r["hasta_id"] == hasta_id and
            r["tarih"] == tarih
        ):
            r["onayli"] = onayli
            return {"success": True, "randevu": r}
    raise HTTPException(status_code=404, detail="Randevu bulunamadı")

# File upload support
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {
        "filename": file.filename,
        "url": f"https://doctor-api-production.up.railway.app/uploads/{file.filename}"
    }

# Serve static files from the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")