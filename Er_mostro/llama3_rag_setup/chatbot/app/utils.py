import requests
from .config import EDA_SERVICE_URL, ETL_SERVICE_URL

def get_eda_json_from_service(upload_id):
    url = f"{EDA_SERVICE_URL}/eda/run_eda/{upload_id}"
    resp = requests.post(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("eda_json", data)

def upload_file_to_etl(file_bytes, filename, user):
    url = f"{ETL_SERVICE_URL}/upload/"
    files = {"file": (filename, file_bytes)}
    data = {"user": user}
    resp = requests.post(url, files=files, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["upload_id"]