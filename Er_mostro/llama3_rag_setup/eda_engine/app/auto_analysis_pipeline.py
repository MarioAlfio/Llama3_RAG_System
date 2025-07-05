# L'output JSON conterrà quindi solo le statistiche delle feature numeriche, 
import pandas as pd
import numpy as np
import json
import io
import psycopg2
from .config import DB_URL
from log_config import logger
from fastapi import HTTPException

class UniversalEDAPipeline:
    """
    Pipeline EDA semplificata: per ora restituisce solo la describe() del DataFrame come output strutturato (JSON).
    """
    def __init__(self, df):
        self.df = df.copy()

    def run_complete_analysis(self):
        # Colonne numeriche
        numeric_cols = [
            col for col in self.df.columns
            if pd.api.types.is_numeric_dtype(self.df[col])
            and not pd.api.types.is_datetime64_any_dtype(self.df[col])
            and not pd.api.types.is_object_dtype(self.df[col])
        ]
        # Colonne categoriche
        categorical_cols = [
            col for col in self.df.columns
            if pd.api.types.is_object_dtype(self.df[col])
        ]
        # Colonne data
        date_cols = [
            col for col in self.df.columns
            if pd.api.types.is_datetime64_any_dtype(self.df[col]) or 'date' in col.lower()
        ]
        result = {
            'describe': self.df[numeric_cols].describe().fillna('').astype(str).to_dict(),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'date_columns': date_cols
        }
        return json.dumps(result, indent=2, default=str)

    def has_object_features(self):
        """
        Restituisce True se ci sono colonne di tipo object (feature categoriche/testuali), altrimenti False.
        """
        object_cols = self.df.select_dtypes(include=['object']).columns
        return len(object_cols) > 0

    def get_object_value_counts(self):
        """
        Restituisce un dizionario con value_counts() per ogni colonna di tipo object (inclusi i NaN),
        dopo aver convertito eventuali colonne data in datetime.
        Esempio: { 'Test Results': { 'Positive': 10, 'Negative': 5, ... } }
        """
        # Prima converto le colonne data
        self.convert_date_columns()
        # Poi calcolo value_counts solo sulle colonne ancora object
        object_cols = self.df.select_dtypes(include=['object']).columns
        value_counts_dict = {}
        for col in object_cols:
            value_counts_dict[col] = self.df[col].value_counts(dropna=False).to_dict()
        return value_counts_dict

    def convert_date_columns(self):
        """
        Cerca colonne che nel nome contengono 'date' (case-insensitive) e le converte in datetime.
        Modifica il DataFrame in-place. Restituisce la lista delle colonne convertite.
        """
        converted = []
        for col in self.df.columns:
            if 'date' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    converted.append(col)
                except Exception:
                    pass
        return converted

# Funzione utility per chiamate esterne

def run_eda_analysis(df):
    pipeline = UniversalEDAPipeline(df)
    return pipeline.run_complete_analysis()

def run_eda_on_file(upload_id, db):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT file_content, filename FROM raw_uploads WHERE id = %s;", (upload_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            logger.error(f"[run_eda_on_file] File non trovato per upload_id={upload_id}")
            raise HTTPException(status_code=404, detail="File not found")
        file_bytes, filename = row
        # Carica in DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_bytes))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_bytes))
            else:
                logger.error(f"[run_eda_on_file] Formato file non supportato: {filename}")
                raise HTTPException(status_code=400, detail="Unsupported file type")
        except Exception as e:
            logger.error(f"[run_eda_on_file] Errore nel caricamento del file: {e}")
            raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
        # Esegui EDA
        pipeline = UniversalEDAPipeline(df)
        return pipeline.run_complete_analysis()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[run_eda_on_file] Errore imprevisto: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
