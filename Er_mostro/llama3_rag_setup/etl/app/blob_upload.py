# llama3_rag_setup/etl/blob_upload.py
import psycopg2
from psycopg2 import sql
import hashlib
from datetime import datetime
import os
import traceback
from . import config
from log_config import logger

def ensure_table_exists():
    try:
        conn = psycopg2.connect(config.DB_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw_uploads (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                file_hash TEXT,
                user_id TEXT,
                upload_time TIMESTAMP,
                file_content BYTEA
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        logger.info("[ensure_table_exists] Tabella raw_uploads verificata/creata.")
    except Exception as e:
        logger.error(f"[ensure_table_exists] Errore nella creazione/verifica tabella: {e}\n{traceback.format_exc()}")
        raise

# Chiamata all'import del modulo
ensure_table_exists()

def save_file_blob_to_db(file_bytes, filename, user='default'):
    logger.info(f"[save_file_blob_to_db] Inizio salvataggio file: {filename} per user: {user}")
    try:
        file_hash = hashlib.md5(file_bytes).hexdigest()
        timestamp = datetime.now()
        conn = psycopg2.connect(config.DB_URL)
        cur = conn.cursor()
        # La tabella è già garantita da ensure_table_exists()
        cur.execute(
            sql.SQL("""
                INSERT INTO raw_uploads (filename, file_hash, user_id, upload_time, file_content)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """),
            (filename, file_hash, user, timestamp, psycopg2.Binary(file_bytes))
        )
        upload_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"[save_file_blob_to_db] File '{filename}' salvato con successo su DB con id {upload_id}")
        return upload_id
    except Exception as e:
        logger.error(f"[save_file_blob_to_db] Errore nel salvataggio file '{filename}': {e}\n{traceback.format_exc()}")
        raise

def get_uploaded_files_metadata():
    logger.info("[get_uploaded_files_metadata] Recupero lista file caricati")
    try:
        conn = psycopg2.connect(config.DB_URL)
        cur = conn.cursor()
        cur.execute('''
            SELECT id, filename, user_id, upload_time, file_hash FROM raw_uploads ORDER BY upload_time DESC;
        ''')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        files = []
        for row in rows:
            files.append({
                'id': row[0],
                'filename': row[1],
                'user': row[2],
                'upload_time': row[3],
                'file_hash': row[4]
            })
        logger.info(f"[get_uploaded_files_metadata] Trovati {len(files)} file nel DB")
        return files
    except Exception as e:
        logger.error(f"[get_uploaded_files_metadata] Errore nel recupero metadati: {e}\n{traceback.format_exc()}")
        raise

def get_file_blob_by_id(upload_id):
    logger.info(f"[get_file_blob_by_id] Recupero file con id {upload_id}")
    try:
        conn = psycopg2.connect(config.DB_URL)
        cur = conn.cursor()
        cur.execute('''
            SELECT file_content, filename FROM raw_uploads WHERE id = %s;
        ''', (upload_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            logger.info(f"[get_file_blob_by_id] File id {upload_id} recuperato con successo")
            return row[0], row[1]
        else:
            logger.warning(f"[get_file_blob_by_id] Nessun file trovato con id {upload_id}")
            return None, None
    except Exception as e:
        logger.error(f"[get_file_blob_by_id] Errore nel recupero file id {upload_id}: {e}\n{traceback.format_exc()}")
        raise

def delete_file_by_id(upload_id):
    try:
        conn = psycopg2.connect(config.DB_URL)
        cur = conn.cursor()
        
        # Prima elimina i record correlati nella tabella eda_results
        cur.execute('DELETE FROM eda_results WHERE upload_id = %s;', (upload_id,))
        logger.info(f"[delete_file_by_id] Eliminati record correlati per upload_id {upload_id}")
        
        # Poi elimina il file dalla tabella raw_uploads
        cur.execute('DELETE FROM raw_uploads WHERE id = %s;', (upload_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"[delete_file_by_id] File con id {upload_id} eliminato dal DB")
        return True
    except Exception as e:
        logger.error(f"[delete_file_by_id] Errore nell'eliminazione file id {upload_id}: {e}\n{traceback.format_exc()}")
        return False