from fastapi import FastAPI, HTTPException
from .database import SessionLocal, engine
from .models import Base, EDAResult
from .auto_analysis_pipeline import run_eda_on_file
from .schemas import EDAResultOut

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/eda/run_eda/{upload_id}", response_model=EDAResultOut)
def run_eda(upload_id: int):
    db = SessionLocal()
    # Recupera il file dal DB (usa la logica di ETL/blob_upload)
    # Esegui EDA
    eda_json = run_eda_on_file(upload_id, db)  # da implementare: carica file, esegui describe, ecc.
    # Salva risultato
    eda_result = EDAResult(upload_id=upload_id, eda_json=eda_json)
    db.add(eda_result)
    db.commit()
    db.refresh(eda_result)
    db.close()
    return eda_result

@app.get("/eda/run_eda/{upload_id}", response_model=EDAResultOut)
def get_eda(upload_id: int):
    db = SessionLocal()
    eda_result = db.query(EDAResult).filter_by(upload_id=upload_id).order_by(EDAResult.created_at.desc()).first()
    db.close()
    if not eda_result:
        raise HTTPException(status_code=404, detail="EDA not found")
    return eda_result