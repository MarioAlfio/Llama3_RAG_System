FROM python:3.10-slim

WORKDIR /app

# Copia prima solo requirements.txt per sfruttare la cache di Docker
COPY llama3_rag_setup/requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il contenuto della cartella llama3_rag_setup in /app/llama3_rag_setup
COPY llama3_rag_setup /app/llama3_rag_setup

# Esponi le porte
EXPOSE 8000
EXPOSE 8501

# Avvia Streamlit specificando il percorso completo
CMD ["streamlit", "run", "llama3_rag_setup/scripts/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

