from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel # type: ignore
from datetime import datetime
from fastapi import HTTPException

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

@app.patch("/randevular/onayla")
def randevu_onayla(payload: dict):
    doktor_id = payload.get("doktor_id")
    hasta_id = payload.get("hasta_id")
    tarih = payload.get("tarih")

    for r in randevular:
        if (
            r["doktor_id"] == doktor_id and
            r["hasta_id"] == hasta_id and
            r["tarih"] == tarih
        ):
            r["onayli"] = True
            return {"message": "Randevu onaylandı", "randevu": r}
    
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