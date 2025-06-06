from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel # type: ignore
from datetime import datetime
from fastapi import HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
DATABASE_URL = os.getenv("POSTGRESQL_URL", "sqlite:///./test.db")
print("Veritabanı bağlantısı:", repr(DATABASE_URL))

engine = create_engine(DATABASE_URL)
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
    adres = Column(String)
    tc_kimlik_no = Column(String)
    kan_grubu = Column(String)
    ilaclar = Column(Text)
    not_ = Column(Text)
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


class YeniHastaKayit(BaseModel):
    id: str
    ad: str
    soyad: str
    email: str
    cinsiyet: str
    dogum_tarihi: str
    sehir: str
    adres: str
    tc_kimlik_no: str
    kan_grubu: str
    ilaclar: str
    not_: str

class RandevuCreate(BaseModel):
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


@app.post("/hasta_kayit")
def hasta_kayit(hasta: YeniHastaKayit, db: Session = Depends(get_db)):
    db_hasta = db.query(Hasta).filter(Hasta.id == hasta.id).first()
    if db_hasta:
        raise HTTPException(status_code=400, detail="Hasta zaten mevcut")
    yeni_hasta = Hasta(
        id=hasta.id,
        ad=hasta.ad,
        soyad=hasta.soyad,
        email=hasta.email,
        cinsiyet=hasta.cinsiyet,
        dogum_tarihi=hasta.dogum_tarihi,
        sehir=hasta.sehir,
        adres=hasta.adres,
        tc_kimlik_no=hasta.tc_kimlik_no,
        kan_grubu=hasta.kan_grubu,
        ilaclar=hasta.ilaclar,
        not_=hasta.not_,
        created_at=datetime.now()
    )
    db.add(yeni_hasta)
    db.commit()
    db.refresh(yeni_hasta)
    return {"message": "Hasta başarıyla kaydedildi", "hasta_id": yeni_hasta.id}

@app.get("/hastalar")
def hasta_listesi(db: Session = Depends(get_db)):
    hastalar = db.query(Hasta).all()
    result = []
    for h in hastalar:
        result.append({
            "id": h.id,
            "ad": h.ad,
            "soyad": h.soyad,
            "email": h.email,
            "cinsiyet": h.cinsiyet,
            "dogum_tarihi": h.dogum_tarihi,
            "sehir": h.sehir,
            "created_at": h.created_at.isoformat() if h.created_at else None
        })
    return {"toplam": len(result), "veriler": result}

@app.post("/randevular")
def randevu_olustur(randevu: RandevuCreate, db: Session = Depends(get_db)):
    yeni_randevu = Randevu(
        hasta_id=randevu.hasta_id,
        doktor_id=randevu.doktor_id,
        tarih=randevu.tarih,
        not_=randevu.not_,
        olusturulma=datetime.now(),
        onayli=False
    )
    db.add(yeni_randevu)
    db.commit()
    db.refresh(yeni_randevu)
    return {"message": "Randevu oluşturuldu", "randevu": {
        "id": yeni_randevu.id,
        "hasta_id": yeni_randevu.hasta_id,
        "doktor_id": yeni_randevu.doktor_id,
        "tarih": yeni_randevu.tarih,
        "not": yeni_randevu.not_,
        "olusturulma": yeni_randevu.olusturulma.isoformat(),
        "onayli": yeni_randevu.onayli
    }}

@app.get("/randevular/{hasta_id}")
def hasta_randevulari(hasta_id: str, db: Session = Depends(get_db)):
    randevular = db.query(Randevu).filter(Randevu.hasta_id == hasta_id).all()
    result = []
    for r in randevular:
        result.append({
            "id": r.id,
            "hasta_id": r.hasta_id,
            "doktor_id": r.doktor_id,
            "tarih": r.tarih,
            "not": r.not_,
            "onayli": r.onayli,
            "olusturulma": r.olusturulma.isoformat() if r.olusturulma else None
        })
    return {"hasta_id": hasta_id, "randevu_sayisi": len(result), "randevular": result}

@app.get("/randevular")
def tum_randevular(db: Session = Depends(get_db)):
    randevular = db.query(Randevu).all()
    result = []
    for r in randevular:
        result.append({
            "id": r.id,
            "hasta_id": r.hasta_id,
            "doktor_id": r.doktor_id,
            "tarih": r.tarih,
            "not": r.not_,
            "onayli": r.onayli,
            "olusturulma": r.olusturulma.isoformat() if r.olusturulma else None
        })
    return {"toplam_randevu": len(result), "randevular": result}

@app.patch("/randevular")
def randevu_guncelle(payload: dict, db: Session = Depends(get_db)):
    doktor_id = payload.get("doktor_id")
    hasta_id = payload.get("hasta_id")
    tarih = payload.get("tarih")
    onayli = payload.get("onayli")

    r = db.query(Randevu).filter(
        Randevu.doktor_id == doktor_id,
        Randevu.hasta_id == hasta_id,
        Randevu.tarih == tarih
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    r.onayli = onayli
    db.commit()
    db.refresh(r)
    return {"success": True, "randevu": {
        "id": r.id,
        "hasta_id": r.hasta_id,
        "doktor_id": r.doktor_id,
        "tarih": r.tarih,
        "not": r.not_,
        "onayli": r.onayli,
        "olusturulma": r.olusturulma.isoformat() if r.olusturulma else None
    }}

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


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/hasta_kayit")
def hasta_kayit(hasta: YeniHastaKayit, db: Session = Depends(get_db)):
    db_hasta = db.query(Hasta).filter(Hasta.id == hasta.id).first()
    if db_hasta:
        raise HTTPException(status_code=400, detail="Hasta zaten mevcut")
    yeni_hasta = Hasta(
        id=hasta.id,
        ad=hasta.ad,
        soyad=hasta.soyad,
        email=hasta.email,
        cinsiyet=hasta.cinsiyet,
        dogum_tarihi=hasta.dogum_tarihi,
        sehir=hasta.sehir,
        adres=hasta.adres,
        tc_kimlik_no=hasta.tc_kimlik_no,
        kan_grubu=hasta.kan_grubu,
        ilaclar=hasta.ilaclar,
        not_=hasta.not_,
        created_at=datetime.now()
    )
    db.add(yeni_hasta)
    db.commit()
    db.refresh(yeni_hasta)
    return {"message": "Hasta başarıyla kaydedildi", "hasta_id": yeni_hasta.id}