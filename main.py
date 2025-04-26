from fastapi import FastAPI
from pydantic import BaseModel # type: ignore
from datetime import datetime

app = FastAPI()

# Sahte veri tabanı
hastalar = []

class Hasta(BaseModel):
    id: int
    ad: str
    soyad: str
    yas: int
    cinsiyet: str
    tani: str

@app.get("/")
def root():
    return {"message": "API aktif 🚀"}

@app.get("/doktorlar")
def doktor_listesi():
    return [
        {"id": 1, "ad": "Dr. ayse ozmen"},
        {"id": 2, "ad": "Dr. Mehmet kulakli"}
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

class Randevu(BaseModel):
    hasta_id: int
    doktor_id: int
    tarih: str  # ISO 8601 format
    aciklama: str

randevular = []

@app.post("/randevu")
def randevu_olustur(randevu: Randevu):
    randevu_kaydi = {
        "hasta_id": randevu.hasta_id,
        "doktor_id": randevu.doktor_id,
        "tarih": randevu.tarih,
        "aciklama": randevu.aciklama,
        "olusturulma": datetime.now().isoformat()
    }
    randevular.append(randevu_kaydi)
    return {"message": "Randevu oluşturuldu", "randevu": randevu_kaydi}

@app.get("/randevular/{hasta_id}")
def hasta_randevulari(hasta_id: int):
    hasta_randevular = [r for r in randevular if r["hasta_id"] == hasta_id]
    return {"hasta_id": hasta_id, "randevu_sayisi": len(hasta_randevular), "randevular": hasta_randevular}

@app.get("/randevular")
def tum_randevular():
    return {"toplam_randevu": len(randevular), "randevular": randevular}