from fastapi import FastAPI, UploadFile, File, HTTPException
from .blob_upload import save_file_blob_to_db, get_uploaded_files_metadata, delete_file_by_id

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    upload_id = save_file_blob_to_db(content, file.filename)
    return {"upload_id": upload_id}

@app.get("/files/")
def list_files():
    return get_uploaded_files_metadata()

@app.delete("/files/{upload_id}")
def delete_file(upload_id: int):
    success = delete_file_by_id(upload_id)
    if success:
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="File non trovato o errore eliminazione")
