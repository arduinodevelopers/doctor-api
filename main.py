from fastapi import FastAPI
from fastapi import File, UploadFile
import os
from pydantic import BaseModel # type: ignore
from datetime import datetime

app = FastAPI()

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
    hasta_id: int
    doktor_id: int
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
        "olusturulma": datetime.now().isoformat()
    }
    randevular.append(randevu_kaydi)
    return {"message": "Randevu oluşturuldu", "randevu": randevu_kaydi}

@app.get("/randevular/{hasta_id}")
def hasta_randevulari(hasta_id: int):
    hasta_randevu_listesi = [r for r in randevular if r["hasta_id"] == hasta_id]
    return {"hasta_id": hasta_id, "randevu_sayisi": len(hasta_randevu_listesi), "randevular": hasta_randevu_listesi}

@app.get("/randevular")
def tum_randevular():
    return {"toplam_randevu": len(randevular), "randevular": randevular}


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