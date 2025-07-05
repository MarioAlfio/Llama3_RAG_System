import sys
import os

# Aggiungi il path della cartella etl al Python path
sys.path.append('/app/etl')

from extract import extract
from transform import transform
from load import load
from config import TABLE_NAME, DB_URL

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_etl.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    df = extract(file_path)
    df_t = transform(df)
    load(df_t, TABLE_NAME, DB_URL)
    print(f"ETL completato per {file_path}") 