import pandas as pd
from sqlalchemy import create_engine, text
import logging
import os
from datetime import datetime

# Configurazione logging avanzato
logger = logging.getLogger("etl.load")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
if not os.path.exists("../logs"):
    os.makedirs("../logs")
fh = logging.FileHandler("../logs/load.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

def load(df, table_name, db_url, file_metadata=None):
    logger.info(f"Loading data into table {table_name}")
    engine = create_engine(db_url)
    
    # Carica i dati nella tabella principale
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    logger.info(f"Loaded {len(df)} rows into {table_name}")
    
    # Crea tabella metadati se non esiste
    try:
        with engine.connect() as conn:
            # Crea la tabella file_metadata
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    table_name VARCHAR(255) NOT NULL,
                    rows_count INTEGER NOT NULL,
                    columns_count INTEGER NOT NULL,
                    file_size_kb FLOAT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type VARCHAR(10),
                    description TEXT
                );
            """))
            conn.commit()
            logger.info("File metadata table created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating file_metadata table: {e}")
        # Se non riesce a creare la tabella, salta l'inserimento dei metadati
        return
    
    # Inserisci metadati del file
    if file_metadata:
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO file_metadata 
                    (filename, table_name, rows_count, columns_count, file_size_kb, file_type, description)
                    VALUES (:filename, :table_name, :rows_count, :columns_count, :file_size_kb, :file_type, :description)
                """), {
                    'filename': file_metadata.get('filename', 'unknown'),
                    'table_name': table_name,
                    'rows_count': len(df),
                    'columns_count': len(df.columns),
                    'file_size_kb': file_metadata.get('file_size_kb', 0),
                    'file_type': file_metadata.get('file_type', 'unknown'),
                    'description': file_metadata.get('description', '')
                })
                conn.commit()
            logger.info(f"Metadata saved for {file_metadata.get('filename', 'unknown')}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            # Non bloccare il caricamento se i metadati falliscono

def init_metadata_table(db_url):
    """Inizializza la tabella file_metadata se non esiste"""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    table_name VARCHAR(255) NOT NULL,
                    rows_count INTEGER NOT NULL,
                    columns_count INTEGER NOT NULL,
                    file_size_kb FLOAT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type VARCHAR(10),
                    description TEXT
                );
            """))
            conn.commit()
            logger.info("File metadata table initialized successfully")
            return True
    except Exception as e:
        logger.error(f"Error initializing file_metadata table: {e}")
        return False

def get_file_history(db_url):
    """Recupera lo storico dei file caricati"""
    try:
        # Assicurati che la tabella esista
        init_metadata_table(db_url)
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, filename, table_name, rows_count, columns_count, 
                       uploaded_at, file_type, description
                FROM file_metadata 
                ORDER BY uploaded_at DESC
            """))
            return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Error getting file history: {e}")
        return []

def check_file_exists(db_url, filename):
    """Verifica se un file è già stato caricato"""
    try:
        # Assicurati che la tabella esista
        init_metadata_table(db_url)
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count FROM file_metadata 
                WHERE filename = :filename
            """), {'filename': filename})
            return result.fetchone()['count'] > 0
    except Exception as e:
        logger.error(f"Error checking file existence: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        logger.error("Usage: python load.py <csv_path> <table_name> <db_url>")
        exit(1)
    df = pd.read_csv(sys.argv[1])
    load(df, sys.argv[2], sys.argv[3])
