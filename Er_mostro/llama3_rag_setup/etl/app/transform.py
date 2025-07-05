import logging
import os
import pandas as pd

# Configurazione logging avanzato
logger = logging.getLogger("etl.transform")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
if not os.path.exists("../logs"):
    os.makedirs("../logs")
fh = logging.FileHandler("../logs/transform.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

def transform(df):
    logger.info(f"Transforming DataFrame with {len(df)} rows and {len(df.columns)} columns")
    
    # Crea una copia per evitare modifiche al DataFrame originale
    df_transformed = df.copy()
    
    # Gestione sicura delle colonne datetime
    for col in df_transformed.columns:
        # Se la colonna sembra essere una data
        if df_transformed[col].dtype == 'object':
            # Prova a convertire in datetime
            try:
                # Converti in datetime ignorando timezone
                temp_series = pd.to_datetime(df_transformed[col], errors='coerce', utc=False)
                # Solo se almeno il 50% dei valori sono stati convertiti con successo
                if temp_series.notna().sum() > len(temp_series) * 0.5:
                    df_transformed[col] = temp_series
                    logger.info(f"Converted column {col} to datetime")
                else:
                    logger.info(f"Column {col} has too many invalid dates, keeping as object")
            except Exception as e:
                logger.warning(f"Could not convert column {col} to datetime: {str(e)}")
                continue
    
    # Pulizia generale
    # Rimuovi righe completamente vuote
    initial_rows = len(df_transformed)
    df_transformed = df_transformed.dropna(how='all')
    if len(df_transformed) < initial_rows:
        logger.info(f"Removed {initial_rows - len(df_transformed)} completely empty rows")
    
    # Reset index dopo le modifiche
    df_transformed = df_transformed.reset_index(drop=True)
    
    # Log dei tipi di colonne finali
    logger.info("Final column types:")
    for col in df_transformed.columns:
        logger.info(f"  {col}: {df_transformed[col].dtype}")
    
    logger.info(f"Transformation completed. Final shape: {df_transformed.shape}")
    return df_transformed

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("Usage: python transform.py <csv_path>")
        exit(1)
    df = pd.read_csv(sys.argv[1])
    df_t = transform(df)
    print(df_t.head())
