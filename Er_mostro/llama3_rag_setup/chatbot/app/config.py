import os
from dotenv import load_dotenv

load_dotenv()

EDA_SERVICE_URL = os.getenv("EDA_SERVICE_URL", "http://eda:8002")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ETL_SERVICE_URL = os.getenv("ETL_SERVICE_URL", "http://etl:8001")