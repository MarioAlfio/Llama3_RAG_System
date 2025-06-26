import os

# Path di default per i dati
DATA_PATH = os.getenv("DATA_PATH", "/app/data/")

# Database connection string
DB_USER = os.getenv("DB_USER", "raguser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ragpass")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ragdb")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Nome tabella di default
TABLE_NAME = os.getenv("TABLE_NAME", "raw_upload") 