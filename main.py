from fastapi import FastAPI
from pydantic import BaseModel

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
        {"id": 1, "ad": "Dr. Ayşe"},
        {"id": 2, "ad": "Dr. Mehmet"}
    ]

@app.post("/hastalar")
def hasta_ekle(hasta: Hasta):
    hastalar.append(hasta)
    return {"message": "Hasta eklendi", "hasta": hasta}

@app.get("/hastalar")
def hasta_listesi():
    return hastalar