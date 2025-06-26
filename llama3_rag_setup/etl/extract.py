import pandas as pd
import logging
import os

# Configurazione logging avanzato
logger = logging.getLogger("etl.extract")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
if not os.path.exists("../logs"):
    os.makedirs("../logs")
fh = logging.FileHandler("../logs/extract.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

def extract(file_path):
    logger.info(f"Extracting data from {file_path}")
    
    # Verifica che il file esista
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Verifica che il file non sia vuoto
    if os.path.getsize(file_path) == 0:
        logger.error(f"File is empty: {file_path}")
        raise ValueError(f"File is empty: {file_path}")
    
    try:
        if file_path.endswith('.csv'):
            # Prova prima con encoding utf-8
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                # Se fallisce, prova con latin-1
                df = pd.read_csv(file_path, encoding='latin-1')
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            logger.error("Unsupported file type")
            raise ValueError("Unsupported file type")
        
        # Verifica che il DataFrame non sia vuoto
        if df.empty:
            logger.error("DataFrame is empty after reading")
            raise ValueError("DataFrame is empty after reading")
        
        # Verifica che ci siano colonne
        if len(df.columns) == 0:
            logger.error("No columns found in DataFrame")
            raise ValueError("No columns found in DataFrame")
        
        logger.info(f"Extracted {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("Usage: python extract.py <file_path>")
        exit(1)
    df = extract(sys.argv[1])
    print(df.head())
