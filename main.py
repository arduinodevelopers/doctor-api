from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API aktif 🚀"}

@app.get("/doktorlar")
def doktor_listesi():
    return [
        {"id": 1, "ad": "Dr. Ayşe"},
        {"id": 2, "ad": "Dr. Mehmet"}
    ]