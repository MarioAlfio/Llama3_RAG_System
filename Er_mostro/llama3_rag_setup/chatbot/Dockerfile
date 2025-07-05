FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Copia solo il requirements.txt del chatbot
COPY llama3_rag_setup/chatbot/requirements.txt .

# Installa le dipendenze
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia tutta la struttura llama3_rag_setup (moduli condivisi inclusi)
COPY llama3_rag_setup /app/llama3_rag_setup

WORKDIR /app/llama3_rag_setup/chatbot
ENV PYTHONPATH=/app/llama3_rag_setup/chatbot

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]